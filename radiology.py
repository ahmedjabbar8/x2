from nicegui import ui, app
from database import get_pending_rads, complete_rad, get_all_patients, add_rad_request
from layout import intelligence_layout, get_theme_colors

@ui.page('/radiology')
def radiology_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Imaging Intelligence', 'sub': 'Precision Radiology & Digital Diagnostics',
            'save': 'VALIDATE & UPLOAD REPORT', 'empty': 'Zero pending radiological scans',
            'create': 'INITIATE IMAGING REQUEST', 'test_type': 'Imaging Protocol',
            'patient': 'Target Identity', 'role_badge': 'RADIOLOGIST'
        },
        'AR': {
            'header': 'قسم الأشعة الرقمي', 'sub': 'التشخيص الصوري والتحليل الإشعاعي الرقمي',
            'save': 'تصديق ورفع التقرير', 'empty': 'لا توجد فحوصات قيد المعالجة',
            'create': 'إنشاء طلب فحص جديد', 'test_type': 'نوع البروتوكول الصوري',
            'patient': 'هوية المريض', 'role_badge': 'تقني الأشعة'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/radiology')

    with content:
        with ui.grid(columns=12).classes('w-full gap-10'):
            
            # Left: Imaging Initiation
            with ui.column().classes('col-span-4 gap-6'):
                ui.label(T['create']).classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                with ui.column().classes('glass-card p-8 gap-8'):
                    patients = get_all_patients()
                    p_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in patients}
                    
                    p_select = ui.select(p_options, label=T['patient']).classes('modern-input w-full').props('outlined')
                    s_select = ui.select(['X-Ray', 'MRI', 'CT Scan', 'Ultrasound'], label=T['test_type']).classes('modern-input w-full').props('outlined')
                    
                    def add_req():
                        if not p_select.value or not s_select.value:
                            ui.notify('Mandatory imaging data missing', type='warning', position='top')
                            return
                        add_rad_request(p_select.value, s_select.value)
                        ui.notify('✓ Imaging Cycle Initiated', type='positive', position='top')
                        s_select.value = None
                        refresh_pending()

                    with ui.button(on_click=add_req).classes('w-full h-16 rounded-2xl font-black text-white').style(f"background: linear-gradient(135deg, {colors['accent']}, {colors['accent_secondary']})"):
                        ui.icon('o_settings_overscan', size='sm').classes('material-icons-outlined mr-2')
                        ui.label('INITIATE')

            # Right: Active Scans
            with ui.column().classes('col-span-8 gap-6'):
                ui.label('PENDING RADIOLOGICAL STREAMS').classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                pending_container = ui.column().classes('w-full gap-4')

    def refresh_pending():
        pending_container.clear()
        with pending_container:
            rads = get_pending_rads()
            if not rads:
                with ui.element('div').classes('glass-card w-full py-32 flex flex-col items-center justify-center opacity-10'):
                    ui.icon('o_visibility', size='5em').classes('material-icons-outlined')
                    ui.label(T['empty']).classes('text-sm font-black mt-4 italic tracking-widest')
            else:
                for req in rads:
                    with ui.element('div').classes('glass-card w-full p-8 group'):
                        with ui.row().classes('w-full justify-between items-center mb-8'):
                            with ui.column().classes('gap-1'):
                                ui.label(req['patient_name']).classes('font-black text-2xl group-hover:text-gradient')
                                with ui.row().classes('items-center gap-3'):
                                    ui.icon('o_camera', size='18px', color=colors['accent_secondary']).classes('material-icons-outlined opacity-50')
                                    ui.label(req['scan_type']).classes('text-[10px] font-black uppercase tracking-[0.2em] opacity-60')
                            
                            with ui.row().classes('items-center px-4 py-1.5 rounded-full border border-purple-500/20 bg-purple-500/5'):
                                ui.label('IMAGING').classes('text-[9px] font-black text-purple-400 tracking-widest')
                        
                        # Report Injection
                        with ui.column().classes('w-full gap-4'):
                            report = ui.textarea(placeholder='Inject radiological findings for certification...').classes('modern-input w-full h-32 font-bold p-4').props('outlined')
                            ui.button(T['save'], icon='o_cloud_upload', on_click=lambda id=req['id'], r=report: submit_report(id, r.value)).classes('w-full h-14 rounded-xl font-black text-white').style(f"background: linear-gradient(135deg, {colors['accent']}, {colors['accent_secondary']})")

    def submit_report(req_id, report_val):
        if not report_val:
            ui.notify('Validation failed: Findings required', type='warning', position='top')
            return
        complete_rad(req_id, report_val)
        ui.notify('✓ Radiological Report Certified', type='positive', position='top')
        refresh_pending()

    refresh_pending()
