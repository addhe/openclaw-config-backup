#!/usr/bin/env python3
"""
IMAP Email Checker - Secure email reading via IMAP

Usage:
    python3 imap_check.py --help
    python3 imap_check.py --server imap.gmail.com --email user@gmail.com --password "app_password" list-folders
    python3 imap_check.py --server imap.gmail.com --email user@gmail.com --password "app_password" unread
    python3 imap_check.py --server imap.gmail.com --email user@gmail.com --password "app_password" search --query "from:boss@company.com"
    python3 imap_check.py --server imap.gmail.com --email user@gmail.com --password "app_password" read --uid 123

Credentials can also be passed via environment variables:
    IMAP_SERVER, IMAP_EMAIL, IMAP_PASSWORD
"""

import argparse
import imaplib
import smtplib
import os
import sys
from email import message_from_bytes
from email.header import decode_header
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Dict, Any


def decode_str(s: str) -> str:
    """Decode MIME encoded string."""
    if s is None:
        return ""
    decoded_parts = decode_header(s)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            charset = charset or 'utf-8'
            try:
                result.append(part.decode(charset, errors='replace'))
            except (LookupError, UnicodeDecodeError):
                result.append(part.decode('utf-8', errors='replace'))
        else:
            result.append(str(part))
    return ''.join(result)


def get_body(msg: Message) -> str:
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='replace')
                    break
                except Exception:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='replace')
        except Exception:
            body = str(msg.get_payload())
    
    return body.strip()


def format_date(date_str: str) -> str:
    """Format email date for display."""
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return date_str or "Unknown"


