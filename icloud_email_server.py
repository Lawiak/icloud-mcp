#!/usr/bin/env python3

import imaplib
import smtplib
import email
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Any, Optional
from datetime import datetime
import ssl

from fastmcp import FastMCP
from pydantic import BaseModel


# iCloud Email Configuration
IMAP_SERVER = "imap.mail.me.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.mail.me.com"
SMTP_PORT = 587
USERNAME = "your.email@icloud.com"
APP_PASSWORD = "your-app-specific-password"

# Initialize MCP server
mcp = FastMCP("iCloud Email Server")


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
            self.imap_connection.logout()
        if self.smtp_connection:
            self.smtp_connection.quit()


email_manager = EmailManager()


@mcp.tool()
def get_email_folders() -> List[str]:
    """Get list of email folders/mailboxes"""
    try:
        email_manager.connect_imap()
        typ, folders = email_manager.imap_connection.list()
        folder_list = []
        
        for folder in folders:
            folder_name = folder.decode().split(' "/" ')[-1].strip('"')
            folder_list.append(folder_name)
        
        email_manager.disconnect()
        return folder_list
        
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def read_emails(folder: str = "INBOX", limit: int = 10) -> List[Dict[str, Any]]:
    """Read emails from specified folder"""
    try:
        email_manager.connect_imap()
        email_manager.imap_connection.select(folder)
        
        # Search for all emails
        typ, messages = email_manager.imap_connection.search(None, 'ALL')
        email_ids = messages[0].split()
        
        # Get recent emails (limited by limit parameter)
        recent_emails = email_ids[-limit:] if len(email_ids) > limit else email_ids
        
        emails = []
        for email_id in reversed(recent_emails):
            typ, msg_data = email_manager.imap_connection.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Decode subject
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # Get email content
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
            
            emails.append({
                "id": email_id.decode(),
                "from": email_message["From"],
                "to": email_message["To"],
                "subject": subject,
                "date": email_message["Date"],
                "body": body[:500] + "..." if len(body) > 500 else body
            })
        
        email_manager.disconnect()
        return emails
        
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def send_email(to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None) -> Dict[str, str]:
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
        if bcc:
            msg['Bcc'] = bcc
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        recipients = [to]
        if cc:
            recipients.extend(cc.split(','))
        if bcc:
            recipients.extend(bcc.split(','))
        
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
            return {"status": "error", "message": f"Failed to create folder: {result[1][0].decode()}"}
            
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


@mcp.tool()
def search_emails(query: str, folder: str = "INBOX") -> List[Dict[str, Any]]:
    """Search for emails with specific criteria"""
    try:
        email_manager.connect_imap()
        email_manager.imap_connection.select(folder)
        
        # Search for emails containing the query in subject or body
        typ, messages = email_manager.imap_connection.search(None, f'(OR SUBJECT "{query}" BODY "{query}")')
        email_ids = messages[0].split()
        
        emails = []
        for email_id in email_ids:
            typ, msg_data = email_manager.imap_connection.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Decode subject
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            emails.append({
                "id": email_id.decode(),
                "from": email_message["From"],
                "subject": subject,
                "date": email_message["Date"]
            })
        
        email_manager.disconnect()
        return emails
        
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    mcp.run()