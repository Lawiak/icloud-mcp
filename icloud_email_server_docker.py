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
mcp = FastMCP("iCloud Email Server (Docker)")

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
        "server_name": "iCloud Email Server (Docker)",
        "username": USERNAME,
        "imap_server": f"{IMAP_SERVER}:{IMAP_PORT}",
        "smtp_server": f"{SMTP_SERVER}:{SMTP_PORT}",
        "version": "1.0.0-docker"
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
                folder_name = folder.decode().split(' "/" ')[-1].strip('"')
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
                        "id": email_id.decode() if isinstance(email_id, bytes) else str(email_id),
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

@mcp.tool()
def create_folder(folder_name: str) -> Dict[str, str]:
    """Create a new email folder"""
    try:
        email_manager.connect_imap()
        result = email_manager.imap_connection.create(folder_name)
        email_manager.disconnect()
        
        if result[0] == 'OK':
            return {"status": "success", "message": f"Folder '{folder_name}' created"}
        else:
            return {"status": "error", "message": f"Failed to create folder: {result[1][0].decode() if result[1] else 'Unknown error'}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def move_email(email_id: str, source_folder: str, destination_folder: str) -> Dict[str, str]:
    """Move an email from one folder to another"""
    try:
        email_manager.connect_imap()
        
        # Select source folder
        email_manager.imap_connection.select(source_folder)
        
        # Copy email to destination folder
        email_manager.imap_connection.copy(email_id, destination_folder)
        
        # Mark original email for deletion
        email_manager.imap_connection.store(email_id, '+FLAGS', '\\Deleted')
        
        # Expunge to actually delete
        email_manager.imap_connection.expunge()
        
        email_manager.disconnect()
        
        return {"status": "success", "message": f"Email moved from {source_folder} to {destination_folder}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(f"Starting iCloud Email MCP Server (Docker)")
    print(f"Username: {USERNAME}")
    print(f"IMAP Server: {IMAP_SERVER}:{IMAP_PORT}")
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    mcp.run()