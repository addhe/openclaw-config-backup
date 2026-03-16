# Ansible Usage Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Provisioning](#provisioning)
4. [Deployment](#deployment)
5. [Operations](#operations)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Install Ansible Collections

```bash
cd ansible/
ansible-galaxy collection install google.cloud
ansible-galaxy collection install ansible.builtin
ansible-galaxy collection install community.general
```

### Install Python Dependencies

```bash
pip install google-auth google-auth-httplib2 google-api-python-client requests
```

### Install GCP CLI

```bash
# Ubuntu/Debian
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt update && sudo apt install google-cloud-sdk

# Authenticate
gcloud auth login
gcloud auth application-default login
```

---

## Initial Setup

### 1. Clone Repository

```bash
git clone git@github.com:addhe/openclaw-config-backup.git
cd openclaw-config-backup/ansible
```

### 2. Create Vault Password Files

```bash
# Staging
echo "your-staging-password" > .vault_password_staging
chmod 600 .vault_password_staging

# Production
echo "your-production-password" > .vault_password_production
chmod 600 .vault_password_production
```

### 3. Create Vault Files

```bash
# Staging vault
ansible-vault create inventory/staging/group_vars/vault.yml
```

Fill with:
```yaml
---
vault_gcp_project_id: "your-project-id"
vault_gcp_service_account_email: "ansible@your-project-id.iam.gserviceaccount.com"
vault_gcp_service_account_key: "/path/to/key.json"
vault_telegram_bot_token: "YOUR_BOT_TOKEN"
vault_telegram_allowed_users:
  - "@BroAwn"
vault_gateway_token: "YOUR_GATEWAY_TOKEN"
vault_openai_api_key: "YOUR_OPENAI_API_KEY"
```

### 4. Configure GCP Credentials

```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-project-id"
```

### 5. Verify Setup

```bash
# Test GCP connectivity
ansible localhost -m google.cloud.gcp_compute_instance_info -a "project=your-project-id zone=asia-southeast2-a"

# Test inventory
ansible-inventory -i inventory/staging/gcp_compute.yml --list
```

---

## Provisioning

### Provision Staging VM

```bash
# Basic provision
ansible-playbook -i inventory/staging playbooks/provision/openclaw-vm.yml

# With extra variables
ansible-playbook -i inventory/staging playbooks/provision/openclaw-vm.yml \
  -e "gcp_machine_type_spot=e2-standard-2" \
  -e "gcp_disk_size_gb=50"

# Dry run
ansible-playbook -i inventory/staging playbooks/provision/openclaw-vm.yml --check
```

### Provision Production VM

```bash
# Using production config
ansible-playbook -i inventory/production playbooks/provision/openclaw-vm.yml
```

### Expected Output

```
PLAY [Provision OpenClaw VM] **************************************************

TASK [Display environment] ****************************************************
ok: [localhost] => {
    "msg": "Provisioning for environment: staging"
}

...

TASK [Display created instance] ***********************************************
ok: [localhost] => {
    "msg": [
        "Instance created: ocl-openclaw-stg-20260304220000-1234",
        "External IP: 34.101.xxx.xxx",
        "Internal IP: 10.20.0.2",
        "Status: RUNNING"
    ]
}

PLAY RECAP ********************************************************************
localhost                  : ok=25   changed=12   unreachable=0    failed=0
```

---

## Deployment

### Full Deployment (Recommended)

```bash
# Staging
ansible-playbook -i inventory/staging playbooks/site.yml

# Production
ansible-playbook -i inventory/production playbooks/site.yml
```

### Step-by-Step Deployment

```bash
# 1. Apply base role (security, packages, etc.)
ansible-playbook -i inventory/staging playbooks/deploy/base.yml

# 2. Deploy OpenClaw
ansible-playbook -i inventory/staging playbooks/deploy/openclaw.yml
```

### Deploy Specific Components

```bash
# Only OpenClaw prerequisites
ansible-playbook -i inventory/staging playbooks/deploy/openclaw.yml --tags prereq

# Only OpenClaw installation
ansible-playbook -i inventory/staging playbooks/deploy/openclaw.yml --tags install

# Only OpenClaw configuration
ansible-playbook -i inventory/staging playbooks/deploy/openclaw.yml --tags config
```

---

## Operations

### List All Instances

```bash
# Using dynamic inventory
ansible-inventory -i inventory/staging/gcp_compute.yml --list | jq '._meta.hostvars | keys'

# Using gcloud
gcloud compute instances list --filter="labels.environment=staging"
```

### Ping All Instances

```bash
# Staging
ansible -i inventory/staging/gcp_compute.yml all -m ping

# Production
ansible -i inventory/production/gcp_compute.yml all -m ping
```

### Gather Facts

```bash
ansible -i inventory/staging/gcp_compute.yml all -m setup
```

### Run Ad-hoc Commands

```bash
# Check uptime
ansible -i inventory/staging/gcp_compute.yml all -a "uptime"

# Check disk space
ansible -i inventory/staging/gcp_compute.yml all -a "df -h"

# Check memory
ansible -i inventory/staging/gcp_compute.yml all -a "free -m"
```

### Update Packages

```bash
ansible -i inventory/staging/gcp_compute.yml all -b -m apt -a "update_cache=yes upgrade=dist"
```

### Restart Service

```bash
ansible -i inventory/staging/gcp_compute.yml all -b -m systemd -a "name=openclaw state=restarted"
```

---

## Troubleshooting

### Debug Mode

```bash
# Verbose output
ansible-playbook playbooks/site.yml -vvv

# Debug task
ansible-playbook playbooks/site.yml --start-at-task="Task Name"
```

### Check Syntax

```bash
ansible-playbook playbooks/site.yml --syntax-check
```

### List Tasks

```bash
ansible-playbook playbooks/site.yml --list-tasks
```

### List Tags

```bash
ansible-playbook playbooks/site.yml --list-tags
```

### Common Errors

#### GCP Authentication Error

```
Error: google.auth.exceptions.DefaultCredentialsError
```

**Solution:**
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

#### Vault Decryption Error

```
Error: Attempting to decrypt but no vault secrets found
```

**Solution:**
```bash
# Check vault password file exists
ls -la .vault_password_staging

# Check vault file is encrypted
head -1 inventory/staging/group_vars/vault.yml
# Should show: $ANSIBLE_VAULT;1.1;AES256
```

#### Dynamic Inventory Not Working

```
Error: No hosts matched
```

**Solution:**
```bash
# Check GCP credentials
gcloud auth list

# Check project ID
gcloud config get-value project

# Debug inventory
ansible-inventory -i inventory/staging/gcp_compute.yml --list -vvv
```

#### Instance Not Running

```
Error: Wait for instance to be running
```

**Solution:**
```bash
# Check instance status
gcloud compute instances describe INSTANCE_NAME --zone=asia-southeast2-a

# Check instance logs
gcloud compute instances get-serial-port-output INSTANCE_NAME --zone=asia-southeast2-a
```

---

## Quick Reference

### Commands Summary

| Task | Command |
|------|---------|
| Deploy Worker from Snapshot | See [WORKER_DEPLOYMENT.md](WORKER_DEPLOYMENT.md) |
| Provision Staging | `ansible-playbook -i inventory/staging playbooks/provision/openclaw-vm.yml` |
| Provision Production | `ansible-playbook -i inventory/production playbooks/provision/openclaw-vm.yml` |
| Full Deploy Staging | `ansible-playbook -i inventory/staging playbooks/site.yml` |
| Full Deploy Production | `ansible-playbook -i inventory/production playbooks/site.yml` |
| Apply Base Only | `ansible-playbook -i inventory/staging playbooks/deploy/base.yml` |
| Deploy OpenClaw Only | `ansible-playbook -i inventory/staging playbooks/deploy/openclaw.yml` |
| List Instances | `gcloud compute instances list --filter="name:ocl-worker"` |
| SSH to Worker | `gcloud compute ssh ocl-worker-devops-001-stg --zone=asia-southeast2-a` |
| Edit Vault Staging | `ansible-vault edit inventory/staging/group_vars/vault.yml` |
| Edit Vault Production | `ansible-vault edit inventory/production/group_vars/vault.yml` |

### Worker Management

| Task | Command |
|------|---------|
| List Workers | `gcloud compute instances list --filter="name:ocl-worker"` |
| Start Worker | `gcloud compute instances start ocl-worker-devops-001-stg --zone=asia-southeast2-a` |
| Stop Worker | `gcloud compute instances stop ocl-worker-devops-001-stg --zone=asia-southeast2-a` |
| Delete Worker | `gcloud compute instances delete ocl-worker-devops-001-stg --zone=asia-southeast2-a --quiet` |
| Check OpenClaw Status | `gcloud compute ssh WORKER_NAME --zone=asia-southeast2-a --command="sudo systemctl status openclaw"` |
| View Worker Logs | `gcloud compute ssh WORKER_NAME --zone=asia-southeast2-a --command="sudo journalctl -u openclaw -n 50"` |
| Update Bot Token | `gcloud compute ssh WORKER_NAME --command="sudo sed -i 's/OLD_TOKEN/NEW_TOKEN/g' /home/openclaw/.openclaw/openclaw.json && sudo systemctl restart openclaw"` |

---

## Support

- **Documentation:** `docs/` directory
- **Worker Deployment:** [WORKER_DEPLOYMENT.md](WORKER_DEPLOYMENT.md)
- **Issues:** [GitHub Issues](https://github.com/addhe/openclaw-config-backup/issues)
- **Logs:** Check `/var/log/ansible/` on target hosts