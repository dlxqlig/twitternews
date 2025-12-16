#!/bin/bash

# Stop existing service if running
systemctl stop twitternews.service 2>/dev/null

# Copy service file to systemd directory
cp /root/work/twitternews/twitternews.service /etc/systemd/system/

# Reload systemd daemon
systemctl daemon-reload

# Enable service to start on boot
systemctl enable twitternews.service

# Start the service
systemctl start twitternews.service

# Show status
systemctl status twitternews.service
