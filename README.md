Here's the updated `installation-guide.md` with GitHub tarball installation instructions and improved organization:

# Snake Game

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A classic terminal-based Snake game with customizable speed levels and persistent high score tracking. Control the snake using Vim-style `hjkl` keys.

## Table of Contents

- [Compatibility](#compatibility)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Controls](#controls)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## Compatibility

- ✅ Linux (all major distributions)
- ✅ macOS
- ❌ Windows (Will never support intentionally)

## Installation

### From GitHub Release

1. Download the latest release tarball:

```bash
wget https://github.com/mr-zlaam/snake-game/releases/download/game/snake-game-v1.0.tar.gz
```

2. Extract and install:

```bash
tar -xzf snake-game-v1.0.tar.gz
cd snake-game-v1.0
sudo ./install.sh
```

### Using install.sh (Recommended)

```bash
# Make the installer executable
chmod +x install.sh

# Run the installer
sudo ./install.sh
```

### Manual Installation

```bash
# Create directories
sudo mkdir -p /usr/local/share/snake-game
mkdir -p ~/.config/snake-game

# Install game files
sudo cp snake_game.py /usr/local/share/snake-game/

# Create launcher
sudo tee /usr/local/bin/snake-game >/dev/null <<EOF
#!/bin/sh
exec python3 /usr/local/share/snake-game/snake_game.py "\$@"
EOF

# Set permissions
sudo chmod 755 /usr/local/bin/snake-game /usr/local/share/snake-game/snake_game.py
```

## How to Play

```bash
snake-game [--help]
```

### Controls

| Key    | Action                  |
| ------ | ----------------------- |
| ↑ or k | Move up                 |
| ↓ or j | Move down               |
| ← or h | Move left               |
| → or l | Move right              |
| Space  | Pause/resume            |
| q      | Quit (when paused)      |
| r      | Restart after game over |
| s      | Start game from menu    |
| l      | Set level (1-9)         |

### Game Features

- 9 difficulty levels (1=slowest, 9=fastest)
- Persistent high score tracking
- Real-time score display
- Terminal-responsive sizing

## Troubleshooting

| Issue                 | Solution                                     |
| --------------------- | -------------------------------------------- |
| "Command not found"   | Run `source ~/.bashrc` or relogin            |
| Game won't start      | Check Python 3.6+ is installed               |
| High score not saving | Check permissions on `~/.config/snake-game/` |

## Uninstallation

```bash
sudo rm -rf /usr/local/share/snake-game /usr/local/bin/snake-game
rm -rf ~/.config/snake-game
```


---
