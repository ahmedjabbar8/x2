from nicegui import ui, app

def aviation_procurement_page():
    # Page Setup
    ui.query('body').style('background: #0B0E14; margin: 0; overflow-x: hidden;')
    
    # Custom CSS for "Outcrowd" Hover Effects and Aviation Aesthetics
    ui.add_head_html("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=Outfit:wght@300;600;900&display=swap');
        
        :root {
            --primary: #4F46E5;
            --accent: #00F5D4;
            --bg-dark: #0B0E14;
            --glass: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --font-main: 'Inter', sans-serif;
            --font-logo: 'Outfit', sans-serif;
        }

        body { font-family: var(--font-main); color: white; }

        /* Background Radar Animation */
        .radar-bg {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: radial-gradient(circle at 50% 50%, #151921 0%, #0B0E14 100%);
            z-index: -1;
            overflow: hidden;
        }
        .radar-line {
            position: absolute;
            top: 50%; left: 50%;
            width: 150vw; height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            transform-origin: center;
            opacity: 0.1;
            animation: radar-sweep 8s infinite linear;
        }
        @keyframes radar-sweep {
            from { transform: translate(-50%, -50%) rotate(0deg); }
            to { transform: translate(-50%, -50%) rotate(0deg); }
        }
        .grid-overlay {
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
        }

        /* Procurement Card - THE CORE HOVER EFFECT */
        .procurement-card {
            background: var(--glass);
            backdrop-filter: blur(20px) saturate(160%);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 32px;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
        }

        /* Glow Border on Hover */
        .procurement-card::before {
            content: '';
            position: absolute;
            inset: 0;
            border: 1px solid transparent;
            border-radius: inherit;
            background: linear-gradient(135deg, var(--accent), var(--primary)) border-box;
            -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.5s ease;
        }

        .procurement-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 20px 40px -10px rgba(0, 245, 212, 0.15);
        }

        .procurement-card:hover::before {
            opacity: 1;
        }

        /* Hover Reveal Info */
        .reveal-info {
            max-height: 200px;
            opacity: 1;
            margin-top: 24px;
        }

        /* Info is already revealed */

        /* Animated Icon */
        .card-icon {
            font-size: 32px;
            color: var(--accent);
            margin-bottom: 24px;
            transition: transform 0.5s ease;
        }
        .procurement-card:hover .card-icon {
            transform: rotate(-10deg) scale(1.2);
        }

        .text-gradient {
            background: linear-gradient(135deg, white 60%, rgba(255,255,255,0.4));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .tag {
            padding: 4px 12px;
            border-radius: 99px;
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border: 1px solid rgba(255,255,255,0.1);
        }
    </style>
    """)

    # Layout Construction
    with ui.element('div').classes('radar-bg'):
        ui.element('div').classes('radar-line')
        ui.element('div').classes('grid-overlay')

    with ui.column().classes('w-full max-w-7xl mx-auto px-10 py-20 gap-20'):
        
        # Header Section
        with ui.column().classes('w-full gap-4'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('o_flight_takeoff', size='md').classes('material-icons-outlined text-emerald-400')
                ui.label('AVIATION CORE').classes('text-[10px] font-black tracking-[0.5em] opacity-40')
            
            with ui.row().classes('w-full justify-between items-end'):
                ui.label('Strategic Procurement Hub').classes('text-7xl font-black text-gradient leading-tight tracking-tighter').style('font-family: var(--font-logo)')
                with ui.column().classes('items-end'):
                    ui.label('LIVE OPERATIONAL DATA').classes('text-[8px] font-black opacity-30 tracking-[0.4em]')
                    ui.label('SECURE NETWORK').classes('text-[#00F5D4] text-xs font-black italic tracking-widest')

        # Procurement Grid
        with ui.grid(columns='repeat(auto-fit, minmax(360px, 1fr))').classes('w-full gap-10'):
            
            def procurement_card(icon, part_name, stock, price, category):
                with ui.element('div').classes('procurement-card group'):
                    with ui.row().classes('w-full justify-between items-start'):
                        ui.icon(icon).classes('card-icon material-icons-outlined')
                        ui.label(category).classes('tag bg-white/5 opacity-50')
                    
                    with ui.column().classes('gap-1'):
                        ui.label(part_name).classes('text-2xl font-black tracking-tight mb-2')
                        with ui.row().classes('items-baseline gap-2'):
                            ui.label(price).classes('text-3xl font-bold text-gradient')
                            ui.label('USD / UNIT').classes('text-[8px] font-black opacity-30')

                    # Reveal Info (Visible on Hover)
                    with ui.column().classes('reveal-info w-full gap-6 pt-6 border-t border-white/5'):
                        with ui.grid(columns=2).classes('w-full gap-4'):
                            with ui.column().classes('gap-1'):
                                ui.label('LEAD TIME').classes('text-[8px] font-black opacity-30 tracking-widest')
                                ui.label('48 HOURS').classes('text-xs font-bold')
                            with ui.column().classes('gap-1'):
                                ui.label('AVAILABILITY').classes('text-[8px] font-black opacity-30 tracking-widest')
                                ui.label(f'{stock} UNITS').classes('text-xs font-bold text-emerald-400')
                        
                        ui.button('INITIATE PROCUREMENT').classes('w-full h-12 rounded-xl font-black text-white bg-white/5 hover:bg-emerald-500 transition-colors')

            # Mock Data Injection
            procurement_card('o_settings_input_component', 'Hydraulic Actuator X-200', 14, '$12,450', 'SYSTEMS')
            procurement_card('o_memory', 'Avionics Control Unit V2', 3, '$48,200', 'ELECTRONICS')
            procurement_card('o_engineering', 'Titanium Compressor Blade', 85, '$3,900', 'ENGINE')
            procurement_card('o_visibility', 'Head-Up Display Assembly', 2, '$115,000', 'COCKPIT')
            procurement_card('o_radar', 'L-Band Radar Transceiver', 5, '$34,100', 'SURVEILLANCE')
            procurement_card('o_shield', 'Reinforced Fuselage Panel', 22, '$8,600', 'STRUCTURE')

    # Status Bar
    with ui.row().classes('fixed bottom-0 left-0 w-full glass p-4 border-t border-white/5 px-20 justify-between items-center no-print'):
        with ui.row().classes('items-center gap-6'):
            ui.label('STATUS: NOMINAL').classes('text-[9px] font-black text-emerald-400 tracking-widest')
            ui.label('FREQ: 114.30 MHZ').classes('text-[9px] font-black opacity-30 tracking-widest')
        ui.label('© 2026 AVIATION PROCUREMENT CORE').classes('text-[8px] font-black opacity-20')

# Direct Page Binding
@ui.page('/aviation')
def aviation():
    aviation_procurement_page()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Aviation Procurement Hub', dark=True)
