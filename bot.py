import discord
from discord.ext import commands
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents (no privileged intents needed)
intents = discord.Intents.default()

# Bot setup with - prefix
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

ACCOUNTS_FILE = "accounts.json"

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
    """Generate an account and send it via DM"""
    service = service.lower()
    data = load_accounts()

    if service not in data or not data[service]:
        await ctx.send(f"No accounts available for **{service}**.", delete_after=10)
        return

    account = random.choice(data[service])

    # Try sending DM first
    try:
        await ctx.author.send(f"**{service.upper()} Account:**\n```{account}```")
    except discord.Forbidden:
        await ctx.send(
            f"❌ I cannot DM you. Enable 'Allow DMs from server members'.",
            delete_after=15
        )
        return
    else:
        # Only remove account if DM succeeds
        data[service].remove(account)
        save_accounts(data)
        await ctx.send(f"✅ Account sent to your DM.", delete_after=10)

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
- `-gen <service>` → Generate an account via DM
- `-stock [service]` → Check stock for a service or all

**Admin / Moderator Commands (Require Manage Server permission):**
- `-add <service> <account>` → Add an account to service
- `-remove <service> <account>` → Remove an account
- `-reset <service>` → Remove all accounts from a service
"""
    await ctx.send(msg, delete_after=60)

# ----------------------
# Admin / Moderator commands
# ----------------------
def is_admin(ctx):
    return ctx.author.guild_permissions.manage_guild or ctx.author.guild_permissions.administrator

@bot.command()
async def add(ctx, service: str, *, account: str):
    """Add an account (Admin only)"""
    if not is_admin(ctx):
        await ctx.send("❌ You do not have permission to use this command.", delete_after=10)
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
        await ctx.send("❌ You do not have permission to use this command.", delete_after=10)
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
        await ctx.send("❌ You do not have permission to use this command.", delete_after=10)
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
