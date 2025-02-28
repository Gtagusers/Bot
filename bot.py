import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("token")

# Create intents
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

# Create bot instance with intents
bot = commands.Bot(command_prefix="+", case_sensitive=False, intents=intents)

# Remove default help command
bot.remove_command("help")

# Event when the bot is ready
@bot.event
async def on_ready():
    print("Bot logged in")

# Sync slash commands (required for new commands to be available)
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync commands to Discord
    print(f'Logged in as {bot.user}')

# Slash giveaway command
@bot.tree.command(name="gw")
async def gw(interaction: discord.Interaction, winner: discord.Member, duration: int, msg: str):
    # Send a confirmation that the command was received
    await interaction.response.send_message(f"Starting giveaway for {msg} with winner {winner.mention}.")

    # Deleting the interaction message
    await interaction.message.delete()
    
    # Calculate giveaway duration
    dur_m
    
bot.run(TOKEN)
