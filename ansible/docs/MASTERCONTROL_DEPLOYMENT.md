# IrishEcho MasterControl - Deployment Guide

## Overview

IrishEcho MasterControl adalah control plane bot untuk RandomOps infrastructure. Bot ini **RESTRICTED**:
- **DM ONLY** - Tidak ada akses ke group chat
- **OWNER ONLY** - Hanya Om Awan (@BroAwn) yang bisa akses
- **NO EXCEPTIONS** - Tidak ada pengecualian

## Prerequisites

### 1. Buat Bot Token di Telegram

```bash
# Chat dengan @BotFather di Telegram
/newbot
# Name: IrishEcho MasterControl
# Username: IrishEcho_MasterControl_Bot
# Simpan token yang diberikan
```

### 2. Update Vault dengan Token Baru

```bash
cd /home/addheputra/openclaw-config-backup/ansible

# Decrypt vault
ansible-vault decrypt inventory/mastercontrol/group_vars/vault.yml

# Edit dan tambahkan:
vault_mastercontrol_bot_token: "YOUR_BOT_TOKEN_HERE"
vault_mastercontrol_gateway_token: "YOUR_GATEWAY_TOKEN_HERE"
vault_sensitive_password: "Putra"

# Encrypt kembali
ansible-vault encrypt inventory/mastercontrol/group_vars/vault.yml
```

### 3. Pastikan GCP Service Account

```bash
# Verify service account key exists
ls -la inventory/staging/gcp-sa-key.json

# Test authentication
gcloud auth application-default login
gcloud config set project awanmasterpiece
```

## Deployment

### Option A: Quick Deploy (Rekomendasi)

```bash
cd /home/addheputra/openclaw-config-backup/ansible

# Provision VM dari snapshot yang sudah ada
gcloud compute instances create mastercontrol-001-stg \
  --project=awanmasterpiece \
  --zone=us-central1-b \
  --machine-type=e2-small \
  --provisioning-model=SPOT \
  --source-snapshot=openclaw-mastercontrol-base-v1 \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-ssd \
  --network-interface=network=openclaw-staging-network,subnet=openclaw-staging-subnet \
  --tags=mastercontrol,staging,restricted,dm-only \
  --labels=environment=staging,role=mastercontrol,id=001,managed_by=manual \
  --service-account=awan-master-service-account@awanmasterpiece.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/compute,https://www.googleapis.com/auth/devstorage.read_only

# SSH dan update config
gcloud compute ssh mastercontrol-001-stg --zone=us-central1-b \
  --command="sudo sed -i 's/MASTERCONTROL_BOT_TOKEN/{{ vault_mastercontrol_bot_token }}/g' /home/mastercontrol/.openclaw/openclaw.json && sudo systemctl restart openclaw"
```

### Option B: Full Ansible Deploy

```bash
cd /home/addheputra/openclaw-config-backup/ansible

# Step 1: Provision VM
ansible-playbook playbooks/mastercontrol/provision.yml

# Step 2: Deploy base system
ansible-playbook playbooks/deploy/base.yml \
  -i inventory/mastercontrol/hosts.yml \
  --ask-vault-pass

# Step 3: Deploy MasterControl
ansible-playbook playbooks/mastercontrol/deploy.yml \
  -i inventory/mastercontrol/hosts.yml \
  --ask-vault-pass
```

## Configuration Files

| File | Purpose |
|------|---------|
| `inventory/mastercontrol/group_vars/all.yml` | GCP & network settings |
| `inventory/mastercontrol/group_vars/mastercontrol.yml` | Bot configuration |
| `inventory/mastercontrol/group_vars/vault.yml` | Secrets (encrypted) |
| `roles/mastercontrol-config/files/AGENTS.md` | Workspace rules |
| `roles/mastercontrol-config/files/SOUL.md` | Bot personality |
| `roles/mastercontrol-config/files/IDENTITY.md` | Bot identity |
| `roles/mastercontrol-config/files/USER.md` | Owner info |
| `roles/mastercontrol-config/files/MEMORY.md` | Long-term memory |

