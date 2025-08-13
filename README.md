# Local AI Avatar Video Generator

**Run locally, no audio, 10–25s clips, multi-character.**

## Quickstart

Use one of the provided scripts to start the server:

```bash
# Start as a background daemon (recommended)
./start_daemon.sh [PORT]

# Or start in foreground
./start_server.sh [PORT]

# Or use the original script
./run_direct.sh [PORT]
```

The default port is 8084 if not specified.

## Server Management Scripts

The application includes several utility scripts:

- `start_daemon.sh`: Starts the server as a background process (won't terminate when terminal closes)
- `start_server.sh`: Starts the server in the foreground
- `kill_server.sh`: Utility to kill server processes
  - `./kill_server.sh all`: Kill all server processes
  - `./kill_server.sh 8084`: Kill process on specific port
- `db_migrate.py`: Database management
  - `python db_migrate.py`: Migrate database schema
  - `python db_migrate.py --recreate`: Recreate database from scratch

## Setup Requirements

```bash
sudo apt-get update && sudo apt-get install -y python3-venv python3-dev ffmpeg
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
# Install the right torch for your system (GPU highly recommended)
```

## Creating Characters

You can create a character through the web interface or using the provided script:

```bash
./create_character.py --name "Test Character" --image /path/to/image.jpg --url http://localhost:8084
```

## Features

- Create characters from images with automatic background removal
- Edit character appearance (scale, rotation, brightness, contrast)
- Configure animation settings (movement, breathing, path type)
- Generate videos with AI avatars on custom backgrounds
- Place multiple characters in scenes
- Configure video settings (duration, resolution, FPS)
- View generated videos
- System information
- Help documentation
- Advanced settings

## Usage

1. **Upload a Character**: Enter name, upload image, process with background removal
2. **Select and Edit Characters**: Browse characters, edit appearance and animation
3. **Generate Video**: Select characters, describe scene, configure settings, generate

## Troubleshooting

If you encounter issues:

1. Check server logs in `server.log`
2. Ensure database is properly initialized: `python db_migrate.py --recreate`
3. Verify storage directories have write permissions
4. Kill and restart server: `./kill_server.sh all && ./start_daemon.sh 8084`
