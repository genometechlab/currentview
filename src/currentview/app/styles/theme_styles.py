from .constants import (
    BORDER_RADIUS,
    BORDER_RADIUS_LG,
    COLOR_BORDER,
    COLOR_BG_INPUT,
    COLOR_BG_SECONDARY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    COLOR_INFO,
    GRADIENT_PRIMARY,
    FORM_CONTROL_HEIGHT,
    TRANSITION,
)

# ── Shared token map (injected into CSS via .format) ─────────────────────────
_T = {
    "radius": BORDER_RADIUS,
    "radius_lg": BORDER_RADIUS_LG,
    "border": COLOR_BORDER,
    "bg_input": COLOR_BG_INPUT,
    "bg_secondary": COLOR_BG_SECONDARY,
    "text": COLOR_TEXT,
    "text_muted": COLOR_TEXT_MUTED,
    "success": COLOR_SUCCESS,
    "danger": COLOR_DANGER,
    "warning": COLOR_WARNING,
    "info": COLOR_INFO,
    "gradient": GRADIENT_PRIMARY,
    "ctrl_h": FORM_CONTROL_HEIGHT,
    "transition": TRANSITION,
    "accent": "#6366f1",
    "accent_hover": "#4f46e5",
    "accent_ring": "rgba(99, 102, 241, 0.15)",
}


def get_base_styles() -> str:
    return """
    /* ── Cards ──────────────────────────────────────────────────────── */
    .glass-card {{
        border-radius: {radius_lg};
        padding: 24px;
    }}
    .glass-card.hoverable {{
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .glass-card.hoverable:hover {{
        transform: translateY(-1px);
    }}
    .glass-card.glass-card--default {{
        background: {bg_input} !important;
        border: 1px solid {border} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 4px 12px rgba(0,0,0,.03) !important;
    }}
    .glass-card.glass-card--flat {{
        background: {bg_input} !important;
        border: 1px solid {border} !important;
        box-shadow: none !important;
    }}
    .glass-card.glass-card--ghost {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* ── Labels ─────────────────────────────────────────────────────── */
    .modern-label {{ font-weight: 500; margin-bottom: 8px;  font-size: 0.95rem; }}
    .small-label  {{ font-size: 0.85rem; margin-bottom: 6px; }}

    /* ── Buttons ────────────────────────────────────────────────────── */
    .modern-btn {{ transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important; }}
    .modern-btn:hover {{ transform: translateY(-1px); }}

    /* ── Inputs ─────────────────────────────────────────────────────── */
    .modern-input {{ transition: {transition}; }}
    .modern-input:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent_ring} !important;
        outline: none;
    }}

    /* ── Dropdown ───────────────────────────────────────────────────── */
    .modern-dropdown {{
        cursor: pointer !important;
        border-radius: {radius} !important;
        transition: {transition} !important;
    }}
    .modern-dropdown .dash-dropdown-grid-container.dash-dropdown-trigger {{
        min-height: {ctrl_h} !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 12px !important;
        box-sizing: border-box !important;
    }}
    .modern-dropdown .dash-dropdown-trigger-icon {{ margin-left: auto !important; flex-shrink: 0 !important; }}
    .modern-dropdown:focus-within {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent_ring} !important;
        outline: none !important;
    }}
    .dash-dropdown-content {{
        border-radius: {radius} !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0,0,0,.08) !important;
        z-index: 9999 !important;
    }}
    .dash-dropdown-content .dash-dropdown-grid-container.dash-dropdown-search-container {{
        display: flex !important;
        align-items: center !important;
        padding: 0 12px !important;
        gap: 8px !important;
    }}
    .dash-dropdown-content .dash-dropdown-search {{
        border: none !important;
        outline: none !important;
        width: 100% !important;
        padding: 10px 0 !important;
        font-size: 0.9375rem !important;
        background: transparent !important;
    }}

    /* ── Modals ─────────────────────────────────────────────────────── */
    .modal-header, .modal-footer {{ border: none !important; }}

    /* ── Switch ─────────────────────────────────────────────────────── */
    .form-switch {{ padding-left: 0 !important; margin-bottom: 0 !important; }}
    .form-switch .form-check-input {{
        width: 3em !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        cursor: pointer !important;
        float: none !important;
    }}

    /* ── Fade-in ────────────────────────────────────────────────────── */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to   {{ opacity: 1; transform: translateY(0);   }}
    }}
    """.format(
        **_T
    )


