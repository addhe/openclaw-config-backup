# OpenClaw Ansible Infrastructure

End-to-end provisioning dan deployment untuk OpenClaw di GCP dengan spot instances.

## Quick Links

- [README.md](docs/README.md) - Documentation overview
- [NAMING_CONVENTION.md](docs/NAMING_CONVENTION.md) - Naming standards
- [USAGE.md](docs/USAGE.md) - How to use playbooks

## VM Naming Convention

```
ocl-worker-{role}-{numeric-id}-{env}
```

| Component | Description | Example |
|-----------|-------------|---------|
| `role` | Worker role | `devops`, `backend`, `infosec` |
| `numeric-id` | 3-digit ID | `001`, `002`, `003` |
| `env` | Environment | `stg`, `prd` |

**Examples:**
- `ocl-worker-devops-001-stg` - DevOps worker (staging)
- `ocl-worker-backend-002-stg` - Backend worker (staging)
- `ocl-worker-infosec-001-prd` - InfoSec worker (production)

## Quick Start

```bash
# Install requirements
ansible-galaxy collection install -r requirements.yml

# Setup vault (staging)
echo "password" > .vault_password_staging
ansible-vault create inventory/staging/group_vars/vault.yml

# Provision VM with specific role
ansible-playbook playbooks/provision/openclaw-vm.yml \
  -e "deploy_env=staging gcp_worker_role=devops gcp_worker_id=001"

# Full deployment
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
│   └── production/       # Production environment
├── playbooks/
│   ├── provision/        # VM provisioning
│   ├── deploy/           # Application deployment
│   └── site.yml          # Full deployment
├── roles/
│   ├── base/             # Base VM standardization
│   ├── gcp-compute/      # GCP provisioning
│   └── openclaw-*/       # OpenClaw roles
└── docs/                 # Documentation
```

## Support

See [USAGE.md](docs/USAGE.md) for detailed instructions.