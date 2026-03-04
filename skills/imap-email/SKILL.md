---
name: imap-email
description: Read emails via IMAP. Use when the user wants to check their inbox, read unread emails, search emails, or view specific emails. Supports Gmail, Outlook, Yahoo, and any IMAP-compatible email provider. Requires IMAP server address, email, and app password.
---

# IMAP Email Checker

Secure email reading via IMAP. Check inbox, unread emails, search, and read specific messages.

## Setup

Most email providers require an **App Password** (not your regular password):
- **Gmail**: Enable 2FA → Google Account → Security → App passwords → Generate
- **Outlook**: Microsoft Account → Advanced security options → App passwords
- **Yahoo**: Account Security → Generate app password

## Quick Commands

```bash
# List all folders
python3 scripts/imap_check.py -s imap.gmail.com -e user@gmail.com -p "app_password" list-folders

# Show unread emails
python3 scripts/imap_check.py -s imap.gmail.com -e user@gmail.com -p "app_password" unread

# Show recent emails
python3 scripts/imap_check.py -s imap.gmail.com -e user@gmail.com -p "app_password" recent

# Search emails
python3 scripts/imap_check.py -s imap.gmail.com -e user@gmail.com -p "app_password" search -q "from:boss@company.com"

# Read full email by UID
python3 scripts/imap_check.py -s imap.gmail.com -e user@gmail.com -p "app_password" read -u 123
```

## Environment Variables

For convenience, credentials can be stored as environment variables:
```bash
export IMAP_SERVER=imap.gmail.com
export IMAP_EMAIL=user@gmail.com
export IMAP_PASSWORD="app_password"
```

Then run without explicit credentials:
```bash
python3 scripts/imap_check.py unread
```

## Common IMAP Servers

| Provider      | IMAP Server          |
|---------------|---------------------|
| Gmail         | imap.gmail.com      |
| Outlook/Hotmail | outlook.office365.com |
| Yahoo         | imap.mail.yahoo.com |
| iCloud        | imap.mail.me.com    |
| Fastmail      | imap.fastmail.com   |

## Search Syntax

The search command supports:
- `from:email@domain.com` - Filter by sender
- `to:email@domain.com` - Filter by recipient
- `subject:text` - Filter by subject
- `since:YYYY-MM-DD` - Emails since date
- `before:YYYY-MM-DD` - Emails before date
- Plain text - Search in message body

Example: `search -q "from:amazon since:2024-01-01"`

## Security Notes

- **Never log or store passwords in plain text files**
- Use app passwords, not your main account password
- Consider using environment variables for credentials
- The script uses SSL/TLS by default (IMAPS port 993)