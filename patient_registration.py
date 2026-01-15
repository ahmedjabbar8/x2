from nicegui import ui, app
from database import add_patient, get_all_patients, delete_patient, get_today_registrations
from layout import intelligence_layout, get_theme_colors
from datetime import datetime

IRAQ_LOCATIONS = {
    'Baghdad (بغداد)': ['Karkh (الكرخ)', 'Rusafa (الرصافة)', 'Adhamiya (الأعظمية)', 'Kadhimiya (الكاظمية)', 'Mansour (المنصور)', 'Karada (الكرادة)', 'Sadr City (مدينة الصدر)', 'Taji (التاجي)'],
    'Basra (البصرة)': ['Ashar (العشار)', 'Zubair (الزبير)', 'Qurna (القرنة)', 'Abul-Khasib (أبي الخصيب)', 'Fao (الفاو)', 'Hartha (الهوير)'],
    'Nineveh (نينوى)': ['Mosul (الموصل)', 'Tal Afar (تلعفر)', 'Sinjar (سنجار)', 'Hamdaniya (الحمدانية)', 'Sheikhan (شيخان)', 'Hammam al-Alil (حمام العليل)'],
    'Erbil (أربيل)': ['Ankawa (عنكاوا)', 'Sorān (سوران)', 'Koy Sanjaq (كوي سنجق)', 'Choman (چۆمان)', 'Shaqlawa (شقلاوة)'],
    'Najaf (النجف)': ['Kufa (الكوفة)', 'Manathera (المناذرة)', 'Meshkhab (المشخاب)', 'Haidariya (الحيدرية)'],
    'Karbala (كربلاء)': ['Hindiya (الهندية)', 'Ain al-Tamur (عين التمر)', 'Hurr (الحر)'],
    'Anbar (الأنبار)': ['Ramadi (الرمادي)', 'Fallujah (الفلوجة)', 'Hit (هيت)', 'Haditha (حديثة)', 'Rutba (الرطبة)', 'Ana (عنة)'],
    'Dhi Qar (ذي قار)': ['Nasiriyah (الناصرية)', 'Shatrah (الشطرة)', 'Rifai (الرفاعي)', 'Suq al-Shuyukh (سوق الشيوخ)'],
    'Babil (بابل)': ['Hilla (الحلة)', 'Mahawil (المحاويل)', 'Musayyib (المسيب)', 'Hashimiya (الهاشمية)'],
    'Sulaymaniyah (السليمانية)': ['Ranya (رانية)', 'Pshdar (پشدر)', 'Dukan (دوكان)', 'Halabja (حلبجة)'],
    'Diyala (ديالى)': ['Baqubah (بعقوبة)', 'Khanaqin (خانقين)', 'Muqdadiya (المقدادية)', 'Khalis (الخالص)'],
    'Kirkuk (كركوك)': ['Hawija (الحويجة)', 'Daquq (دقوق)', 'Dibis (دبس)'],
    'Maysan (ميسان)': ['Amarah (العمارة)', 'Maimouna (الميمونة)', 'Majar al-Kabir (المجر الكبير)'],
    'Wasit (واسط)': ['Kut (الكوت)', 'Aziziya (العزيزية)', 'Suwaira (الصويرة)', 'Hay (الحي)'],
    'Muthanna (المثنى)': ['Samawah (السماوة)', 'Rumaitha (الرميثة)', 'Khidhir (الخضر)'],
    'Qadisiyah (القادسية)': ['Diwaniyah (الديوانية)', 'Shamiya (الشامية)', 'Hamza (الحمزة)'],
    'Salah al-Din (صلاح الدين)': ['Tikrit (تكريت)', 'Samarra (سامراء)', 'Balad (بلد)', 'Dujail (الدجيل)', 'Baiji (بيجي)'],
    'Duhok (دهوك)': ['Zakho (زاخو)', 'Amedi (العمادية)', 'Semel (سميل)', 'Akre (عقرة)']
}

