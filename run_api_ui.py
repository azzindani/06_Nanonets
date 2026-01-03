#!/usr/bin/env python
"""
Launcher script for the API-based Gradio UI.

This script launches the Gradio UI that connects to the FastAPI backend
via HTTP calls instead of directly importing core modules.

Usage:
    python run_api_ui.py                          # Default settings
    python run_api_ui.py --api-url http://server:8000  # Custom API URL
    python run_api_ui.py --port 7862              # Custom UI port
    python run_api_ui.py --start-api              # Auto-start API server
"""
import argparse
import subprocess
import sys
import time
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def check_api_server(api_url: str, timeout: int = 5) -> bool:
    """Check if API server is accessible."""
    try:
        import requests
        response = requests.get(f"{api_url}/api/v1/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def start_api_server(port: int = 8000):
    """Start the API server in background."""
    print(f"Starting API server on port {port}...")
    
    # Start API server as subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "api.server"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
    )
    
    # Wait for server to start
    api_url = f"http://localhost:{port}"
    for i in range(30):  # Wait up to 30 seconds
        if check_api_server(api_url):
            print(f"  ✓ API server started successfully")
            return process
        time.sleep(1)
        print(f"  Waiting for API server... ({i+1}s)")
    
    print("  ✗ Failed to start API server")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Launch the API-based OCR UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_api_ui.py
    python run_api_ui.py --api-url http://192.168.1.100:8000
    python run_api_ui.py --port 7862 --share
    python run_api_ui.py --start-api
        """
    )
    
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="URL of the API server (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7861,
        help="Port for the Gradio UI (default: 7861)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for the Gradio UI (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio link"
    )
    
    parser.add_argument(
        "--start-api",
        action="store_true",
        help="Automatically start the API server if not running"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="Port for API server if --start-api is used (default: 8000)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("NANONETS OCR - API CLIENT UI LAUNCHER")
    print("=" * 60)
    
    api_process = None
    
    # Check/start API server
    if args.start_api:
        if not check_api_server(args.api_url):
            api_process = start_api_server(args.api_port)
            if api_process is None:
                print("Failed to start API server. Please start it manually:")
                print("    python -m api.server")
                sys.exit(1)
        else:
            print(f"  ✓ API server already running at {args.api_url}")
    else:
        if check_api_server(args.api_url):
            print(f"  ✓ API server accessible at {args.api_url}")
        else:
            print(f"  ⚠ API server not responding at {args.api_url}")
            print("    Start it with: python -m api.server")
            print("    Or use --start-api flag to auto-start")
    
    print("=" * 60)
    
    try:
        # Import and run the API UI
        from ui.app_api import run_api_ui
        
        run_api_ui(
            api_url=args.api_url,
            server_name=args.host,
            server_port=args.port,
            share=args.share
        )
    except KeyboardInterrupt:
        print("\n  Shutting down...")
    finally:
        # Cleanup API server if we started it
        if api_process:
            print("  Stopping API server...")
            api_process.terminate()
            api_process.wait()


if __name__ == "__main__":
    main()
