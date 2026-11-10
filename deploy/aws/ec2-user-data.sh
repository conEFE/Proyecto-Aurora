#!/bin/bash
# Script de arranque (user data) para una EC2 con Amazon Linux 2023 (x86_64 o arm64/Graviton).
# Instala Docker y el plugin Compose, agrega 2 GB de swap y prepara /opt/aurora. No contiene secretos.
set -euxo pipefail

dnf update -y
dnf install -y docker git cronie
systemctl enable --now docker crond
usermod -aG docker ec2-user

# Plugin Docker Compose (v2) desde las releases oficiales
arch=$(uname -m)
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${arch}" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 2 GB de swap: una t4g.small tiene 2 GB de RAM
if [ ! -f /swapfile ]; then
  dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
fi

mkdir -p /opt/aurora
chown ec2-user:ec2-user /opt/aurora
