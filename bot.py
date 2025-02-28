import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
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
    print(f"Bot logged in as {bot.user}")

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
    # Send a confirmation that the command was received
    host = interaction.user
    winner_ids_list = winner_ids.split()  # Split winner IDs if they are space-separated
    winners = []

    for winner_id in winner_ids_list:
        try:
            winner = await bot.fetch_user(int(winner_id))
            winners.append(winner)
        except discord.NotFound:
            await interaction.response.send_message(f"User with ID {winner_id} not found.", ephemeral=True)
            return

    # Prepare giveaway embed
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

    # Send the giveaway embed
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

        # Choose winners randomly
        import random
        winners = random.sample([winner.mention for winner in winners], winners_count)
        embed.add_field(name="Winner(s)", value=", ".join(winners), inline=False)
        await giveaway_message.edit(embed=embed)

    # Start the countdown task
    bot.loop.create_task(countdown())

    # Acknowledge command execution
    await interaction.response.send_message(f"Giveaway started for {msg}! Winners will be chosen in {duration} seconds.")

bot.run(TOKEN)
