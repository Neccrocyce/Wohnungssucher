#!/bin/bash

# Exit on errors
set -e

# --- CONFIGURATION ---
USERNAME="wsuser"
SERVICE_SERVICE="wohnungssucher.service"
SERVICE_TIMER="wohnungssucher.timer"
SERVICE_DIR="/etc/systemd/system"
PROGRAM_DIR="/usr/bin/wohnungssucher"

# Create user wsuser without home directory
if id "$USERNAME" &>/dev/null; then
    echo "User '$USERNAME' already exists."
else
    echo "Creating user '$USERNAME'"
    sudo useradd --no-create-home --system --shell /usr/sbin/nologin "$USERNAME"
fi

# Copy service files
echo "Copying $SERVICE_SERVICE and $SERVICE_SERVICE_TIMER to $SERVICE_DIR"
for SERVICE_FILE in "$SERVICE_SERVICE" "$SERVICE_TIMER"; do
    sudo cp "$SERVICE_FILE" "$SERVICE_DIR/"
done

# Copy source files
echo "Copying Source files to $PROGRAM_DIR"
sudo cp -r "core/" "$PROGRAM_DIR/core/"
sudo cp -r "wohnungssucher_platforms/" "$PROGRAM_DIR/wohnungssucher_platforms/"
sudo cp "main.py" "$PROGRAM_DIR/"
sudo cp "mail_tester.py" "$PROGRAM_DIR/"
sudo cp "user_configuration.py" "$PROGRAM_DIR/"

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Setup complete."
