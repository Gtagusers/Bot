import logging
import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random

logging.basicConfig(level=logging.DEBUG)

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("token")

# Create intents and set everything to True
intents = discord.Intents.default()
intents.messages = True        # Allows the bot to receive message events
intents.guilds = True          # Allows the bot to receive guild-related events (e.g., joining, leaving, etc.)
intents.members = True         # Allows the bot to receive member-related events (e.g., member join, leave, etc.)
intents.bans = True            # Allows the bot to receive ban-related events
intents.emojis = True          # Allows the bot to receive emoji-related events
intents.integrations = True    # Allows the bot to receive integration-related events
intents.webhooks = True        # Allows the bot to receive webhook-related events
intents.invites = True         # Allows the bot to receive invite-related events
intents.voice_states = True    # Allows the bot to receive voice state-related events
intents.presences = True       # Allows the bot to receive presence (status) update events
intents.reactions = True       # Allows the bot to receive reactions to messages
intents.typing = True          # Allows the bot to receive typing-related events
intents.guild_messages = True  # Allows the bot to receive guild message events (in addition to DM messages)
intents.message_content = True # Allows the bot to access the content of messages (needed for content-based interactions)
intents.guild_emojis = True    # Allows the bot to receive guild emoji events
intents.guild_integrations = True # Allows the bot to access guild integrations (like webhooks and bots in guilds)
intents.direct_messages = True # Allows the bot to receive direct messages
intents.direct_message_reactions = True # Allows the bot to receive reactions in direct messages
intents.direct_message_typing = True # Allows the bot to receive typing events in DMs
intents.guild_voice_states = True # Allows the bot to listen to voice state changes in guilds

# Now, to apply all intents, we set them to true
intents.all()  # Enabling all intents at once

# Create bot instance with intents
bot = commands.Bot(command_prefix="+", case_sensitive=False, intents=intents)

# Remove default help command
bot.remove_command("help")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced!")

# Ping command to test latency and show an emoji
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)  # Latency in milliseconds
    pong_emoji = "🏓"  # You can use any emoji you like
    await interaction.response.send_message(f"{pong_emoji} Pong! Latency is {latency}ms")

# Slash giveaway command
@bot.tree.command(name="gw")
@app_commands.describe(
    winners_count="Number of winners",
    duration="Duration in seconds",
    msg="Giveaway message",
    winner_ids="User IDs of the winners"
)
async def gw(
    interaction: discord.Interaction,
    winners_count: int,
    duration: int,
    msg: str,
    winner_ids: str
):
    # Get the host of the giveaway
    host = interaction.user

    # Split the winner IDs by spaces and validate them
    winner_ids_list = winner_ids.split()
    winners = []
    for winner_id in winner_ids_list:
        try:
            winner = await bot.fetch_user(int(winner_id))
            winners.append(winner)
        except discord.NotFound:
            await interaction.response.send_message(f"User with ID {winner_id} not found.", ephemeral=True)
            return

    # Create the giveaway embed
    embed = discord.Embed(
        title=f"Giveaway: {msg}",
        description=f"Hosted by: {host.mention}\nNumber of Winners: {winners_count}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Winners", value=", ".join([winner.mention for winner in winners]), inline=False)
    
    # Calculate giveaway end time
    end_time = datetime.utcnow() + timedelta(seconds=duration)
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    embed.add_field(name="Ends At", value=end_time_str, inline=False)

    # Send the giveaway message
    giveaway_message = await interaction.channel.send(embed=embed)

    # Countdown task (live update)
    async def countdown():
        while True:
            # Calculate remaining time
            now = datetime.utcnow()
            remaining_time = end_time - now
            if remaining_time.total_seconds() <= 0:
                break
            days, remainder = divmod(remaining_time.seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left = f"{days}d {hours}h {minutes}m {seconds}s"
            
            # Update embed with time left
            embed.set_field_at(2, name="Time Remaining", value=time_left, inline=False)
            await giveaway_message.edit(embed=embed)
            await asyncio.sleep(1)

        # When the giveaway ends
        embed.set_field_at(2, name="Time Remaining", value="Giveaway ended", inline=False)
        await giveaway_message.edit(embed=embed)

        # Randomly select winners
        winner_mentions = random.sample([winner.mention for winner in winners], winners_count)
        embed.add_field(name="Winner(s)", value=", ".join(winner_mentions), inline=False)
        await giveaway_message.edit(embed=embed)

    # Start the countdown task
    bot.loop.create_task(countdown())

    # Acknowledge the command execution
    await interaction.response.send_message(f"Giveaway started for {msg}! Winners will be chosen in {duration} seconds.")

bot.run(TOKEN)
