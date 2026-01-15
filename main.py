from nicegui import ui, app
from database import init_db, get_dashboard_stats
from auth import verify_password
from layout import intelligence_layout, get_theme_colors, inject_theme
import registration
import patient_registration
import laboratory
import radiology
import accounting
import archive
import waiting_room
import settings
import doctor
import triage
import pharmacy

def init_app():
    app.add_static_files('/static', 'static')
    init_db()

@ui.page('/login')
def login_page():
    colors = get_theme_colors()
    inject_theme(app.storage.user.get('lang', 'AR'))
    
    with ui.column().classes('w-full h-screen items-center justify-center p-4'):
        # Premium Logo Animation Area
        with ui.column().classes('items-center mb-8 gap-2'):
            ui.label('WELCOME BACK').classes('text-[12px] font-black tracking-[0.4em] opacity-40')
            ui.label('Medical Intelligence').classes('text-3xl font-black text-gradient')

        with ui.element('div').classes('glass-card w-full max-w-[450px] p-12 flex flex-col items-center gap-8'):
            ui.icon('shield', size='4em', color=colors.get('accent', '#2DD4BF')).classes('material-icons-outlined opacity-50 mb-2')
            
            with ui.column().classes('w-full gap-4'):
                username = ui.input(placeholder='Username').classes('w-full modern-input').props('outlined')
                password = ui.input(placeholder='Password', password=True, password_toggle_button=True).classes('w-full modern-input').props('outlined')

            def try_login():
                success, user = verify_password(username.value, password.value)
                if success:
                    app.storage.user.update({
                        'authenticated': True,
                        'username': user['username'],
                        'role': user['role'],
                        'lang': app.storage.user.get('lang', 'AR')
                    })
                    
                    # --- ROLE BASED REDIRECT ---
                    if user['role'] == 'lab':
                        ui.navigate.to('/laboratory')
                    elif user['role'] == 'registration':
                        ui.navigate.to('/patient_registration')
                    else:
                        ui.navigate.to('/')
                else:
                    ui.notify('Invalid Credentials', type='negative', position='top')

            btn_bg = "linear-gradient(135deg, #007AFF, #5AC8FA)" # Crystal Blue Accent

            ui.button('AUTHORIZE ACCESS', on_click=try_login).classes('w-full h-16 rounded-2xl font-black text-white shadow-lg').style(f"background: {btn_bg}")
            
            ui.label('SECURED CLINICAL CORE V3.1').classes('text-[10px] font-black opacity-30 mt-4 tracking-[0.2em]')

@ui.page('/')
def dashboard():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    # Helper to check permissions
    user_role = app.storage.user.get('role', 'user')
    
    # If Lab tries to access dashboard, bounce them back (optional security)
    if user_role == 'lab':
        ui.navigate.to('/laboratory')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'sys_title': 'HealthPro Intelligence', 'reg': 'Registration', 'acc': 'Accounting', 
            'lab': 'Laboratory', 'rad': 'Radiology', 'arch': 'Archive', 'wait': 'Live Monitor',
            'doc': 'Clinic', 'triage': 'Triage', 'set': 'Settings', 'pharma': 'Pharmacy',
            'data': 'Data Tool', 'connect': 'Call Center'
        },
        'AR': {
            'sys_title': 'HealthPro Intelligence', 'reg': 'التسجيل', 'acc': 'الحسابات',
            'lab': 'المختبر', 'rad': 'الأشعة', 'arch': 'فهرس المرضى', 'wait': 'المراقب المباشر',
            'doc': 'العيادة', 'triage': 'الفحص الأولي', 'set': 'الإعدادات', 'pharma': 'الصيدلية',
            'data': 'أداة البيانات', 'connect': 'مركز الاتصال'
        }
    }
    T = TR[lang]

    content = intelligence_layout('sys_title', '', TR, current_nav='/')
    stats = get_dashboard_stats()


    with content:

        # Neo-Tiles Grid (Compacted)
        with ui.grid(columns='repeat(auto-fit, minmax(180px, 1fr))').classes('w-full gap-4 mb-6 max-w-6xl mx-auto'):
            
            def service_card(title_key, icon, color, url, badge=None):
                with ui.link('', url).classes('dynamic-card p-6 flex flex-col items-center gap-4 relative group text-center hover:bg-white/5'):
                    # Badge (Counter)
                    if badge and badge != '0':
                        with ui.element('div').classes('absolute top-2 right-2 bg-red-500 text-white text-[10px] font-black px-1.5 py-0.5 rounded-md z-20 shadow-lg'):
                            ui.label(badge)

                    ui.icon(icon, size='1.4em', color=color).classes('material-icons-outlined transition-transform mb-1')
                    ui.label(T.get(title_key, title_key)).classes('text-[14px] font-black tracking-tight uppercase')

            # Filtered Tiles based on Role
            # Admin gets everything
            is_admin = user_role == 'admin'
            
            if is_admin or user_role == 'registration':
                service_card('reg', 'how_to_reg', '#3498db', '/patient_registration')
                service_card('wait', 'monitor', '#2980b9', '/waiting_room')
            
            if is_admin or user_role == 'accounting':
                service_card('acc', 'payments', '#2ecc71', '/accounting', badge=str(stats.get('pending_accounting', 0)))
            
            if is_admin or user_role in ['doctor', 'nurse']:
                service_card('triage', 'medical_information', '#f1c40f', '/triage', badge=str(stats.get('pending_triage', 0)))
            
            if is_admin or user_role == 'doctor':
                service_card('doc', 'medical_services', '#e67e22', '/doctor', badge=str(stats.get('pending_doctor', 0)))
            
            if is_admin or user_role == 'lab':
                service_card('lab', 'science', '#9b59b6', '/laboratory', badge=str(stats.get('pending_labs', 0)))
            
            if is_admin or user_role == 'radiology':
                service_card('rad', 'visibility', '#34495e', '/radiology', badge=str(stats.get('pending_rads', 0)))
            
            if is_admin or user_role == 'pharmacy':
                service_card('pharma', 'medication', '#27ae60', '/pharmacy', badge=str(stats.get('pending_pharmacy', 0)))
            
            if is_admin:
                service_card('arch', 'groups', '#16a085', '/archive')
                service_card('data', 'bar_chart', '#c0392b', '/settings')
                service_card('connect', 'support_agent', '#8e44ad', '#')
                service_card('set', 'tune', '#7f8c8d', '/settings')




init_app()
ui.run(storage_secret='HS_31_SECRET', port=8080)