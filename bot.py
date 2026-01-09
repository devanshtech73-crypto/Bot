import discord
from discord.ext import commands
import json, random, os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="-", intents=intents)

ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def gen(ctx, service: str):
    service = service.lower()
    data = load_accounts()

    if service not in data or not data[service]:
        await ctx.send("No accounts available.")
        return

    account = random.choice(data[service])
    data[service].remove(account)
    save_accounts(data)

    try:
        await ctx.author.send(f"**{service.upper()} Account:**\n```{account}```")
        await ctx.send("Account sent to DM.")
    except:
        await ctx.send("Enable DMs from server members.")

bot.run(TOKEN)
