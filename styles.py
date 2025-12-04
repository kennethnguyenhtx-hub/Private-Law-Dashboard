"""
Styling constants and functions for Private Laws Dashboard
"""

from dash import html

# =============================================================================
# COLOR THEME - Blue shades with proper contrast + Orange for filtering
# =============================================================================

COLORS = {
    # Backgrounds
    'bg_dark': '#0d1117',
    'bg_card': '#161b22',
    'bg_elevated': '#1c2128',
    'bg_hover': '#21262d',
    
    # Borders & Dividers
    'border': '#30363d',
    'border_light': '#484f58',
    'divider': '#21262d',
    
    # Text
    'text_primary': '#f0f6fc',
    'text_secondary': '#8b949e',
    'text_muted': '#6e7681',
    
    # Accent Blues
    'accent_primary': '#58a6ff',
    'accent_light': '#79c0ff',
    'accent_dark': '#1f6feb',
    'accent_subtle': '#388bfd26',
    
    # Filter/Historical Orange
    'filter_orange': '#d4a84b',
    'filter_orange_light': '#e8c078',
    'filter_orange_subtle': '#d4a84b33',
    
    # Highlight
    'highlight_row': '#1f6feb',
    'highlight_header': '#58a6ff',
    
    # Chart colors
    'bar_default': '#58a6ff',
    'bar_active': '#d4a84b',
    'bar_muted': '#30363d',
    
    # Status
    'success': '#3fb950',
    'warning': '#d29922',
    'error': '#f85149'
}

# =============================================================================
# CUSTOM CSS FOR INDEX
# =============================================================================

CUSTOM_CSS = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #161b22;
            }
            ::-webkit-scrollbar-thumb {
                background: #30363d;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #484f58;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                position: sticky !important;
                top: 0 !important;
                z-index: 10 !important;
            }
            
            .rc-slider-track {
                background-color: #58a6ff !important;
            }
            .rc-slider-handle {
                border-color: #58a6ff !important;
            }
            .rc-slider-rail {
                background-color: #30363d !important;
            }
            
            /* Custom checkbox styling */
            input[type="checkbox"] {
                accent-color: #d4a84b;
                width: 14px;
                height: 14px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# =============================================================================
# COMPONENT STYLES
# =============================================================================

def section_header_style():
    """Style for main section headers."""
    return {
        'color': COLORS['text_primary'],
        'fontSize': '20px',
        'fontWeight': '600',
        'marginBottom': '0',
        'paddingBottom': '5px',
        'borderBottom': f"2px solid {COLORS['accent_primary']}",
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
    }


def subsection_header_style():
    """Style for subsection headers."""
    return {
        'color': COLORS['text_primary'],
        'fontSize': '15px',
        'fontWeight': '500',
        'marginBottom': '4px',
        'marginTop': '0',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
    }


def card_style():
    """Style for card containers."""
    return {
        'backgroundColor': COLORS['bg_card'],
        'border': f"1px solid {COLORS['border']}",
        'borderRadius': '8px',
        'padding': '20px',
        'paddingTop': '0px'
    }


def gradient_divider():
    """Creates a gradient divider element."""
    return html.Div(style={
        'height': '1px',
        'background': f"linear-gradient(90deg, transparent, {COLORS['border_light']}, transparent)",
        'margin': '16px 0'
    })


def label_style():
    """Style for field labels in info panel."""
    return {
        'color': COLORS['text_muted'],
        'fontSize': '11px',
        'fontWeight': '600',
        'textTransform': 'uppercase',
        'letterSpacing': '0.5px',
        'display': 'block',
        'marginBottom': '4px'
    }


def value_style():
    """Style for field values in info panel."""
    return {
        'color': COLORS['text_primary'],
        'fontSize': '15px',
        'fontWeight': '500'
    }


def button_hidden_style():
    """Style for hidden reset buttons."""
    return {
        'padding': '4px 12px',
        'backgroundColor': 'transparent',
        'border': f"1px solid {COLORS['border']}",
        'borderRadius': '4px',
        'color': COLORS['text_muted'],
        'cursor': 'pointer',
        'fontSize': '11px',
        'display': 'none'
    }


def button_visible_style():
    """Style for visible reset buttons."""
    style = button_hidden_style()
    style['display'] = 'inline-block'
    return style
