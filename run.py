#!/usr/bin/env python
"""Main entry point for the Nanopore Signal Visualizer application."""

from dash_app import create_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, port=8050)