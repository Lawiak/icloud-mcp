# iCloud Email MCP Server

A Model Context Protocol (MCP) server that enables Claude Desktop to interact with iCloud email accounts. This server provides full email functionality including reading, sending, and managing emails through your iCloud account.

## Features

- **Read emails** from any folder while preserving unread status
- **Send emails** with support for CC recipients and attachments
- **List email folders** and navigate mailboxes
- **Create new folders** for email organization
- **Move emails** between folders
- **Search emails** across your mailbox
- **Manage read/unread status** explicitly when desired
- **Filter unread emails** specifically
- **Test connections** and server health

## Prerequisites

- **iCloud account** with App-Specific Password enabled
- **Docker** installed on your system
- **Claude Desktop** configured for MCP servers

## Setup

### 1. Generate iCloud App-Specific Password

1. Sign in to [appleid.apple.com](https://appleid.apple.com)
2. Go to **Sign-In and Security** > **App-Specific Passwords**
3. Generate a new password for "Email MCP Server"
4. Save this password - you'll need it for configuration

### 2. Clone and Configure

```bash
git clone https://github.com/Lawiak/icloud-mcp.git
cd icloud-mcp
```

Create your environment file:
```bash
cp .env.example .env
nano .env
```

Configure your credentials in `.env`:
```env
ICLOUD_USERNAME=your.email@icloud.com
ICLOUD_APP_PASSWORD=your-app-specific-password
```

### 3. Build Docker Container

```bash
docker build -t icloud-mcp-server:latest .
```

### 4. Configure Claude Desktop

Edit your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "icloud-email": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/path/to/your/icloud-mcp/.env",
        "icloud-mcp-server:latest",
        "python", "server.py"
      ]
    }
  }
}
```

**For remote deployment** (e.g., Raspberry Pi), use SSH:
```json
{
  "mcpServers": {
    "icloud-email": {
      "command": "ssh",
      "args": [
        "user@your-server-ip",
        "docker", "run", "-i", "--rm",
        "--env-file", "/path/to/icloud-mcp/.env",
        "icloud-mcp-server:latest",
        "python", "server.py"
      ]
    }
  }
}
```

### 5. Restart Claude Desktop

Close and restart Claude Desktop to load the new MCP server configuration.

## Usage

Once configured, you can ask Claude Desktop to:

- "Read my latest emails" (preserves unread status, shows preview)
- "Read my emails with full content" (complete email bodies)
- "Read email ID 123 in full" (complete content of specific email)
- "Show me only my unread emails"  
- "Send an email to john@example.com with subject 'Meeting' and message 'Hello!'"
- "Send an email with attachments" (using base64-encoded content)
- "Send an email with files from local paths" (if files are accessible)
- "Mark email ID 123 as read"
- "Mark email ID 456 as unread"
- "Show me my email folders"
- "Move email ID 123 from INBOX to Archive"
- "Create a new folder called 'Projects'"

### Email Content Options

**Preview Mode** (default): Email bodies are truncated to 200 characters for quick scanning.

**Full Content Mode**: Get complete email content including:
- Full text and HTML body content
- Attachment information (filename, type, size) 
- Complete recipient details (To, CC, BCC)
- Additional email headers
- All content without truncation

### Email Attachments

**Sending Attachments**: The server supports multiple methods for sending attachments:

1. **Base64-encoded content**: For programmatic use or when you have file data
   - Supports all file types (PDFs, images, documents, etc.)
   - 25MB size limit per attachment
   - Automatic MIME type detection

2. **Local file paths**: For files accessible to the Docker container
   - Requires files to be in mounted volumes for Docker deployment
   - Automatic file validation and encoding

**Attachment formats**: Text files, PDFs, images, office documents, archives, etc.

### Unread Status Management

**Important**: This server preserves your email's unread status by default. When Claude Desktop reads emails, they remain unread in your iCloud account unless you explicitly ask to mark them as read.

## Server Configuration

### iCloud Email Settings
- **IMAP Server**: imap.mail.me.com:993 (SSL)
- **SMTP Server**: smtp.mail.me.com:587 (StartTLS)

### Environment Variables
- `ICLOUD_USERNAME`: Your iCloud email address
- `ICLOUD_APP_PASSWORD`: App-specific password from Apple ID

## Troubleshooting

### Connection Issues
1. Verify your App-Specific Password is correct
2. Ensure two-factor authentication is enabled on your Apple ID
3. Check that the Docker container can access the internet

### Claude Desktop Issues
1. Check Claude Desktop logs for connection errors
2. Verify the file paths in your configuration are correct
3. Ensure Docker is running and accessible

### Testing the Server
```bash
# Test Docker container directly
docker run --rm --env-file .env icloud-mcp-server:latest python -c "
from server import test_email_connection
print('Connection test completed')
"
```

## Security Notes

- App-Specific Passwords are safer than your main iCloud password
- Keep your `.env` file secure and never commit it to version control
- The Docker container runs as a non-root user for security
- All email communication uses encrypted connections (SSL/TLS)

## Architecture

This MCP server uses:
- **FastMCP** for Model Context Protocol implementation
- **Python imaplib/smtplib** for email operations
- **Docker** for containerized deployment
- **STDIO transport** for Claude Desktop communication

## License

This project is open source and available under the MIT License.