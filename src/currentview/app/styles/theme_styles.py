def get_base_styles() -> str:
    """Styles shared across both themes — loaded once on every switch."""
    return """
    /* ── Cards ────────────────────────────────────────────────────────── */
    .glass-card {
        border-radius: 12px;
        padding: 24px;
    }

    .glass-card.hoverable {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .glass-card.glass-card--default {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    }

    .glass-card.glass-card--flat {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
    }

    .glass-card.glass-card--ghost {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .glass-card.hoverable:hover {
        transform: translateY(-1px);
    }

    /* ── Labels ────────────────────────────────────────────────────────── */
    .modern-label {
        font-weight: 500;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }

    .small-label {
        font-size: 0.85rem;
        margin-bottom: 6px;
    }

    /* ── Buttons ───────────────────────────────────────────────────────── */
    .modern-btn {
        transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
    }

    .modern-btn:hover {
        transform: translateY(-1px);
    }

    /* ── Inputs ────────────────────────────────────────────────────────── */
    .modern-input {
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .modern-input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        outline: none;
    }

    .modal-header,
    .modal-footer {
        border: none !important;
    }

    /* ── Form switch shared ─────────────────────────────────────────────── */
    .form-switch {
        padding-left: 0 !important;
        margin-bottom: 0 !important;
    }

    .form-switch .form-check-input {
        width: 3em !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        cursor: pointer !important;
        float: none !important;
    }

    /* ── Fade-in ────────────────────────────────────────────────────────── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to   { opacity: 1; transform: translateY(0);   }
    }
    """


def get_light_mode_styles() -> str:
    """Light mode styles."""
    return """
    /* ── Page ──────────────────────────────────────────────────────────── */
    #theme-container {
        background: #f1f5f9 !important;
        color: #1e293b !important;
    }

    #top-bar {
        background: #1e293b !important;
    }

    #app-title {
        color: #f1f5f9 !important;
    }

    /* ── Cards ──────────────────────────────────────────────────────────── */
    .glass-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    }

    .glass-card.hoverable:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
    }

    /* ── Labels ─────────────────────────────────────────────────────────── */
    .modern-label  { color: #374151 !important; }
    .small-label   { color: #6b7280 !important; }
    .card-title    { color: #2d3748 !important; }

    /* ── Buttons — keep their brand colors, just refine hover ───────────── */
    .modern-btn:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        filter: brightness(0.93) !important;
    }

    /* ── Inputs ─────────────────────────────────────────────────────────── */
    .modern-input {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        color: #1e293b !important;
    }

    .modern-input::placeholder { color: #94a3b8 !important; }
    .modern-input:disabled     { background: #f8fafc !important; color: #94a3b8 !important; }

    /* ── Form controls ──────────────────────────────────────────────────── */
    .form-control, .form-select {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #e2e8f0 !important;
    }

    .form-control:focus, .form-select:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
    }

    .form-control::placeholder { color: #94a3b8 !important; opacity: 1 !important; }
    .form-control:disabled     { background: #f8fafc !important; color: #94a3b8 !important; }

    textarea.form-control {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #e2e8f0 !important;
    }

    .input-group-text {
        background: #f8fafc !important;
        color: #475569 !important;
        border: 1.5px solid #e2e8f0 !important;
    }

    input[type="color"] {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
    }

    /* ── Form switch ────────────────────────────────────────────────────── */
    .form-switch .form-check-input:checked {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
    }

    /* ── Tabs ───────────────────────────────────────────────────────────── */
    .nav-tabs .nav-link         { color: #64748b !important; background: transparent !important; border: none !important; }
    .nav-pills .nav-link        { color: #64748b !important; }
    .nav-pills .nav-link.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: #ffffff !important; }
    .nav-pills .nav-link.disabled,
    .nav-tabs  .nav-link.disabled { color: #cbd5e1 !important; opacity: 0.5 !important; cursor: not-allowed !important; }

    /* ── Misc ───────────────────────────────────────────────────────────── */
    .form-text   { color: #64748b !important; }
    .btn-link    { color: #6366f1 !important; text-decoration: none !important; }
    .btn-link:hover { color: #4f46e5 !important; }

    .alert-danger  { background: #fef2f2 !important; border: 1px solid #fca5a5 !important; color: #dc2626 !important; }
    .alert-success { background: #f0fdf4 !important; border: 1px solid #86efac !important; color: #16a34a !important; }

    .offcanvas        { background: #ffffff !important; color: #1e293b !important; }
    .offcanvas-header { border-bottom: 1px solid #e2e8f0 !important; }
    .offcanvas hr     { border-color: #e2e8f0 !important; opacity: 0.6 !important; }

    hr { border-color: #e2e8f0 !important; }

    .modal-content {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
    }

    .list-group-item        { background: #ffffff !important; color: #1e293b !important; border: 1px solid #e2e8f0 !important; }
    .list-group-item:hover  { background: #f8fafc !important; }
    .list-group-item.active { background: #6366f1 !important; border-color: #6366f1 !important; color: #ffffff !important; }
    """


