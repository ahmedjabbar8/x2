from nicegui import ui, app
from database import (
    get_waiting_list, complete_appointment, process_waiting, 
    get_patient_vitals, add_lab_request, add_rad_request, 
    add_pharmacy_request, check_drug_interactions, get_archives
)
import sqlite3
import random
from layout import intelligence_layout, get_theme_colors

@ui.page('/doctor')
def doctor_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Clinical Ecosystem', 'sub': 'Precision Patient Management & Intelligence',
            'save': 'FINALIZE CLINICAL RECORD', 'empty': 'Zero patients found in waiting queue',
            'history': 'Clinical Records', 'dx': 'Differential Diagnosis', 'rx': 'Therapeutic Framework',
            'role_badge': 'SENIOR CLINICIAN', 'workspace': 'CLINICAL COMMAND CENTER',
            'scribe': 'AI SCRIBE: READY', 'scribe_active': 'AI SCRIBE: LISTENING...',
            'interact_warn': 'HIGH SEVERITY INTERACTION DETECTED',
            'suggest': 'SMART SUGGESTIONS'
        },
        'AR': {
            'header': 'البيئة العيادية', 'sub': 'إدارة وتحليل بيانات المرضى السريرية',
            'save': 'إنهاء الزيارة والأرشفة', 'empty': 'لا يوجد مرضى جاهزون حالياً',
            'history': 'السجل المرضي', 'dx': 'التشخيص والتقييم السريري', 'rx': 'الخطة العلاجية والدوائية',
            'role_badge': 'طبيب استشاري', 'workspace': 'مركز الإدارة الطبية',
            'scribe': 'الكاتب الآلي: جاهز', 'scribe_active': 'الكاتب الآلي: يستمع...',
            'interact_warn': 'تحذير: تداخل دوائي خطير مكتشف!',
            'suggest': 'مقترحات ذكية'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/doctor')

    class DoctorState:
        selected_p = None
        current_dx = ""
        current_rx = ""
        is_scribing = False
        rx_drugs = []

    S = DoctorState()

    def open_workspace(p):
        S.selected_p = p
        S.current_dx = ""
        S.current_rx = ""
        S.rx_drugs = []
        render_workspace.refresh()

    with content:
        with ui.grid(columns=12).classes('w-full gap-10'):
            # --- LEFT QUEUE ---
            with ui.column().classes('col-span-3 gap-6'):
                ui.label('WAITING LOG').classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                
                @ui.refreshable
                def refresh_queue():
                    all_waiting = get_waiting_list()
                    # Show all with priority coloring
                    with ui.column().classes('w-full gap-4'):
                        if not all_waiting:
                            with ui.element('div').classes('glass-card w-full py-24 flex items-center justify-center opacity-30 text-center'):
                                ui.label(T['empty']).classes('text-xs font-black italic px-4')
                        else:
                            for p in all_waiting:
                                is_sel = S.selected_p and S.selected_p['patient_id'] == p['patient_id']
                                prio_color = '#FF4B4B' if p.get('priority_level') == 'Red' else ('#F5BC4B' if p.get('priority_level') == 'Yellow' else colors['accent'])
                                
                                with ui.row().classes(f"glass-card w-full p-4 items-center justify-between cursor-pointer group border-l-4") \
                                    .style(f"border-color: {prio_color} !important; opacity: {1 if is_sel else 0.8};") \
                                    .on('click', lambda p=p: open_workspace(p)):
                                    with ui.column().classes('gap-0'):
                                        ui.label(p['patient_name']).classes('font-bold text-sm')
                                        ui.label(f"ID: {p['patient_id']} • {p['status']}").classes('text-[9px] opacity-40 uppercase tracking-widest')
                                    if p.get('priority_level') == 'Red':
                                        ui.icon('bolt', color='red', size='xs')

                refresh_queue()
                ui.timer(5.0, refresh_queue.refresh)

            # --- CLINICAL WORKSPACE ---
            with ui.column().classes('col-span-9 gap-6'):
                ui.label(T['workspace']).classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                
                @ui.refreshable
                def render_workspace():
                    if not S.selected_p:
                        with ui.element('div').classes('glass-card w-full h-[600px] flex items-center justify-center opacity-10'):
                            with ui.column().classes('items-center'):
                                ui.icon('medical_services', size='6em').classes('material-icons-outlined')
                                ui.label('INITIATE CLINICAL REVIEW').classes('text-xl font-black mt-6 tracking-widest')
                        return

                    p = S.selected_p
                    vitals = get_patient_vitals(p['patient_id'])
                    
                    with ui.column().classes('glass-card w-full p-8 gap-8'):
                        # 1. Patient Info & Vitals Header
                        with ui.row().classes('w-full justify-between items-center pb-6 border-b border-black/5'):
                            with ui.row().classes('items-center gap-4'):
                                ui.avatar(p['patient_name'][0].upper(), color=colors['accent'], text_color='white').classes('w-16 h-16 font-black text-2xl')
                                with ui.column().classes('gap-0'):
                                    ui.label(p['patient_name']).classes('text-3xl font-black')
                                    ui.label(f"RECORD: HS-{p['patient_id']} • {p['gender']} • {p['age']}Y").classes('text-[9px] font-black opacity-40 tracking-widest')
                            
                            # Vitals
                            if vitals:
                                with ui.row().classes('gap-6'):
                                    def v_node(lbl, val, col):
                                        with ui.column().classes('items-center'):
                                            ui.label(val).classes('text-lg font-black').style(f"color: {col}")
                                            ui.label(lbl).classes('text-[8px] opacity-40 font-black tracking-widest')
                                    v_node('BP', vitals['blood_pressure'], '#FF4B4B')
                                    v_node('TEMP', f"{vitals['temperature']}°", '#F5BC4B')
                                    v_node('HR', vitals['heart_rate'], colors['accent'])

                        # 2. AI Scribe & Suggestions
                        with ui.row().classes('w-full justify-between items-center bg-black/5 p-4 rounded-xl border border-black/5'):
                             with ui.row().classes('items-center gap-4'):
                                 def toggle_scribe():
                                     S.is_scribing = not S.is_scribing
                                     if S.is_scribing:
                                         ui.notify('AI Scribe: Listening...', color='red', icon='mic')
                                     render_workspace.refresh()
                                 
                                 ui.button(on_click=toggle_scribe).props(f"flat round icon={'mic' if not S.is_scribing else 'mic_none'} color={'red' if S.is_scribing else 'grey-9'}")
                                 ui.label(T['scribe_active'] if S.is_scribing else T['scribe']).classes('text-xs font-bold opacity-60')
                             
                             with ui.row().classes('items-center gap-2'):
                                 ui.icon('psychology', size='xs', color='purple')
                                 ui.label(T['suggest']).classes('text-[10px] font-black opacity-40')
                                 with ui.row().classes('gap-2'):
                                     def use_template(t):
                                         S.current_dx += f"\n- {t}"
                                         render_workspace.refresh()
                                     for t in ['Hypertension Check', 'Post-Op Review', 'Viral Fever']:
                                         ui.button(t, on_click=lambda t=t: use_template(t)).props('outline dense size=xs').classes('rounded-full text-[9px]')

                        # 3. Assessment & Clinical Records (DX)
                        with ui.grid(columns=2).classes('w-full gap-6'):
                            with ui.column().classes('gap-3'):
                                ui.label(T['dx']).classes('text-[10px] font-black opacity-40 tracking-widest')
                                dx_area = ui.textarea(value=S.current_dx, on_change=lambda e: setattr(S, 'current_dx', e.value)).classes('modern-input w-full h-40 font-bold p-4 text-sm').props('outlined')
                            
                            with ui.column().classes('gap-3'):
                                ui.label('HISTORICAL TRENDS (PREVIOUS LABS)').classes('text-[10px] font-black opacity-40 tracking-widest')
                                archives = get_archives(p['patient_id'])
                                with ui.column().classes('w-full h-40 overflow-y-auto glass-card p-4 gap-2'):
                                    if not archives: ui.label('No previous records').classes('text-[10px] opacity-20')
                                    for a in archives[:5]:
                                        with ui.row().classes('w-full justify-between items-center bg-white/5 p-2 rounded'):
                                            ui.label(a['record_type']).classes('text-[9px] font-black')
                                            ui.label(a['details']).classes('text-[9px] opacity-60 truncate max-w-[150px]')

                        # 4. Therapeutic Framework & CDS (RX)
                        with ui.column().classes('w-full gap-3 pt-4'):
                            ui.label(T['rx']).classes('text-[10px] font-black opacity-40 tracking-widest')
                            
                            @ui.refreshable
                            def render_rx():
                                # Check for interactions in real-time
                                conflicts = check_drug_interactions(S.rx_drugs)
                                if conflicts:
                                    with ui.row().classes('w-full bg-red-600/20 p-4 rounded-xl items-center gap-4 border border-red-600/40 mb-2'):
                                        ui.icon('warning', color='red', size='md')
                                        with ui.column().classes('gap-0'):
                                            ui.label(T['interact_warn']).classes('text-xs font-black text-red-400')
                                            for c in conflicts:
                                                ui.label(f"• {c['drug_a']} + {c['drug_b']}: {c['description']}").classes('text-[10px] text-red-300')

                                with ui.row().classes('w-full gap-2 mb-4'):
                                    drug_input = ui.input(placeholder='Add medication (e.g. Aspirin, Warfarin)').classes('modern-input flex-grow').props('outlined dense')
                                    def add_drug():
                                        if drug_input.value:
                                            S.rx_drugs.append(drug_input.value)
                                            drug_input.set_value('')
                                            render_rx.refresh()
                                    ui.button(icon='add', on_click=add_drug).props('flat round').classes('bg-white/5')
                                
                                with ui.row().classes('w-full gap-2'):
                                    for d in S.rx_drugs:
                                        with ui.row().classes('items-center bg-white/10 px-3 py-1 rounded-full gap-2 border border-white/5'):
                                            ui.label(d).classes('text-xs font-bold')
                                            ui.icon('close', size='xs').classes('cursor-pointer').on('click', lambda d=d: (S.rx_drugs.remove(d), render_rx.refresh()))

                            render_rx()
                            rx_area = ui.textarea(placeholder='Enter instructions & dosages...', on_change=lambda e: setattr(S, 'current_rx', e.value)).classes('modern-input w-full h-32 font-bold p-4 text-sm').props('outlined')

                        # 5. Secondary Referrals (Lab/Rad)
                        with ui.grid(columns=2).classes('w-full gap-8'):
                             with ui.column().classes('p-6 rounded-2xl bg-white/5 border border-white/10'):
                                 ui.label('LAB/RAD REFERRAL').classes('text-[10px] font-black opacity-40 mb-4')
                                 with ui.row().classes('items-center gap-4'):
                                     lab_type = ui.select(['CBC', 'Glucose', 'TSH', 'Lipid Profile'], label='Select Protocol').classes('flex-grow').props('outlined dense')
                                     ui.button(icon='science', on_click=lambda: (add_lab_request(p['patient_id'], lab_type.value), ui.notify('Lab Request Sent'))).props('flat round color=primary')
                             
                             with ui.column().classes('p-6 rounded-2xl bg-white/5 border border-white/10'):
                                 ui.label('FINALIZATION').classes('text-[10px] font-black opacity-40 mb-4')
                                 def submit_final():
                                     # Combine drugs into RX text
                                     final_rx = f"Meds: {', '.join(S.rx_drugs)}\nInstr: {S.current_rx}"
                                     complete_appointment(p.get('appointment_id', 0), S.current_dx, final_rx)
                                     process_waiting(p['id'])
                                     ui.notify('✓ Clinical Record Finalized', type='positive')
                                     S.selected_p = None
                                     refresh_queue.refresh()
                                     render_workspace.refresh()

                                 ui.button(T['save'], icon='verified', on_click=submit_final).classes('w-full h-12 rounded-xl text-white font-black').style(f"background: {colors.get('gradient')}")

                render_workspace()