def get_light_mode_styles() -> str:
    return """
    /* ── Page ───────────────────────────────────────────────────────── */
    #theme-container {{ background: #f1f5f9 !important; color: {text} !important; }}
    #top-bar         {{ background: {text} !important; }}
    #app-title        {{ color: #f1f5f9 !important; }}

    /* ── Cards ──────────────────────────────────────────────────────── */
    .glass-card {{
        background: {bg_input} !important;
        border: 1px solid {border} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 4px 12px rgba(0,0,0,.03) !important;
    }}
    .glass-card.hoverable:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,.08) !important; }}

    /* ── Labels ─────────────────────────────────────────────────────── */
    .modern-label {{ color: #374151 !important; }}
    .small-label  {{ color: #6b7280 !important; }}
    .card-title   {{ color: #2d3748 !important; }}

    /* ── Buttons ────────────────────────────────────────────────────── */
    .modern-btn:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,.15) !important;
        filter: brightness(0.93) !important;
    }}

    /* ── Inputs & form controls ─────────────────────────────────────── */
    .modern-input,
    .form-control,
    .form-select {{
        background: {bg_input} !important;
        border: 1.5px solid {border} !important;
        color: {text} !important;
    }}
    .modern-input::placeholder,
    .form-control::placeholder {{ color: #94a3b8 !important; opacity: 1 !important; }}
    .modern-input:disabled,
    .form-control:disabled      {{ background: #f8fafc !important; color: #94a3b8 !important; }}

    .form-control:focus,
    .form-select:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent_ring} !important;
    }}

    textarea.form-control {{
        background: {bg_input} !important;
        color: {text} !important;
        border: 1.5px solid {border} !important;
    }}

    .input-group-text {{
        background: {bg_secondary} !important;
        color: {text_muted} !important;
        border: 1.5px solid {border} !important;
    }}

    input[type="color"] {{
        background: {bg_input} !important;
        border: 1.5px solid {border} !important;
    }}

    /* ── Dropdown ───────────────────────────────────────────────────── */
    .modern-dropdown {{
        background: {bg_input} !important;
        border: 1.5px solid {border} !important;
    }}
    .modern-dropdown .dash-dropdown-value                             {{ color: {text} !important; }}
    .modern-dropdown .dash-dropdown-value.dash-dropdown-placeholder  {{ color: #94a3b8 !important; }}
    .modern-dropdown .dash-dropdown-trigger-icon                     {{ color: #94a3b8 !important; }}

    .dash-dropdown-content {{
        background: {bg_input} !important;
        border: 1.5px solid {border} !important;
        color: {text} !important;
    }}
    .dash-dropdown-content .dash-dropdown-search-container           {{ border-bottom: 1.5px solid {border} !important; }}
    .dash-dropdown-content .dash-dropdown-search                     {{ color: {text} !important; }}
    .dash-dropdown-content .dash-dropdown-search::placeholder        {{ color: #94a3b8 !important; }}
    .dash-dropdown-content .dash-dropdown-search-icon                {{ color: #94a3b8 !important; }}

    /* ── Switch ─────────────────────────────────────────────────────── */
    .form-switch .form-check-input:checked {{
        background-color: {accent} !important;
        border-color: {accent} !important;
    }}

    /* ── Tabs ───────────────────────────────────────────────────────── */
    .nav-tabs  .nav-link         {{ color: #64748b !important; background: transparent !important; border: none !important; }}
    .nav-pills .nav-link         {{ color: #64748b !important; }}
    .nav-pills .nav-link.active  {{ background: {gradient} !important; color: #fff !important; }}
    .nav-pills .nav-link.disabled,
    .nav-tabs  .nav-link.disabled {{ color: #cbd5e1 !important; opacity: .5 !important; cursor: not-allowed !important; }}

    /* ── Misc ───────────────────────────────────────────────────────── */
    .form-text       {{ color: #64748b !important; }}
    .btn-link        {{ color: {accent} !important; text-decoration: none !important; }}
    .btn-link:hover  {{ color: {accent_hover} !important; }}

    .alert-danger  {{ background: #fef2f2 !important; border: 1px solid #fca5a5 !important; color: {danger} !important; }}
    .alert-success {{ background: #f0fdf4 !important; border: 1px solid #86efac !important; color: {success} !important; }}

    hr {{ border-color: {border} !important; }}

    .offcanvas        {{ background: {bg_input} !important; color: {text} !important; }}
    .offcanvas-header {{ border-bottom: 1px solid {border} !important; }}
    .offcanvas hr     {{ border-color: {border} !important; opacity: .6 !important; }}

    .modal-content {{
        background: {bg_input} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
    }}

    .list-group-item        {{ background: {bg_input} !important; color: {text} !important; border: 1px solid {border} !important; }}
    .list-group-item:hover  {{ background: {bg_secondary} !important; }}
    .list-group-item.active {{ background: {accent} !important; border-color: {accent} !important; color: #fff !important; }}
    """.format(
        **_T
    )


