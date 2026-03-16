# OpenClaw Ansible Infrastructure

End-to-end provisioning dan deployment untuk OpenClaw di GCP dengan spot instances.

## Quick Links

- [README.md](docs/README.md) - Documentation overview
- [NAMING_CONVENTION.md](docs/NAMING_CONVENTION.md) - Naming standards
- [USAGE.md](docs/USAGE.md) - How to use playbooks
- [WORKER_DEPLOYMENT.md](docs/WORKER_DEPLOYMENT.md) - Deploy workers from base image

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GCP Project                            │
│                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │  DevOps Worker      │  │  Backend Worker     │       │
│  │  ocl-worker-devops  │  │  ocl-worker-backend │       │
│  │  -001-stg           │  │  -001-stg           │       │
│  │  -002-stg           │  │  -002-stg           │       │
│  │  -...               │  │  -...               │       │
│  └─────────────────────┘  └─────────────────────┘       │
│                                                          │
│  Base Images (Snapshots):                                │
│  - openclaw-worker-devops-base-stg-v5                   │
│  - openclaw-worker-backend-base-stg-v5                  │
│                                                          │
│  Features:                                               │
│  - Auto-identity from GCP metadata                       │
│  - Pre-configured OpenClaw 2026.3.2                     │
│  - Ollama Cloud API auth                                 │
│  - Role-specific persona (DevOps/Backend)               │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Deploy Worker from Base Image (Recommended)

```bash
# DevOps Worker
gcloud compute instances create ocl-worker-devops-002-stg \
  --project=awanmasterpiece \
  --zone=asia-southeast2-a \
  --machine-type=e2-medium \
  --provisioning-model=SPOT \
  --source-snapshot=openclaw-worker-devops-base-stg-v5 \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-ssd \
  --network-interface=network=openclaw-staging-network,subnet=openclaw-staging-subnet \
  --tags=staging,openclaw \
  --labels=environment=staging,role=devops,managed_by=manual \
  --service-account=awan-master-service-account@awanmasterpiece.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/compute,https://www.googleapis.com/auth/devstorage.read_only

# Backend Worker
gcloud compute instances create ocl-worker-backend-002-stg \
  --project=awanmasterpiece \
  --zone=asia-southeast2-a \
  --machine-type=e2-medium \
  --provisioning-model=SPOT \
  --source-snapshot=openclaw-worker-backend-base-stg-v5 \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-ssd \
  --network-interface=network=openclaw-staging-network,subnet=openclaw-staging-subnet \
  --tags=staging,openclaw \
  --labels=environment=staging,role=backend,managed_by=manual \
  --service-account=awan-master-service-account@awanmasterpiece.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/compute,https://www.googleapis.com/auth/devstorage.read_only
```

**What happens on first boot:**
1. ✅ Startup script reads instance name from GCP metadata
2. ✅ Parses: `ocl-worker-devops-002-stg` → role=devops, id=002, env=stg
3. ✅ Updates IDENTITY.md with correct identity
4. ✅ Restarts OpenClaw
5. ✅ Worker is ready with correct identity!

### Provision from Scratch (Ansible)

```bash
# Install requirements
ansible-galaxy collection install -r requirements.yml

# Setup vault (staging)
echo "password" > .vault_password_staging
ansible-vault create inventory/staging/group_vars/vault.yml

# Provision staging
ansible-playbook -i inventory/staging playbooks/site.yml
```

## Environment Commands

| Environment | Config File | Vault Password |
|-------------|-------------|----------------|
| Staging | `ansible-staging.cfg` | `.vault_password_staging` |
| Production | `ansible-production.cfg` | `.vault_password_production` |

## Directory Structure

```
ansible/
├── inventory/
│   ├── staging/          # Staging environment
│   │   ├── group_vars/   # Group variables (including vault)
│   │   ├── host_vars/    # Host-specific variables
│   │   └── gcp-sa-key.json
│   └── production/       # Production environment
├── playbooks/
│   ├── provision/        # VM provisioning
│   ├── deploy/           # Application deployment
│   └── site.yml          # Full deployment
├── roles/
│   ├── base/             # Base VM standardization
│   ├── gcp-compute/      # GCP provisioning
│   └── openclaw-*/       # OpenClaw roles
├── files/                # Static files
│   ├── AGENTS.md         # OpenClaw workspace files
│   ├── SOUL.md
│   ├── USER.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   ├── IDENTITY.md       # Template (overwritten by startup script)
│   ├── startup-script.sh # Identity configuration script
│   └── worker-identity.service
├── docs/                 # Documentation
└── README.md
```

## Base Image Management

### Current Base Images (v5)

| Snapshot | Role | Features |
|----------|------|----------|
| `openclaw-worker-devops-base-stg-v5` | DevOps | OpenClaw 2026.3.2, DevOps persona, Ollama auth, identity script |
| `openclaw-worker-backend-base-stg-v5` | Backend | OpenClaw 2026.3.2, Backend persona, Ollama auth, identity script |

### Creating New Base Image

1. Deploy worker from existing base image
2. Make updates (if needed)
3. Stop the instance
4. Create snapshot:
```bash
gcloud compute disks snapshot ocl-worker-devops-001-stg \
  --project=awanmasterpiece \
  --zone=asia-southeast2-a \
  --snapshot-names=openclaw-worker-devops-base-stg-v6 \
  --description="DevOps worker base v6 - updated features"
```

## Bot Token Management

### All Tokens in Vault
**IMPORTANT**: All bot tokens are stored in encrypted vault files. Never commit tokens to git!

```bash
# View/edit vault (requires vault password)
ansible-vault edit inventory/staging/group_vars/vault.yml
```

### Adding New Bot Token
1. Create new bot via [@BotFather](https://t.me/BotFather)
2. Add token to vault:
```bash
ansible-vault edit inventory/staging/group_vars/vault.yml
# Add: vault_telegram_bot_tokens.devops["002"] = "YOUR_NEW_TOKEN"
```
3. Deploy with Ansible:
```bash
ansible-playbook playbooks/deploy/openclaw.yml -i inventory/staging/hosts.yml --ask-vault-pass
```

### Token Rotation Strategy
For production, consider:
1. Use GCP Secret Manager for bot tokens
2. Fetch token at startup from Secret Manager
3. Never embed tokens in base images

## Support

See [USAGE.md](docs/USAGE.md) for detailed instructions.