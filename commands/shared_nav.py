import adsk.core
app = adsk.core.Application.get()
MAX_DEPTH = 10

def initialize_navigation(inputs, data_ref):
    proj_dd = inputs.itemById('target_project')
    if data_ref:
        active_proj = data_ref.parentProject.name
        found = False
        for i in range(proj_dd.listItems.count):
            if proj_dd.listItems.item(i).name == active_proj:
                proj_dd.listItems.item(i).isSelected = True
                found = True
                break
        if found:
            update_subfolders(inputs, 'target_project')
            chain = []
            parent = data_ref.parentFolder
            while parent and not parent.isRoot:
                chain.insert(0, parent.name)
                parent = parent.parentFolder
            for lvl, fname in enumerate(chain):
                if lvl >= MAX_DEPTH: break
                dd_id = f'subfolder_{lvl}'
                dd = inputs.itemById(dd_id)
                if not dd or not dd.isVisible: break
                f_found = False
                for item in dd.listItems:
                    if item.name == fname:
                        item.isSelected = True
                        f_found = True
                        break
                if f_found:
                    update_subfolders(inputs, dd_id)
    else:
        if proj_dd.listItems.count > 0:
            proj_dd.listItems.item(0).isSelected = True
            update_subfolders(inputs, 'target_project')

def update_subfolders(inputs, changed_id):
    proj_dd = inputs.itemById('target_project')
    if not proj_dd.selectedItem: return
    selected_proj = proj_dd.selectedItem.name
    
    target_proj = None
    for p in app.data.dataProjects:
        if p.name == selected_proj:
            target_proj = p
            break
    if not target_proj: return

    if changed_id == 'target_project':
        fill_dropdown(inputs, 0, target_proj.rootFolder)
        hide_dropdowns(inputs, 1)
        
    elif changed_id.startswith('subfolder_'):
        idx = int(changed_id.split('_')[-1])
        dd = inputs.itemById(changed_id)
        sel_name = dd.selectedItem.name if dd.selectedItem else None
        
        if not sel_name or sel_name == 'Select...':
            hide_dropdowns(inputs, idx + 1)
            return
            
        cur_folder = target_proj.rootFolder
        for i in range(idx + 1):
            curr_dd = inputs.itemById(f'subfolder_{i}')
            val = curr_dd.selectedItem.name
            if val == 'Select...': return
            matched = None
            for f in cur_folder.dataFolders:
                if f.name == val:
                    matched = f
                    break
            if matched: cur_folder = matched
            else: return 
        
        if idx + 1 < MAX_DEPTH:
            fill_dropdown(inputs, idx + 1, cur_folder)
            hide_dropdowns(inputs, idx + 2)

def fill_dropdown(inputs, lvl, parent_f):
    dd = inputs.itemById(f'subfolder_{lvl}')
    dd.listItems.clear()
    dd.listItems.add('Select...', True)
    
    subs = []
    try:
        for f in parent_f.dataFolders:
            subs.append(f.name)
    except Exception as e:
        app.log(f'Warning reading folders: {str(e)}')
    subs.sort()
    
    if subs:
        for n in subs: dd.listItems.add(n, False)
        dd.isVisible = True
    else:
        dd.isVisible = False 

def hide_dropdowns(inputs, start_lvl):
    for i in range(start_lvl, MAX_DEPTH):
        dd = inputs.itemById(f'subfolder_{i}')
        dd.listItems.clear()
        dd.isVisible = False
        dd.listItems.add('Select...', True)

def get_selected_folder(inputs):
    p_name = inputs.itemById('target_project').selectedItem.name
    t_proj = None
    for p in app.data.dataProjects:
        if p.name == p_name:
            t_proj = p
            break
    if not t_proj: return None

    s_folder = t_proj.rootFolder
    for i in range(MAX_DEPTH):
        dd = inputs.itemById(f'subfolder_{i}')
        if not dd.isVisible: break
        sel = dd.selectedItem
        if not sel or sel.name == 'Select...': break
        
        matched = None
        for f in s_folder.dataFolders:
            if f.name == sel.name:
                matched = f
                break
        if matched: s_folder = matched
        else: break
    return s_folder