def get_dark_mode_styles() -> str:
    # Dark-only palette (zinc)
    d = {
        **_T,
        "page_bg": "#09090b",
        "bar_bg": "#0a0a0a",
        "card_bg": "#18181b",
        "input_bg": "#27272a",
        "border": "#27272a",
        "border_mid": "#3f3f46",
        "border_hi": "#52525b",
        "text": "#e4e4e7",
        "text_muted": "#a1a1aa",
        "text_dim": "#71717a",
        "title": "#fafafa",
        "accent": "#6366f1",
        "accent_hover": "#a5b4fc",
        "accent_ring": "rgba(99, 102, 241, 0.2)",
    }

    return """
    /* ── Page ───────────────────────────────────────────────────────── */
    #theme-container {{ background: {page_bg} !important; color: {text} !important; }}
    #top-bar         {{ background: {bar_bg} !important; border-bottom: 1px solid {border} !important; }}
    #app-title        {{ color: {title} !important; }}

    /* ── Cards ──────────────────────────────────────────────────────── */
    .glass-card.glass-card--default {{
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,.4) !important;
    }}
    .glass-card.glass-card--flat {{
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        box-shadow: none !important;
    }}
    .glass-card.glass-card--ghost {{ background: transparent !important; border: none !important; box-shadow: none !important; }}
    .glass-card.hoverable:hover   {{ box-shadow: 0 4px 16px rgba(0,0,0,.5) !important; }}

    /* ── Labels ─────────────────────────────────────────────────────── */
    .modern-label {{ color: {text} !important; }}
    .small-label  {{ color: {text_muted} !important; }}
    .card-title   {{ color: #f4f4f5 !important; }}

    /* ── Buttons ────────────────────────────────────────────────────── */
    .modern-btn:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.4) !important; filter: brightness(1.1) !important; }}
    .modern-btn i.bi  {{ color: inherit !important; }}

    .btn-primary   {{ background: transparent !important; border: 1px solid {accent} !important; color: #818cf8 !important; }}
    .btn-primary:hover {{ background: rgba(99,102,241,.12) !important; border-color: #818cf8 !important; color: #a5b4fc !important; }}

    .btn-success   {{ background: transparent !important; border: 1px solid {success} !important; color: #34d399 !important; }}
    .btn-success:hover {{ background: rgba(16,185,129,.12) !important; border-color: #34d399 !important; color: #6ee7b7 !important; }}

    .btn-danger    {{ background: transparent !important; border: 1px solid {danger} !important; color: #f87171 !important; }}
    .btn-danger:hover {{ background: rgba(239,68,68,.12) !important; border-color: #f87171 !important; color: #fca5a5 !important; }}

    .btn-warning   {{ background: transparent !important; border: 1px solid {warning} !important; color: #fbbf24 !important; }}
    .btn-warning:hover {{ background: rgba(245,158,11,.12) !important; border-color: #fbbf24 !important; color: #fde68a !important; }}

    .btn-info      {{ background: transparent !important; border: 1px solid {info} !important; color: #60a5fa !important; }}
    .btn-info:hover {{ background: rgba(59,130,246,.12) !important; border-color: #60a5fa !important; color: #93c5fd !important; }}

    .btn-secondary {{ background: {border} !important; border: 1px solid {border_mid} !important; color: {text_muted} !important; }}
    .btn-secondary:hover {{ background: {border_mid} !important; border-color: {border_hi} !important; color: #d4d4d8 !important; }}

    /* ── Inputs & form controls ─────────────────────────────────────── */
    .modern-input,
    .form-control,
    .form-select {{
        background: {input_bg} !important;
        border: 1px solid {border_mid} !important;
        color: {text} !important;
    }}
    .modern-input:focus,
    .form-control:focus,
    .form-select:focus {{
        background: {input_bg} !important;
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent_ring} !important;
        color: {text} !important;
    }}
    .modern-input::placeholder,
    .form-control::placeholder {{ color: {text_dim} !important; opacity: 1 !important; }}
    .modern-input:disabled,
    .form-control:disabled      {{ background: {card_bg} !important; color: {border_hi} !important; }}

    textarea.form-control               {{ background: {input_bg} !important; color: {text} !important; border: 1px solid {border_mid} !important; }}
    textarea.form-control::placeholder  {{ color: {text_dim} !important; }}

    .input-group-text {{ background: {border_mid} !important; color: {text_muted} !important; border: 1px solid {border_mid} !important; }}
    input[type="color"] {{ background: {input_bg} !important; border: 1px solid {border_mid} !important; }}

    /* ── Dropdown ───────────────────────────────────────────────────── */
    .modern-dropdown {{ background: {input_bg} !important; border: 1px solid {border_mid} !important; }}
    .modern-dropdown .dash-dropdown-value                            {{ color: {text} !important; }}
    .modern-dropdown .dash-dropdown-value.dash-dropdown-placeholder {{ color: {text_dim} !important; }}
    .modern-dropdown .dash-dropdown-trigger-icon                    {{ color: {text_dim} !important; }}

    .dash-dropdown-content {{
        background: {input_bg} !important;
        border: 1px solid {border_mid} !important;
        box-shadow: 0 4px 12px rgba(0,0,0,.4) !important;
        color: {text} !important;
    }}
    .dash-dropdown-content .dash-dropdown-search-container          {{ border-bottom: 1px solid {border_mid} !important; background: {input_bg} !important; }}
    .dash-dropdown-content .dash-options-list-option                {{ color: {text} !important; }}
    .dash-dropdown-content .dash-dropdown-search                    {{ color: {text} !important; }}
    .dash-dropdown-content .dash-dropdown-search::placeholder       {{ color: {text_dim} !important; }}
    .dash-dropdown-content .dash-dropdown-search-icon               {{ color: {text_dim} !important; }}

    /* ── Switch ─────────────────────────────────────────────────────── */
    .form-switch .form-check-input         {{ background-color: {border_mid} !important; border-color: {border_hi} !important; }}
    .form-switch .form-check-input:checked {{ background-color: {accent} !important; border-color: {accent} !important; }}

    /* ── Tabs ───────────────────────────────────────────────────────── */
    .nav-tabs  .nav-link         {{ color: {text_muted} !important; background: transparent !important; border: none !important; }}
    .nav-pills .nav-link         {{ color: {text_muted} !important; }}
    .nav-pills .nav-link.active  {{ background: {gradient} !important; color: #fff !important; }}
    .nav-pills .nav-link.disabled,
    .nav-tabs  .nav-link.disabled {{ color: {border_mid} !important; opacity: .5 !important; cursor: not-allowed !important; }}

    /* ── Misc ───────────────────────────────────────────────────────── */
    .form-text       {{ color: {text_dim} !important; }}
    .btn-link        {{ color: #818cf8 !important; text-decoration: none !important; }}
    .btn-link:hover  {{ color: {accent_hover} !important; }}

    .alert-danger  {{ background: {border} !important; border: 1px solid {danger} !important; color: #f87171 !important; }}
    .alert-success {{ background: {border} !important; border: 1px solid {success} !important; color: #34d399 !important; }}

    hr {{ border-color: {border} !important; }}

    .offcanvas        {{ background: {bar_bg} !important; color: {text} !important; }}
    .offcanvas-header {{ border-bottom: 1px solid {border} !important; }}
    .offcanvas hr     {{ border-color: {border} !important; opacity: .5 !important; }}

    .modal-content {{
        background: {card_bg} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
    }}

    .list-group-item        {{ background: {input_bg} !important; color: {text} !important; border: 1px solid {border_mid} !important; }}
    .list-group-item:hover  {{ background: {border_mid} !important; }}
    .list-group-item.active {{ background: {accent} !important; border-color: {accent} !important; color: #fff !important; }}

    i.bi {{ color: inherit !important; }}
    """.format(
        **d
    )


def get_theme_clientside_callback() -> str:
    base = get_base_styles()
    light = get_light_mode_styles()
    dark = get_dark_mode_styles()

    return f"""
    function(theme) {{
        const existing = document.getElementById('dash-theme-styles');
        if (existing) existing.remove();

        const isDark   = theme === 'dark';
        const sunIcon  = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        if (sunIcon)  sunIcon.className  = isDark ? 'bi bi-sun'       : 'bi bi-sun-fill';
        if (moonIcon) moonIcon.className = isDark ? 'bi bi-moon-fill' : 'bi bi-moon';

        const style = document.createElement('style');
        style.id = 'dash-theme-styles';
        style.innerHTML = `{base}` + (isDark ? `{dark}` : `{light}`);
        document.head.appendChild(style);
        return '';
    }}
    """
