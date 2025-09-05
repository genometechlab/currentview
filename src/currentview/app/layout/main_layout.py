import uuid
import dash_bootstrap_components as dbc
from dash import dcc, html

from .components import (
    create_top_bar,
    create_initialization_card,
    create_add_condition_card,
    create_visualization_card,
    create_add_condition_alert_box,
)
from .plot_style_settings import create_plot_style_settings
from .modals import create_file_browser_modal, create_file_saver_modal
from ..config import DEFAULT_BAM_PATH, DEFAULT_POD5_PATH, DEFAULT_PLOT_HEIGHT

# Assuming you'll add this import:
from .elements import create_card, create_button


def create_layout() -> html.Div:
    """Create the main application layout."""
    return html.Div(
        [
            # Modern Top Bar with glass effect
            create_top_bar(),
            # Spacer div to push content below fixed header
            html.Div(style={"height": "72px"}),
            # Settings Panel (Offcanvas) with modern styling
            dbc.Offcanvas(
                [
                    html.H4(
                        "Plot Settings", className="mb-4", style={"fontWeight": "600"}
                    ),
                    html.Hr(style={"opacity": "0.1"}),
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                create_plot_style_settings("signals"),
                                label="Signals Plot",
                                tab_id="signals-settings-tab",
                            ),
                            dbc.Tab(
                                create_plot_style_settings("stats"),
                                label="Statistics Plot",
                                tab_id="stats-settings-tab",
                            ),
                        ],
                        id="settings-tabs",
                        active_tab="signals-settings-tab",
                        className="nav-pills",
                    ),
                ],
                id="settings-panel",
                is_open=False,
                placement="start",
                backdrop=True,
                style={
                    "width": "500px",
                    "background": "rgba(255, 255, 255, 0.95)",
                    "backdropFilter": "blur(20px)",
                },
            ),
            # Main Container with all existing content
            dbc.Container(
                [
                    # Stores
                    dcc.Store(id="session-id", data=str(uuid.uuid4())),
                    dcc.Store(id="stats-store", data=[]),
                    dcc.Store(id="files-store", data={}),
                    dcc.Store(id="conditions-metadata", data={}),
                    dcc.Store(id="plot-trigger", data=0),
                    dcc.Store(id="theme-store", data="light"),
                    # Custom CSS for dark mode
                    html.Div(id="theme-styles", style={"display": "none"}),
                    # File browser modals
                    create_file_browser_modal(
                        "bam-modal",
                        "Select BAM File",
                        file_extension=".bam",
                        default=DEFAULT_BAM_PATH,
                    ),
                    create_file_browser_modal(
                        "pod5-modal",
                        "Select POD5 File",
                        allow_dir=True,
                        file_extension=None,
                        default=DEFAULT_POD5_PATH,
                    ),
                    create_file_saver_modal(
                        "html-modal",
                        "Select the output file",
                        allow_dir=False,
                        file_extension="html",
                        default="./",
                    ),
                    # Initialization Card
                    create_initialization_card(),
                    # Main Interface (hidden initially)
                    html.Div(
                        [
                            # Add Condition Card
                            create_add_condition_card(),
                            # Add condition alert box
                            create_add_condition_alert_box(),
                            # Conditions List
                            create_card(
                                [
                                    html.H4(
                                        [
                                            html.I(className="bi bi-list-check me-2"),
                                            "Conditions",
                                        ],
                                        className="mb-3 card-title",
                                        style={"fontWeight": "600", "color": "#2d3748"},
                                    ),
                                    html.Hr(style={"opacity": "0.1"}),
                                    html.Div(id="conditions"),
                                ],
                                className="mb-4",
                            ),
                            # Visualization
                            create_visualization_card(),
                        ],
                        id="main",
                        style={"display": "none"},
                    ),
                    # Alert for notifications
                    dbc.Alert(
                        id="alert",
                        is_open=False,
                        duration=4000,
                        style={
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                        },
                    ),
                ],
                fluid=True,
                style={"padding": "2rem", "maxWidth": "1400px"},
            ),
        ],
        id="theme-container",
        style={
            "minHeight": "100vh",
            "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            "backgroundAttachment": "fixed",
        },
    )
