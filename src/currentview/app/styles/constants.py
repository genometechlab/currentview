# ============================================================================
# Design System Constants
# ============================================================================

FORM_CONTROL_HEIGHT = "44px"
FORM_CONTROL_HEIGHT_SM = "38px"
FORM_CONTROL_HEIGHT_LG = "52px"

BORDER_RADIUS = "10px"
BORDER_RADIUS_SM = "8px"
BORDER_RADIUS_LG = "12px"

COLOR_BORDER = "#e2e8f0"
COLOR_BG_INPUT = "#ffffff"
COLOR_BG_SECONDARY = "#f8fafc"
COLOR_TEXT = "#1e293b"
COLOR_TEXT_MUTED = "#475569"

TRANSITION = "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"

# ============================================================================
# Colour Palette
# ============================================================================

COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#ef4444"
COLOR_WARNING = "#f59e0b"
COLOR_INFO = "#3b82f6"

GRADIENT_PRIMARY = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

# Per-colour shadow tints (used by buttons)
SHADOW_COLOR_PRIMARY = "rgba(102, 126, 234, 0.25)"
SHADOW_COLOR_SUCCESS = "rgba(16, 185, 129, 0.25)"
SHADOW_COLOR_DANGER = "rgba(239, 68, 68, 0.25)"
SHADOW_COLOR_WARNING = "rgba(245, 158, 11, 0.25)"
SHADOW_COLOR_INFO = "rgba(59, 130, 246, 0.25)"

# Generic shadow (e.g. cards, dropdowns)
SHADOW_SM = "0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.03)"

# Dark mode palette (zinc)
DARK_BG_PAGE = "#09090b"
DARK_BG_CARD = "#18181b"
DARK_BG_INPUT = "#27272a"
DARK_BORDER = "#3f3f46"
DARK_TEXT = "#e4e4e7"
DARK_TEXT_MUTED = "#a1a1aa"

# ============================================================================
# Styling Constants
# ============================================================================

TAB_STYLE = {"borderRadius": "8px 8px 0 0"}
ACTIVE_TAB_STYLE = {
    "borderRadius": "8px 8px 0 0",
    "background": GRADIENT_PRIMARY,
    "color": "white",
}

# Border radius helpers for joined / grouped elements
RADIUS_LEFT = "10px 0 0 10px"
RADIUS_RIGHT = "0 10px 10px 0"
RADIUS_NONE = "0"
