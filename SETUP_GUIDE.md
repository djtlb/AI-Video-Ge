# AI Avatar Video Generator - Setup Guide

## Overview

This document provides instructions for setting up and running the AI Avatar Video Generator application.

## Scripts Created

1. **run_direct.sh** - Script to run the server with database initialization
2. **init_db.py** - Script to initialize the database
3. **create_character.py** - Script to create a new character

## Running the Server

Use the following command to run the server:

```bash
./run_direct.sh [PORT]
```

The default port is 8084 if not specified.

## Creating Characters

After the server is running, you can create a character using:

```bash
./create_character.py --name "Test Character" --image /path/to/image.jpg --url http://localhost:8084
```

Or use the web interface by opening http://localhost:8084 in your browser.

## Generating Videos

After creating characters, you can generate videos through the web interface or by using the API.

## API Endpoints

- `/system/info` - Get system information
- `/characters` - Manage characters
- `/generate` - Generate videos
- `/renders` - Access rendered videos

## Troubleshooting

If you encounter issues:
1. Ensure the database is initialized
2. Check for port conflicts
3. Verify all required directories exist in app/storage