class IMAPChecker:
    def __init__(self, server: str, email_addr: str, password: str, folder: str = "INBOX"):
        self.server = server
        self.email = email_addr
        self.password = password
        self.folder = folder
        self.conn: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> bool:
        """Connect to IMAP server."""
        try:
            self.conn = imaplib.IMAP4_SSL(self.server)
            self.conn.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect: {e}", file=sys.stderr)
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server."""
        if self.conn:
            try:
                self.conn.close()
                self.conn.logout()
            except Exception:
                pass
    
    def list_folders(self) -> List[str]:
        """List all folders/mailboxes."""
        if not self.conn:
            return []
        
        try:
            status, folders = self.conn.list()
            if status != "OK":
                return []
            
            result = []
            for folder in folders:
                if folder:
                    parts = folder.decode().split('"')
                    # Folder name is usually the last quoted part
                    for part in parts:
                        if part and part.strip() and not part.startswith('\\'):
                            result.append(part.strip())
            return result
        except Exception as e:
            print(f"ERROR listing folders: {e}", file=sys.stderr)
            return []
    
    def select_folder(self, folder: str) -> bool:
        """Select a folder/mailbox."""
        if not self.conn:
            return False
        try:
            status, data = self.conn.select(f'"{folder}"')
            return status == "OK"
        except Exception as e:
            print(f"ERROR selecting folder: {e}", file=sys.stderr)
            return False
    
    def get_unread(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails from selected folder."""
        if not self.conn:
            return []
        
        try:
            status, messages = self.conn.search(None, "UNSEEN")
            if status != "OK":
                return []
            
            uids = messages[0].split()
            if not uids:
                return []
            
            # Limit results
            uids = uids[-limit:] if len(uids) > limit else uids
            
            results = []
            for uid in uids:
                email_data = self._fetch_email(uid)
                if email_data:
                    results.append(email_data)
            
            return results
        except Exception as e:
            print(f"ERROR fetching unread: {e}", file=sys.stderr)
            return []
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails (by date) from selected folder."""
        if not self.conn:
            return []
        
        try:
            status, messages = self.conn.search(None, "ALL")
            if status != "OK":
                return []
            
            uids = messages[0].split()
            if not uids:
                return []
            
            # Get most recent
            uids = uids[-limit:] if len(uids) > limit else uids
            
            results = []
            for uid in reversed(uids):
                email_data = self._fetch_email(uid)
                if email_data:
                    results.append(email_data)
            
            return results
        except Exception as e:
            print(f"ERROR fetching recent: {e}", file=sys.stderr)
            return []
    
    def search_emails(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search emails with query."""
        if not self.conn:
            return []
        
        try:
            # Parse simple search syntax
            criteria = self._parse_search_query(query)
            status, messages = self.conn.search(None, *criteria)
            if status != "OK":
                return []
            
            uids = messages[0].split()
            if not uids:
                return []
            
            uids = uids[-limit:] if len(uids) > limit else uids
            
            results = []
            for uid in reversed(uids):
                email_data = self._fetch_email(uid)
                if email_data:
                    results.append(email_data)
            
            return results
        except Exception as e:
            print(f"ERROR searching: {e}", file=sys.stderr)
            return []
    
    def read_email(self, uid: int) -> Optional[Dict[str, Any]]:
        """Read full email by UID."""
        return self._fetch_email(str(uid).encode(), full=True)
    
    def _parse_search_query(self, query: str) -> List[str]:
        """Parse search query into IMAP criteria."""
        criteria = []
        
        # Simple parsing for common patterns
        parts = query.split()
        i = 0
        while i < len(parts):
            part = parts[i].lower()
            
            if part.startswith("from:"):
                criteria.extend(["FROM", parts[i][5:]])
            elif part.startswith("to:"):
                criteria.extend(["TO", parts[i][3:]])
            elif part.startswith("subject:"):
                criteria.extend(["SUBJECT", parts[i][8:]])
            elif part.startswith("since:"):
                # Format: YYYY-MM-DD
                criteria.extend(["SINCE", parts[i][6:]])
            elif part.startswith("before:"):
                criteria.extend(["BEFORE", parts[i][7:]])
            else:
                # General text search
                criteria.extend(["TEXT", parts[i]])
            
            i += 1
        
        if not criteria:
            criteria = ["ALL"]
        
        return criteria
    
    def _fetch_email(self, uid: bytes, full: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch email by UID."""
        try:
            status, msg_data = self.conn.fetch(uid, "(RFC822)" if full else "(RFC822.HEADER)")
            if status != "OK" or not msg_data:
                return None
            
            raw_email = msg_data[0][1]
            msg = message_from_bytes(raw_email)
            
            result = {
                "uid": int(uid),
                "from": decode_str(msg.get("From", "")),
                "to": decode_str(msg.get("To", "")),
                "subject": decode_str(msg.get("Subject", "")),
                "date": format_date(msg.get("Date", "")),
            }
            
            if full:
                result["body"] = get_body(msg)[:5000]  # Limit body size
            
            return result
        except Exception as e:
            print(f"ERROR fetching email: {e}", file=sys.stderr)
            return None
    
    def delete_email(self, uid: int) -> bool:
        """Delete a single email by UID."""
        if not self.conn:
            return False
        try:
            status, _ = self.conn.store(str(uid), "+FLAGS", "\\Deleted")
            if status == "OK":
                self.conn.expunge()
                return True
            return False
        except Exception as e:
            print(f"ERROR deleting email: {e}", file=sys.stderr)
            return False
    
    def delete_from_sender(self, sender: str, limit: int = 50, dry_run: bool = False) -> Dict[str, Any]:
        """Delete all emails from a specific sender."""
        if not self.conn:
            return {"deleted": 0, "error": "Not connected"}
        
        try:
            # Search for emails from sender
            status, messages = self.conn.search(None, f'FROM "{sender}"')
            if status != "OK":
                return {"deleted": 0, "error": "Search failed"}
            
            uids = messages[0].split()
            if not uids:
                return {"deleted": 0, "message": "No emails found from this sender"}
            
            uids = uids[:limit]  # Apply limit
            
            if dry_run:
                # Fetch and return what would be deleted
                emails = []
                for uid in uids:
                    email_data = self._fetch_email(uid)
                    if email_data:
                        emails.append(email_data)
                return {"would_delete": len(emails), "emails": emails}
            
            # Actually delete
            deleted = 0
            for uid in uids:
                try:
                    status, _ = self.conn.store(uid, "+FLAGS", "\\Deleted")
                    if status == "OK":
                        deleted += 1
                except Exception:
                    continue
            
            self.conn.expunge()
            return {"deleted": deleted}
        except Exception as e:
            return {"deleted": 0, "error": str(e)}
    
    def mark_read(self, uid: int) -> bool:
        """Mark an email as read (remove \\Seen flag)."""
        if not self.conn:
            return False
        try:
            status, _ = self.conn.store(str(uid), "-FLAGS", "\\Seen")
            return status == "OK"
        except Exception as e:
            print(f"ERROR marking email as read: {e}", file=sys.stderr)
            return False


class SMTPSender:
    """Send emails via SMTP."""
    
    def __init__(self, server: str, email_addr: str, password: str, port: int = 465):
        self.server = server
        self.email = email_addr
        self.password = password
        self.port = port
    
    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Send an email."""
        try:
            msg = MIMEMultipart("alternative") if html else MIMEText(body)
            msg["From"] = self.email
            msg["To"] = to
            msg["Subject"] = subject
            
            if html:
                msg.attach(MIMEText(body, "html"))
            
            with smtplib.SMTP_SSL(self.server, self.port) as smtp:
                smtp.login(self.email, self.password)
                smtp.sendmail(self.email, to, msg.as_string())
            
            return True
        except Exception as e:
            print(f"ERROR sending email: {e}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(
        description="IMAP Email Checker - Secure email reading via IMAP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Connection options
    parser.add_argument("--server", "-s", help="IMAP server (e.g., imap.gmail.com)")
    parser.add_argument("--email", "-e", help="Email address")
    parser.add_argument("--password", "-p", help="Email password or app password")
    parser.add_argument("--folder", "-f", default="INBOX", help="Folder to check (default: INBOX)")
    
    # Commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # list-folders
    subparsers.add_parser("list-folders", help="List all folders/mailboxes")
    
    # unread
    unread_parser = subparsers.add_parser("unread", help="Show unread emails")
    unread_parser.add_argument("--limit", "-l", type=int, default=10, help="Max emails to show")
    
    # recent
    recent_parser = subparsers.add_parser("recent", help="Show recent emails")
    recent_parser.add_argument("--limit", "-l", type=int, default=10, help="Max emails to show")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search emails")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    
    # read
    read_parser = subparsers.add_parser("read", help="Read full email by UID")
    read_parser.add_argument("--uid", "-u", type=int, required=True, help="Email UID to read")
    
    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete email(s) by UID or sender")
    delete_parser.add_argument("--uid", "-u", type=int, help="Single UID to delete")
    delete_parser.add_argument("--from-sender", "-f", help="Delete all emails from this sender")
    delete_parser.add_argument("--limit", "-l", type=int, default=50, help="Max emails to delete")
    delete_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    
    # mark-read
    markread_parser = subparsers.add_parser("mark-read", help="Mark email as read by UID")
    markread_parser.add_argument("--uid", "-u", type=int, required=True, help="Email UID to mark as read")
    
    # send
    send_parser = subparsers.add_parser("send", help="Send an email via SMTP")
    send_parser.add_argument("--to", "-t", required=True, help="Recipient email address")
    send_parser.add_argument("--subject", "-s", required=True, help="Email subject")
    send_parser.add_argument("--body", "-b", required=True, help="Email body text")
    send_parser.add_argument("--html", action="store_true", help="Send as HTML email")
    send_parser.add_argument("--smtp-server", help="SMTP server (default: same as IMAP server)")
    send_parser.add_argument("--smtp-port", type=int, default=465, help="SMTP port (default: 465)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Get credentials from args or env
    server = args.server or os.environ.get("IMAP_SERVER")
    email_addr = args.email or os.environ.get("IMAP_EMAIL")
    password = args.password or os.environ.get("IMAP_PASSWORD")
    
    if not all([server, email_addr, password]):
        print("ERROR: Missing credentials. Provide via --server/--email/--password or IMAP_SERVER/IMAP_EMAIL/IMAP_PASSWORD env vars.", file=sys.stderr)
        sys.exit(1)
    
    # Connect
    checker = IMAPChecker(server, email_addr, password, args.folder)
    if not checker.connect():
        sys.exit(1)
    
    try:
        if args.command == "list-folders":
            folders = checker.list_folders()
            print(f"Found {len(folders)} folders:\n")
            for folder in folders:
                print(f"  {folder}")
        
        elif args.command == "unread":
            if not checker.select_folder(args.folder):
                print(f"ERROR: Could not select folder '{args.folder}'", file=sys.stderr)
                sys.exit(1)
            emails = checker.get_unread(args.limit)
            if not emails:
                print("No unread emails found.")
            else:
                print(f"Found {len(emails)} unread email(s):\n")
                for e in emails:
                    print(f"[{e['uid']}] {e['date']}")
                    print(f"    From: {e['from']}")
                    print(f"    Subject: {e['subject']}")
                    print()
        
        elif args.command == "recent":
            if not checker.select_folder(args.folder):
                print(f"ERROR: Could not select folder '{args.folder}'", file=sys.stderr)
                sys.exit(1)
            emails = checker.get_recent(args.limit)
            if not emails:
                print("No emails found.")
            else:
                print(f"Recent {len(emails)} email(s):\n")
                for e in emails:
                    print(f"[{e['uid']}] {e['date']}")
                    print(f"    From: {e['from']}")
                    print(f"    Subject: {e['subject']}")
                    print()
        
        elif args.command == "search":
            if not checker.select_folder(args.folder):
                print(f"ERROR: Could not select folder '{args.folder}'", file=sys.stderr)
                sys.exit(1)
            emails = checker.search_emails(args.query, args.limit)
            if not emails:
                print("No emails found matching query.")
            else:
                print(f"Found {len(emails)} email(s):\n")
                for e in emails:
                    print(f"[{e['uid']}] {e['date']}")
                    print(f"    From: {e['from']}")
                    print(f"    Subject: {e['subject']}")
                    print()
        
        elif args.command == "read":
            if not checker.select_folder(args.folder):
                print(f"ERROR: Could not select folder '{args.folder}'", file=sys.stderr)
                sys.exit(1)
            email_data = checker.read_email(args.uid)
            if not email_data:
                print(f"ERROR: Email with UID {args.uid} not found.", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"[{email_data['uid']}] {email_data['date']}")
                print(f"From: {email_data['from']}")
                print(f"To: {email_data['to']}")
                print(f"Subject: {email_data['subject']}")
                print("\n" + "="*50 + "\n")
                print(email_data.get('body', '(No text body)'))
        
        elif args.command == "delete":
            if not checker.select_folder(args.folder):
                print(f"ERROR: Could not select folder '{args.folder}'", file=sys.stderr)
                sys.exit(1)
            
            if args.uid:
                # Delete single email by UID
                success = checker.delete_email(args.uid)
                if success:
                    print(f"✅ Deleted email UID {args.uid}")
                else:
                    print(f"❌ Failed to delete email UID {args.uid}", file=sys.stderr)
                    sys.exit(1)
            
            elif args.from_sender:
                # Delete all emails from sender
                result = checker.delete_from_sender(args.from_sender, args.limit, args.dry_run)
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}", file=sys.stderr)
                    sys.exit(1)
                
                if args.dry_run:
                    print(f"📧 Would delete {result['would_delete']} email(s) from '{args.from_sender}':\n")
                    for e in result.get("emails", []):
                        print(f"  [{e['uid']}] {e['date']}")
                        print(f"      Subject: {e['subject']}")
                else:
                    print(f"✅ Deleted {result['deleted']} email(s) from '{args.from_sender}'")
            
            else:
                print("ERROR: Specify --uid or --from-sender", file=sys.stderr)
                sys.exit(1)
        
        elif args.command == "mark-read":
            if not checker.select_folder(args.folder):
                print(f"ERROR: Could not select folder '{args.folder}'", file=sys.stderr)
                sys.exit(1)
            success = checker.mark_read(args.uid)
            if success:
                print(f"✅ Marked email UID {args.uid} as read")
            else:
                print(f"❌ Failed to mark email UID {args.uid} as read", file=sys.stderr)
                sys.exit(1)
        
        elif args.command == "send":
            smtp_server = args.smtp_server or server
            smtp_port = args.smtp_port
            
            sender = SMTPSender(smtp_server, email_addr, password, smtp_port)
            success = sender.send(args.to, args.subject, args.body, args.html)
            
            if success:
                print(f"✅ Email sent to {args.to}")
            else:
                print(f"❌ Failed to send email", file=sys.stderr)
                sys.exit(1)
    
    finally:
        checker.disconnect()


if __name__ == "__main__":
    main()