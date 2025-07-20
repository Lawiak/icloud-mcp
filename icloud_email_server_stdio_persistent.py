#!/usr/bin/env python3

import os
import sys
import time
import threading
from fastmcp import FastMCP

# Import our email functionality 
from icloud_email_server_docker import (
    USERNAME, APP_PASSWORD, IMAP_SERVER, SMTP_SERVER,
    EmailManager, mcp
)

def keep_alive():
    """Keep the server alive even without MCP client connection"""
    print("🔄 Keep-alive thread started")
    while True:
        time.sleep(60)  # Check every minute
        print(f"⏰ Server still running... (Username: {USERNAME})")

def run_persistent_stdio_server():
    """Run MCP server with STDIO but keep it alive"""
    print("🚀 Starting iCloud Email MCP Server (Persistent STDIO)")
    print(f"📧 Username: {USERNAME}")
    print(f"🔗 IMAP: {IMAP_SERVER}")
    print(f"🔗 SMTP: {SMTP_SERVER}")
    print("📡 Transport: STDIO (Model Context Protocol)")
    print("🔄 Keep-alive mode: Container will stay running")
    print("")
    
    # Start keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    try:
        # Try to run the MCP server
        print("🎯 Starting MCP server...")
        mcp.run()
    except Exception as e:
        print(f"⚠️  MCP server error: {e}")
        print("🔄 Falling back to keep-alive mode...")
        
        # If MCP server fails, just keep container alive
        try:
            while True:
                time.sleep(30)
                print("📡 Waiting for MCP client connection...")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            sys.exit(0)

if __name__ == "__main__":
    run_persistent_stdio_server()