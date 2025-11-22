"""
Main entry point for Nanonets VL OCR application.
"""
import argparse
import sys

from config import settings


def run_api():
    """Run the FastAPI server."""
    from api.server import run_server
    run_server()


def run_ui():
    """Run the Gradio interface."""
    from ui.app import run_ui as start_ui
    start_ui()


def run_both():
    """Run both API and UI (for development)."""
    import threading

    # Start API in background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Run UI in main thread
    run_ui()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Nanonets VL OCR - Document Processing System"
    )
    parser.add_argument(
        "--mode",
        choices=["api", "ui", "both"],
        default="ui",
        help="Run mode: api (FastAPI server), ui (Gradio interface), or both"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Override host address"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override port number"
    )

    args = parser.parse_args()

    # Override settings if provided
    if args.host:
        settings.api.host = args.host
        settings.ui.server_name = args.host
    if args.port:
        if args.mode == "api":
            settings.api.port = args.port
        else:
            settings.ui.server_port = args.port

    print("=" * 60)
    print("Nanonets VL OCR System")
    print("=" * 60)
    print(f"  Mode: {args.mode}")
    print(f"  Model: {settings.model.name}")

    if args.mode == "api":
        print(f"  API: http://{settings.api.host}:{settings.api.port}")
        run_api()
    elif args.mode == "ui":
        print(f"  UI: http://{settings.ui.server_name}:{settings.ui.server_port}")
        run_ui()
    else:
        print(f"  API: http://{settings.api.host}:{settings.api.port}")
        print(f"  UI: http://{settings.ui.server_name}:{settings.ui.server_port}")
        run_both()


if __name__ == "__main__":
    main()
