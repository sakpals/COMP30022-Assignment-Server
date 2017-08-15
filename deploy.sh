#!/bin/sh
#
# Designed to be run on a clean debian jessie or stretch
# Currently installs synapse (matrix homeserver) and caddy (reverse proxy)
#

# Install prereqs
apt-get install --yes software-properties-common apt-transport-https unzip

add-apt-repository https://matrix.org/packages/debian/

wget -qO - https://matrix.org/packages/debian/repo-key.asc | apt-key add -

apt update

apt upgrade

apt install --yes matrix-synapse

# Create homeserver config
/usr/bin/python -B -m synapse.app.homeserver -c homeserver.yaml --generate-config --server-name=itproject.noconroy.net --report-stats=no

sed -i 's/web_client: True/web_client: False/' homeserver.yaml

synctl start

#Download and install caddy
wget https://github.com/mholt/caddy/releases/download/v0.10.6/caddy_v0.10.6_linux_amd64.tar.gz

tar xvf caddy_v0.10.6_linux_amd64.tar.gz

cp caddy /usr/local/bin
chown root:root /usr/local/bin/caddy
chmod 775 /usr/local/bin/caddy

mkdir /etc/caddy
mkdir /etc/ssl/caddy
chmod 0700 /etc/ssl/caddy

# Create 'Caddyfile'
cat << 'EOF' > /etc/caddy/Caddyfile
itproject.noconroy.net {
  log stdout
  errors stderr
  proxy / localhost:8008
}

example.noconroy.net {
  root /var/www/example.noconroy.net
}
EOF
chmod 444 /etc/caddy/Caddyfile

# Make web directories
mkdir -p /var/www/example.noconroy.net

# Copy systemd caddy service
cp init/linux-systemd/caddy.service /etc/systemd/system/
sed -i 's/User=www-data/User=root/' /etc/systemd/system/caddy.service
sed -i 's/Group=www-data/Group=root/' /etc/systemd/system/caddy.service
chown root:root /etc/systemd/system/caddy.service
chmod 644 /etc/systemd/system/caddy.service

# Run caddy
systemctl daemon-reload
systemctl start caddy.service
systemctl enable caddy.service

