from nicegui import ui, app
from database import (
    get_unpaid_invoices, pay_invoice, get_all_patients, 
    get_patient_invoices, get_paid_invoices_by_date, 
    refund_invoice, set_setting, get_setting
)
from datetime import datetime
from layout import intelligence_layout, get_theme_colors

@ui.page('/accounting')
def accounting_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Financial Intelligence',
            'sub': 'Clinical Revenue & Transaction Management',
            'tabs': {
                'payment': 'Ready for Payment',
                'statement': 'Account Statement',
                'log': 'Transaction Log',
                'refunds': 'Refunds & Adjustments'
            },
            'table': {
                'id': 'ID', 'name': 'Patient Name', 'phone': 'Phone', 'doctor': 'Doctor', 'action': 'Action'
            },
            'details': 'Financial Details',
            'print': 'Print Receipt',
            'pay': 'Authorize Payment',
            'refund': 'Process Refund',
            'iqd': 'IQD',
            'search': 'Search Patients...',
            'no_data': 'No records found'
        },
        'AR': {
            'header': 'الإدارة المالية المتقدمة',
            'sub': 'إدارة الإيرادات والتحصيلات والتدقيق المالي',
            'tabs': {
                'payment': 'مهيئة للدفع',
                'statement': 'كشف حساب',
                'log': 'الفهرس المالي',
                'refunds': 'الخصم والاسترجاع'
            },
            'table': {
                'id': 'المعرف', 'name': 'اسم المريض', 'phone': 'الهاتف', 'doctor': 'الطبيب', 'action': 'الإجراء'
            },
            'details': 'التفاصيل المالية',
            'print': 'طباعة الوصل',
            'pay': 'تخويل الدفع',
            'refund': 'إجراء استرجاع',
            'iqd': 'د.ع',
            'search': 'بحث عن مريض...',
            'no_data': 'لا توجد بيانات متاحة'
        }
    }
    T = TR[lang]

    # Modal State & Logic
    class State:
        log_date = datetime.now().strftime('%Y-%m-%d')
    state = State()

    content = intelligence_layout('header', 'sub', TR, current_nav='/accounting')

    with content:
        with ui.tabs().classes('w-full max-w-6xl mx-auto mb-6 no-print') as tabs:
            ui.tab('payment', label=T['tabs']['payment'], icon='o_payments')
            ui.tab('statement', label=T['tabs']['statement'], icon='o_table_view')
            ui.tab('log', label=T['tabs']['log'], icon='o_history')
            ui.tab('refunds', label=T['tabs']['refunds'], icon='o_remove_circle_outline')

        with ui.tab_panels(tabs, value='payment').classes('w-full bg-transparent no-print'):
            # --- TAB 1: READY FOR PAYMENT ---
            with ui.tab_panel('payment'):
                @ui.refreshable
                def render_payment_tab():
                    invoices = get_unpaid_invoices()
                    with ui.column().classes('w-full max-w-5xl mx-auto gap-4'):
                        if not invoices:
                            ui.label(T['no_data']).classes('opacity-20 text-center py-20 w-full italic')
                        for inv in invoices:
                            with ui.row().classes('glass-card w-full p-6 items-center justify-between hover:bg-white/5'):
                                with ui.column().classes('gap-1'):
                                    ui.label(inv['patient_name']).classes('text-xl font-black text-gradient')
                                    ui.label(inv['description']).classes('text-[10px] font-black opacity-30 tracking-widest uppercase')
                                
                                with ui.row().classes('items-center gap-8'):
                                    ui.label(f"{inv['amount']:,} {T['iqd']}").classes('text-2xl font-black')
                                    ui.button(on_click=lambda i=inv: authorize_payment(i)).props('icon=check round unelevated').classes('bg-gradient-to-r from-emerald-500 to-teal-600 text-white')

                render_payment_tab()

            # --- TAB 2: ACCOUNT STATEMENT ---
            with ui.tab_panel('statement'):
                with ui.column().classes('w-full max-w-7xl mx-auto gap-6'):
                    search = ui.input(placeholder=T['search']).classes('modern-input w-full max-w-md self-center').props('outlined dense')
                    
                    columns = [
                        {'name': 'id', 'label': T['table']['id'], 'field': 'id', 'required': True, 'align': 'left'},
                        {'name': 'name', 'label': T['table']['name'], 'field': 'name', 'sortable': True, 'align': 'left'},
                        {'name': 'phone', 'label': T['table']['phone'], 'field': 'phone', 'align': 'left'},
                        {'name': 'doctor', 'label': T['table']['doctor'], 'field': 'doctor', 'align': 'left'},
                        {'name': 'action', 'label': T['table']['action'], 'field': 'action', 'align': 'center'}
                    ]
                    
                    def on_search(e):
                        filtered = [p for p in get_all_patients() if e.value.lower() in p['name'].lower() or e.value in str(p['phone'])]
                        table.rows = filtered

                    table = ui.table(columns=columns, rows=get_all_patients(), row_key='id').classes('w-full glass-card overflow-hidden')
                    table.add_slot('body-cell-action', '''
                        <q-td :props="props">
                            <q-btn flat round color="primary" icon="visibility" @click="$parent.$emit('view_details', props.row.id)" />
                            <q-btn flat round color="secondary" icon="print" @click="$parent.$emit('print_patient', props.row)" />
                        </q-td>
                    ''')
                    
                    search.on('update:model-value', on_search)
                    
                    table.on('view_details', lambda e: show_patient_details(e.args))
                    table.on('print_patient', lambda e: print_receipt_mode(e.args))

            # --- TAB 3: TRANSACTION LOG ---
            with ui.tab_panel('log'):
                @ui.refreshable
                def render_log_tab():
                    date_val = datetime.now().strftime('%Y-%m-%d')
                    with ui.column().classes('w-full max-w-6xl mx-auto gap-6'):
                        with ui.row().classes('w-full justify-between items-center'):
                            ui.label(T['tabs']['log']).classes('text-2xl font-black text-gradient uppercase')
                            ui.input(value=date_val, on_change=lambda e: (setattr(state, 'log_date', e.value), render_log_tab.refresh())).props('type=date').classes('modern-input w-48')
                        
                        target_date = getattr(state, 'log_date', date_val)
                        paid_invoices = get_paid_invoices_by_date(target_date)
                        
                        if not paid_invoices:
                            ui.label(T['no_data']).classes('opacity-20 text-center py-20 w-full')
                        else:
                            for inv in paid_invoices:
                                with ui.row().classes('w-full p-4 border-b border-white/5 items-center justify-between opacity-80 hover:opacity-100 transition-opacity'):
                                    with ui.row().classes('gap-4 items-center'):
                                        ui.label(inv['paid_at']).classes('text-[10px] opacity-40 font-mono')
                                        ui.label(inv['patient_name']).classes('font-bold text-xs')
                                        ui.label(inv['description']).classes('text-[9px] opacity-30 uppercase tracking-tighter')
                                    ui.label(f"+{inv['amount']:,}").classes('text-xs font-black text-emerald-400')

                render_log_tab()

            # --- TAB 4: REFUNDS & ADJUSTMENTS ---
            with ui.tab_panel('refunds'):
                @ui.refreshable
                def render_refund_tab():
                    with ui.column().classes('w-full max-w-5xl mx-auto gap-8'):
                        # Section: Refundable Active Transactions
                        with ui.column().classes('w-full gap-4'):
                            ui.label('REFUNDABLE TRANSACTIONS').classes('text-[10px] font-black opacity-30 tracking-[0.4em]')
                            recent_paid = get_paid_invoices_by_date(datetime.now().strftime('%Y-%m-%d'))[:10]
                            if not recent_paid:
                                ui.label('No recent paid transactions').classes('text-[10px] opacity-20 italic')
                            for inv in recent_paid:
                                with ui.row().classes('glass-card w-full p-4 items-center justify-between border-l-4 border-red-500/20'):
                                    with ui.column().classes('gap-0'):
                                        ui.label(inv['patient_name']).classes('font-black text-sm')
                                        ui.label(inv['description']).classes('text-[9px] opacity-40')
                                    ui.button('Refund Ticket', on_click=lambda i=inv: confirm_refund(i)) \
                                        .props('flat color=red size=sm').classes('font-black')

                        # Section: Cancelled Bookings (Auditing)
                        with ui.column().classes('w-full gap-4 mt-10'):
                            ui.label('CANCELLED BOOKINGS (NEEDS AUDIT)').classes('text-[10px] font-black opacity-30 tracking-[0.4em]')
                            from database import get_appointments
                            cancelled = [a for a in get_appointments() if a['status'] == 'Cancelled'][:10]
                            if not cancelled:
                                ui.label('No cancelled bookings found').classes('text-[10px] opacity-20 italic')
                            for appt in cancelled:
                                with ui.row().classes('glass-card w-full p-4 items-center justify-between opacity-60'):
                                    with ui.column().classes('gap-0'):
                                        ui.label(appt['patient_name']).classes('font-bold text-xs')
                                        ui.label(f"Dr. {appt['doctor_name']} - {appt['visit_date']}").classes('text-[8px]')
                                    ui.icon('o_cancel', color='red', size='xs')

                render_refund_tab()

        # --- HIDDEN PRINT AREA ---
        with ui.column().classes('fixed-top w-full h-full bg-white text-black p-10 z-[3000] hidden print:block') as print_area:
            ui.label('PAYMENT RECEIPT').classes('text-3xl font-black border-b-4 border-black pb-2 w-full text-center')
            with ui.row().classes('w-full justify-between mt-10'):
                 print_patient_name = ui.label('').classes('text-xl font-bold')
                 print_date = ui.label('').classes('text-xl opacity-60')
            
            ui.separator().classes('my-4 bg-black/10')
            print_details = ui.column().classes('w-full gap-4')
            ui.separator().classes('my-4 bg-black/10')
            
            with ui.row().classes('w-full justify-between mt-10'):
                 ui.label('TOTAL SETTLEMENT').classes('text-2xl font-black')
                 print_total = ui.label('').classes('text-2xl font-black')
            
            ui.label('Thank you for choosing HealthPro Intelligence').classes('w-full text-center mt-20 opacity-40 italic text-sm')

        # Modal Logic

        def authorize_payment(inv):
            with ui.dialog() as dialog, ui.column().classes('glass-card p-10 w-[450px] gap-8'):
                ui.label(T['pay']).classes('text-2xl font-black')
                ui.label(inv['patient_name']).classes('text-xl opacity-60 text-center w-full')
                ui.label(f"{inv['amount']:,} {T['iqd']}").classes('text-4xl font-black text-gradient text-center w-full')
                
                discount = ui.number('Apply Discount (IQD)', value=0).classes('modern-input w-full').props('outlined')
                
                def proceed():
                    pay_invoice(inv['id'], discount.value or 0, "Authorized from Dashboard")
                    dialog.close()
                    ui.notify('Payment Confirmed', type='positive')
                    render_payment_tab.refresh()
                    render_log_tab.refresh()
                    render_refund_tab.refresh()

                ui.button('CONFIRM TRANSACTION', on_click=proceed).classes('w-full h-14 rounded-xl font-black text-white').style(f"background: {colors['gradient']}")
            dialog.open()

        def confirm_refund(inv):
            with ui.dialog() as dialog, ui.column().classes('glass-card p-10 w-[400px] gap-6'):
                ui.label('REFUND AUTHORIZATION').classes('text-lg font-black text-red-500')
                ui.label(f"Refund {inv['amount']:,} IQD to {inv['patient_name']}?").classes('text-sm opacity-80')
                reason = ui.input('Reason for Refund').classes('modern-input w-full').props('outlined')
                
                with ui.row().classes('w-full gap-3 justify-end'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    ui.button('Execute Refund', on_click=lambda: (refund_invoice(inv['id'], reason.value), dialog.close(), ui.notify('Refunded', color='red'), render_refund_tab.refresh())).props('unelevated color=red')
            dialog.open()

        def show_patient_details(pid):
            invoices = get_patient_invoices(pid)
            patient = next((p for p in get_all_patients() if p['id'] == pid), None)
            if not patient: return
            
            # Calculate Totals
            total_paid = sum(inv['amount'] for inv in invoices if inv['status'] == 'Paid')
            total_pending = sum(inv['amount'] for inv in invoices if inv['status'] == 'Unpaid')
            total_refunded = sum(inv['amount'] for inv in invoices if inv['status'] == 'Refunded')

            with ui.dialog() as dialog, ui.column().classes('bg-[#a1a1aa] p-0 w-[700px] gap-0 rounded-3xl overflow-hidden border border-white/10 shadow-2xl'):
                # 1. Premium Solid Header
                with ui.row().classes('w-full p-8 bg-gradient-to-r from-blue-600 to-blue-800 items-center justify-between text-white'):
                    with ui.column().classes('gap-1 text-right'):
                        ui.label(T['details']).classes('text-[10px] font-black opacity-60 tracking-[0.4em] uppercase')
                        ui.label(patient['name']).classes('text-3xl font-black tracking-tight')
                    ui.icon('o_account_balance_wallet', size='3em').classes('opacity-30')

                # 2. Patient Metadata Bar
                with ui.row().classes('w-full bg-black/5 p-6 border-b border-black/5 justify-around text-right'):
                    with ui.column().classes('items-center gap-1'):
                        ui.label(T['table']['id']).classes('text-[8px] font-black opacity-30')
                        ui.label(str(patient['id'])).classes('text-xs font-bold text-blue-600')
                    with ui.column().classes('items-center gap-1'):
                        ui.label(T['table']['phone']).classes('text-[8px] font-black opacity-30')
                        ui.label(patient['phone']).classes('text-xs font-bold text-gray-900')
                    with ui.column().classes('items-center gap-1'):
                        ui.label(T['table']['doctor']).classes('text-[8px] font-black opacity-30')
                        ui.label(patient['doctor']).classes('text-xs font-bold text-gray-900')

                # 3. Transaction List
                with ui.column().classes('w-full p-8 gap-4 max-h-[400px] overflow-y-auto bg-gray-50'):
                    if not invoices:
                        ui.label(T['no_data']).classes('opacity-20 text-center py-10 w-full italic')
                    for inv in invoices:
                        status_cfg = {
                            'Paid': ('bg-emerald-500/20 text-emerald-400 border border-emerald-500/30', 'check_circle'),
                            'Unpaid': ('bg-amber-500/20 text-amber-400 border border-amber-500/30', 'pending'),
                            'Refunded': ('bg-red-500/20 text-red-400 border border-red-500/30', 'history')
                        }.get(inv['status'], ('bg-white/5 text-white/50', 'info'))
                        
                        with ui.row().classes('w-full p-5 bg-white rounded-2xl items-center justify-between border border-black/5 shadow-sm hover:border-blue-200'):
                            with ui.row().classes('gap-4 items-center'):
                                ui.icon(status_cfg[1], size='xs').classes(status_cfg[0].split()[1])
                                with ui.column().classes('gap-0 text-right'):
                                    ui.label(inv['description']).classes('text-sm font-black text-gray-900')
                                    ui.label(inv['created_at']).classes('text-[9px] opacity-30 font-bold')
                            
                            with ui.column().classes('items-end gap-1'):
                                ui.label(f"{inv['amount']:,}").classes('text-lg font-black text-gray-900')
                                ui.label(inv['status']).classes(f'text-[7px] font-black uppercase px-3 py-1 rounded-full {status_cfg[0]}')

                # 4. Financial Summary Footer
                with ui.row().classes('w-full p-8 bg-white border-t border-black/5 justify-between items-center'):
                    with ui.row().classes('gap-8'):
                        with ui.column().classes('items-center gap-1'):
                            ui.label('PAID').classes('text-[7px] font-black opacity-30')
                            ui.label(f"{total_paid:,}").classes('text-sm font-black text-emerald-600')
                        with ui.column().classes('items-center gap-1'):
                            ui.label('PENDING').classes('text-[7px] font-black opacity-30')
                            ui.label(f"{total_pending:,}").classes('text-sm font-black text-amber-600')
                        with ui.column().classes('items-center gap-1'):
                            ui.label('REFUNDED').classes('text-[7px] font-black opacity-30')
                            ui.label(f"{total_refunded:,}").classes('text-sm font-black text-red-600')
                    
                    ui.button('CLOSE', on_click=dialog.close).props('flat text-color=grey-9').classes('font-black text-xs opacity-40 hover:opacity-100 transition-all')

            dialog.open()

        def print_receipt_mode(patient):
            # Fill print area and call window.print
            patient_invoices = [i for i in get_patient_invoices(patient['id']) if i['status'] == 'Paid']
            if not patient_invoices:
                ui.notify('No paid invoices to print', type='warning')
                return
            
            print_patient_name.set_text(patient['name'])
            print_date.set_text(datetime.now().strftime('%Y-%m-%d %H:%M'))
            print_details.clear()
            total = 0
            with print_details:
                for inv in patient_invoices:
                    with ui.row().classes('w-full justify-between'):
                        ui.label(inv['description']).classes('text-lg')
                        ui.label(f"{inv['amount']:,}").classes('text-lg font-bold')
                    total += inv['amount']
            print_total.set_text(f"{total:,} IQD")
            
            ui.run_javascript('window.print()')
