from nicegui import ui, app
from database import get_pending_pharmacy, dispense_medicine, get_all_patients, add_pharmacy_request
import sqlite3
from layout import intelligence_layout, get_theme_colors

@ui.page('/pharmacy')
def pharmacy_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Pharma Logic', 'sub': 'Medication Dispensing & Clinical Inventory Control',
            'dispense': 'AUTHORIZE DISPENSING', 'empty': 'Zero pending pharmaceutical prescriptions',
            'create': 'INITIATE INTERNAL ORDER', 'meds': 'Medication Protocol Details',
            'patient': 'Target Identity Selection', 'role_badge': 'CHIEF PHARMACIST',
            'status_unpaid': 'WAITING FOR SETTLEMENT', 'status_paid': 'SETTLED & READY'
        },
        'AR': {
            'header': 'مركز الصيدلية الرقمي', 'sub': 'صرف الأدوية والرقابة على المخزون السريري',
            'dispense': 'تخويل صرف الدواء', 'empty': 'لا يوجد وصفات طبية قيد الانتظار',
            'create': 'إنشاء طلب دوائي داخلي', 'meds': 'تفاصيل وبروتوكول المادة الدوائية',
            'patient': 'اختيار هوية المريض', 'role_badge': 'كبير الصيادلة',
            'status_unpaid': 'بانتظار تسوية الحساب', 'status_paid': 'تمت التسوية - جاهز للصرف'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/pharmacy')

    with content:
        with ui.grid(columns=12).classes('w-full gap-10'):
            
            # Left: Internal Order Module
            with ui.column().classes('col-span-4 gap-6'):
                ui.label(T['create']).classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                with ui.column().classes('glass-card p-10 gap-8'):
                    patients = get_all_patients()
                    p_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in patients}
                    
                    p_select = ui.select(p_options, label=T['patient'], with_input=True).classes('modern-input w-full').props('outlined')
                    m_input = ui.textarea(placeholder='Inject pharmacological parameters...').classes('modern-input w-full h-32 font-bold p-4').props('outlined')
                    
                    def add_req():
                        if not p_select.value or not m_input.value:
                            ui.notify('Mandatory pharmaceutical data missing', type='warning', position='top')
                            return
                        add_pharmacy_request(p_select.value, m_input.value)
                        ui.notify('✓ Internal Pharmacy Order Created', type='positive', position='top')
                        m_input.value = ''
                        refresh_pending()

                    with ui.button(on_click=add_req).classes('w-full h-16 rounded-2xl font-black text-white').style(f"background: linear-gradient(135deg, {colors['accent']}, {colors['accent_secondary']})"):
                        ui.icon('o_add_task', size='sm').classes('material-icons-outlined mr-2')
                        ui.label('COMMIT ORDER')

            # Right: Prescription Stream
            with ui.column().classes('col-span-8 gap-6'):
                ui.label('LIVE PRESCRIPTION STREAM').classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                pending_container = ui.column().classes('w-full gap-4')

    def refresh_pending():
        pending_container.clear()
        with pending_container:
            requests = get_pending_pharmacy()
            if not requests:
                with ui.element('div').classes('glass-card w-full py-40 flex flex-col items-center justify-center opacity-10'):
                    ui.icon('o_medication', size='5em').classes('material-icons-outlined')
                    ui.label(T['empty']).classes('text-sm font-black mt-4 italic tracking-widest')
                return

            for req in requests:
                is_paid = req['status'] == 'Paid'
                status_lbl = T['status_paid'] if is_paid else T['status_unpaid']
                status_col = colors['accent'] if is_paid else '#F5BC4B'
                
                with ui.element('div').classes('glass-card w-full p-8 group'):
                    with ui.row().classes('w-full justify-between items-center mb-6 pb-4 border-b border-white/5'):
                        with ui.row().classes('items-center gap-5'):
                            ui.avatar(req['patient_name'][0].upper(), color='zinc-800', text_color='white').classes('w-12 h-12 font-black shadow-inner')
                            with ui.column().classes('gap-0'):
                                ui.label(req['patient_name']).classes('font-black text-2xl group-hover:text-gradient')
                                ui.label(f"REQ-HS-{req['id']} • AUTHORED: {req['created_at']}").classes('text-[9px] font-black opacity-30 tracking-widest uppercase')
                        
                        with ui.row().classes('items-center px-4 py-2 rounded-xl border').style(f"border-color: {status_col}20; background: {status_col}05"):
                            ui.element('div').classes('w-2 h-2 rounded-full mr-3').style(f"background: {status_col}")
                            ui.label(status_lbl).classes('text-[9px] font-black tracking-widest').style(f"color: {status_col}")
                    
                    ui.label(req['medicine_details']).classes('text-sm font-bold opacity-80 mb-8 block p-6 rounded-2xl bg-black/20 italic whitespace-pre-wrap')
                    
                    with ui.row().classes('w-full justify-end gap-3'):
                        if not is_paid:
                            def pay_here(req_id=req['id']):
                                from database import pay_invoice
                                conn = sqlite3.connect("system.db")
                                c = conn.cursor()
                                c.execute("SELECT id FROM invoices WHERE description LIKE ? AND patient_id = ? AND status = 'Unpaid'", (f"Pharmacy: {req['medicine_details'][:20]}%", req['patient_id']))
                                inv = c.fetchone()
                                conn.close()
                                if inv:
                                    pay_invoice(inv[0], 0, "")
                                    ui.notify('✓ Local Pharmaceutical Settlement Processed', type='positive', position='top')
                                    refresh_pending()
                                else:
                                    ui.notify('Settlement record not found in core', type='warning', position='top')
                            
                            with ui.button(on_click=pay_here).classes('h-14 px-8 rounded-xl font-black text-white').style(f"background: linear-gradient(135deg, #F5BC4B, #F43F5E)"):
                                ui.icon('o_payments', size='sm').classes('material-icons-outlined mr-2')
                                ui.label('BYPASS & SETTLE')
                            
                            ui.button(icon='o_lock', color='grey').classes('h-14 px-8 rounded-xl opacity-30').props('disabled')
                        else:
                            with ui.button(on_click=lambda id=req['id']: complete_dispense(id)).classes('h-16 px-12 rounded-2xl font-black text-white').style(f"background: linear-gradient(135deg, {colors['accent']}, {colors['accent_secondary']})"):
                                ui.icon('o_medication', size='sm').classes('material-icons-outlined mr-2')
                                ui.label(T['dispense'])

    def complete_dispense(req_id):
        dispense_medicine(req_id)
        ui.notify('✓ Medication Cycle Successfully Dispensed', type='positive', position='top')
        refresh_pending()

    refresh_pending()
    ui.timer(8.0, refresh_pending)
