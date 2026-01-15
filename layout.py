from nicegui import ui, app
from datetime import datetime

def get_theme_colors(theme='dracula'):
    return {
        'bg': '#FFFFFF',           # Pure White
        'card': '#F5F5F7',         # Silk Light Card
        'sidebar': '#FFFFFF',
        'border': 'rgba(0, 0, 0, 0.1)', # Soft Border
        'text': '#1D1D1F',         # Deep Ink Text
        'text_secondary': '#6E6E73',
        'accent': '#007AFF',       # Apple Blue
        'accent_secondary': '#5AC8FA', 
        'gradient': 'linear-gradient(135deg, #007AFF, #5AC8FA)', 
        'error': '#FF3B30',
        'input_bg': '#FFFFFF',
        'shadow': '0 8px 30px rgba(0, 0, 0, 0.06)',
        'ring': 'rgba(0, 122, 255, 0.15)'
    }


def inject_theme(lang='AR'):
    """Injects the custom Modern Dark Dynamic CSS into the current page."""
    theme = app.storage.user.get('theme', 'dracula')
    colors = get_theme_colors(theme)
    ui.add_head_html(f'''
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Outlined" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;700&family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

        :root {{
            --bg-dark: {colors['bg']};
            --sidebar-bg: {colors.get('sidebar', '#141416')};
            --card-bg: {colors['card']};
            --accent-primary: {colors['accent']};
            --accent-secondary: {colors['accent_secondary']};
            --text-main: {colors['text']};
            --text-muted: {colors['text_secondary']};
            --gradient-flow: {colors.get('gradient', 'linear-gradient(45deg, #12c2e9, #c471ed, #f64f59)')};
        }}

        * {{
            font-family: 'Tajawal', "Outfit", "Inter", sans-serif;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}


        body {{
            background: var(--bg-dark) !important;
            color: var(--text-main) !important;
            margin: 0; padding: 0;
            overflow-x: hidden;
            background-image: radial-gradient(circle at 10% 20%, rgba(0, 122, 255, 0.02) 0%, transparent 50%),
                             radial-gradient(circle at 90% 80%, rgba(0, 122, 255, 0.03) 0%, transparent 50%);
        }}

        /* Global Card Styling (The Magic) */
        .glass-card, .dynamic-card {{
            background: var(--card-bg) !important;
            border: 1px solid rgba(0, 0, 0, 0.03) !important;
            border-radius: 20px !important;
            color: var(--text-main) !important;
            position: relative;
            overflow: hidden !important;
            box-shadow: {colors['shadow']} !important;
            text-decoration: none !important;
        }}

        .glass-card:hover, .dynamic-card:hover {{
            background: #FFFFFF !important;
            border-color: var(--accent-primary) !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08) !important;
        }}

        /* Modern Typography */
        .text-gradient {{
            background: var(--gradient-flow);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}

        /* Premium Inputs */
        .modern-input .q-field__inner {{
            background: {colors['input_bg']} !important;
            border-radius: 14px !important;
        }}
        .modern-input .q-field__control:before {{ border: 1px solid {colors['border']} !important; border-radius: 14px !important; }}
        .modern-input .q-field__control:after {{ border-radius: 14px !important; }}
        .modern-input.q-field--focused .q-field__control {{
            box-shadow: 0 0 0 4px {colors['ring']} !important;
            border-color: var(--accent-primary) !important;
        }}
        /* Compact UI Adjustments */
        .compact-card {{
            padding: 0.75rem !important;
            border-radius: 12px !important;
        }}
        .compact-input .q-field__inner {{
            padding: 0.4rem 0.6rem !important;
            font-size: 0.9rem !important;
        }}
        .compact-button {{
            min-height: 2rem !important;
            padding: 0 0.75rem !important;
            font-size: 0.85rem !important;
        }}
        .modern-input .q-field__inner {{
            background: {colors['input_bg']} !important;
            border-radius: 14px !important;
        }}
        .modern-input .q-field__control:before {{ border: 1px solid {colors['border']} !important; border-radius: 14px !important; }}
        .modern-input .q-field__control:after {{ border-radius: 14px !important; }}
        .modern-input.q-field--focused .q-field__control {{
            box-shadow: 0 0 0 4px {colors['ring']} !important;
            border-color: var(--accent-primary) !important;
        }}

        /* Crystal Silk Design Navbar - LIGHT GLASS */
        /* Universal Crystal White Navbar */
        .navbar {{
            background: rgba(255, 255, 255, 0.8) !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
            backdrop-filter: blur(50px) saturate(200%) !important;
            -webkit-backdrop-filter: blur(50px) saturate(200%) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
            height: 56px !important;
            color: #1D1D1F !important;
        }}

        .navbar-content {{
            height: 100%;
            display: flex;
            align-items: center;
            padding: 0 16px;
        }}

        .silk-btn {{
            background: rgba(0, 0, 0, 0.03) !important;
            border-radius: 12px !important;
            color: inherit !important;
        }}

        .silk-btn:hover {{
            background: rgba(0, 0, 0, 0.06) !important;
        }}

        .navbar-brand {{
            color: var(--accent-primary) !important;
            font-weight: bold;
            font-size: 1.5rem;
        }}

        .nav-link {{
            color: var(--text-muted);
            font-weight: 700;
            padding: 8px 16px;
            border-radius: 12px;
            font-size: 0.85rem;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
        }}

        .nav-link:hover, .nav-link.active {{
            color: var(--accent-primary) !important;
            background: rgba(0, 122, 255, 0.05);
        }}

        .nav-link.active {{
            background: var(--accent-primary) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(0, 122, 255, 0.2);
        }}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-primary); }}
        
        /* --- CLINICAL DIAGNOSTIC UI (TRIAGE SPECIAL) --- */
        .clinical-vitals-card {{
            background: linear-gradient(145deg, rgba(255,255,255,0.02), rgba(255,255,255,0.05)) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
            border-radius: 20px !important;
        }}

        .clinical-vitals-card:hover {{
            border-color: var(--accent-primary) !important;
            box-shadow: 0 15px 40px rgba(139, 92, 246, 0.15) !important;
        }}

        .vitals-input-group {{
            background: rgba(0,0,0,0.2) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            border: 1px dashed var(--accent-secondary);
        }}

        .ai-brain-panel {{
            background: rgba(139, 92, 246, 0.03) !important;
            border: 1px solid rgba(139, 92, 246, 0.2) !important;
            border-radius: 24px !important;
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }}

        .patient-row-card {{
            border-radius: 15px !important;
            border-left: 5px solid var(--accent-primary) !important;
            background: rgba(255,255,255,0.02) !important;
            margin-bottom: 10px;
        }}

        .patient-row-card:hover {{
            background: rgba(255,255,255,0.06) !important;
        }}

        .pulsing-dot {{
            width: 8px; height: 8px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #10B981;
        }}

        .glow-text {{
            text-shadow: 0 0 15px var(--accent-primary);
        }}

        /* Medical Hierarchy Typography */
        .medical-label {{
            font-size: 0.7rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
            opacity: 0.6 !important;
        }}

        .medical-value {{
            font-family: 'Outfit', sans-serif !important;
            font-weight: 800 !important;
        }}
    ''')

