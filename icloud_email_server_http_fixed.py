#!/usr/bin/env python3

import os
import imaplib
import smtplib
import email
import ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# iCloud Email Configuration from environment variables
IMAP_SERVER = "imap.mail.me.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.mail.me.com"
SMTP_PORT = 587

# Get credentials from environment variables
USERNAME = os.getenv("ICLOUD_USERNAME", "your.email@icloud.com")
APP_PASSWORD = os.getenv("ICLOUD_APP_PASSWORD", "your-app-specific-password")

class EmailManager:
    def __init__(self):
        self.imap_connection = None
        self.smtp_connection = None
    
    def connect_imap(self):
        """Connect to iCloud IMAP server"""
        try:
            context = ssl.create_default_context()
            self.imap_connection = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
            self.imap_connection.login(USERNAME, APP_PASSWORD)
            return True
        except Exception as e:
            raise Exception(f"IMAP connection failed: {str(e)}")
    
    def connect_smtp(self):
        """Connect to iCloud SMTP server"""
        try:
            self.smtp_connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            self.smtp_connection.starttls()
            self.smtp_connection.login(USERNAME, APP_PASSWORD)
            return True
        except Exception as e:
            raise Exception(f"SMTP connection failed: {str(e)}")
    
    def disconnect(self):
        """Disconnect from email servers"""
        if self.imap_connection:
            try:
                self.imap_connection.logout()
            except:
                pass
        if self.smtp_connection:
            try:
                self.smtp_connection.quit()
            except:
                pass

email_manager = EmailManager()

# Direct function implementations (not FastMCP decorated)
def get_server_info_direct() -> Dict[str, str]:
    """Get server information and configuration"""
    return {
        "server_name": "iCloud Email Server (HTTP)",
        "username": USERNAME,
        "imap_server": f"{IMAP_SERVER}:{IMAP_PORT}",
        "smtp_server": f"{SMTP_SERVER}:{SMTP_PORT}",
        "version": "1.0.0-http",
        "status": "running"
    }

def test_email_connection_direct() -> Dict[str, str]:
    """Test the email server connection"""
    try:
        email_manager.connect_imap()
        email_manager.disconnect()
        return {"status": "success", "message": "Email connection test successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_email_folders_direct() -> List[str]:
    """Get list of email folders/mailboxes"""
    try:
        email_manager.connect_imap()
        typ, folders = email_manager.imap_connection.list()
        folder_list = []
        
        for folder in folders:
            if folder:
                folder_name = folder.decode().split(' "/" ')[-1].strip('"')
                folder_list.append(folder_name)
        
        email_manager.disconnect()
        return folder_list
        
    except Exception as e:
        return [f"Error: {str(e)}"]

def read_emails_direct(folder: str = "INBOX", limit: int = 5) -> List[Dict[str, Any]]:
    """Read emails from specified folder"""
    try:
        email_manager.connect_imap()
        email_manager.imap_connection.select(folder)
        
        # Search for all emails
        typ, messages = email_manager.imap_connection.search(None, 'ALL')
        if not messages[0]:
            return []
            
        email_ids = messages[0].split()
        
        # Get recent emails (limited by limit parameter)
        recent_emails = email_ids[-limit:] if len(email_ids) > limit else email_ids
        
        emails = []
        for email_id in reversed(recent_emails):
            try:
                typ, msg_data = email_manager.imap_connection.fetch(email_id, '(RFC822)')
                if msg_data and msg_data[0] and msg_data[0][1]:
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Decode subject
                    subject = "No Subject"
                    if email_message["Subject"]:
                        decoded_header = decode_header(email_message["Subject"])
                        if decoded_header and decoded_header[0][0]:
                            subject = decoded_header[0][0]
                            if isinstance(subject, bytes):
                                subject = subject.decode()
                    
                    # Get email content (simplified)
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break
                                except:
                                    body = "Could not decode body"
                    else:
                        try:
                            body = email_message.get_payload(decode=True).decode()
                        except:
                            body = "Could not decode body"
                    
                    emails.append({
                        "id": email_id.decode(),
                        "from": email_message.get("From", "Unknown"),
                        "to": email_message.get("To", "Unknown"),
                        "subject": subject,
                        "date": email_message.get("Date", "Unknown"),
                        "body": body[:200] + "..." if len(body) > 200 else body
                    })
            except Exception as e:
                emails.append({"error": f"Error reading email {email_id}: {str(e)}"})
        
        email_manager.disconnect()
        return emails
        
    except Exception as e:
        return [{"error": str(e)}]

def send_email_direct(to: str, subject: str, body: str, cc: Optional[str] = None) -> Dict[str, str]:
    """Send an email"""
    try:
        email_manager.connect_smtp()
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = USERNAME
        msg['To'] = to
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = cc
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        recipients = [to]
        if cc:
            recipients.extend([addr.strip() for addr in cc.split(',')])
        
        email_manager.smtp_connection.send_message(msg, to_addrs=recipients)
        email_manager.disconnect()
        
        return {"status": "success", "message": f"Email sent to {to}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

class MCPHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "status": "running",
                    "server": "iCloud Email MCP Server (HTTP Fixed)",
                    "version": "1.0.1",
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
                info = get_server_info_direct()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(info, indent=2).encode())
                    
            elif self.path == '/test':
                result = test_email_connection_direct()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode())
                    
            elif self.path == '/folders':
                folders = get_email_folders_direct()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"folders": folders}, indent=2).encode())
                    
            elif self.path.startswith('/emails'):
                # Parse query parameters
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                
                folder = params.get('folder', ['INBOX'])[0]
                limit = int(params.get('limit', ['5'])[0])
                
                emails = read_emails_direct(folder, limit)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"emails": emails}, indent=2).encode())
                
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"❌ Error handling request {self.path}: {str(e)}")
            self.send_error(500, f"Error: {str(e)}")

    def log_message(self, format, *args):
        """Override to reduce log spam"""
        print(f"[{self.address_string()}] {format % args}")

def run_http_server():
    """Run the HTTP server"""
    print("🌐 Starting iCloud Email MCP Server in HTTP mode (Fixed)")
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