import discord
from discord.ext import commands
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('BOT_PREFIX', '!')
WHITELIST_FILE = os.getenv('WHITELIST_FILE', 'whitelist.json')
ADMIN_ROLES = json.loads(os.getenv('ADMIN_ROLES', '[]'))

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Whitelist data structure
whitelist = {
    "enabled": False,
    "ips": []
}

# Load whitelist from file
def load_whitelist():
    global whitelist
    try:
        if os.path.exists(WHITELIST_FILE):
            with open(WHITELIST_FILE, 'r') as f:
                whitelist = json.load(f)
            print("Whitelist loaded successfully")
    except Exception as e:
        print(f"Error loading whitelist: {e}")

# Save whitelist to file
def save_whitelist():
    try:
        with open(WHITELIST_FILE, 'w') as f:
            json.dump(whitelist, f, indent=2)
        sync_with_fivem()  # Sync with FiveM server
    except Exception as e:
        print(f"Error saving whitelist: {e}")

# Validate IP address format
def is_valid_ip(ip):
    ipv4_pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    return re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip)

# Check if user has admin permissions
def is_admin(member):
    if member.guild_permissions.administrator:
        return True
    return any(role.id in ADMIN_ROLES for role in member.roles)

# Sync whitelist with FiveM server resources
def sync_with_fivem():
    try:
        # This path should point to your FiveM server resources
        fivem_path = os.getenv('FIVEM_RESOURCES_PATH', '/path/to/fivem/server/resources')
        destination = os.path.join(fivem_path, 'whitelist_bot/whitelist.json')
        
        if os.path.exists(fivem_path):
            with open(destination, 'w') as f:
                json.dump(whitelist, f, indent=2)
            print("Whitelist synchronized with FiveM server")
    except Exception as e:
        print(f"Error syncing with FiveM server: {e}")

# Bot events
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    load_whitelist()
    activity = discord.Activity(
        name=f"IP Whitelisting | {'ON' if whitelist['enabled'] else 'OFF'}",
        type=discord.ActivityType.watching
    )
    await bot.change_presence(activity=activity)

# Bot commands
@bot.command(name='wl-add', help='Add an IP to the whitelist')
@commands.check(lambda ctx: is_admin(ctx.author))
async def add_ip(ctx, ip: str):
    if not is_valid_ip(ip):
        await ctx.send("Invalid IP address format.")
        return
    
    if ip in whitelist['ips']:
        await ctx.send("This IP is already whitelisted.")
        return
    
    whitelist['ips'].append(ip)
    save_whitelist()
    await ctx.send(f"Successfully added {ip} to the whitelist.")

@bot.command(name='wl-remove', help='Remove an IP from the whitelist')
@commands.check(lambda ctx: is_admin(ctx.author))
async def remove_ip(ctx, ip: str):
    if ip not in whitelist['ips']:
        await ctx.send("This IP is not in the whitelist.")
        return
    
    whitelist['ips'].remove(ip)
    save_whitelist()
    await ctx.send(f"Successfully removed {ip} from the whitelist.")

@bot.command(name='wl-list', help='List all whitelisted IPs')
@commands.check(lambda ctx: is_admin(ctx.author))
async def list_ips(ctx):
    if not whitelist['ips']:
        await ctx.send("The whitelist is currently empty.")
        return
    
    embed = discord.Embed(
        title="Whitelisted IPs",
        description="\n".join(whitelist['ips']),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Total: {len(whitelist['ips'])} IPs | Whitelisting is {'ENABLED' if whitelist['enabled'] else 'DISABLED'}")
    await ctx.send(embed=embed)

@bot.command(name='wl-enable', help='Enable IP whitelisting')
@commands.check(lambda ctx: is_admin(ctx.author))
async def enable_whitelist(ctx):
    if whitelist['enabled']:
        await ctx.send("Whitelisting is already enabled.")
        return
    
    whitelist['enabled'] = True
    save_whitelist()
    await bot.change_presence(activity=discord.Activity(
        name="IP Whitelisting | ON",
        type=discord.ActivityType.watching
    ))
    await ctx.send("IP whitelisting has been enabled.")

@bot.command(name='wl-disable', help='Disable IP whitelisting')
@commands.check(lambda ctx: is_admin(ctx.author))
async def disable_whitelist(ctx):
    if not whitelist['enabled']:
        await ctx.send("Whitelisting is already disabled.")
        return
    
    whitelist['enabled'] = False
    save_whitelist()
    await bot.change_presence(activity=discord.Activity(
        name="IP Whitelisting | OFF",
        type=discord.ActivityType.watching
    ))
    await ctx.send("IP whitelisting has been disabled.")

@bot.command(name='wl-help', help='Show help for whitelist commands')
async def whitelist_help(ctx):
    embed = discord.Embed(
        title="IP Whitelist Bot Help",
        description="Commands for managing the FiveM server IP whitelist",
        color=discord.Color.blue()
    )
    embed.add_field(
        name=f"{PREFIX}wl-add <IP>",
        value="Add an IP to the whitelist",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}wl-remove <IP>",
        value="Remove an IP from the whitelist",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}wl-list",
        value="List all whitelisted IPs",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}wl-enable",
        value="Enable IP whitelisting",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}wl-disable",
        value="Disable IP whitelisting",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}wl-help",
        value="Show this help message",
        inline=False
    )
    embed.set_footer(text="Note: All commands require admin privileges")
    await ctx.send(embed=embed)

# Error handling
@add_ip.error
@remove_ip.error
@list_ips.error
@enable_whitelist.error
@disable_whitelist.error
async def whitelist_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide the required arguments. Use !wl-help for more info.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
if __name__ == '__main__':
    bot.run(TOKEN)