def intelligence_layout(title_key, sub_key, TR, current_nav='/'):
    """
    Standardizes theme injection and provides the header for all pages.
    """
    colors = get_theme_colors()
    
    lang = app.storage.user.get('lang', 'AR')
    inject_theme(lang)
    
    def toggle_lang():
        app.storage.user['lang'] = 'EN' if lang == 'AR' else 'AR'
        ui.navigate.reload()

    def toggle_dark_mode():
        app.storage.user['theme'] = 'light' if dark_mode else 'dracula'
        ui.navigate.reload()

    # Header / Navbar - Crystal Silk
    with ui.header().classes('navbar flex items-center justify-between px-4'):
        # Left: Branding & Navigation
        with ui.row().classes('items-center gap-3'):
            with ui.row().classes('items-center gap-2 cursor-pointer').on('click', lambda: ui.navigate.to('/')):
                ui.icon('o_health_and_safety', size='24px').classes('text-blue-600')
                ui.label('HEALTHPRO').classes('font-black text-sm tracking-tight text-gray-900')
            
            ui.separator().props('vertical').classes('h-5 opacity-20')
            
            # Subtitle/Context
            ui.label(TR.get(title_key, 'Dashboard')).classes('text-[10px] font-bold opacity-60 uppercase tracking-wider')

        # Center: Clock (Silk Style)
        with ui.row().classes('absolute-center items-center gap-2 bg-black/5 dark:bg-white/5 px-4 py-1 rounded-full border border-black/5 dark:border-white/5'):
            clock_label = ui.label().classes('text-[12px] font-black tracking-tighter opacity-80')
            def update_time():
                now = datetime.now()
                time_str = now.strftime("%I:%M:%S %p") if lang == "EN" else f'{now.strftime("%I:%M:%S")} {"مساءً" if now.hour >= 12 else "صباحاً"}'
                clock_label.set_text(time_str)
            ui.timer(1.0, update_time)

        # Right: User & Tools
        with ui.row().classes('items-center gap-2'):
            # Language Toggle
            with ui.button(on_click=toggle_lang) \
                .props('flat round dense size=sm').classes('silk-btn'):
                ui.icon('o_translate', size='18px')
            
            ui.separator().props('vertical').classes('h-5 opacity-20 mx-1')
            
            # Exit
            with ui.button(on_click=lambda: (app.storage.user.update({'authenticated': False}), ui.navigate.to('/login'))) \
                .props('flat round dense size=sm').classes('text-red-400 hover:text-red-500'):
                ui.icon('o_logout', size='16px')

    # Content Container - Compensating for 48px navbar
    content = ui.column().classes('w-full items-center pt-14')
    return content
