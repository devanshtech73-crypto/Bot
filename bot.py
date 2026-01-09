import discord
from discord.ext import commands
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # Required for creating permissioned channels

bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

ACCOUNTS_FILE = "accounts.json"
CATEGORY_NAME = "Generated Accounts"  # Category to store private channels

# ----------------------
# Helper functions
# ----------------------
def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump({}, f)
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_admin(ctx):
    return ctx.author.guild_permissions.manage_guild or ctx.author.guild_permissions.administrator

async def get_or_create_private_channel(ctx):
    guild = ctx.guild
    # Check for category
    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
    if category is None:
        category = await guild.create_category(CATEGORY_NAME)
    
    # Check if user channel exists
    channel_name = f"{ctx.author.name}-{ctx.author.discriminator}"
    channel = discord.utils.get(category.channels, name=channel_name)
    if channel is None:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        # Allow mods/admins to read
        for member in guild.members:
            if member.guild_permissions.manage_guild or member.guild_permissions.administrator:
                overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    return channel

# ----------------------
# Events
# ----------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ----------------------
# User commands
# ----------------------
@bot.command()
async def gen(ctx, service: str):
    """Generate an account and post in private channel"""
    service = service.lower()
    data = load_accounts()

    if service not in data or not data[service]:
        await ctx.send(f"No accounts available for **{service}**.", delete_after=10)
        return

    account = random.choice(data[service])
    channel = await get_or_create_private_channel(ctx)

    # Post account in private channel
    await channel.send(f"**{service.upper()} Account:**\n```{account}```")
    
    # Remove account after posting
    data[service].remove(account)
    save_accounts(data)

    await ctx.send(f"✅ Account posted in your private channel: {channel.mention}", delete_after=15)

@bot.command()
async def stock(ctx, service: str = None):
    """Check stock of accounts"""
    data = load_accounts()
    if service:
        service = service.lower()
        if service not in data:
            await ctx.send(f"Service `{service}` not found.", delete_after=10)
            return
        await ctx.send(f"**{service.upper()} Stock:** {len(data[service])}", delete_after=10)
    else:
        msg = "**Account Stock:**\n"
        for s, accounts in data.items():
            msg += f"{s.upper()}: {len(accounts)}\n"
        await ctx.send(msg, delete_after=20)

@bot.command()
async def help(ctx):
    """Show help message"""
    msg = """
**Blazy GEN Bot Commands**
**User Commands:**
- `-gen <service>` → Generate an account (posted in your private channel)
- `-stock [service]` → Check stock for a service or all
- `-help` → Show this help message

**Admin / Moderator Commands (Require Manage Server permission):**
- `-add <service> <account>` → Add an account
- `-remove <service> <account>` → Remove an account
- `-reset <service>` → Remove all accounts from a service
"""
    await ctx.send(msg, delete_after=60)

# ----------------------
# Admin / Moderator commands
# ----------------------
@bot.command()
async def add(ctx, service: str, *, account: str):
    """Add an account (Admin only)"""
    if not is_admin(ctx):
        await ctx.send("❌ You do not have permission.", delete_after=10)
        return

    data = load_accounts()
    service = service.lower()
    if service not in data:
        data[service] = []
    data[service].append(account)
    save_accounts(data)
    await ctx.send(f"✅ Account added to **{service}**.", delete_after=10)

@bot.command()
async def remove(ctx, service: str, *, account: str):
    """Remove an account (Admin only)"""
    if not is_admin(ctx):
        await ctx.send("❌ You do not have permission.", delete_after=10)
        return

    data = load_accounts()
    service = service.lower()
    if service in data and account in data[service]:
        data[service].remove(account)
        save_accounts(data)
        await ctx.send(f"✅ Account removed from **{service}**.", delete_after=10)
    else:
        await ctx.send("❌ Account not found.", delete_after=10)

@bot.command()
async def reset(ctx, service: str):
    """Reset all accounts for a service (Admin only)"""
    if not is_admin(ctx):
        await ctx.send("❌ You do not have permission.", delete_after=10)
        return

    data = load_accounts()
    service = service.lower()
    if service in data:
        data[service] = []
        save_accounts(data)
        await ctx.send(f"✅ All accounts removed from **{service}**.", delete_after=10)
    else:
        await ctx.send("❌ Service not found.", delete_after=10)

# ----------------------
# Run bot
# ----------------------
bot.run(TOKEN)
