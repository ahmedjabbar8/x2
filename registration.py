from nicegui import ui, app
from database import add_user
from layout import intelligence_layout, get_theme_colors

@ui.page('/registration')
def registration_page():
    # Security: Ensure only authenticated admins can access
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    
    if app.storage.user.get('role') != 'admin':
        ui.notify('Access Denied: Admins only', type='negative')
        ui.navigate.to('/')
        return

    colors = get_theme_colors()
    content = intelligence_layout('Register New User', '', {}, current_nav='/registration')

    with content:
        with ui.column().classes('w-full items-center p-8'):
            with ui.element('div').classes('glass-card w-full max-w-lg p-10 flex flex-col items-center gap-8'):
                ui.icon('person_add', size='4em', color=colors['accent']).classes('material-icons-outlined opacity-50 mb-2')
                
                with ui.column().classes('w-full gap-4'):
                    new_user = ui.input('New Username').classes('w-full modern-input').props('outlined')
                    new_pass = ui.input('New Password', password=True).classes('w-full modern-input').props('outlined')
                    new_role = ui.select(['user', 'admin'], value='user', label='Role').classes('w-full modern-input').props('outlined')
                
                def register_user():
                    if not new_user.value or not new_pass.value:
                        ui.notify('Please fill all fields', type='warning')
                        return

                    if add_user(new_user.value, new_pass.value, new_role.value):
                        ui.notify(f'User {new_user.value} created successfully!', type='positive')
                        new_user.value = ''
                        new_pass.value = ''
                    else:
                        ui.notify('Error: Username likely exists', type='negative')

                ui.button('CREATE INFRASTRUCTURE ACCOUNT', on_click=register_user, icon='verified').classes('w-full h-16 rounded-2xl font-black text-white shadow-lg').style("background: linear-gradient(135deg, #007AFF, #5AC8FA)")
