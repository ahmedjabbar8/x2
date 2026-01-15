from nicegui import ui, app
from database import get_waiting_list, add_to_waiting_room, process_waiting, get_all_patients
from layout import intelligence_layout, get_theme_colors

@ui.page('/waiting_room')
def waiting_room_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Waiting Ecosystem', 'sub': 'Live Patient Flow & Hospitality Logistics',
            'call': 'AUTHORIZE CALL', 'empty': 'Zero patients currently in clinical queue',
            'add': 'INITIATE QUEUE ENTRY', 'select': 'Target Identity Selection',
            'role_badge': 'RECEPTIONIST'
        },
        'AR': {
            'header': 'إدارة طابور الانتظار', 'sub': 'تدفق المرضى المباشر والخدمات اللوجستية',
            'call': 'استدعاء المريض', 'empty': 'لا يوجد مرضى في الانتظار حالياً',
            'add': 'إدراج مريض في الطابور', 'select': 'البحث واختيار هوية المريض',
            'role_badge': 'موظف الاستقبال'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/waiting_room')

    with content:
        with ui.grid(columns=12).classes('w-full gap-10'):
            
            # Left: Intake Engine
            with ui.column().classes('col-span-4 gap-6'):
                ui.label(T['add']).classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                with ui.column().classes('glass-card p-10 gap-8'):
                    patients = get_all_patients()
                    p_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in patients}
                    p_select = ui.select(p_options, label=T['select'], with_input=True).classes('modern-input w-full').props('outlined')
                    
                    def add_to_q():
                        if not p_select.value:
                            ui.notify('Mandatory identity selection missing', type='warning', position='top')
                            return
                        if add_to_waiting_room(p_select.value):
                            ui.notify('✓ Patient Routed to Live Flow', type='positive', position='top')
                            p_select.value = None
                            refresh_list()
                        else:
                            ui.notify('Identity already exists in active queue', type='info', position='top')

                    with ui.button(on_click=add_to_q).classes('w-full h-16 rounded-2xl font-black text-white shadow-xl').style(f"background: linear-gradient(135deg, #007AFF, #5AC8FA)"):
                        ui.icon('o_person_add', size='sm').classes('material-icons-outlined mr-2')
                        ui.label('COMMIT ENTRY')

            # Right: Live Flow Stream
            with ui.column().classes('col-span-8 gap-6'):
                ui.label('LIVE CLINICAL STREAM').classes('text-[10px] font-black opacity-40 tracking-[0.4em]')
                waiting_container = ui.column().classes('w-full gap-4')

    def refresh_list():
        waiting_container.clear()
        with waiting_container:
            wait_list = get_waiting_list()
            if not wait_list:
                with ui.element('div').classes('glass-card w-full py-40 flex flex-col items-center justify-center opacity-10'):
                    ui.icon('o_groups', size='5em').classes('material-icons-outlined')
                    ui.label(T['empty']).classes('text-sm font-black mt-4 italic tracking-widest')
                return

            for i, p in enumerate(wait_list):
                with ui.element('div').classes('glass-card w-full p-6 flex flex-row items-center justify-between group hover:border-emerald-500/30'):
                    with ui.row().classes('items-center gap-6'):
                        # Industrial Seq Indicator
                        with ui.element('div').classes('w-12 h-12 rounded-xl flex items-center justify-center font-black shadow-inner bg-black/20 border border-white/5').style(f"color: {colors['accent']}"):
                            ui.label(f"{i+1:02d}")
                        
                        with ui.column().classes('gap-0'):
                            with ui.row().classes('items-center gap-2'):
                                ui.label(p['patient_name']).classes('font-black text-xl group-hover:text-gradient')
                                # Priority Badge
                                prio = p.get('priority_level', 'Green')
                                prio_cols = {'Red': 'bg-red-500', 'Yellow': 'bg-yellow-500', 'Green': 'bg-emerald-500'}
                                ui.label(prio.upper()).classes(f"text-[8px] font-black text-white px-2 py-0.5 rounded-full {prio_cols.get(prio, 'bg-gray-500')}")
                            
                            ui.label(f"ID:{p['patient_id']} • {p['gender']} • {p['age']}Y • LOGGED: {p['arrived_at']}").classes('text-[9px] font-black opacity-30 tracking-widest uppercase')
                    
                    with ui.button(on_click=lambda id=p['id']: call_patient(id)).classes('h-14 px-8 rounded-xl font-black text-white shadow-lg').style(f"background: linear-gradient(135deg, #007AFF, #5AC8FA)"):
                        ui.icon('o_volume_up', size='sm').classes('material-icons-outlined mr-2')
                        ui.label(T['call'])

    def call_patient(w_id):
        process_waiting(w_id)
        ui.notify('✓ Patient Called to Clinical Hub', type='positive', position='top')
        refresh_list()

    refresh_list()
    ui.timer(10.0, refresh_list)
