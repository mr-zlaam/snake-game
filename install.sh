#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
GAME_NAME="snake-game"
INSTALL_DIR="/usr/local/share/$GAME_NAME"
BIN_DIR="/usr/local/bin"
GAME_FILE="snake_game.py"
CONFIG_DIR="$HOME/.config/$GAME_NAME"
HIGH_SCORE_FILE="$CONFIG_DIR/high_score.txt"
PYTHON_URL="https://www.python.org/downloads/"

# Function to check Python version
check_python() {
    if ! command -v python3 &>/dev/null; then
        echo -e "${RED}Error: Python 3 is not installed.${NC}"
        echo -e "Please install Python 3 from ${YELLOW}$PYTHON_URL${NC}"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$(printf '%s\n' "3.6" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.6" ]]; then
        echo -e "${RED}Error: Python 3.6 or higher is required. Found Python $PYTHON_VERSION${NC}"
        echo -e "Please upgrade Python from ${YELLOW}$PYTHON_URL${NC}"
        exit 1
    fi
}

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run this script with sudo: ${YELLOW}sudo ./install.sh${NC}"
    exit 1
fi

# Check Python before proceeding
check_python

# Create installation directory
echo -e "${GREEN}Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

# Copy the game file
echo -e "${GREEN}Installing $GAME_NAME to $INSTALL_DIR...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/$GAME_FILE" ]; then
    cp "$SCRIPT_DIR/$GAME_FILE" "$INSTALL_DIR/"
else
    echo -e "${RED}Error: Could not find $GAME_FILE in $SCRIPT_DIR${NC}"
    exit 1
fi

# Set permissions
chmod 755 "$INSTALL_DIR/$GAME_FILE"

# Create config directory and high score file if they don't exist
echo -e "${GREEN}Setting up configuration directory...${NC}"
mkdir -p "$CONFIG_DIR"
chown "$SUDO_USER:$SUDO_USER" "$CONFIG_DIR"
if [ ! -f "$HIGH_SCORE_FILE" ]; then
    echo "0" > "$HIGH_SCORE_FILE"
    chown "$SUDO_USER:$SUDO_USER" "$HIGH_SCORE_FILE"
fi

# Create wrapper script instead of symlink
echo -e "${GREEN}Creating launcher in $BIN_DIR...${NC}"
cat > "$BIN_DIR/$GAME_NAME" <<EOF
#!/bin/sh
exec python3 "$INSTALL_DIR/$GAME_FILE" "\$@"
EOF

chmod 755 "$BIN_DIR/$GAME_NAME"

# Verify installation
echo -e "${GREEN}Verifying installation...${NC}"
if [ -f "$BIN_DIR/$GAME_NAME" ] && [ -f "$INSTALL_DIR/$GAME_FILE" ]; then
    echo -e "${GREEN}Installation successful!${NC}"
else
    echo -e "${RED}Installation failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "You can now run the game with: ${YELLOW}$GAME_NAME${NC}"
echo -e "\nTo uninstall, run:"
echo -e "${YELLOW}sudo rm -rf '$INSTALL_DIR' '$BIN_DIR/$GAME_NAME' && rm -rf '$CONFIG_DIR'${NC}"