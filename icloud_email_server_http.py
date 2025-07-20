#!/usr/bin/env python3

import os
import asyncio
import json
from typing import Any, Dict

# Import our email functionality
from icloud_email_server_docker import (
    get_server_info, test_email_connection, get_email_folders,
    read_emails, send_email, create_folder, move_email,
    USERNAME, APP_PASSWORD, IMAP_SERVER, SMTP_SERVER
)

# Simple HTTP server for testing
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class MCPHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "running",
                "server": "iCloud Email MCP Server (HTTP)",
                "version": "1.0.0",
                "username": USERNAME,
                "endpoints": {
                    "/": "Server status",
                    "/info": "Server information",
                    "/test": "Test email connection",
                    "/folders": "List email folders",
                    "/emails?folder=INBOX&limit=5": "Read emails",
                    "/health": "Health check"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "server": "running"}).encode())
            
        elif self.path == '/info':
            try:
                info = get_server_info()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(info, indent=2).encode())
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
                
        elif self.path == '/test':
            try:
                result = test_email_connection()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode())
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
                
        elif self.path == '/folders':
            try:
                folders = get_email_folders()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"folders": folders}, indent=2).encode())
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
                
        elif self.path.startswith('/emails'):
            try:
                # Parse query parameters
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                
                folder = params.get('folder', ['INBOX'])[0]
                limit = int(params.get('limit', ['5'])[0])
                
                emails = read_emails(folder, limit)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"emails": emails}, indent=2).encode())
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        """Override to reduce log spam"""
        print(f"[{self.address_string()}] {format % args}")

def run_http_server():
    """Run the HTTP server"""
    print("🌐 Starting iCloud Email MCP Server in HTTP mode")
    print(f"📧 Username: {USERNAME}")
    print(f"🔗 IMAP: {IMAP_SERVER}")
    print(f"🔗 SMTP: {SMTP_SERVER}")
    print("🎯 Server will run on http://0.0.0.0:8080")
    print("")
    print("Available endpoints:")
    print("  GET /         - Server status")
    print("  GET /health   - Health check")
    print("  GET /info     - Server information")
    print("  GET /test     - Test email connection")
    print("  GET /folders  - List email folders")
    print("  GET /emails?folder=INBOX&limit=5 - Read emails")
    print("")
    
    server = HTTPServer(('0.0.0.0', 8080), MCPHTTPHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()

if __name__ == "__main__":
    run_http_server()