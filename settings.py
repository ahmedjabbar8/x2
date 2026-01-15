from nicegui import ui, app
from database import get_setting, set_setting, get_settings_by_category
from layout import intelligence_layout, get_theme_colors

@ui.page('/settings')
def settings_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    # Restricted Access Logic
    user_role = app.storage.user.get('role', 'user')
    if user_role not in ['admin', 'manager']:
        ui.notify('Restricted Access: Administrative Privileges Required', type='negative', position='top')
        ui.navigate.to('/')
        return


    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    # Translation Dictionary
    TR = {
        'EN': {
            'header': 'Smart Settings Center',
            'sub': 'System Intelligence & Global Configuration',
            'save': 'Save',
            'back': 'Back',
            'categories': {
                'lis': 'LIS 4.0 (Laboratory)',
                'physician': 'Physician Intel',
                'ai': 'AI & Analytics',
                'reg': 'Registration',
                'rbac': 'Permissions',
                'finance': 'Finance',
                'triage': 'Triage & Vitals',
                'rad': 'Radiology',
                'global': 'System Settings',
                'maint': 'Maintenance',
                'remote': 'Remote Core'
            }
        },
        'AR': {
            'header': 'مركز الإعدادات الذكي',
            'sub': 'ذكاء النظام والتكوين الشامل',
            'save': 'حفظ',
            'back': 'رجوع',
            'categories': {
                'lis': 'نظام المختبر الآلي 4.0',
                'physician': 'ذكاء الطبيب السريري',
                'ai': 'الذكاء الاصطناعي والتحليلات',
                'reg': 'التسجيل والتعريب',
                'rbac': 'الأدوار والصلاحيات',
                'finance': 'الحسابات والمالية',
                'triage': 'الفرز الفوري والعلامات الحيوية',
                'rad': 'الأشعة والأرشفة الصورية',
                'global': 'إعدادات النظام العامة',
                'maint': 'صيانة النظام',
                'remote': 'التحكم عن بعد'
            }
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/settings')

    # State Management for Navigation
    class SettingsState:
        current_view = 'grid' # 'grid' or 'details'
        selected_category = 'lis'
    
    s_state = SettingsState()

    with content:
        @ui.refreshable
        def render_settings_ui():
            # --- VIEW 1: CATEGORY GRID ---
            if s_state.current_view == 'grid':
                with ui.column().classes('w-full max-w-5xl mx-auto gap-6 items-center py-12'):
                    
                    with ui.grid(columns='repeat(auto-fit, minmax(160px, 1fr))').classes('w-full gap-5'):
                        def category_card(key, icon, icon_color):
                            with ui.column().classes('glass-card p-6 items-center justify-center gap-3 cursor-pointer text-center border border-black/5 hover:bg-blue-50') \
                                .on('click', lambda: (setattr(s_state, 'current_view', 'details'), setattr(s_state, 'selected_category', key), render_settings_ui.refresh())):
                                
                                ui.icon(icon, size='1.0em', color=icon_color).classes('material-icons-outlined mb-1')
                                ui.label(T['categories'][key]).classes('text-[11px] font-black tracking-tight uppercase').style(f"color: {colors['text']}")
                                pass

                        category_card('lis', 'biotech', '#9b59b6')
                        category_card('physician', 'medical_services', '#e67e22')
                        category_card('ai', 'psychology', '#8e44ad')
                        category_card('reg', 'how_to_reg', '#3498db')
                        category_card('rbac', 'admin_panel_settings', '#c0392b')
                        category_card('finance', 'monetization_on', '#2ecc71')
                        category_card('triage', 'emergency', '#f1c40f')
                        category_card('rad', 'visibility', '#34495e')
                        category_card('global', 'settings_applications', '#7f8c8d')
                        category_card('maint', 'settings_suggest', '#16a085')
                        category_card('remote', 'phone_iphone', '#3498db')

            # --- VIEW 2: CATEGORY DETAILS (Full Page Compact) ---
            else:
                with ui.column().classes('w-full min-h-screen px-10 py-6 gap-6 relative'):
                    accent_col = colors['accent']
                    
                    # 1. Back Button (Compact)
                    ui.button(on_click=lambda: (setattr(s_state, 'current_view', 'grid'), render_settings_ui.refresh())) \
                        .props('icon=arrow_back round unelevated size=sm') \
                        .classes('fixed top-20 left-10 z-50 shadow-md') \
                        .style(f"background: {colors['card']}; color: {accent_col}; border: 1px solid {colors['border']};")

                    # 2. Save Button (Checkmark)
                    ui.button(on_click=lambda: ui.notify(f'✓ Updated {T["categories"][s_state.selected_category]}', type='positive', color=accent_col)) \
                        .props('icon=check round unelevated size=md') \
                        .classes('fixed bottom-8 right-8 shadow-2xl z-50') \
                        .style(f"background: {colors['gradient']}; color: white;")

                    # Header (Compact)
                    with ui.column().classes('w-full items-center mb-10'):
                        ui.label(T['categories'][s_state.selected_category]).classes('text-2xl font-black uppercase tracking-tighter') \
                            .style(f"color: {accent_col};")

                    cat = s_state.selected_category

                    # Detail Content Section (Full Width Polish)
                    with ui.column().classes('w-full max-w-4xl mx-auto gap-8'):
                        
                        # --- LIS SETTINGS ---
                        if cat == 'lis':
                            with ui.grid(columns=2).classes('w-full gap-8'):
                                with ui.column().classes('gap-4 p-6 glass-card border border-white/5'):
                                    ui.label('HARDWARE CONNECTIVITY').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.input('Machine IP', placeholder='192.168.10.50').classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                    ui.input('COM Port / TCP', placeholder='Port 8000').classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                    ui.select(['ASTM E1394', 'HL7 v2.5', 'Proprietary'], label='Protocol', value='ASTM E1394').classes('w-full').props(f'outlined color={accent_col} dense')
                                
                                with ui.column().classes('gap-4 p-6 glass-card border border-white/5'):
                                    ui.label('AUTOMATION LOGIC').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.switch('Auto-Fetch Result', value=True).props(f'color={accent_col} size=sm')
                                    ui.switch('Panic Limit Detection', value=True).props(f'color={accent_col} size=sm')
                                    ui.switch('Silent Machine Comm.', value=False).props(f'color={accent_col} size=sm')
                                    ui.slider(min=1, max=60, value=5).props(f'label color={accent_col} dense')
                                    ui.label('Machine Sync interval (sec)').classes('text-[8px] opacity-40')

                        # --- PHYSICIAN INTEL ---
                        elif cat == 'physician':
                            with ui.column().classes('w-full gap-6'):
                                with ui.column().classes('w-full p-6 glass-card border border-white/5 gap-4'):
                                    ui.label('CLINICAL DECISION SUPPORT').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.switch('Drug Interaction Engine', value=True).props(f'color={accent_col} size=sm')
                                    ui.switch('AI Dosage Checker', value=False).props(f'color={accent_col} size=sm')
                                    ui.switch('Smart Diagnosis Scribe', value=True).props(f'color={accent_col} size=sm')
                                
                                with ui.column().classes('w-full p-6 glass-card border border-white/5 gap-4'):
                                    ui.label('AI SENSITIVITY').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.slider(min=70, max=99, value=90).props(f'label color={accent_col} dense')
                                    ui.label('Diagnostic Confidence Threshold (%)').classes('text-[8px] opacity-40')

                        # --- AI & ANALYTICS ---
                        elif cat == 'ai':
                            with ui.column().classes('w-full gap-6'):
                                with ui.column().classes('w-full p-6 glass-card border border-white/5 gap-4'):
                                    ui.label('NEURAL ENGINE CONFIG').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.input('API Endpoint', value='https://ai.med-intel.com/v4').classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                    ui.input('Secure Token', password=True).classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                
                                with ui.grid(columns=2).classes('w-full gap-4'):
                                    with ui.column().classes('p-4 glass-card border border-white/5 gap-2'):
                                        ui.checkbox('Revenue Forecast', value=True).props(f'color={accent_col} size=sm')
                                        ui.checkbox('Outbreak AI', value=True).props(f'color={accent_col} size=sm')
                                    with ui.column().classes('p-4 glass-card border border-white/5 gap-2'):
                                        ui.checkbox('Churn Predictor', value=False).props(f'color={accent_col} size=sm')
                                        ui.checkbox('Log Anomaly Det.', value=True).props(f'color={accent_col} size=sm')

                        # --- REGISTRATION & LOCALIZATION ---
                        elif cat == 'reg':
                            with ui.grid(columns=2).classes('w-full gap-6'):
                                with ui.column().classes('p-6 glass-card border border-white/5 gap-4'):
                                    ui.label('LOCALIZATION (IRAQ)').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.switch('Arabic Name Mapping', value=True).props(f'color={accent_col} size=sm')
                                    ui.switch('District Search Flow', value=True).props(f'color={accent_col} size=sm')
                                    ui.select(['Baghdad Standard', 'Basra Standard', 'Erbil/KRD'], label='Base Logic', value='Baghdad Standard').classes('w-full').props(f'outlined dense color={accent_col}')
                                
                                with ui.column().classes('p-6 glass-card border border-white/5 gap-4'):
                                    ui.label('CORE VALIDATION').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.switch('ID Number Masking', value=False).props(f'color={accent_col} size=sm')
                                    ui.switch('Phone Verification', value=True).props(f'color={accent_col} size=sm')

                        # --- RBAC / PERMISSIONS ---
                        elif cat == 'rbac':
                            ui.label('PERMISSION ARCHITECTURE').classes('text-[9px] font-black opacity-40 tracking-widest mb-2')
                            with ui.column().classes('w-full gap-2'):
                                roles = [('ADMIN', 'Full Control', 'emerald'), ('DOCTOR', 'Clinical Only', 'blue'), ('LAB', 'Testing Only', 'purple'), ('NURSE', 'Triage Only', 'orange')]
                                for r, d, c in roles:
                                    with ui.row().classes('w-full p-4 glass-card border border-white/5 items-center justify-between'):
                                        with ui.row().classes('items-center gap-3'):
                                            ui.icon('verified_user', color=c, size='xs')
                                            ui.label(r).classes('font-black text-xs')
                                        ui.label(d).classes('text-[10px] opacity-40 font-bold')

                        # --- FINANCE ---
                        elif cat == 'finance':
                            with ui.column().classes('w-full gap-6'):
                                with ui.row().classes('w-full gap-6'):
                                    ui.input('Base Currency', value='IQD').classes('glass-card p-4 modern-input w-48').props(f'outlined dense color={accent_col}')
                                    ui.input('VAT Rate (%)', value='0').classes('glass-card p-4 modern-input w-48').props(f'outlined dense color={accent_col}')
                                
                                with ui.column().classes('w-full p-6 glass-card border border-white/5 gap-4'):
                                    ui.label('PAYMENT GATEWAYS').classes('text-[9px] font-black opacity-40 tracking-widest')
                                    ui.switch('Enable ZainCash', value=True).props(f'color={accent_col} size=sm')
                                    ui.switch('NassWallet Support', value=True).props(f'color={accent_col} size=sm')
                                    ui.switch('Direct Visa/Master', value=False).props(f'color={accent_col} size=sm')

                        # --- TRIAGE & VITALS ---
                        elif cat == 'triage':
                            with ui.column().classes('w-full gap-6'):
                                ui.label('DANGER ZONE THRESHOLDS').classes('text-[9px] font-black opacity-40 tracking-widest')
                                with ui.grid(columns=3).classes('w-full gap-4'):
                                    ui.input('BP Max (Syst.)', value='140').classes('glass-card p-4').props(f'outlined dense color={accent_col}')
                                    ui.input('Temp Max (°C)', value='38.5').classes('glass-card p-4').props(f'outlined dense color={accent_col}')
                                    ui.input('HR Max (BPM)', value='110').classes('glass-card p-4').props(f'outlined dense color={accent_col}')
                                
                                ui.switch('Pulse Ox Monitor Support', value=True).props(f'color={accent_col} size=sm').classes('font-bold')

                        # --- RADIOLOGY ---
                        elif cat == 'rad':
                            with ui.column().classes('w-full gap-6'):
                                ui.label('PACS/RIS INTEGRATION').classes('text-[9px] font-black opacity-40 tracking-widest')
                                ui.input('PACS Server Address', placeholder='dicom.server.internal').classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                ui.select(['JPEG2000', 'Lossless', 'RAW'], label='Transfer Syntax', value='JPEG2000').classes('w-full').props(f'outlined dense color={accent_col}')

                        # --- GLOBAL SETTINGS ---
                        elif cat == 'global':
                            with ui.column().classes('w-full gap-6 p-6 glass-card border border-white/5'):
                                ui.label('INSTITUTIONAL IDENTITY').classes('text-[9px] font-black opacity-40 tracking-widest')
                                ui.input('Entity Name', value='Al-Hayat Specialized').classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                ui.input('Entity Address', value='Baghdad, Al-Mansour').classes('modern-input w-full').props(f'outlined color={accent_col} dense')
                                with ui.row().classes('w-full justify-between items-center mt-4'):
                                    ui.label('System Language').classes('text-xs font-bold')
                                    with ui.row().classes('gap-2'):
                                        ui.button('ENG', color=accent_col).props('unelevated size=sm')
                                        ui.button('ARB', color=accent_col).props('outline size=sm')

                        # --- MAINTENANCE ---
                        elif cat == 'maint':
                            with ui.column().classes('w-full items-center gap-10 mt-16'):
                                ui.icon('construction', size='6em', color=accent_col).classes('opacity-10')
                                with ui.row().classes('gap-4'):
                                    ui.button('Wipe Cache', icon='delete_sweep').props('outline color=orange size=sm')
                                    ui.button('Repair DB', icon='rebase_edit').props('outline color=blue size=sm')
                                    ui.button('System Update', icon='system_update').props(f'unelevated color={accent_col} size=sm shadow=none')

                        # --- REMOTE CORE (REAL CONNECTIVITY SUITE) ---
                        elif cat == 'remote':
                            def update_remote_setting(key, val):
                                set_setting(key, 'true' if val else 'false', 'remote')
                                ui.notify(f"Remote Core: {key} updated", color=accent_col)

                            # Detect Local IP
                            import socket
                            def get_lan_ip():
                                try:
                                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                    s.connect(("8.8.8.8", 80))
                                    ip = s.getsockname()[0]
                                    s.close()
                                    return ip
                                except: return "127.0.0.1"
                            
                            local_ip = get_lan_ip()
                            local_url = f"http://{local_ip}:8080"

                            with ui.column().classes('w-full gap-8 pb-20'):
                                # 1. LOCAL ACCESS (WiFi Only)
                                with ui.column().classes('w-full p-8 bg-[#1a1a1a] rounded-[32px] border border-white/10 gap-6 shadow-2xl'):
                                    with ui.row().classes('w-full items-center justify-between'):
                                        with ui.column().classes('gap-1'):
                                            ui.label('LOCAL NETWORK ACCESS').classes('text-[10px] font-black opacity-40 tracking-[0.4em] text-emerald-400')
                                            ui.label('Same WiFi / LAN Connection').classes('text-xs font-bold text-white/50')
                                        ui.icon('wifi', color='emerald-400', size='sm').classes('opacity-30')

                                    with ui.column().classes('w-full bg-emerald-500/5 p-6 rounded-2xl border border-emerald-500/20 gap-4'):
                                        ui.label('CONNECT VIA PHONE').classes('text-[8px] font-black opacity-30')
                                        with ui.row().classes('w-full items-center justify-between'):
                                            ui.label(local_url).classes('text-emerald-400 font-mono text-sm font-black')
                                            ui.button(icon='content_copy', on_click=lambda: ui.run_javascript(f"navigator.clipboard.writeText('{local_url}')")).props('flat round size=sm color=emerald')
                                        ui.label('Note: Phone must be on the same WiFi as this computer.').classes('text-[9px] opacity-40 italic')

                                # 2. GLOBAL SYSTEM CONTROLS
                                with ui.column().classes('w-full p-8 bg-[#1a1a1a] rounded-[32px] border border-white/10 gap-6 shadow-2xl'):
                                    ui.label('SMART PERMISSIONS').classes('text-[10px] font-black opacity-40 tracking-[0.4em] text-blue-400')
                                    
                                    with ui.row().classes('w-full items-center justify-between'):
                                        ui.label('Remote Mobile Control').classes('text-sm font-bold text-white')
                                        ui.switch(value=get_setting('mobile_control') == 'true', 
                                                  on_change=lambda e: update_remote_setting('mobile_control', e.value)).props(f'color={accent_col}')
                                    
                                    with ui.row().classes('w-full items-center justify-between'):
                                        ui.label('Live BI Streaming').classes('text-sm font-bold text-white')
                                        ui.switch(value=get_setting('bi_streaming') == 'true', 
                                                  on_change=lambda e: update_remote_setting('bi_streaming', e.value)).props(f'color={accent_col}')
                                    
                                    with ui.row().classes('w-full items-center justify-between'):
                                        ui.label('Terminal Access (SSH)').classes('text-sm font-bold text-white')
                                        ui.switch(value=get_setting('ssh_access') == 'true', 
                                                  on_change=lambda e: update_remote_setting('ssh_access', e.value)).props('color=red')

                                # 3. ONLINE CLOUD BRIDGE (Universal Internet Access)
                                with ui.column().classes('w-full p-10 bg-gradient-to-br from-[#52525b] to-[#71717a] rounded-[40px] border border-white/10 gap-8 items-center text-center relative overflow-hidden'):
                                    ui.element('div').classes('absolute -top-20 -right-20 w-40 h-40 bg-indigo-600/20 blur-[100px]')
                                    ui.icon('o_cloud_sync', size='4em', color='indigo-400').classes('drop-shadow-[0_0_15px_rgba(129,140,248,0.4)]')
                                    
                                    with ui.column().classes('gap-1'):
                                        ui.label('GLOBAL ONLINE BRIDGE').classes('text-[11px] font-black tracking-[0.6em] text-indigo-400 uppercase')
                                        ui.label('Access via 4G/5G from Anywhere').classes('text-sm font-black text-white/40')

                                    # The Guide Sections
                                    with ui.column().classes('w-full gap-4 text-right'):
                                        with ui.column().classes('w-full bg-white/5 p-6 rounded-2xl border border-white/10 gap-2 items-end'):
                                            ui.label('الخطوة 1: تشغيل الجسر').classes('text-xs font-black text-indigo-400')
                                            ui.label('افتح موجه الأوامر المحمول (CMD) والصق الكود التالي:').classes('text-[10px] font-bold opacity-60 text-right w-full')
                                            
                                            tunnel_cmd = f"cloudflared tunnel --url {local_url}"
                                            with ui.row().classes('w-full bg-black/40 p-4 rounded-xl items-center justify-between mt-2'):
                                                ui.label(tunnel_cmd).classes('text-indigo-400 font-mono text-[9px] select-all')
                                                ui.button(icon='content_copy', on_click=lambda: ui.run_javascript(f"navigator.clipboard.writeText('{tunnel_cmd}')")).props('flat round size=xs color=indigo')

                                        with ui.column().classes('w-full bg-white/5 p-6 rounded-2xl border border-white/10 gap-2 items-end'):
                                            ui.label('الخطوة 2: الدخول للتطبيق').classes('text-xs font-black text-emerald-400')
                                            ui.label('بعد تشغيل الكود، سيظهر لك رابط ينتهي بـ .trycloudflare.com افتحه من هاتفك فوراً.').classes('text-[10px] font-bold opacity-60 text-right w-full')
                                            
                                    ui.label('ملاحظة: تأكد من وصول الإنترنت لهذا الكمبيوتر حالياً.').classes('text-[10px] font-black opacity-20 italic')

        render_settings_ui()
