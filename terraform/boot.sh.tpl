#!/usr/bin/env bash
# This script is ran on server's first boot.
# The goal is to create the environment needed to run the service.
# + Install reverse proxy (Caddy) which will provide TLS.
# + Install Django application.
# + Install Gunicorn (runs django)
#
# Other things to add:
# + ufw/iptables rules.
#

${SECRET}
# Normal system update
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get upgrade

# Install Caddy, pulled from their docs.
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo apt-key add -
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee -a /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy

# Install Caddyfile for project
cat <<EOF > /etc/caddy/Caddyfile
{
    # Global options block. Entirely optional, https is on by default
    # Optional email key for lets encrypt
    email admin@automatedassessmentsystem.com
    # Optional staging lets encrypt for testing. Comment out for production.
    # TODO: Uncomment after DNS A record points to the server IP.
    acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
automatedassessmentsystem.com {
    # proxy any requests for this domain to the local server
    reverse_proxy 127.0.0.1:8000
    # serve static content
    file_server /var/www/static
}

www.automatedassessmentsystem.com {
    # proxy any requests for this domain to the local server
    reverse_proxy 127.0.0.1:8000
    # serve static content
    file_server /var/www/static
}
EOF

# Reload after configuration change.
systemctl reload caddy

# TODO:  Use git to install Django
# TODO:  craft .env file used by gunicorn and django.
# Run
DJANGO_SETTINGS_MODULE=AAS.settings.prod
# TODO:
# FIXME: pass TF vars for db
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py crontab add



# Install Gunicorn
# TODO: FIXME: Just copied and pasted configuration, needs to be proper.
cat <<EOF >  /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target
EOF

cat <<EOF >/etc/systemd/system/gunicorn.service 
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=gunicorn
Group=www-data
# TODO: Expose .env file
EnvironmentFile=
WorkingDirectory=/home/sammy/myproject
ExecStart=/home/sammy/myproject/myprojectenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/sammy/myproject/myproject.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl start gunicorn
systemctl enable gunicorn

# We should be GOOD TO GO!
