import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import os
from dotenv import load_dotenv

# Load env (Render will inject env vars automatically)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents (NO privileged intents needed)
intents = discord.Intents.default()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = Bot()

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

# /gen command
@bot.tree.command(name="gen", description="Generate an account")
@app_commands.describe(service="Service name like mcfa, xbox")
async def gen(interaction: discord.Interaction, service: str):
    service = service.lower()
    data = load_accounts()

    if service not in data or not data[service]:
        await interaction.response.send_message(
            "No accounts available for this service.",
            ephemeral=True
        )
        return

    account = random.choice(data[service])
    data[service].remove(account)
    save_accounts(data)

    try:
        await interaction.user.send(
            f"**{service.upper()} Account**\n```{account}```"
        )
        await interaction.response.send_message(
            "Account sent to your DM.",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Please enable DMs from server members.",
            ephemeral=True
        )

# /stock command
@bot.tree.command(name="stock", description="Check account stock")
@app_commands.describe(service="Service name like mcfa, xbox")
async def stock(interaction: discord.Interaction, service: str):
    service = service.lower()
    data = load_accounts()

    if service not in data:
        await interaction.response.send_message(
            "Service not found.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"{service.upper()} stock: {len(data[service])}",
        ephemeral=True
    )

bot.run(TOKEN)
