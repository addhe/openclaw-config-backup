# Phase I: OpenClaw VM Provisioning & Deployment

## 🎯 Objective

Deploy OpenClaw on a VM using Ansible with secrets stored in Ansible Vault.

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Control Node                          │
│  (Laptop/Workstation where Ansible runs)                │
│                                                          │
│  ├── ansible/                                            │
│  │   ├── inventory/                                      │
│  │   ├── playbooks/                                      │
│   │   ├── roles/                                         │
│   │   ├── group_vars/                                    │
│  │   └── vault/                                          │
│  └── secrets/ (Ansible Vault encrypted)                  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ SSH
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Target VM                             │
│                                                          │
│  ├── OpenClaw Gateway                                    │
│  ├── Node.js runtime                                     │
│  ├── Config files (~/.openclaw/)                        │
│  └── Systemd service                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
openclaw-config-backup/
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── all.vault.yml        # Encrypted secrets
│   ├── playbooks/
│   │   ├── provision.yml            # VM setup
│   │   ├── deploy.yml               # Deploy OpenClaw
│   │   └── site.yml                 # Full deployment
│   ├── roles/
│   │   ├── openclaw-prereq/         # Dependencies
│   │   ├── openclaw-install/        # Install OpenClaw
│   │   └── openclaw-config/         # Deploy config
│   ├── files/
│   │   ├── openclaw.json.j2         # Config template
│   │   ├── .env.j2                  # Env template
│   │   └── openclaw.service.j2      # Systemd service
│   └── vault/
│       └── secrets.yml              # Ansible Vault file
└── README.md
```

---

## 🔐 Secrets Management (Ansible Vault)

### Secrets to Store:
- Telegram Bot Token
- Gateway Auth Token
- OpenAI API Key
- Any other API credentials

### Vault File Structure:
```yaml
# vault/secrets.yml (encrypted)
vault_telegram_bot_token: "7748465090:AAEPQiL3K_..."
vault_gateway_token: "d0a6eebd8ae7be572fc832df..."
vault_openai_api_key: "sk-proj-rzi6M1g5Iu..."
```

---

## 🚀 Playbook Flow

### 1. `provision.yml` - VM Setup
- Install Node.js (v22+)
- Install npm, git, curl
- Create openclaw user
- Setup firewall (UFW)
- Configure system limits

### 2. `deploy.yml` - OpenClaw Deployment
- Install OpenClaw via npm
- Deploy configuration files
- Setup systemd service
- Start OpenClaw Gateway

### 3. `site.yml` - Full Deployment
- Import provision.yml
- Import deploy.yml

---

## 📝 Execution Steps

```bash
# 1. Create vault password file (keep secure!)
echo "YOUR_VAULT_PASSWORD" > .vault_password
chmod 600 .vault_password

# 2. Create/edit encrypted vault
ansible-vault create vault/secrets.yml
# or edit existing
ansible-vault edit vault/secrets.yml

# 3. Run provisioning
ansible-playbook -i inventory/hosts.yml playbooks/provision.yml --vault-password-file .vault_password

# 4. Run deployment
ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml --vault-password-file .vault_password

# 5. Or run everything
ansible-playbook -i inventory/hosts.yml playbooks/site.yml --vault-password-file .vault_password
```

---

## 🛡️ Security Best Practices

1. **Never commit `.vault_password` file** - add to .gitignore
2. **Never commit decrypted vault files**
3. **Use SSH key authentication** for VM access
4. **Restrict openclaw user permissions**
5. **Enable firewall, only expose necessary ports**
6. **Rotate secrets regularly**

---

## 📊 Phase I vs Phase II Comparison

| Aspect | Phase I | Phase II |
|--------|---------|----------|
| Platform | VM (Compute Engine) | Kubernetes (GKE) |
| Secrets | Ansible Vault | GCP Secret Manager / Vault |
| Config | File-based | ConfigMaps/Secrets |
| Scaling | Vertical | Horizontal |
| Service | Systemd | Deployment/Service |
| Storage | Local disk | Persistent Volumes |

---

## ✅ Deliverables

- [ ] Ansible directory structure
- [ ] Inventory configuration
- [ ] Ansible Vault with secrets
- [ ] Provision playbook
- [ ] Deploy playbook
- [ ] Config templates (Jinja2)
- [ ] Systemd service template
- [ ] README with usage instructions

---

Ghost infrastructure planning 👻