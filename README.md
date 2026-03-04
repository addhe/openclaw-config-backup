# OpenClaw Configuration Backup

Repository ini berisi konfigurasi dan file OpenClaw yang aman untuk di-share.

## Struktur

```
openclaw-config-backup/
├── AGENTS.md              # Panduan workspace untuk agent
├── TOOLS.md               # Catatan lokal tools
├── IDENTITY.md            # Identitas bot
├── SOUL.md                 # Karakter dan personality
├── USER.md                 # Info user
├── HEARTBEAT.md            # Konfigurasi heartbeat
├── openclaw.template.json  # Template config (TANPA secrets!)
├── .gitignore              # Exclude semua file sensitif
└── skills/                 # Custom skills
    ├── acfranzen/glance/
    ├── chrome-headless/
    └── imap-email/
```

## Yang TIDAK Di-commit (untuk keamanan)

- `openclaw.json` - berisi bot token, gateway token, dan config sensitif
- `.env` - berisi API keys (OpenAI, dll)
- `MEMORY.md` - memori personal
- `memory/` - file memory harian
- `credentials/` - file kredensial
- `logs/` - log files

## Cara Setup (di mesin baru)

1. Clone repository ini
2. Copy `openclaw.template.json` ke `~/.openclaw/openclaw.json`
3. Isi semua placeholder dengan nilai asli:
   - `YOUR_BOT_TOKEN_HERE` → Telegram bot token
   - `YOUR_GATEWAY_TOKEN_HERE` → Gateway auth token
   - `YOUR_MODEL_HERE` → Model yang digunakan
   - `YOUR_WORKSPACE_PATH` → Path workspace
   - `YOUR_GROUP_ID` → Telegram group ID
   - `YOUR_USERNAME` → Username allowlist
4. Buat file `.env` dengan API keys yang diperlukan
5. Install skills yang diperlukan dari `skills/` folder

## Security Notes

⚠️ **JANGAN PERNAH** commit file berikut:
- Bot tokens
- API keys
- Gateway tokens
- Personal memory files
- Credentials

⚠️ **SELALU** gunakan template untuk config yang akan di-share.

## Skills Included

### Local Skills (full copy)
- `chrome-headless` - Chromium headless automation
- `imap-email` - Email via IMAP
- `acfranzen/glance` - Glance skill

### NPM Skills (symlinks, tidak perlu backup)
- `clawhub`
- `healthcheck`
- `skill-creator`
- `weather`
- `agent-browser`

---

Dibuat oleh RandomBot untuk Om Awan 👻