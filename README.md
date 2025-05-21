 Python Discord bot for FiveM server IP whitelisting management. This bot allows server administrators to manage IP whitelists through Discord commands

# Features

Add/remove IP addresses from whitelist

List all whitelisted IPs

Enable/disable whitelisting

IP validation

Permission system (admin-only commands)

Automatic whitelist file synchronization with FiveM server

# Setup Instructions

Create a new Discord bot application at Discord Developer Portal

Invite the bot to your server with appropriate permissions

Install required Python packages: pip install discord.py python-dotenv

# Deployment Instructions

Install Python 3.8 or higher

Install required packages:

    pip install discord.py python-dotenv

Create the bot files:

bot.py (main bot code)

.env (configuration)

whitelist.json (will be created automatically)

Set up the FiveM server script:

Create a folder in your resources directory named whitelist_bot

Add the Lua script as server.lua

Add ensure whitelist_bot to your server.cfg

Start the bot:

      python bot.py

# Security Features
Role-based access control for commands

IP address validation

Secure token storage in environment variables

Automatic synchronization with FiveM server

File monitoring for changes




