from nicegui import ui, app
from database import get_waiting_list, add_triage_record, get_all_patients, get_latest_triage, route_patient_to_doctor
from datetime import datetime
from layout import intelligence_layout, get_theme_colors

@ui.page('/triage')
def triage_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Vitals Gateway', 'sub': 'Critical Assessment & Emergency Triage',
            'save': 'COMMIT & ROUTE', 'empty': 'Zero patients in current reception',
            'queue': 'Incoming Live Flow', 'entry': 'Vitals Protocol', 'bp': 'Blood Pressure',
            'temp': 'Body Temp', 'hr': 'Heart Rhythm', 'weight': 'Mass (kg)',
            'height': 'Height (cm)', 'spo2': 'O2 Saturation',
            'select': 'Select patient from flow to begin protocol',
            'prio_red': 'RED (CRITICAL)', 'prio_yellow': 'YELLOW (URGENT)', 'prio_green': 'GREEN (STABLE)',
            'ai_title': 'Clinical Intelligence', 'ai_sub': 'Offline Assessment Engine',
            'ai_refer': 'Refer to Emergency Physician Immediately',
            'ai_urgent': 'Urgent Nursing Review Required',
            'ai_stable': 'Proceed with routine clinical routing',
            'ai_pediatric': 'Pediatric Caution: Monitoring required',
            'ai_hypertension': 'Hypertension Alert: BP higher than normal',
            'ai_fever': 'Hyperthermia detected: Cooling & Hydration',
            'ai_spo2': 'Hypoxia Warning: Oxygen therapy may be needed',
            'gcs': 'GCS (Coma Scale)', 'pain': 'Pain Level (0-10)', 'symptoms': 'Main Complaint / Symptoms',
            'bmi': 'Body Mass Index', 'status': 'Status', 'esi': 'ESI Level'
        },
        'AR': {
            'header': 'محطة الفرز السريري', 'sub': 'التقييم السريع والعلامات الحيوية',
            'save': 'حفظ وتحويل للطبيب', 'empty': 'لا يوجد مرضى في الانتظار',
            'queue': 'التدفق المباشر', 'entry': 'نافذة القياسات السريرية', 'bp': 'ضغط الدم',
            'temp': 'درجة الحرارة', 'hr': 'نبض القلب', 'weight': 'الوزن (كغم)',
            'height': 'الطول (سم)', 'spo2': 'نسبة الأكسجين (%)',
            'select': 'اختر مريضاً من القائمة للبدء بالتقييم',
            'prio_red': 'أحمر (حرج)', 'prio_yellow': 'أصفر (عاجل)', 'prio_green': 'أخضر (مستقر)',
            'ai_title': 'الذكاء السريري', 'ai_sub': 'محرك التقييم الذاتي (بدون إنترنت)',
            'ai_refer': 'يجب الإحالة إلى طبيب الطوارئ فوراً',
            'ai_urgent': 'مراجعة تمريضية عاجلة مطلوبة',
            'ai_stable': 'المضي قدماً في التوجيه السريري الروتيني',
            'ai_pediatric': 'تنبيه للأطفال: المراقبة الدقيقة مطلوبة',
            'ai_hypertension': 'تنبيه ضغط الدم: الضغط أعلى من المعدل الطبيعي',
            'ai_fever': 'تم اكتشاف ارتفاع حرارة: تبريد وترطيب',
            'ai_spo2': 'تحذير نقص الأكسجين: قد تكون هناك حاجة للعلاج بالأكسجين',
            'gcs': 'مقياس غلاسكو (GCS)', 'pain': 'مستوى الألم (0-10)', 'symptoms': 'الأعراض والشكوى الرئيسية',
            'bmi': 'مؤشر كتلة الجسم', 'status': 'الحالة العامة', 'esi': 'مستوى الخطورة (ESI)'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/triage')

    class TriageState:
        selected_p = None
        current_prio = 'Green'
        esi_level = 5
        ai_insights = []
        bmi = 0
        gcs = 15
        ready_patients = set() # Track patients who have saved results

    class ClinicalIntelligence:
        @staticmethod
        def analyze(vitals, patient):
            insights = []
            sbp = vitals.get('sbp', 0)
            temp = vitals.get('temp', 0)
            hr = vitals.get('hr', 0)
            spo2 = vitals.get('spo2', 0)
            gcs = vitals.get('gcs', 15)
            symptoms = vitals.get('symptoms', '').lower()
            age = patient.get('age', 30)

            # ESI Level & Global Priority
            esi = 5
            if gcs < 8 or (spo2 > 0 and spo2 < 85) or sbp > 220 or sbp < 70:
                esi = 1 # Resuscitation
                insights.append(('ai_refer', 'error'))
            elif (sbp > 180 or temp > 39.5 or hr > 130 or hr < 45 or (spo2 > 0 and spo2 < 90)):
                esi = 2 # Emergent
                insights.append(('ai_refer', 'error'))
            elif sbp > 150 or temp > 38.5 or (spo2 > 0 and spo2 < 94):
                esi = 3 # Urgent
                insights.append(('ai_urgent', 'warning'))
            else:
                esi = 4 if hr > 100 else 5
                insights.append(('ai_stable', 'success'))

            # Symptom Analysis (Keyword based AI)
            critical_keywords = ['chest pain', 'stroke', 'bleeding', 'unconscious', 'ألم صدر', 'نزيف', 'جلطة', 'فقدان وعي']
            if any(k in symptoms for k in critical_keywords):
                esi = min(esi, 2)
                insights.append(('ai_refer', 'error'))

            # Specific Condition Insights
            if sbp > 140: insights.append(('ai_hypertension', 'warning'))
            if temp > 37.8: insights.append(('ai_fever', 'warning'))
            if spo2 > 0 and spo2 < 92: insights.append(('ai_spo2', 'error'))
            if age < 12 and (temp > 38.0 or hr > 110): insights.append(('ai_pediatric', 'info'))
            
            return insights, esi

    S = TriageState()
    CI = ClinicalIntelligence()

    def select_patient(p):
        S.selected_p = p
        from database import get_latest_triage
        latest = get_latest_triage(p['patient_id'])
        if latest:
            # Pre-populate some states if needed (or we'll set them in render_entry)
            S.esi_level = latest.get('esi_level', 5)
            S.bmi = latest.get('bmi', 0)
        triage_dialog.open()
        render_entry.refresh()

    with content:
        @ui.refreshable
        def refresh_queue():
            waiting = get_waiting_list()
            triage_q = [p for p in waiting if 'Triaged' not in p['status']]
            
            # Dashboard Stats
            with ui.row().classes('w-full justify-between items-center mb-4 px-2'):
                with ui.column().classes('gap-0'):
                    ui.label('PROTOCOL QUEUE').classes('medical-label text-indigo-400 opacity-100')
                    ui.label(f'{len(triage_q)} ACTIVE CASES').classes('text-[10px] font-black opacity-40')
                with ui.row().classes('items-center gap-2 bg-emerald-500/10 px-3 py-1 rounded-full'):
                    ui.element('div').classes('pulsing-dot w-2 h-2')
                    ui.label('LIVE STREAM').classes('text-[8px] font-black text-emerald-400')

            with ui.column().classes('w-full gap-3'):
                if not triage_q:
                    with ui.element('div').classes('clinical-vitals-card w-full py-28 flex flex-col items-center justify-center opacity-30 text-center px-4'):
                        ui.icon('o_check_circle', size='4em', color='indigo-400').classes('material-icons-outlined')
                        ui.label(T['empty']).classes('text-xs font-bold mt-4 tracking-[0.2em]')
                    return
                
                for p in triage_q:
                    is_ready = p['patient_id'] in S.ready_patients
                    with ui.row().classes(f"patient-row-card w-full p-5 items-center justify-between cursor-pointer transition-all border-l-[6px]") \
                        .style(f"border-left-color: {('#10B981' if is_ready else colors.get('accent'))} !important; background: rgba(255,255,255,0.02)") \
                        .on('click', lambda p=p: select_patient(p)):
                        with ui.row().classes('items-center gap-4'):
                            with ui.element('div').classes('relative'):
                                ui.avatar(p['patient_name'][0].upper(), color='zinc-600', text_color='white').classes('w-12 h-12 font-black shadow-xl border-2 border-white/20')
                                if is_ready:
                                    with ui.element('div').classes('absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-[#52525b] flex items-center justify-center'):
                                        ui.icon('check', size='10px', color='white')
                            with ui.column().classes('gap-0'):
                                ui.label(p['patient_name']).classes('font-black text-base text-white medical-value')
                                ui.label(f"ID: {p['patient_id']} • {p['age']}Y").classes('medical-label text-zinc-500')
                        
                        with ui.row().classes('items-center gap-3'):
                            if is_ready:
                                ui.label('RESULTS READY').classes('text-[8px] font-black text-emerald-400 tracking-widest')
                            ui.icon('o_arrow_forward', size='sm', color='indigo-400').classes('opacity-40')

        # MAIN CLINICAL DASHBOARD (SINGLE COLUMN)
        with ui.column().classes('w-full items-center max-w-5xl mx-auto gap-8 pt-4'):
            refresh_queue()
            ui.timer(5.0, refresh_queue.refresh)

        # TRIAGE MODAL DIALOG
        with ui.dialog().classes('w-full') as triage_dialog:
            with ui.column().classes('w-full max-w-5xl p-0'):
                @ui.refreshable
                def render_entry():
                    if not S.selected_p: return
                    p = S.selected_p
                    
                    with ui.column().classes('clinical-vitals-card w-full p-10 gap-8 border-t-8 border-t-indigo-500 overflow-visible').style(f"background: #a1a1aa !important; border-top-color: {('#B91C1C' if S.esi_level <= 2 else ('#D97706' if S.esi_level == 3 else '#10B981'))} !important") as workspace:
                        from database import get_latest_triage
                        latest = get_latest_triage(p['patient_id'])
                        
                        # HEADER
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('gap-1'):
                                ui.label(p['patient_name']).classes('text-4xl font-black glow-text medical-value text-white')
                                with ui.row().classes('items-center gap-3'):
                                    ui.label(f"HS-{p['patient_id']}").classes('medical-label text-indigo-400 opacity-100')
                                    ui.separator().props('vertical').classes('h-3 opacity-20')
                                    ui.label(f"{p['age']}Y • {p['gender']}").classes('medical-label text-zinc-400')
                            
                            with ui.row().classes('items-center gap-4'):
                                # BMI Badge
                                with ui.row().classes('bg-slate-600 px-4 py-2 rounded-xl items-center gap-2 border border-white/10 shadow-lg'):
                                    ui.label('BMI').classes('text-[10px] font-black text-white/60')
                                    bmi_label = ui.label('0.0').classes('text-lg font-black text-white')
                                
                                # ESI Badge
                                esi_colors = {1: 'bg-red-700', 2: 'bg-red-500', 3: 'bg-amber-600', 4: 'bg-emerald-600', 5: 'bg-emerald-800'}
                                with ui.row().classes(f"items-center px-6 py-3 rounded-2xl shadow-xl transition-colors border-2 border-white/20 {esi_colors[S.esi_level]}") as esi_badge:
                                    ui.label('ESI').classes('text-[11px] font-black text-white mr-3 tracking-widest')
                                    esi_label = ui.label(str(S.esi_level)).classes('text-3xl font-black text-white')

                        # INPUT GRID
                        with ui.grid(columns=3).classes('w-full gap-8'):
                            def v_box(lbl, icon, placeholder, color, key=None):
                                val = latest.get(key, '') if latest and key else ''
                                with ui.column().classes('gap-2'):
                                    with ui.row().classes('items-center gap-2'):
                                        ui.icon(icon, color=color, size='24px').classes('drop-shadow-sm')
                                        ui.label(lbl).classes('medical-label text-white !opacity-80')
                                    return ui.input(placeholder=placeholder, value=val).classes('modern-input w-full medical-value text-xl').props('outlined dense')

                            bp_in = v_box(T['bp'], 'bloodtype', '120/80', '#FF4B4B', 'blood_pressure')
                            t_in = v_box(T['temp'], 'thermostat', '37.0', '#F5BC4B', 'temperature')
                            hr_in = v_box(T['hr'], 'favorite', '75', '#F43F5E', 'heart_rate')
                            spo2_in = v_box(T['spo2'], 'opacity', '98', '#10B981', 'spo2')
                            w_in = v_box(T['weight'], 'monitor_weight', '70', colors.get('accent'), 'weight')
                            h_in = v_box(T['height'], 'straighten', '175', colors.get('accent_secondary'), 'height')

                        with ui.grid(columns=3).classes('w-full gap-8 mt-2'):
                            gcs_val = latest.get('gcs', 15) if latest else 15
                            gcs_in = ui.select([i for i in range(3, 16)], value=gcs_val, label=T['gcs']).classes('modern-input w-full medical-value text-lg').props('outlined dense')
                            
                            pain_val = latest.get('pain_scale', 0) if latest else 0
                            pain_in = ui.select([i for i in range(0, 11)], value=pain_val, label=T['pain']).classes('modern-input w-full medical-value text-lg').props('outlined dense')
                            
                            symptom_val = latest.get('main_complaint', '') if latest else ''
                            symptoms_in = ui.input(placeholder=T['symptoms'], value=symptom_val).classes('modern-input w-full col-span-1 medical-value').props('outlined dense icon=o_medical_services')

                        # ANALYSIS LOGIC
                        def update_analysis():
                            try:
                                sbp = int(bp_in.value.split('/')[0]) if '/' in bp_in.value else 0
                                temp = float(t_in.value) if t_in.value else 0
                                hr = int(hr_in.value) if hr_in.value else 0
                                spo2 = int(spo2_in.value) if spo2_in.value else 0
                                gcs = int(gcs_in.value)
                                w = float(w_in.value) if w_in.value else 0
                                h = float(h_in.value) if h_in.value else 0
                                symptoms = symptoms_in.value or ''
                                if w > 0 and h > 0:
                                    h_m = h / 100
                                    S.bmi = round(w / (h_m * h_m), 1)
                                    bmi_label.set_text(str(S.bmi))
                                S.ai_insights, S.esi_level = CI.analyze({'sbp': sbp, 'temp': temp, 'hr': hr, 'spo2': spo2, 'gcs': gcs, 'symptoms': symptoms}, p)
                                esi_label.set_text(str(S.esi_level))
                                esi_badge.classes(remove='bg-red-700 bg-red-600 bg-red-500 bg-amber-600 bg-amber-500 bg-emerald-400 bg-emerald-600 bg-emerald-800')
                                esi_badge.classes(add=esi_colors[S.esi_level])
                                workspace.style(f"border-top-color: {('#B91C1C' if S.esi_level <= 2 else ('#D97706' if S.esi_level == 3 else '#10B981'))} !important")
                                render_ai_engine.refresh()
                            except: pass

                        for f in [bp_in, t_in, hr_in, spo2_in, w_in, h_in, gcs_in, pain_in, symptoms_in]:
                            f.on('update:model-value', update_analysis)

                        # AI INTELLIGENCE PANEL
                        @ui.refreshable
                        def render_ai_engine():
                            with ui.column().classes('ai-brain-panel w-full p-6 mt-6 overflow-hidden'):
                                with ui.row().classes('items-center gap-4 relative z-10'):
                                    ui.avatar('o_psychology', color='indigo-600', text_color='white').classes('w-14 h-14 shadow-2xl border-2 border-white/10')
                                    with ui.column().classes('gap-0'):
                                        ui.label(T['ai_title'].upper()).classes('medical-label text-blue-600 opacity-100 font-black')
                                        ui.label(T['ai_sub']).classes('text-[12px] opacity-60 font-medium tracking-tight text-gray-700')
                                
                                # Dynamic Recommendations
                                with ui.column().classes('w-full gap-3 mt-6 relative z-10'):
                                    if not S.ai_insights:
                                        with ui.column().classes('w-full py-10 items-center justify-center border-dashed border-2 border-white/5 rounded-2xl'):
                                            ui.spinner(size='lg', color='indigo-400')
                                            ui.label('ANALYZING STREAM...').classes('medical-label mt-4 text-indigo-200 opacity-40')
                                    else:
                                        for key, type in S.ai_insights:
                                            col = 'red-600' if type == 'error' else ('amber-600' if type == 'warning' else ('blue-600' if type == 'info' else 'emerald-600'))
                                            icon = 'dangerous' if type == 'error' else ('warning' if type == 'warning' else ('info' if type == 'info' else 'check_circle'))
                                            
                                            with ui.row().classes(f'w-full p-5 glass-card border-l-[12px] border-{col} items-center justify-between shadow-sm bg-white/40'):
                                                with ui.row().classes('items-center gap-6'):
                                                    ui.icon(icon, color=col, size='22px').classes('drop-shadow-lg')
                                                    ui.label(T[key]).classes(f'text-xs font-black text-gray-900 uppercase tracking-tight')
                                                ui.icon('auto_awesome', color=col, size='16px').classes('opacity-40')

                        render_ai_engine()

                        # BUTTON STACK
                        with ui.row().classes('w-full gap-4 mt-8'):
                            # SAVE RESULTS (Indicator Green)
                            def save_results():
                                if not bp_in.value or not t_in.value:
                                    return ui.notify('Missing Critical Vitals', type='warning')
                                from database import add_triage_record
                                add_triage_record(p['patient_id'], w_in.value, h_in.value, bp_in.value, t_in.value, hr_in.value, 
                                                priority=('Red' if S.esi_level <= 2 else ('Yellow' if S.esi_level == 3 else 'Green')),
                                                spo2=spo2_in.value, gcs=gcs_in.value, pain=pain_in.value, esi=S.esi_level, 
                                                bmi=S.bmi, complaint=symptoms_in.value)
                                S.ready_patients.add(p['patient_id'])
                                ui.notify('✓ Vitals Captured', type='positive', color='emerald-500')
                                refresh_queue.refresh()

                            ui.button('UPLOAD DATA | رفع النتائج', icon='cloud_upload', on_click=save_results) \
                                .classes('flex-1 h-16 rounded-xl font-black text-white shadow-xl shadow-emerald-900/20 bg-emerald-600 border-b-4 border-emerald-800')

                            # CLOSE & ROUTE
                            def finalize_route():
                                if p['patient_id'] not in S.ready_patients:
                                    save_results()
                                if p['patient_id'] in S.ready_patients:
                                    from database import route_patient_to_doctor
                                    route_patient_to_doctor(p['patient_id'], priority=('Red' if S.esi_level <= 2 else ('Yellow' if S.esi_level == 3 else 'Green')))
                                    ui.notify(f"✓ {p['patient_name']} Routed to Physician", type='positive', color='indigo-600')
                                    triage_dialog.close()
                                    S.selected_p = None
                                    refresh_queue.refresh()

                            ui.button(f"FINISH & ROUTE | {T['save']}", icon='check_circle', on_click=finalize_route) \
                                .classes('flex-1 h-16 rounded-xl font-black text-white shadow-xl bg-indigo-600 border-b-4 border-indigo-800')

                render_entry()
