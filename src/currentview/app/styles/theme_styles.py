def get_base_styles():
    """Get base CSS styles for the application with flat design."""
    return """
    /* Base flat card styles */
    .glass-card {
        background: #ffffff !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        padding: 24px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Modern label styles */
    .modern-label {
        font-weight: 500;
        color: #374151;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    
    .small-label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 6px;
    }
    
    /* Flat button styles */
    .modern-btn {
        transition: all 0.2s ease;
    }
    
    .modern-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        filter: brightness(0.95);
    }
    
    /* Flat input styles */
    .modern-input {
        transition: all 0.2s ease;
    }
    
    .modern-input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        outline: none;
    }
    
    /* Simple fade in animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    """


def get_dark_mode_styles():
    """Get dark mode specific styles with flat design."""
    return """
    /* Dark mode background - true black/gray */
    #theme-container {
        background: #000000 !important;  /* Pure black background */
        color: #e4e4e7 !important;
    }
    
    /* Dark mode top bar - slightly elevated */
    #top-bar {
        background: #0a0a0a !important;  /* Near black */
        border-bottom: 1px solid #27272a !important;
        backdrop-filter: none !important;
    }
    
    #app-title {
        color: #fafafa !important;
    }
    
    /* Flat cards in dark mode - elevated gray */
    .glass-card {
        background: #18181b !important;  /* Zinc-900 */
        border: 1px solid #27272a !important;  /* Zinc-800 */
        color: #e4e4e7 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
    }
    
    .glass-card:hover {
        background: #18181b !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6) !important;
    }
    
    /* Modern labels in dark mode */
    .modern-label {
        color: #e4e4e7 !important;
    }
    
    .modern-btn {
        background: #27272a !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.5) !important;
    }

    /* Primary button */
    .btn-primary {
        border: 1px solid #6366f1 !important;
        color: #6366f1 !important;
    }

    .btn-primary:hover {
        background: #3f3f46 !important;
        border-color: #818cf8 !important;
        color: #818cf8 !important;
    }

    .btn-primary i {
        color: inherit !important;
    }

    /* Success button */
    .btn-success {
        border: 1px solid #10b981 !important;
        color: #10b981 !important;
    }

    .btn-success:hover {
        background: #3f3f46 !important;
        border-color: #34d399 !important;
        color: #34d399 !important;
    }

    /* Danger button */
    .btn-danger {
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }

    .btn-danger:hover {
        background: #3f3f46 !important;
        border-color: #f87171 !important;
        color: #f87171 !important;
    }

    /* Warning button */
    .btn-warning {
        border: 1px solid #f5e239 !important;
        color: #f5e239 !important;
    }

    .btn-warning:hover {
        background: #3f3f46 !important;
        border-color: #fef08a !important;
        color: #fef08a !important;
    }

    /* Info button */
    .btn-info {
        border: 1px solid #3b82f6 !important;
        color: #3b82f6 !important;
    }

    .btn-info:hover {
        background: #3f3f46 !important;
        border-color: #60a5fa !important;
        color: #60a5fa !important;
    }

    /* Secondary button */
    .btn-secondary {
        border: 1px solid #71717a !important;
        color: #a1a1aa !important;
    }

    .btn-secondary:hover {
        background: #3f3f46 !important;
        border-color: #a1a1aa !important;
        color: #d4d4d8 !important;
    }
    
    .small-label {
        color: #a1a1aa !important;
    }
    
    .card-title {
        color: #e4e4e7 !important
    }
    
    /* Flat inputs in dark mode */
    .modern-input {
        background: #27272a !important;  /* Zinc-800 */
        border: 1px solid #3f3f46 !important;  /* Zinc-700 */
        color: #e4e4e7 !important;
    }
    
    .modern-input:focus {
        background: #27272a !important;
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    .modern-input::placeholder {
        color: #71717a !important;  /* Zinc-500 */
    }
    
    .modern-input:disabled {
        background: #18181b !important;
        color: #52525b !important;
    }
    
    /* Flat buttons in dark mode */
    .modern-btn {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Form controls dark mode - flat */
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
    
    .form-control::placeholder {
        color: #71717a !important;
        opacity: 1 !important;
    }
    
    .form-control:disabled {
        background: #18181b !important;
        color: #52525b !important;
    }
    
    /* Textarea dark mode */
    textarea.form-control {
        background: #27272a !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
    }
    
    textarea.form-control::placeholder {
        color: #71717a !important;
    }
    
    /* Input group text dark mode */
    .input-group-text {
        background: #3f3f46 !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
    }
    
    /* Color input dark mode */
    input[type="color"] {
        background: #27272a !important;
        border: 1px solid #3f3f46 !important;
    }
    
    /* Modal dark mode - flat */
    .modal-content {
        background: #18181b !important;
        backdrop-filter: none !important;
        color: #e4e4e7 !important;
        border: 1px solid #27272a !important;
    }
    
    /* List group dark mode */
    .list-group-item {
        background: #27272a !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
    }
    
    .list-group-item:hover {
        background: #3f3f46 !important;
    }
    
    .list-group-item.active {
        background: #6366f1 !important;  /* Keep purple accent */
        border-color: #6366f1 !important;
    }
    
    /* Alert dark mode */
    .alert-danger {
        background: #27272a !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    
    .alert-success {
        background: #27272a !important;
        border: 1px solid #10b981 !important;
        color: #10b981 !important;
    }
    
    /* Tabs dark mode - flat */
    .nav-tabs .nav-link {
        color: #a1a1aa !important;
        background: transparent !important;
        border: none !important;
    }
    
    .nav-tabs .nav-link.active, .nav-pills .nav-link.active {
        background: #6366f1 !important;  /* Keep purple accent */
        color: #ffffff !important;
        border: none !important;
    }
    
    /* Offcanvas dark mode */
    .offcanvas {
        background: #0a0a0a !important;
        backdrop-filter: none !important;
        color: #e4e4e7 !important;
    }
    
    .offcanvas-header {
        border-bottom: 1px solid #27272a !important;
    }
    
    .offcanvas hr {
        border-color: #27272a !important;
        opacity: 0.5 !important;
    }
    
    /* Form text dark mode */
    .form-text {
        color: #71717a !important;
    }
    
    /* HR elements */
    hr {
        border-color: #27272a !important;
    }
    
    /* Plot container dark mode */
    #plot-container {
        background: #18181b !important;
    }
    
    /* Form switch dark mode */
    .form-switch {
        padding-left: 0 !important;
        margin-bottom: 0 !important;
    }
    
    .form-switch .form-check-input {
        width: 3em !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        background-color: #3f3f46 !important;
        border-color: #3f3f46 !important;
        cursor: pointer !important;
        float: none !important;
    }
    
    .form-switch .form-check-input:checked {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
    }
    
    /* Button link dark mode */
    .btn-link {
        color: #6366f1 !important;
        text-decoration: none !important;
    }
    
    .btn-link:hover {
        color: #818cf8 !important;
    }
    
    /* Icons in dark mode */
    i.bi {
        color: inherit !important;
    }
    """


