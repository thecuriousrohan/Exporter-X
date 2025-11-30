import adsk.core, adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
from .. import shared_nav
import re

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_folderExport3D'
CMD_NAME = '3D Export (Folder)'
CMD_Description = 'Export all 3D designs from a selected folder.'
IS_PROMOTED = True

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')
MAX_DEPTH = 10

local_handlers = []

def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    futil.add_handler(cmd_def.commandCreated, command_created)
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
    control.isPromoted = IS_PROMOTED

def stop():
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    if panel:
        cmd_ctrl = panel.controls.itemById(CMD_ID)
        if cmd_ctrl: cmd_ctrl.deleteMe()
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def: cmd_def.deleteMe()

def command_created(args: adsk.core.CommandCreatedEventArgs):
    inputs = args.command.commandInputs
    
    proj_dd = inputs.addDropDownCommandInput('target_project', 'Target Project', adsk.core.DropDownStyles.TextListDropDownStyle)
    for project in app.data.dataProjects:
        proj_dd.listItems.add(project.name, False)
    
    for i in range(MAX_DEPTH):
        dd = inputs.addDropDownCommandInput(f'subfolder_{i}', f'Subfolder {i+1}', adsk.core.DropDownStyles.TextListDropDownStyle)
        dd.isVisible = False
        dd.listItems.add('Select...', True)
        
    fmt_dd = inputs.addDropDownCommandInput('out_format', 'Output Format', adsk.core.DropDownStyles.TextListDropDownStyle)
    fmt_dd.listItems.add('STEP', True)
    fmt_dd.listItems.add('STL', False)
    fmt_dd.listItems.add('OBJ', False)
    
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

    active_doc = app.activeDocument
    data_ref = active_doc.dataFile if active_doc else None
    shared_nav.initialize_navigation(inputs, data_ref)

def command_input_changed(args: adsk.core.InputChangedEventArgs):
    inputs = args.inputs
    changed_id = args.input.id
    if changed_id == 'target_project' or changed_id.startswith('subfolder_'):
        shared_nav.update_subfolders(inputs, changed_id)

def command_execute(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    out_format = inputs.itemById('out_format').selectedItem.name
    
    start_folder = shared_nav.get_selected_folder(inputs)
    if not start_folder:
        ui.messageBox('Target folder is invalid.')
        return
        
    app.log(f'Scanning folder {start_folder.name} for 3D designs...')
    
    matched_documents = []
    for df in start_folder.dataFiles:
        # only grab 3D designs, ignore 2d drawings
        if df.fileExtension == 'f3d':
            matched_documents.append({'name': df.name, 'id': df.id})
            
    if not matched_documents:
        ui.messageBox('No 3D designs found in the selected folder.')
        return
        
    dest_dlg = ui.createFolderDialog()
    dest_dlg.title = 'Choose Destination Directory'
    if dest_dlg.showDialog() != adsk.core.DialogResults.DialogOK:
        return
    output_dir = dest_dlg.folder
    
    if ui.messageBox(f'Found {len(matched_documents)} files in {start_folder.name}.\nContinue with Export?', 'Confirm Folder Export', adsk.core.MessageBoxButtonTypes.YesNoButtonType) != adsk.core.DialogResults.DialogYes:
        return
        
    app.log(f'Exporting {len(matched_documents)} files to {output_dir}...')
    
    wins = 0
    losses = 0
    
    for i, doc_info in enumerate(matched_documents):
        n = doc_info['name']
        did = doc_info['id']
        app.log(f'[{i+1}/{len(matched_documents)}] Processing: {n}')
        
        opened_doc = None
        should_close = False
        try:
            cloud_file = app.data.findFileById(did)
            if not cloud_file:
                app.log(f'  Error: File ID {did} missing from cloud.')
                losses += 1
                continue
                
            opened_doc = app.documents.open(cloud_file, False)
            design_prod = opened_doc.products.itemByProductType('DesignProductType')
            should_close = True
            
            if not design_prod:
                app.log('  Skipped: File is not a 3D design.')
                losses += 1
                continue
                
            exporter = design_prod.exportManager
            clean_name = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', n) 
            final_path = os.path.join(output_dir, clean_name)
            
            if out_format == 'STEP':
                final_path += '.stp'
                opt = exporter.createSTEPExportOptions(final_path)
                exporter.execute(opt)
            elif out_format == 'STL':
                final_path += '.stl'
                opt = exporter.createSTLExportOptions(design_prod.rootComponent, final_path)
                opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
                exporter.execute(opt)
            elif out_format == 'OBJ':
                final_path += '.obj'
                opt = exporter.createOBJExportOptions(design_prod.rootComponent, final_path)
                opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
                exporter.execute(opt)
                
            wins += 1
            app.log('  Done.')
            
        except Exception as e:
            app.log(f'  Failed: {str(e)}')
            losses += 1
        finally:
            if should_close and opened_doc:
                try: opened_doc.close(False)
                except: pass
                
        adsk.doEvents()
        
    ui.messageBox(f'Folder Export Finished!\nSuccessfully processed {wins} files.\nErrors/Skipped: {losses}\nCheck Text Commands for logs.')

def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
