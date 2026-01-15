from nicegui import ui, app
from database import get_archives
from layout import intelligence_layout, get_theme_colors

@ui.page('/archive')
def archive_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return

    lang = app.storage.user.get('lang', 'AR')
    colors = get_theme_colors()
    
    TR = {
        'EN': {
            'header': 'Historical Vault',
            'sub': 'End-to-End Clinical Records & Archival',
            'search': 'Search clinical history...',
            'empty': 'Zero historical records available',
            'date': 'TIMESTAMP',
            'patient': 'PATIENT IDENTITY',
            'type': 'PROTOCOL',
            'details': 'CLINICAL DATA',
            'records_title': 'CHRONOLOGICAL LOG',
            'total_records': 'Total Vault Size',
            'this_month': 'Current Cycle',
            'filter': 'Filter',
            'export': 'Export Data'
        },
        'AR': {
            'header': 'الأرشيف المركزي',
            'sub': 'سجلات البيانات التاريخية والمؤرشفة',
            'search': 'بحث في الأرشيف الشامل...',
            'empty': 'لا توجد سجلات تاريخية متوفرة',
            'date': 'التاريخ والوقت',
            'patient': 'هوية المريض',
            'type': 'نوع الإجراء',
            'details': 'التفاصيل السريرية',
            'records_title': 'السجل الزمني للعمليات',
            'total_records': 'إجمالي السجلات',
            'this_month': 'دورة هذا الشهر',
            'filter': 'تصفية',
            'export': 'تصدير'
        }
    }
    T = TR[lang]

    content = intelligence_layout('header', 'sub', TR, current_nav='/archive')

    with content:
        # Header Section
        with ui.row().classes('w-full items-center justify-between mb-12'):
            with ui.column().classes('gap-1'):
                ui.label(T['records_title']).classes('text-[10px] font-black tracking-[0.3em] opacity-40')
                ui.label(T['header']).classes('text-4xl font-black text-gradient')
            
            with ui.row().classes('gap-3'):
                ui.button(T['filter'], icon='filter_list').classes('bg-white/5 border border-white/10 rounded-xl px-6 font-bold')
                ui.button(T['export'], icon='download').classes('rounded-xl px-6 font-black text-white').style(f"background: linear-gradient(135deg, {colors['accent']}, {colors['accent_secondary']})")

        # Stats Grid
        with ui.row().classes('w-full gap-8 mb-12'):
            # Total Records
            with ui.element('div').classes('glass-card flex-1 p-8'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('gap-1'):
                        ui.label(T['total_records']).classes('text-xs font-bold opacity-40 uppercase tracking-widest')
                        ui.label('1,234').classes('text-3xl font-black')
                    ui.icon('inventory_2', size='3em', color=colors['accent']).classes('material-icons-outlined opacity-20')
            
            # This Month
            with ui.element('div').classes('glass-card flex-1 p-8'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('gap-1'):
                        ui.label(T['this_month']).classes('text-xs font-bold opacity-40 uppercase tracking-widest')
                        ui.label('89').classes('text-3xl font-black')
                    ui.icon('calendar_today', size='3em', color=colors['accent_secondary']).classes('material-icons-outlined opacity-20')

        # Search Box
        with ui.element('div').classes('glass-card w-full mb-10 p-4'):
            with ui.row().classes('w-full items-center gap-4 px-4'):
                ui.icon('search', size='md', color=colors['accent']).classes('material-icons-outlined')
                search_input = ui.input(placeholder=T['search']).props('outlined dense borderless').classes('modern-input flex-1 h-12 font-bold')

        # Table Section
        columns = [
            {'name': 'date', 'label': T['date'], 'field': 'date', 'sortable': True, 'align': 'left'},
            {'name': 'patient', 'label': T['patient'], 'field': 'patient_name', 'sortable': True, 'align': 'left'},
            {'name': 'type', 'label': T['type'], 'field': 'record_type', 'sortable': True, 'align': 'left'},
            {'name': 'details', 'label': T['details'], 'field': 'details', 'sortable': False, 'align': 'left'},
        ]

        def get_rows():
            try:
                archives = get_archives()
                return [dict(row) for row in archives]
            except: return []

        rows = get_rows()
        
        if not rows:
            with ui.element('div').classes('glass-card w-full p-24 flex flex-col items-center opacity-20'):
                ui.icon('folder_off', size='5em').classes('material-icons-outlined')
                ui.label(T['empty']).classes('text-xl font-bold mt-4')
        else:
            with ui.element('div').classes('glass-card w-full p-2 overflow-hidden'):
                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='id',
                    pagination={'rowsPerPage': 10}
                ).classes('w-full bg-transparent')
                
                # Custom Table Styling for Dual Theme
                ui.add_head_html(f'''
                <style>
                    .q-table__card {{ background: transparent !important; box-shadow: none !important; }}
                    .q-table thead tr th {{ 
                        color: #1D1D1F !important; 
                        font-weight: 800 !important;
                        text-transform: uppercase !important;
                        font-size: 10px !important;
                        letter-spacing: 2px !important;
                        border-bottom: 1px solid rgba(0,0,0,0.05) !important;
                    }}
                    .q-table tbody td {{ 
                        color: #1D1D1F !important; 
                        font-weight: 500 !important;
                        border-bottom: 1px solid rgba(0,0,0,0.05) !important;
                        padding: 16px !important;
                        white-space: normal !important;
                        word-break: break-all !important;
                    }}
                    .q-table tbody tr:hover {{ background: rgba(0, 122, 255, 0.05) !important; }}
                    .q-table__bottom {{ 
                        border-top: 1px solid rgba(0,0,0,0.05) !important;
                        color: #6E6E73 !important;
                        font-weight: 800 !important;
                    }}
                </style>
                ''')

            def filter_table(e):
                query = e.value if hasattr(e, 'value') else e
                if not query:
                    table.rows = rows
                else:
                    q_low = query.lower()
                    table.rows = [
                        row for row in rows 
                        if (q_low in str(row.get('patient_name', '')).lower() 
                            or q_low in str(row.get('details', '')).lower() 
                            or q_low in str(row.get('record_type', '')).lower())
                    ]

            search_input.on('update:model-value', filter_table)