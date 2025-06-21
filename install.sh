#!/bin/bash

# Exit on any error
set -e

# Variables
GAME_NAME="snake-game"
INSTALL_DIR="/usr/local/share/$GAME_NAME"
BIN_DIR="/usr/local/bin"
GAME_FILE="snake_game.py"
CONFIG_DIR="$HOME/.config/$GAME_NAME"
HIGH_SCORE_FILE="$CONFIG_DIR/high_score.txt"

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo: sudo ./install.sh"
  exit 1
fi

# Check for Python
if ! command -v python3 &>/dev/null; then
  echo "Python 3 is required but not installed. Please install it first."
  exit 1
fi

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy the game file (handles both cases whether run from extracted dir or not)
echo "Installing $GAME_NAME to $INSTALL_DIR..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/$GAME_FILE" ]; then
  cp "$SCRIPT_DIR/$GAME_FILE" "$INSTALL_DIR/"
else
  echo "Error: Could not find $GAME_FILE in $SCRIPT_DIR"
  exit 1
fi

# Set permissions
chmod 755 "$INSTALL_DIR/$GAME_FILE"

# Create config directory and high score file if they don't exist
echo "Setting up configuration directory..."
mkdir -p "$CONFIG_DIR"
chown "$SUDO_USER:$SUDO_USER" "$CONFIG_DIR"
if [ ! -f "$HIGH_SCORE_FILE" ]; then
  echo "0" > "$HIGH_SCORE_FILE"
  chown "$SUDO_USER:$SUDO_USER" "$HIGH_SCORE_FILE"
fi

# Create symbolic link
echo "Creating symbolic link in $BIN_DIR..."
ln -sf "$INSTALL_DIR/$GAME_FILE" "$BIN_DIR/$GAME_NAME"
chmod 755 "$BIN_DIR/$GAME_NAME"

echo "Installation complete! You can now run the game with '$GAME_NAME'."
echo "To uninstall, run: sudo rm -rf '$INSTALL_DIR' '$BIN_DIR/$GAME_NAME' && rm -rf '$CONFIG_DIR'"