## Security Configuration

### DM Only (Strict)
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "strict",
      "groups": {
        "enabled": false
      },
      "allowFrom": ["319535690"],
      "groupPolicy": "deny"
    }
  }
}
```

### Owner Only
```json
{
  "allowFrom": ["319535690"]
}
```

### Gateway Local Only
```json
{
  "gateway": {
    "bind": "127.0.0.1"
  }
}
```

## Post-Deployment Checklist

- [ ] VM running di GCP
- [ ] OpenClaw service aktif (`systemctl status openclaw`)
- [ ] Bot respond di DM dengan @BroAwn
- [ ] Bot **TIDAK** respond di group chat
- [ ] Bot **TIDAK** respond ke user lain
- [ ] Gateway accessible di localhost:8080

## Testing

### Test DM Access (Owner)
```bash
# Di Telegram, DM ke @IrishEcho_MasterControl_Bot
# Harus respond ke @BroAwn (ID: 319535690)
```

### Test Group Deny
```bash
# Di group RandomOps, mention @IrishEcho_MasterControl_Bot
# Harus TIDAK respond (ignore)
```

### Test Non-Owner Deny
```bash
# User lain DM ke @IrishEcho_MasterControl_Bot
# Harus TIDAK respond (ignore)
```

### Test Gateway
```bash
# SSH ke VM
curl http://localhost:8080/status
```

## Troubleshooting

### Bot Tidak Respond ke Owner
```bash
# Check config
cat /home/mastercontrol/.openclaw/openclaw.json | grep allowFrom
# Harus: "allowFrom": ["319535690"]

# Check DM policy
cat /home/mastercontrol/.openclaw/openclaw.json | grep dmPolicy
# Harus: "dmPolicy": "strict"

# Check logs
journalctl -u openclaw -f
```

### Bot Respond ke Group
```bash
# Check group policy
cat /home/mastercontrol/.openclaw/openclaw.json | grep groupPolicy
# Harus: "groupPolicy": "deny"

# Check groups config
cat /home/mastercontrol/.openclaw/openclaw.json | grep -A5 "groups"
# Harus: "enabled": false
```

### Bot Respond ke User Lain
```bash
# Check allowFrom
cat /home/mastercontrol/.openclaw/openclaw.json | grep -A5 "allowFrom"
# Harus hanya: "319535690"

# Restart jika perlu
sudo systemctl restart openclaw
```

## Maintenance

### Update Bot Token
```bash
# Edit vault
ansible-vault edit inventory/mastercontrol/group_vars/vault.yml

# Update token
# Redeploy config
ansible-playbook playbooks/mastercontrol/deploy.yml \
  -i inventory/mastercontrol/hosts.yml \
  --tags config \
  --ask-vault-pass
```

### Rotate Gateway Token
```bash
# Generate new token
openssl rand -hex 24

# Update vault
ansible-vault edit inventory/mastercontrol/group_vars/vault.yml

# Redeploy
ansible-playbook playbooks/mastercontrol/deploy.yml \
  -i inventory/mastercontrol/hosts.yml \
  --tags config \
  --ask-vault-pass
```

## Quick Reference

```bash
# Provision VM
gcloud compute instances create mastercontrol-001-stg \
  --project=awanmasterpiece \
  --zone=us-central1-b \
  --machine-type=e2-small \
  --provisioning-model=SPOT \
  --source-snapshot=openclaw-mastercontrol-base-v1 \
  --boot-disk-size=20GB \
  --tags=mastercontrol,staging

# SSH
gcloud compute ssh mastercontrol-001-stg --zone=us-central1-b

# Check status
sudo systemctl status openclaw
journalctl -u openclaw -f

# Restart
sudo systemctl restart openclaw
```

---

**Bot:** IrishEcho MasterControl (@IrishEcho_MasterControl_Bot)
**Owner:** Om Awan (@BroAwn, ID: 319535690)
**Access:** DM ONLY, OWNER ONLY
**Last Updated:** 2026-03-16