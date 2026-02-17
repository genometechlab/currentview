import uuid
import dash_bootstrap_components as dbc
from dash import dcc, html

from .components import (
    create_top_bar,
    create_initialization_card,
    create_add_condition_card,
    create_visualization_card,
    create_add_condition_alert_box,
    create_conditions_list_card,
)
from .plot_style_settings import create_plot_style_settings
from .modals import create_input_modal, create_export_modal
from ..config import (
    DEFAULT_BAM_PATH,
    DEFAULT_POD5_PATH,
    EXPORT_FORMATS,
)


def create_stores():
    """Create all application data stores."""
    return [
        dcc.Store(id="session-id", data=str(uuid.uuid4())),
        dcc.Store(id="stats-store", data=[]),
        dcc.Store(id="files-store", data={}),
        dcc.Store(id="conditions-metadata", data={}),
        dcc.Store(id="plot-trigger", data=0),
        dcc.Store(id="theme-store", data="light"),
        dcc.Store(id="molecule-type-store", data="rna"),
        dcc.Store(id="matched-query-base", data=None),
    ]


def create_modals():
    """Create all file browser and export modals."""
    return [
        create_input_modal(
            "bam-modal",
            "Select BAM File",
            file_extension=".bam",
            default=DEFAULT_BAM_PATH,
        ),
        create_input_modal(
            "pod5-modal",
            "Select POD5 File or Directory",
            file_extension=".pod5",
            allow_both=True,
            default=DEFAULT_POD5_PATH,
        ),
        create_export_modal(
            "export-modal",
            "Select the output file",
            allow_dir=False,
            file_extensions=EXPORT_FORMATS,
            default_extension=".html",
            default="./",
        ),
    ]


def create_settings_panel():
    """Create the settings offcanvas panel."""
    return dbc.Offcanvas(
        [
            html.H4("Plot Settings", className="mb-4", style={"fontWeight": "600"}),
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
    )


def create_main_content():
    """Create the main application content (hidden until initialized)."""
    return html.Div(
        [
            create_add_condition_card(),
            create_add_condition_alert_box(),
            create_conditions_list_card(),
            create_visualization_card(),
        ],
        id="main",
        style={"display": "none"},
    )


def create_layout() -> html.Div:
    """Create the main application layout."""
    return html.Div(
        [
            create_top_bar(),
            html.Div(style={"height": "72px"}),  # Spacer for fixed header
            create_settings_panel(),
            dbc.Container(
                [
                    # Application stores
                    *create_stores(),
                    # Hidden div for theme styles
                    html.Div(id="theme-styles", style={"display": "none"}),
                    # Modals
                    *create_modals(),
                    # Initialization card
                    create_initialization_card(),
                    # Main content (hidden initially)
                    create_main_content(),
                    # Global alert
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
