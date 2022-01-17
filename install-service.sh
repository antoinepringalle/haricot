#!/bin/bash

# Creates and enables a systemd service running the python app.py script.

# Create the service file
cat << EOF > /etc/systemd/system/haricot-app.service
[Unit]
Description=Haricot App
After=network.target

[Service]
Restart=always
ExecStart=/usr/bin/python3.9 -m flask run --host=0.0.0.0

[Install]
WantedBy=multi-user.target
EOF

# Enables and starts the service
systemctl enable haricot-app.service
systemctl start haricot-app.service