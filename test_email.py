#!/usr/bin/env python3

import imaplib
import ssl

# iCloud Email Configuration
IMAP_SERVER = "imap.mail.me.com"
IMAP_PORT = 993
USERNAME = "your.email@icloud.com"
APP_PASSWORD = "your-app-specific-password"

def test_imap_connection():
    """Test iCloud IMAP connection"""
    try:
        context = ssl.create_default_context()
        imap_connection = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
        imap_connection.login(USERNAME, APP_PASSWORD)
        
        # Get folders
        typ, folders = imap_connection.list()
        print("Email folders:")
        for folder in folders[:5]:  # Show first 5 folders
            folder_name = folder.decode().split(' "/" ')[-1].strip('"')
            print(f"  - {folder_name}")
        
        # Select inbox and get email count
        imap_connection.select("INBOX")
        typ, messages = imap_connection.search(None, 'ALL')
        email_count = len(messages[0].split()) if messages[0] else 0
        print(f"\nEmails in INBOX: {email_count}")
        
        imap_connection.logout()
        print("\n✅ IMAP connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ IMAP connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_imap_connection()