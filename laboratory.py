from nicegui import ui, app
import random
from database import (
    get_pending_labs, complete_lab, get_all_patients, 
    add_lab_request, get_pending_verification_labs, certify_lab_result
)
from layout import intelligence_layout, get_theme_colors

@ui.page('/laboratory')
def laboratory_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    user_name = app.storage.user.get('username', 'Lab Tech')
    
    TR = {
        'EN': {
            'header': 'BioTech Lab 4.0', 'sub': 'Smart Diagnostic Center & Molecular Validation',
            'bench': 'LAB BENCH', 'verification': 'VALIDATION CENTRE', 'new_req': 'NEW REQUEST',
            'save': 'VALIDATE RESULT', 'empty': 'Zero active diagnostic cycles',
            'create': 'INITIATE LAB PROTOCOL', 'test_type': 'Diagnostic Parameter',
            'patient': 'Target Identity', 'role_badge': 'LAB DIRECTOR',
            'auto_fetch': 'SIMULATE MACHINE SYNC', 'certify': 'CERTIFY & UPLOAD',
            'critical': 'CRITICAL VALUE DETECTED', 'normal': 'Normal Range'
        },
        'AR': {
            'header': 'مختبر التحليلات 4.0', 'sub': 'مركز التشخيص الذكي والتحقق الجزيئي',
            'bench': 'منصة الفحوصات', 'verification': 'مركز المصادقة', 'new_req': 'طلب جديد',
            'save': 'تصديق النتيجة', 'empty': 'لا توجد فحوصات قيد المعالجة',
            'create': 'إنشاء طلب تحليل جديد', 'test_type': 'المعامل المطلوب فحصها',
            'patient': 'هوية المريض', 'role_badge': 'مدير المختبر',
            'auto_fetch': 'مزامنة الجهاز (محاكاة)', 'certify': 'تصديق ورفع النتائج',
            'critical': 'قيمة حرجة مكتشفة!', 'normal': 'النطاق الطبيعي'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/laboratory')

    # --- STATE MANAGEMENT ---
    class LabState:
        active_tab = 'bench'
        selected_p = {'id': None, 'name': 'No Patient Selected'}
    
    S = LabState()

    with content:
        with ui.column().classes('w-full max-w-7xl mx-auto gap-8'):
            
            # --- TOP TABS CONTROL ---
            @ui.refreshable
            def render_tabs():
                with ui.row().classes('w-full justify-center gap-4 mb-4'):
                    def tab_link(key, icon, label):
                        is_active = S.active_tab == key
                        def set_tab(k):
                            S.active_tab = k
                            render_tabs.refresh()
                            render_content.refresh()

                        with ui.button(on_click=lambda k=key: set_tab(k)) \
                            .classes(f"px-6 h-12 rounded-xl font-black transition-all {'text-white' if is_active else 'opacity-50'}") \
                            .style(f"background: {f'linear-gradient(135deg, {colors.get('accent', '#8B5CF6')}, {colors.get('accent_secondary', '#D946EF')})' if is_active else 'rgba(255,255,255,0.05)'}"):
                            ui.icon(icon, size='sm').classes('mr-2')
                            ui.label(label)

                    tab_link('new', 'o_add_circle', T['new_req'])
                    tab_link('bench', 'o_biotech', T['bench'])
                    tab_link('verify', 'o_verified', T['verification'])
            
            render_tabs()

            # --- MAIN CONTENT AREA ---
            @ui.refreshable
            def render_content():
                # A. NEW REQUEST
                if S.active_tab == 'new':
                    with ui.column().classes('w-full items-center'):
                        with ui.column().classes('glass-card p-12 gap-8 w-full max-w-2xl'):
                            ui.label(T['create']).classes('text-[10px] font-black opacity-40 tracking-[0.4em] text-center w-full')
                            
                            # Search Patient
                            search_input = ui.input(placeholder='Search Patient Name/ID').classes('modern-input w-full').props('outlined prepend-inner-icon=search')
                            results_container = ui.column().classes('w-full gap-2 max-h-40 overflow-y-auto hidden bg-black/20 p-2 rounded-xl')

                            def on_search(e):
                                term = e.value.lower()
                                results_container.clear()
                                if len(term) < 1:
                                    results_container.set_visibility(False)
                                    return
                                results_container.set_visibility(True)
                                matches = [p for p in get_all_patients() if term in p['name'].lower() or term in str(p['id'])][:5]
                                with results_container:
                                    for p in matches:
                                        def select_this_p(patient=p):
                                            S.selected_p = patient
                                            results_container.set_visibility(False)
                                            search_input.set_value('')
                                            render_content.refresh()
                                        ui.button(f"{p['name']} ({p['id']})", on_click=select_this_p) \
                                            .props('flat no-caps align=left').classes('w-full text-left font-bold text-sm')

                            search_input.on('update:model-value', on_search)

                            with ui.row().classes('w-full items-center gap-4 bg-black/5 p-4 rounded-xl border border-black/5'):
                                ui.icon('person', size='md', color=colors.get('accent'))
                                p_label = f"{S.selected_p['name']} (ID: {S.selected_p['id']})" if S.selected_p['id'] else S.selected_p['name']
                                ui.label(p_label).classes('font-bold')

                            t_input = ui.input(placeholder=T['test_type'] + ' (e.g. CBC, Glucose, TSH)').classes('modern-input w-full h-14 font-black p-4').props('outlined')
                            
                            def submit_protocol():
                                if not S.selected_p['id'] or not t_input.value:
                                    ui.notify('Mandatory Fields Missing', type='warning')
                                    return
                                add_lab_request(S.selected_p['id'], t_input.value)
                                ui.notify('✓ Protocol Initialized', type='positive')
                                t_input.set_value('')
                                S.active_tab = 'bench'
                                render_tabs.refresh()
                                render_content.refresh()

                            ui.button(T['create'], icon='send', on_click=submit_protocol).classes('w-full h-16 rounded-2xl font-black text-white').style(f"background: {colors.get('gradient')}")

                # B. LAB BENCH (Pending Entry)
                elif S.active_tab == 'bench':
                    labs = get_pending_labs()
                    if not labs:
                        with ui.column().classes('w-full items-center py-40 opacity-20'):
                            ui.icon('science', size='6em')
                            ui.label(T['empty']).classes('font-black tracking-widest uppercase')
                    else:
                        with ui.grid(columns=2).classes('w-full gap-6'):
                            for lab in labs:
                                with ui.column().classes('glass-card p-6 gap-4 border-l-4').style(f"border-color: {colors.get('accent')}"):
                                    with ui.row().classes('w-full justify-between items-center'):
                                        ui.label(lab['patient_name']).classes('text-xl font-black tracking-tight')
                                        ui.button(icon='print', on_click=lambda: ui.notify('Barcode Printing...')).props('flat round size=sm').tooltip('Print Tube Barcode')
                                    
                                    ui.label(lab['test_type']).classes('text-[10px] font-black uppercase tracking-[0.2em] opacity-40')
                                    
                                    with ui.row().classes('w-full gap-2 items-end'):
                                        res_field = ui.input('Result Value').classes('modern-input flex-grow').props('outlined dense')
                                        ui.button(icon='sync', on_click=lambda l=lab, r=res_field: simulate_machine(l, r)).classes('h-10 w-10 material-icons-outlined').props('flat').tooltip(T['auto_fetch'])
                                        ui.button(icon='check', on_click=lambda l=lab, r=res_field: submit_bench(l['id'], r.value)).classes('h-10 w-12 rounded-lg text-white').style(f"background: {colors.get('accent')}")

                # C. VALIDATION CENTRE (Director Approval)
                elif S.active_tab == 'verify':
                    v_labs = get_pending_verification_labs()
                    if not v_labs:
                        ui.label('No results pending validation.').classes('opacity-30 italic p-10')
                    else:
                        for v in v_labs:
                            is_critical = False
                            try:
                                num = float(v['result'].split()[0])
                                if num > 400 or num < 40: is_critical = True
                            except: pass

                            with ui.row().classes('w-full glass-card p-6 items-center justify-between border-l-4 ' + ('border-red-500 bg-red-500/5' if is_critical else 'border-green-500')):
                                with ui.column().classes('gap-1'):
                                    with ui.row().classes('items-center gap-3'):
                                        ui.label(v['patient_name']).classes('font-black text-lg')
                                        if is_critical:
                                             with ui.row().classes('items-center bg-red-500 px-2 py-0.5 rounded gap-1'):
                                                 ui.icon('warning', size='14px', color='white')
                                                 ui.label(T['critical']).classes('text-[8px] font-black text-white')
                                    
                                    ui.label(f"{v['test_type']}: {v['result']} ({v['normal_range']})").classes('text-xs font-bold opacity-70')
                                    ui.label(f"Machine: {v['machine_id']}").classes('text-[10px] opacity-40')
                                
                                ui.button(T['certify'], icon='verified', on_click=lambda rid=v['id']: certify_now(rid)) \
                                    .classes('rounded-xl font-bold bg-emerald-600/20 text-emerald-500 border border-emerald-500/30 hover:bg-emerald-600 hover:text-white')

            def simulate_machine(lab, field):
                mock_data = {
                    'CBC': f"{random.randint(12, 17)} g/dL",
                    'Glucose': f"{random.randint(70, 450)} mg/dL",
                    'TSH': f"{round(random.uniform(0.5, 5.0), 2)} mUI/L"
                }
                field.set_value(mock_data.get(lab['test_type'], f"{random.randint(1, 100)} unit"))
                ui.notify(f"✓ {lab['test_type']} Machine Sync Complete", type='info')

            def submit_bench(rid, val):
                if not val: return
                complete_lab(rid, val, normal_range="See Dept. Standard", machine_id="Mindray-B320")
                ui.notify('Result Sent for Validation', type='positive')
                render_content.refresh()

            def certify_now(rid):
                certify_lab_result(rid, user_name)
                ui.notify('✓ Laboratory Diagnostic Certified', type='positive')
                render_content.refresh()

            render_content()
