# Naming Convention Guide

## Overview

Consistent naming convention untuk semua resources, files, dan playbooks.

---

## VM Naming Convention

### Pattern

```
{org_short}-{application}-{environment_short}-{timestamp}-{random}
```

### Examples

| Environment | VM Name |
|-------------|---------|
| Staging | `ocl-openclaw-stg-20260304220000-1234` |
| Production | `ocl-openclaw-prd-20260304220000-5678` |
| Staging (DB) | `ocl-database-stg-20260304220000-9012` |

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| org_short | Organization short name | `ocl` |
| application | Application name | `openclaw`, `database`, `cache` |
| environment_short | Environment abbreviation | `stg`, `prd` |
| timestamp | Creation timestamp | `20260304220000` |
| random | Random number | `1234` |

---

## GCP Label Naming Convention

### Labels (Key-Value)

| Label Key | Description | Example |
|-----------|-------------|---------|
| `environment` | Environment name | `staging`, `production` |
| `application` | Application name | `openclaw` |
| `role` | Server role | `gateway`, `worker`, `database` |
| `managed_by` | Management tool | `ansible` |
| `project` | Project name | `openclaw` |
| `cost_center` | Cost allocation | `staging-infrastructure` |
| `owner` | Team/person responsible | `devops` |
| `created_at` | Creation date | `2026-03-04` |

### Example Labels

```yaml
gcp_instance_labels:
  environment: "staging"
  application: "openclaw"
  role: "gateway"
  managed_by: "ansible"
  project: "openclaw"
  cost_center: "staging-infrastructure"
  owner: "devops"
  created_at: "2026-03-04"
```

---

## GCP Tag Naming Convention

### Network Tags

| Tag Pattern | Description | Example |
|-------------|-------------|---------|
| `{environment}` | Environment tag | `staging`, `production` |
| `{application}` | Application tag | `openclaw` |
| `ansible-managed` | Managed by Ansible | `ansible-managed` |
| `ssh-allowed` | SSH access allowed | `ssh-allowed` |
| `http-allowed` | HTTP access allowed | `http-allowed` |

### Example Tags

```yaml
gcp_instance_tags:
  - "staging"
  - "openclaw"
  - "ansible-managed"
  - "ssh-allowed"
  - "http-allowed"
```

---

## GCP Resource Naming Convention

### Networks

| Resource | Pattern | Example |
|----------|---------|---------|
| VPC Network | `{org_short}-{environment}-network` | `ocl-staging-network` |
| Subnetwork | `{org_short}-{environment}-subnet` | `ocl-staging-subnet` |
| Firewall | `{org_short}-{environment}-allow-{port}` | `ocl-staging-allow-ssh` |

### Service Accounts

| Resource | Pattern | Example |
|----------|---------|---------|
| Service Account | `{service}@{project}.iam.gserviceaccount.com` | `ansible@ocl-project.iam.gserviceaccount.com` |

---

## Ansible Role Naming Convention

### Pattern

```
{provider}-{service} or {function}
```

### Examples

| Role Name | Description |
|-----------|-------------|
| `base` | Base VM configuration |
| `gcp-compute` | GCP compute instances |
| `gcp-network` | GCP networking |
| `openclaw-prereq` | OpenClaw prerequisites |
| `openclaw-install` | OpenClaw installation |
| `openclaw-config` | OpenClaw configuration |

### Role Directory Structure

```
roles/{role_name}/
├── defaults/
│   └── main.yml        # Default variables
├── vars/
│   └── main.yml        # Role variables
├── tasks/
│   └── main.yml        # Main tasks
├── handlers/
│   └── main.yml        # Handlers
├── templates/
│   └── *.j2            # Jinja2 templates
├── files/
│   └── *               # Static files
├── meta/
│   └── main.yml        # Role metadata
└── README.md           # Role documentation
```

---

## Ansible Playbook Naming Convention

### Pattern

```
{action}-{target}.yml
```

### Examples

| Playbook | Purpose |
|----------|---------|
| `site.yml` | Full deployment |
| `openclaw-vm.yml` | Provision OpenClaw VM |
| `base.yml` | Apply base configuration |
| `openclaw.yml` | Deploy OpenClaw |

### Directory Structure

```
playbooks/
├── site.yml                    # Full deployment
├── provision/
│   ├── openclaw-vm.yml         # Provision OpenClaw VM
│   └── database-vm.yml         # Provision Database VM
└── deploy/
    ├── base.yml                # Apply base role
    ├── openclaw.yml            # Deploy OpenClaw
    └── database.yml            # Deploy Database
```

---

## Ansible Variable Naming Convention

### Pattern

```
{role}_{resource}_{attribute}
```

### Examples

| Variable | Description |
|----------|-------------|
| `gcp_project_id` | GCP project ID |
| `gcp_instance_name_prefix` | VM name prefix |
| `gcp_disk_size_gb` | Disk size in GB |
| `openclaw_version` | OpenClaw version |
| `openclaw_user` | OpenClaw user |
| `base_user_name` | Base admin user |
| `base_ssh_port` | SSH port |

### Environment Variables

Prefix with `vault_` for secrets:

| Variable | Description |
|----------|-------------|
| `vault_gcp_project_id` | GCP project ID (secret) |
| `vault_telegram_bot_token` | Telegram bot token (secret) |
| `vault_gateway_token` | Gateway token (secret) |
| `vault_openai_api_key` | OpenAI API key (secret) |

---

## File Naming Convention

### Inventory Files

| File | Purpose |
|------|---------|
| `hosts.yml` | Static inventory |
| `gcp_compute.yml` | GCP dynamic inventory |

### Group Vars

| File | Purpose |
|------|---------|
| `all.yml` | Common to all groups |
| `gcp.yml` | GCP-specific variables |
| `openclaw.yml` | OpenClaw-specific variables |
| `vault.yml` | Encrypted secrets |

### Vault Password Files

| File | Purpose |
|------|---------|
| `.vault_password_staging` | Staging vault password |
| `.vault_password_production` | Production vault password |

---

## Summary Table

| Resource | Pattern | Example |
|----------|---------|---------|
| VM | `{org}-{app}-{env}-{ts}-{rand}` | `ocl-openclaw-stg-20260304-1234` |
| Network | `{org}-{env}-network` | `ocl-staging-network` |
| Firewall | `{org}-{env}-allow-{port}` | `ocl-staging-allow-ssh` |
| Role | `{provider}-{service}` | `gcp-compute` |
| Playbook | `{action}-{target}.yml` | `provision-openclaw-vm.yml` |
| Variable | `{role}_{resource}_{attr}` | `gcp_disk_size_gb` |
| Secret | `vault_{resource}` | `vault_gateway_token` |