# OpenClaw Ansible Infrastructure

End-to-end provisioning dan deployment untuk OpenClaw di GCP dengan spot instances.

## Quick Links

- [README.md](docs/README.md) - Documentation overview
- [NAMING_CONVENTION.md](docs/NAMING_CONVENTION.md) - Naming standards
- [USAGE.md](docs/USAGE.md) - How to use playbooks

## Quick Start

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