PRIORITIES = {
    'Martyrs': {'label_ar': 'عوائل الشهداء', 'label_en': 'Martyrs', 'color': '#f43f5e', 'icon': 'o_military_tech'},
    'Social': {'label_ar': 'الرعاية الاجتماعية', 'label_en': 'Social Security', 'color': '#3b82f6', 'icon': 'o_diversity_3'},
    'Special': {'label_ar': 'الحالات الخاصة', 'label_en': 'Special Cases', 'color': '#8B5CF6', 'icon': 'o_workspace_premium'},
    'General': {'label_ar': 'الحالات الأخرى', 'label_en': 'General', 'color': '#64748b', 'icon': 'o_person'}
}

class FormState:
    def __init__(self):
        self.gender = 'Male'
        self.priority = 'General'

@ui.page('/patient_registration')
def patient_registration_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    
    # --- Custom CSS from User Snippet ---
    ui.add_head_html('''
        <style>
            :root { --apple-blue: #0071e3; --bg-gray: #f5f5f7; }
            .nav-pill-cont {
                background: white;
                border-radius: 16px;
                padding: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            }
            .nav-pill-cont { background: #f5f5f7; border: 1px solid rgba(0,0,0,0.05); }
            
            .q-tab { 
                border-radius: 12px !important; 
                font-weight: 600 !important; 
                color: #888 !important;
                min-height: 45px !important;
            }
            .q-tab--active { 
                background-color: var(--apple-blue) !important; 
                color: white !important;
                box-shadow: 0 4px 15px rgba(0,113,227,0.3) !important;
            }
            .q-tab__indicator { display: none !important; } /* Hide underline */
            
            .fast-card { 
                border: none !important; 
                border-radius: 18px !important; 
                box-shadow: 0 8px 30px rgba(0,0,0,0.05) !important; 
                background: white;
            }
            .fast-card { background: white; border: 1px solid rgba(0,0,0,0.05) !important; }
            
            .update-flash { animation: flash 0.5s; }
            @keyframes flash { from { background: #e3f2fd; } to { background: transparent; } }
        </style>
    ''')

    TR = {
        'EN': {'mod1': 'New Registration', 'mod2': 'Search & Archive', 'mod3': 'Direct Booking', 'name': 'Full Patient Name', 'phone': 'Phone Number', 'search': 'Search by Name, ID...', 'scan': 'Scan Barcode', 'today': 'Live Today', 'save': 'REGISTER'},
        'AR': {'mod1': 'تسجيل جديد', 'mod2': 'البحث والأرشيف', 'mod3': 'الحجز المباشر', 'name': 'الاسم الكامل للمريض', 'phone': 'رقم الهاتف', 'search': 'ابحث بالاسم، رقم الملف، أو الهوية...', 'scan': 'مسح باركود', 'today': 'تحديث فوري (كل 0.5 ثانية)', 'save': 'تسجيل'}
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', {}, current_nav='/patient_registration')
    form_state = FormState()

    with content:
        # --- TAB NAVIGATION (Pills) ---
        with ui.tabs().classes('nav-pill-cont w-full max-w-5xl mx-auto mb-6 gap-2') as tabs:
            # Note: User snippet order: Search -> Register -> Booking
            tab_search = ui.tab(T['mod2'], icon='o_search').classes('flex-1')
            tab_reg = ui.tab(T['mod1'], icon='o_person_add').classes('flex-1')
            tab_booking = ui.tab(T['mod3'], icon='o_calendar_month').classes('flex-1')

        with ui.tab_panels(tabs, value=tab_search).classes('w-full bg-transparent p-0'):
            
            # --- PANEL 1: SEARCH & ARCHIVE ---
            with ui.tab_panel(tab_search).classes('p-0'):
                with ui.column().classes('fast-card compact-card w-full max-w-6xl mx-auto p-4 gap-4'):
                    with ui.row().classes('w-full gap-4'):
                        # Large Search Input
                        with ui.element('div').classes('flex-grow'):
                            search_input = ui.input(placeholder=T['search']).props('outlined rounded input-class="text-lg"').classes('w-full modern-input compact-input')
                            search_input.on('update:model-value', lambda: perform_search.refresh())
                        
                        # Scan Button
                        ui.button(T['scan'], icon='o_qr_code_scanner').classes('h-8 px-4 rounded-xl bg-gray-800 text-white font-bold hover:bg-black compact-button')

                    # Search Results
                    @ui.refreshable
                    def perform_search():
                        term = search_input.value.lower() if search_input.value else ""
                        if len(term) < 1: return

                        patients = [p for p in get_all_patients() if term in p['name'].lower() or term in str(p['id'])]
                        with ui.column().classes('w-full mt-4 gap-2'):
                            if not patients:
                                ui.label('No records found').classes('w-full text-center opacity-40')
                            else:
                                # Table Header
                                with ui.row().classes('w-full px-4 py-2 bg-gray-50 dark:bg-white/5 rounded-lg text-sm font-bold opacity-60'):
                                    ui.label('Patient Name').classes('w-1/3')
                                    ui.label('File No.').classes('w-1/6')
                                    ui.label('Actions').classes('w-1/2 text-right')

                                for p in patients[:10]:
                                    with ui.row().classes('w-full px-4 py-3 items-center border-b border-gray-100 dark:border-white/5 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors'):
                                        with ui.column().classes('w-1/3 gap-0'):
                                            ui.label(p['name']).classes('font-bold')
                                            ui.label(f"ID: {p['id']}").classes('text-xs opacity-50')
                                        
                                        ui.badge(f"HS-{p['id']}", color='grey-2').classes('text-black')
                                        
                                        with ui.row().classes('w-1/2 justify-end gap-2'):
                                            ui.button('Archive', icon='folder_open').props('flat dense size=sm').classes('text-blue-500')
                                            ui.button('Edit', icon='edit').props('flat dense size=sm').classes('text-teal-500')
                                            ui.button('Book', icon='calendar_today').props('unelevated dense size=sm').classes('bg-blue-600 text-white rounded-lg px-3')
                    
                    perform_search()

            # --- PANEL 2: NEW REGISTRATION ---
            with ui.tab_panel(tab_reg).classes('p-0'):
                with ui.element('div').classes('fast-card compact-card w-full max-w-6xl mx-auto p-8'):
                    # (Re-using the nice form logic from before, but inside the new style card)
                     with ui.grid(columns='repeat(auto-fit, minmax(260px, 1fr))').classes('w-full gap-8'):
                        with ui.column().classes('gap-4'):
                            p_name = ui.input(T['name']).classes('w-full modern-input compact-input text-lg').props('outlined')
                            p_phone = ui.input(T['phone']).classes('w-full modern-input compact-input text-lg').props('outlined')
                            
                            @ui.refreshable
                            def render_gender():
                                with ui.row().classes('w-full items-center justify-between bg-gray-50 dark:bg-white/5 p-3 rounded-xl'):
                                    ui.label('GENDER').classes('text-[10px] font-black opacity-40')
                                    with ui.row().classes('gap-2'):
                                        ui.button('Male', icon='male', on_click=lambda: (setattr(form_state, 'gender', 'Male'), render_gender.refresh())) \
                                            .props(f'flat color={"blue" if form_state.gender=="Male" else "grey"}')
                                        ui.button('Female', icon='female', on_click=lambda: (setattr(form_state, 'gender', 'Female'), render_gender.refresh())) \
                                            .props(f'flat color={"pink" if form_state.gender=="Female" else "grey"}')
                            render_gender()

                        with ui.column().classes('gap-4'):
                            p_gov = ui.select(list(IRAQ_LOCATIONS.keys()), label=T.get('gov', 'Governorate'), on_change=lambda e: (setattr(p_area, 'options', IRAQ_LOCATIONS.get(e.value, [])), p_area.update())).classes('w-full modern-input').props('outlined')
                            p_area = ui.select([], label=T.get('area', 'District')).classes('w-full modern-input').props('outlined')

                            @ui.refreshable
                            def render_prio():
                                with ui.row().classes('w-full gap-2 flex-wrap'):
                                    for k, v in PRIORITIES.items():
                                        sel = form_state.priority == k
                                        ui.button(v['label_ar' if lang=='AR' else 'label_en'], icon=v['icon'], on_click=lambda k=k: (setattr(form_state, 'priority', k), render_prio.refresh())) \
                                            .props('unelevated' if sel else 'outline') \
                                            .classes('rounded-full text-xs') \
                                            .style(f"background-color: {v['color'] if sel else 'transparent'}; color: {'white' if sel else v['color']}; border-color: {v['color']}")
                            render_prio()

                     with ui.row().classes('w-full justify-end mt-8 border-t border-gray-100 dark:border-white/5 pt-4'):
                         def commit_reg():
                             if not p_name.value: return ui.notify('Name Required', type='warning')
                             add_patient(p_name.value, '', '', form_state.gender, p_phone.value, p_gov.value, p_area.value, '', '', '', form_state.priority)
                             ui.notify('Registered Successfully', type='positive')
                             p_name.value = ''
                             p_phone.value = ''
                             perform_search.refresh()
                             refresh_live_booking.refresh()
                         
                         ui.button(T['save'], icon='save', on_click=commit_reg).classes('bg-blue-600 text-white rounded-xl compact-button font-bold shadow-lg')

            # --- PANEL 3: DIRECT BOOKING (Live 0.5s) ---
            with ui.tab_panel(tab_booking).classes('p-0'):
                with ui.column().classes('w-full max-w-6xl mx-auto gap-4'):
                    # Info Banner
                    with ui.row().classes('w-full bg-blue-600 text-white p-6 rounded-2xl shadow-lg items-center gap-4'):
                        with ui.element('div').classes('p-3 bg-white/20 rounded-full'):
                            ui.icon('bolt', size='24px')
                        with ui.column().classes('gap-0'):
                            ui.label(T['today']).classes('text-lg font-bold')
                            ui.label('Patients registered today awaiting booking...').classes('text-sm opacity-80')

                    # Live List Container
                    with ui.column().classes('w-full gap-3') as live_container:
                        @ui.refreshable
                        def refresh_live_booking():
                            # Mocking "flash" effect by toggling a class or just refreshing content
                            today = get_today_registrations()
                            if not today:
                                ui.label('No active registrations waiting...').classes('w-full text-center py-10 opacity-40 italic')
                                return

                            for p in today:
                                prio = PRIORITIES.get(p.get('category', 'General'), PRIORITIES['General'])
                                with ui.row().classes('w-full fast-card p-4 items-center justify-between border-l-4').style(f'border-left-color: {prio["color"]}'):
                                    with ui.row().classes('items-center gap-4'):
                                        ui.avatar(p['name'][0], color=prio['color'], text_color='white')
                                        with ui.column().classes('gap-0'):
                                            ui.label(p['name']).classes('font-bold text-lg')
                                            ui.label(f"{p['reg_date']} • {prio['label_ar' if lang=='AR' else 'label_en']}").classes('text-xs opacity-60')
                                    
                                    with ui.row().classes('items-center gap-2'):
                                        # Role-Based Actions
                                        user_role = app.storage.user.get('role', 'user')
                                        
                                        # Edit (Admin/Registration)
                                        if user_role in ['admin', 'registration']:
                                            ui.button(icon='edit').props('flat round dense color=grey').classes('opacity-50 hover:opacity-100')
                                        
                                        # Reports (All)
                                        ui.button(icon='description').props('flat round dense color=grey').classes('opacity-50 hover:opacity-100')
                                        
                                        # Book (Registration/Admin) - Main Call to Action
                                        if user_role in ['admin', 'registration']:
                                            ui.button('Book Now', icon='calendar_today').props('unelevated color=primary').classes('rounded-lg px-4')
                        
                        refresh_live_booking()
                        # Auto-refresh every 2 seconds (0.5s might be too aggressive for full UI re-render in python-web transport, 2s is safer but feels 'live')
                        ui.timer(2.0, lambda: refresh_live_booking.refresh())
