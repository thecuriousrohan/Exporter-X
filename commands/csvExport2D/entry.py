import adsk.core, adsk.fusion, adsk.drawing
import os
import csv
from ...lib import fusionAddInUtils as futil
from ... import config
from .. import shared_nav
import re

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_csvExport2D'
CMD_NAME = '2D Export (CSV)'
CMD_Description = 'Export 2D drawings listed in a CSV file from a selected folder.'
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
        if cmd_ctrl:
            cmd_ctrl.deleteMe()
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def:
        cmd_def.deleteMe()

def command_created(args: adsk.core.CommandCreatedEventArgs):
    inputs = args.command.commandInputs
    
    inp_csv = inputs.addStringValueInput('import_csv_path', 'Import List (.csv)', '')
    inp_csv.isReadOnly = True
    inputs.addBoolValueInput('browse_csv_btn', 'Browse...', False, '', True)

    proj_dd = inputs.addDropDownCommandInput('target_project', 'Target Project', adsk.core.DropDownStyles.TextListDropDownStyle)
    for project in app.data.dataProjects:
        proj_dd.listItems.add(project.name, False)
    
    for i in range(MAX_DEPTH):
        dd = inputs.addDropDownCommandInput(f'subfolder_{i}', f'Subfolder {i+1}', adsk.core.DropDownStyles.TextListDropDownStyle)
        dd.isVisible = False
        dd.listItems.add('Select...', True)
        
    fmt_dd = inputs.addDropDownCommandInput('out_format', 'Output Format', adsk.core.DropDownStyles.TextListDropDownStyle)
    fmt_dd.listItems.add('PDF', True)
    fmt_dd.listItems.add('DXF', False)
    fmt_dd.listItems.add('DWG', False)
    
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

    active_doc = app.activeDocument
    data_ref = active_doc.dataFile if active_doc else None
    shared_nav.initialize_navigation(inputs, data_ref)

def command_input_changed(args: adsk.core.InputChangedEventArgs):
    inputs = args.inputs
    changed_id = args.input.id
    
    if changed_id == 'browse_csv_btn':
        dialog = ui.createFileDialog()
        dialog.title = 'Select CSV Target List'
        dialog.filter = 'CSV Files (*.csv);;All Files (*.*)'
        if dialog.showOpen() == adsk.core.DialogResults.DialogOK:
            inputs.itemById('import_csv_path').value = dialog.filename

    elif changed_id == 'target_project' or changed_id.startswith('subfolder_'):
        shared_nav.update_subfolders(inputs, changed_id)

def command_execute(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    csv_path = inputs.itemById('import_csv_path').value
    out_format = inputs.itemById('out_format').selectedItem.name
    
    if not os.path.exists(csv_path):
        ui.messageBox('Selected CSV file could not be found.')
        return

    csv_targets = set()
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    csv_targets.add(row[0].strip())
    except Exception as e:
        ui.messageBox(f'Failed to parse CSV:\n{str(e)}')
        return
        
    if not csv_targets:
        ui.messageBox('The CSV list is empty.')
        return

    start_folder = shared_nav.get_selected_folder(inputs)
    if not start_folder:
        ui.messageBox('Target folder is invalid.')
        return
        
    ui.messageBox(f'Initiating search for {len(csv_targets)} DRAWINGS...\nProgress will be shown in the Text Command window.')
    
    search_metrics = {'dir_count': 0}
    matched_documents = []
    lookup_set = csv_targets.copy() 
    
    def search_directories(fldr):
        search_metrics['dir_count'] += 1
        if search_metrics['dir_count'] % 5 == 0:
            app.log(f'Scanning: {search_metrics["dir_count"]} directories searched, Located {len(matched_documents)} of {len(csv_targets)}')
            adsk.doEvents()

        for df in fldr.dataFiles:
            if df.fileExtension == 'f2d' and df.name in lookup_set:
                # Avoid duplicates
                if not any(d['id'] == df.id for d in matched_documents):
                    matched_documents.append({'name': df.name, 'id': df.id})
                else:
                    app.log(f"Warning: duplicate file {df.name} found and skipped.")
        
        for sub in fldr.dataFolders:
            search_directories(sub)
            
    try:
        search_directories(start_folder)
    except Exception as e:
        ui.messageBox(f'Search interrupted:\n{str(e)}')
        return

    if not matched_documents:
        ui.messageBox('No matching drawings found in the selected folder.')
        return
        
    dest_dlg = ui.createFolderDialog()
    dest_dlg.title = 'Choose Destination Directory'
    if dest_dlg.showDialog() != adsk.core.DialogResults.DialogOK:
        return
    output_dir = dest_dlg.folder
    
    if ui.messageBox(f'Located {len(matched_documents)} drawings ready for export.\nContinue?', 'Confirm Export', adsk.core.MessageBoxButtonTypes.YesNoButtonType) != adsk.core.DialogResults.DialogYes:
        return
        
    app.log(f'Exporting {len(matched_documents)} drawings to {output_dir}...')
    
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
                
            app.log(f'  Opening document...')
            opened_doc = app.documents.open(cloud_file)
            should_close = True
            
            app.log(f'  Activating document...')
            opened_doc.activate()
            adsk.doEvents()
            
            drawing_prod = adsk.drawing.Drawing.cast(app.activeProduct)
            if not drawing_prod:
                app.log('  Error: Could not cast to Drawing.')
                losses += 1
                continue
                
            exporter = drawing_prod.exportManager
            clean_name = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', n) 
            final_path = os.path.join(output_dir, clean_name)
            
            app.log(f'  Starting Export to {out_format}...')
            
            if out_format == 'PDF':
                final_path += '.pdf'
                opt = exporter.createPDFExportOptions(final_path)
                opt.sheetsToExport = adsk.drawing.PDFSheetsExport.AllPDFSheetsExport
                exporter.execute(opt)
            elif out_format == 'DXF':
                final_path += '.dxf'
                opt = exporter.createDXFExportOptions(final_path)
                exporter.execute(opt)
            elif out_format == 'DWG':
                final_path += '.dwg'
                opt = exporter.createDWGExportOptions(final_path)
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
        
    ui.messageBox(f'Export Finished!\nSuccessfully processed {wins} drawings.\nErrors: {losses}\nCheck Text Commands for logs.')

def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
