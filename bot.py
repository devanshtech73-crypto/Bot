import discord
from discord.ext import commands
import os
import json

# -------- Intents --------
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True  # REQUIRED for prefix commands

# -------- Bot Setup --------
bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command("help")  # remove default help

# -------- Load Accounts --------
ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump({}, f)
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

accounts_data = load_accounts()

# -------- Helper: Create Private Channel --------
async def create_private_channel(guild, member):
    category_name = "Generated Accounts"
    category = discord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(category_name)

    channel_name = f"{member.name}-account"
    existing = discord.utils.get(guild.channels, name=channel_name)
    if existing:
        return existing

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    return channel

# -------- Commands --------
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.green())
    embed.add_field(name="-gen <service>", value="Generate an account (sent in private channel)", inline=False)
    embed.add_field(name="-stock <service>", value="Shows remaining accounts for service", inline=False)
    embed.add_field(name="-clearchannel", value="Admin: delete your private channel", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def gen(ctx, service: str = None):
    if not service:
        await ctx.send("❌ Please specify a service. Example: `-gen mcfa`")
        return

    service = service.lower()
    if service not in accounts_data or len(accounts_data[service]) == 0:
        await ctx.send(f"❌ No accounts available for {service}.")
        return

    # Pop account from list
    account = accounts_data[service].pop(0)
    save_accounts(accounts_data)

    # Create private channel
    channel = await create_private_channel(ctx.guild, ctx.author)
    await channel.send(f"✅ Here is your **{service}** account: `{account}`")
    await ctx.send(f"✅ Account sent in your private channel: {channel.mention}")

@bot.command()
async def stock(ctx, service: str = None):
    if not service:
        await ctx.send("❌ Please specify a service. Example: `-stock mcfa`")
        return

    service = service.lower()
    count = len(accounts_data.get(service, []))
    await ctx.send(f"📦 `{service}` remaining accounts: {count}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearchannel(ctx):
    """Delete your private channel (Admin only)"""
    if isinstance(ctx.channel, discord.TextChannel):
        await ctx.channel.delete()

# -------- Error Handling --------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have permission to run this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command. Use `-help` to see commands.")
    else:
        await ctx.send(f"❌ Error: {error}")

# -------- Run Bot --------
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN environment variable is missing! Set it in your host dashboard.")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} | Prefix commands ready: '-'")
    print("✅ Bot is fully operational!")

bot.run(TOKEN)
