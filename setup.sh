#!/bin/bash

# Exit on errors
set -e

# Parameters
if [ "$1" == "overwrite" ]; then
    owrite=true
else
    owrite=false
fi

# --- CONFIGURATION ---
USERNAME="wsuser"
SERVICE_SERVICE="wohnungssucher.service"
SERVICE_TIMER="wohnungssucher.timer"
SERVICE_DIR="/etc/systemd/system"
PROGRAM_DIR="/opt/wohnungssucher"

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
    if [ ! -f "$SERVICE_DIR/$SERVICE_FILE" ] || [ "$owrite" = true ]; then
        sudo cp "$SERVICE_FILE" "$SERVICE_DIR/"
    else
        echo "Service file $SERVICE_FILE already exists"
    fi
done

# Copy source files
echo "Copying Source files to $PROGRAM_DIR"
if [ ! -d $PROGRAM_DIR ]; then
    sudo mkdir $PROGRAM_DIR
fi
if [ ! -d "$PROGRAM_DIR/core" ]; then
    sudo mkdir "$PROGRAM_DIR/core"
fi
if [ ! -d "$PROGRAM_DIR/wohnungssucher_platforms" ]; then
    sudo mkdir "$PROGRAM_DIR/wohnungssucher_platforms"
fi

sudo cp -rf "core/." "$PROGRAM_DIR/core"
sudo cp -rf "wohnungssucher_platforms/." "$PROGRAM_DIR/wohnungssucher_platforms"
sudo cp -f "main.py" "$PROGRAM_DIR/"
sudo cp -f "mail_tester.py" "$PROGRAM_DIR/"
sudo cp -f "user_configuration.py" "$PROGRAM_DIR/"

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Setup complete."
