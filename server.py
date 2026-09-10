#!/usr/bin/env python3
"""
Lightweight Web Server for Druggie_buggie Forensic Dashboard.
Serves public/ directory at http://localhost:8080 (matching Portfolio convention).
"""

import http.server
import socketserver
import os
import sys

PORT = 8080
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)


def start_server():
    os.chdir(os.path.dirname(__file__))
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print("==================================================")
        print(f"🚀 Druggie_buggie Forensic Dashboard running at:")
        print(f"   👉 http://localhost:{PORT}")
        print("==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server.")
            sys.exit(0)


if __name__ == "__main__":
    start_server()