def get_dark_mode_styles() -> str:
    """Dark mode styles — Zinc palette, purple accent."""
    return """
    /* ── Page ──────────────────────────────────────────────────────────── */
    #theme-container {
        background: #09090b !important;
        color: #e4e4e7 !important;
    }

    #top-bar {
        background: #0a0a0a !important;
        border-bottom: 1px solid #27272a !important;
    }

    #app-title { color: #fafafa !important; }

    /* ── Cards ──────────────────────────────────────────────────────────── */
    .glass-card.glass-card--default {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
    }

    .glass-card.glass-card--flat {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        box-shadow: none !important;
    }

    .glass-card.glass-card--ghost {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .glass-card.hoverable:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
    }

    /* ── Labels ─────────────────────────────────────────────────────────── */
    .modern-label  { color: #e4e4e7 !important; }
    .small-label   { color: #a1a1aa !important; }
    .card-title    { color: #f4f4f5 !important; }

    /* ── Buttons — outline style, keep accent colors as border/text ──────
       We don't override background on .modern-btn globally so colored
       buttons keep their identity. Only secondary gets the dark treatment. */
    .modern-btn:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        filter: brightness(1.1) !important;
    }

    .btn-primary {
        background: transparent !important;
        border: 1px solid #6366f1 !important;
        color: #818cf8 !important;
    }
    .btn-primary:hover {
        background: rgba(99, 102, 241, 0.12) !important;
        border-color: #818cf8 !important;
        color: #a5b4fc !important;
    }

    .btn-success {
        background: transparent !important;
        border: 1px solid #10b981 !important;
        color: #34d399 !important;
    }
    .btn-success:hover {
        background: rgba(16, 185, 129, 0.12) !important;
        border-color: #34d399 !important;
        color: #6ee7b7 !important;
    }

    .btn-danger {
        background: transparent !important;
        border: 1px solid #ef4444 !important;
        color: #f87171 !important;
    }
    .btn-danger:hover {
        background: rgba(239, 68, 68, 0.12) !important;
        border-color: #f87171 !important;
        color: #fca5a5 !important;
    }

    .btn-warning {
        background: transparent !important;
        border: 1px solid #f59e0b !important;
        color: #fbbf24 !important;
    }
    .btn-warning:hover {
        background: rgba(245, 158, 11, 0.12) !important;
        border-color: #fbbf24 !important;
        color: #fde68a !important;
    }

    .btn-info {
        background: transparent !important;
        border: 1px solid #3b82f6 !important;
        color: #60a5fa !important;
    }
    .btn-info:hover {
        background: rgba(59, 130, 246, 0.12) !important;
        border-color: #60a5fa !important;
        color: #93c5fd !important;
    }

    .btn-secondary {
        background: #27272a !important;
        border: 1px solid #3f3f46 !important;
        color: #a1a1aa !important;
    }
    .btn-secondary:hover {
        background: #3f3f46 !important;
        border-color: #52525b !important;
        color: #d4d4d8 !important;
    }

    /* icons inherit button color */
    .modern-btn i.bi { color: inherit !important; }

    /* ── Inputs ─────────────────────────────────────────────────────────── */
    .modern-input {
        background: #27272a !important;
        border: 1px solid #3f3f46 !important;
        color: #e4e4e7 !important;
    }

    .modern-input:focus {
        background: #27272a !important;
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    .modern-input::placeholder { color: #71717a !important; }
    .modern-input:disabled     { background: #18181b !important; color: #52525b !important; }

    /* ── Form controls ──────────────────────────────────────────────────── */
    .form-control, .form-select {
        background: #27272a !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
    }

    .form-control:focus, .form-select:focus {
        background: #27272a !important;
        color: #e4e4e7 !important;
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    .form-control::placeholder { color: #71717a !important; opacity: 1 !important; }
    .form-control:disabled     { background: #18181b !important; color: #52525b !important; }

    textarea.form-control {
        background: #27272a !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
    }
    textarea.form-control::placeholder { color: #71717a !important; }

    .input-group-text {
        background: #3f3f46 !important;
        color: #a1a1aa !important;
        border: 1px solid #3f3f46 !important;
    }

    input[type="color"] {
        background: #27272a !important;
        border: 1px solid #3f3f46 !important;
    }

    /* ── Form switch ────────────────────────────────────────────────────── */
    .form-switch .form-check-input {
        background-color: #3f3f46 !important;
        border-color: #52525b !important;
    }
    .form-switch .form-check-input:checked {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
    }

    /* ── Tabs ───────────────────────────────────────────────────────────── */
    .nav-tabs .nav-link         { color: #a1a1aa !important; background: transparent !important; border: none !important; }
    .nav-pills .nav-link        { color: #a1a1aa !important; }
    .nav-pills .nav-link.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: #ffffff !important; }
    .nav-pills .nav-link.disabled,
    .nav-tabs  .nav-link.disabled { color: #3f3f46 !important; opacity: 0.5 !important; cursor: not-allowed !important; }

    /* ── Misc ───────────────────────────────────────────────────────────── */
    .form-text   { color: #71717a !important; }
    .btn-link    { color: #818cf8 !important; text-decoration: none !important; }
    .btn-link:hover { color: #a5b4fc !important; }

    .alert-danger  { background: #27272a !important; border: 1px solid #ef4444 !important; color: #f87171 !important; }
    .alert-success { background: #27272a !important; border: 1px solid #10b981 !important; color: #34d399 !important; }

    .offcanvas        { background: #0a0a0a !important; color: #e4e4e7 !important; }
    .offcanvas-header { border-bottom: 1px solid #27272a !important; }
    .offcanvas hr     { border-color: #27272a !important; opacity: 0.5 !important; }

    hr { border-color: #27272a !important; }

    .modal-content {
        background: #18181b !important;
        color: #e4e4e7 !important;
        border: 1px solid #27272a !important;
    }

    .list-group-item        { background: #27272a !important; color: #e4e4e7 !important; border: 1px solid #3f3f46 !important; }
    .list-group-item:hover  { background: #3f3f46 !important; }
    .list-group-item.active { background: #6366f1 !important; border-color: #6366f1 !important; color: #ffffff !important; }

    i.bi { color: inherit !important; }
    """


def get_theme_clientside_callback() -> str:
    """Clientside callback string for theme switching."""
    base = get_base_styles()
    light = get_light_mode_styles()
    dark = get_dark_mode_styles()

    return f"""
    function(theme) {{
        const existing = document.getElementById('dash-theme-styles');
        if (existing) existing.remove();

        const sunIcon  = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        const isDark   = theme === 'dark';

        if (sunIcon)  sunIcon.className  = isDark ? 'bi bi-sun'        : 'bi bi-sun-fill';
        if (moonIcon) moonIcon.className = isDark ? 'bi bi-moon-fill'  : 'bi bi-moon';

        const style = document.createElement('style');
        style.id = 'dash-theme-styles';
        style.innerHTML = `{base}` + (isDark ? `{dark}` : `{light}`);
        document.head.appendChild(style);

        return '';
    }}
    """
