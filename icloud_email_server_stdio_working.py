#!/usr/bin/env python3

import os
import imaplib
import smtplib
import email
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP

# iCloud Email Configuration from environment variables
IMAP_SERVER = "imap.mail.me.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.mail.me.com"
SMTP_PORT = 587

# Get credentials from environment variables
USERNAME = os.getenv("ICLOUD_USERNAME", "your.email@icloud.com")
APP_PASSWORD = os.getenv("ICLOUD_APP_PASSWORD", "your-app-specific-password")

# Initialize MCP server
mcp = FastMCP("iCloud Email Server (STDIO Working)")

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

@mcp.tool()
def get_server_info() -> Dict[str, str]:
    """Get server information and configuration"""
    return {
        "server_name": "iCloud Email Server (STDIO Working)",
        "username": USERNAME,
        "imap_server": f"{IMAP_SERVER}:{IMAP_PORT}",
        "smtp_server": f"{SMTP_SERVER}:{SMTP_PORT}",
        "version": "1.0.0-stdio-working"
    }

@mcp.tool()
def test_email_connection() -> Dict[str, str]:
    """Test the email server connection"""
    try:
        email_manager.connect_imap()
        email_manager.disconnect()
        return {"status": "success", "message": "Email connection test successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_email_folders() -> List[str]:
    """Get list of email folders/mailboxes"""
    try:
        email_manager.connect_imap()
        typ, folders = email_manager.imap_connection.list()
        folder_list = []
        
        for folder in folders:
            if folder:
                # Handle both bytes and string folder names
                if isinstance(folder, bytes):
                    folder_str = folder.decode()
                else:
                    folder_str = str(folder)
                folder_name = folder_str.split(' "/" ')[-1].strip('"')
                folder_list.append(folder_name)
        
        email_manager.disconnect()
        return folder_list
        
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def read_emails(folder: str = "INBOX", limit: int = 5) -> List[Dict[str, Any]]:
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
                # Decode email_id and use BODY[] for reliable fetching
                fetch_id = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
                typ, msg_data = email_manager.imap_connection.fetch(fetch_id, '(BODY[])')
                if msg_data and len(msg_data) > 0 and isinstance(msg_data[0], tuple) and len(msg_data[0]) > 1:
                    email_body = msg_data[0][1]
                    if isinstance(email_body, bytes) and len(email_body) > 10:  # Ensure we have actual content
                        email_message = email.message_from_bytes(email_body)
                    else:
                        continue  # Skip this email if no valid content
                    
                    # Decode subject with proper error handling
                    subject = "No Subject"
                    if email_message["Subject"]:
                        try:
                            decoded_header = decode_header(email_message["Subject"])
                            if decoded_header and decoded_header[0][0]:
                                subject = decoded_header[0][0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode()
                        except:
                            subject = str(email_message["Subject"])
                    
                    # Get email content with robust handling
                    body = ""
                    try:
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload is None:
                                            continue
                                        elif isinstance(payload, bytes):
                                            body = payload.decode('utf-8', errors='ignore')
                                        elif isinstance(payload, str):
                                            body = payload
                                        else:
                                            body = str(payload)
                                        break
                                    except:
                                        continue
                        else:
                            try:
                                payload = email_message.get_payload(decode=True)
                                if payload is None:
                                    body = "Empty message"
                                elif isinstance(payload, bytes):
                                    body = payload.decode('utf-8', errors='ignore')
                                elif isinstance(payload, str):
                                    body = payload
                                else:
                                    body = str(payload)
                            except:
                                body = "Could not decode message"
                    except:
                        body = "Error processing message content"
                    
                    # Handle email_id for display
                    display_id = email_id
                    if isinstance(email_id, bytes):
                        display_id = email_id.decode('utf-8', errors='ignore')
                    else:
                        display_id = str(email_id)
                    
                    emails.append({
                        "id": display_id,
                        "from": email_message.get("From", "Unknown"),
                        "to": email_message.get("To", "Unknown"),
                        "subject": subject,
                        "date": email_message.get("Date", "Unknown"),
                        "body": body[:200] + "..." if len(body) > 200 else body
                    })
            except Exception as e:
                # Handle email_id for error display
                display_id = email_id
                if isinstance(email_id, bytes):
                    display_id = email_id.decode('utf-8', errors='ignore')
                else:
                    display_id = str(email_id)
                emails.append({"error": f"Error reading email {display_id}: {str(e)}"})
        
        email_manager.disconnect()
        return emails
        
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def send_email(to: str, subject: str, body: str, cc: Optional[str] = None) -> Dict[str, str]:
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

if __name__ == "__main__":
    mcp.run()