def get_light_mode_styles():
    """Get light mode specific styles with flat design."""
    return """
    /* Light mode adjustments - flat background */
    #theme-container {
        background: #f8fafc !important;  /* Flat light gray */
    }
    
    #top-bar {
        background: #1e293b !important;  /* Flat dark blue */
    }
    
    #app-title {
        color: #f1f5f9 !important;
    }
    
    .card-title {
        color: #2d3748 !important
    }
    
    /* Form switch light mode */
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
    """


def get_theme_clientside_callback():
    """Get the clientside callback for theme switching."""
    base_styles = get_base_styles()
    dark_styles = get_dark_mode_styles()
    light_styles = get_light_mode_styles()

    return f"""
    function(theme) {{
        // Remove existing theme style if any
        const existingStyle = document.getElementById('dash-theme-styles');
        if (existingStyle) {{
            existingStyle.remove();
        }}
        
        // Update icon classes
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        
        if (theme === 'dark') {{
            // Dark mode: empty sun, filled moon
            if (sunIcon) sunIcon.className = 'bi bi-sun';
            if (moonIcon) moonIcon.className = 'bi bi-moon-fill';
            
            // Create and inject dark theme styles
            const style = document.createElement('style');
            style.id = 'dash-theme-styles';
            style.innerHTML = `{base_styles}{dark_styles}`;
            document.head.appendChild(style);
        }} else {{
            // Light mode: filled sun, empty moon
            if (sunIcon) sunIcon.className = 'bi bi-sun-fill';
            if (moonIcon) moonIcon.className = 'bi bi-moon';
            
            // Light mode styles
            const style = document.createElement('style');
            style.id = 'dash-theme-styles';
            style.innerHTML = `{base_styles}{light_styles}`;
            document.head.appendChild(style);
        }}
        
        return '';  // Return empty string for the dummy output
    }}
    """
