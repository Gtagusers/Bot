import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Slash commands require syncing with Discord's API
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync commands to make sure Discord knows them
    await bot.tree.sync()

giveaways = {}

class Giveaway:
    def __init__(self, channel, host, duration, num_winners, message_id, name, preselected_winner=None):
        self.channel = channel
        self.host = host
        self.duration = duration
        self.end_time = datetime.now() + timedelta(seconds=duration)
        self.entries = set()
        self.message_id = message_id
        self.selected_winner = preselected_winner
        self.num_winners = num_winners
        self.name = name

    def add_entry(self, user):
        self.entries.add(user)

    def draw_winner(self):
        # If a winner is preselected, use that
        if self.selected_winner:
            self.selected_winner = [self.selected_winner]
        elif self.num_winners == 1:
            self.selected_winner = random.choice(list(self.entries))
        else:
            self.selected_winner = random.sample(list(self.entries), self.num_winners)

    def is_finished(self):
        return datetime.now() >= self.end_time

@bot.tree.command(name="ping", description="Ping the bot and get a pong response")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)  # Convert from seconds to milliseconds
    await interaction.response.send_message(f"Pong! 🏓 Latency: {latency}ms")

@bot.tree.command(name="start_giveaway", description="Start a giveaway with a name, duration, and number of winners")
async def start_giveaway(interaction: discord.Interaction, name: str, duration: int, num_winners: int, host: str, preselected_winner: discord.Member = None):
    """Starts a giveaway with a name, duration, number of winners, and an optional pre-selected winner"""
    embed = discord.Embed(
        title=f"Giveaway: {name}",
        description=f"Hosted by: {host}\nReact with 🎉 to enter!\nNumber of Winners: {num_winners}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Time Remaining", value=str(duration) + " seconds", inline=False)

    message = await interaction.channel.send(embed=embed)
    await message.add_reaction("🎉")

    # Store giveaway data by name
    giveaway = Giveaway(interaction.channel, host, duration, num_winners, message.id, name, preselected_winner)
    giveaways[name] = giveaway

    # Start countdown task
    await countdown(giveaway)

    await interaction.response.send_message(f"Giveaway '{name}' has started!", ephemeral=True)

async def countdown(giveaway):
    """Updates the giveaway message with the time left"""
    while not giveaway.is_finished():
        time_left = giveaway.end_time - datetime.now()
        embed = discord.Embed(
            title=f"Giveaway: {giveaway.name}",
            description=f"Hosted by: {giveaway.host}\nReact with 🎉 to enter!\nNumber of Winners: {giveaway.num_winners}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Time Remaining", value=f"{str(time_left).split('.')[0]}", inline=False)

        # Update the giveaway message with the countdown
        try:
            message = await giveaway.channel.fetch_message(giveaway.message_id)
            await message.edit(embed=embed)
        except discord.NotFound:
            break

        await asyncio.sleep(10)  # Update every 10 seconds

    # Once time is over, draw winner
    giveaway.draw_winner()
    await finish_giveaway(giveaway)

async def finish_giveaway(giveaway):
    """Ends the giveaway and announces the winner(s)"""
    embed = discord.Embed(
        title=f"Giveaway Finished: {giveaway.name}",
        description=f"Hosted by: {giveaway.host}\nThe giveaway has ended.",
        color=discord.Color.green()
    )
    if giveaway.selected_winner:
        if isinstance(giveaway.selected_winner, list):
            winners = "\n".join([winner.mention for winner in giveaway.selected_winner])
        else:
            winners = giveaway.selected_winner.mention
        embed.add_field(name="Winner(s)", value=winners, inline=False)
    else:
        embed.add_field(name="Winner(s)", value="No entries.", inline=False)

    message = await giveaway.channel.fetch_message(giveaway.message_id)
    await message.edit(embed=embed)

@bot.tree.command(name="end_giveaway", description="End a giveaway early by its name")
async def end_giveaway(interaction: discord.Interaction, giveaway_name: str):
    """End a giveaway early and pick the winner"""
    giveaway = giveaways.get(giveaway_name)
    if giveaway:
        giveaway.draw_winner()
        await finish_giveaway(giveaway)
        del giveaways[giveaway_name]  # Remove the giveaway from the list after finishing
        await interaction.response.send_message(f"Giveaway '{giveaway_name}' has been ended early and winner(s) picked.", ephemeral=True)
    else:
        await interaction.response.send_message("Giveaway not found.", ephemeral=True)

@bot.tree.command(name="cancel_giveaway", description="Cancel a giveaway before it ends")
async def cancel_giveaway(interaction: discord.Interaction, giveaway_name: str):
    """Cancel a giveaway entirely using the giveaway's name"""
    if giveaway_name in giveaways:
        del giveaways[giveaway_name]
        await interaction.response.send_message(f"Giveaway '{giveaway_name}' has been canceled.", ephemeral=True)
    else:
        await interaction.response.send_message("Giveaway not found.", ephemeral=True)

@bot.tree.command(name="pick_winner", description="Select a winner manually before the giveaway ends")
async def pick_winner(interaction: discord.Interaction, giveaway_name: str, winner: discord.Member):
    """Select a winner manually before the giveaway ends"""
    giveaway = giveaways.get(giveaway_name)
    if giveaway and not giveaway.is_finished():
        giveaway.selected_winner = winner  # Set the winner manually
        await finish_giveaway(giveaway)
        await interaction.response.send_message(f"Winner for '{giveaway_name}' has been manually selected.", ephemeral=True)
    else:
        await interaction.response.send_message("This giveaway has already ended or does not exist.", ephemeral=True)

# Run the bot with the token from the .env file
bot.run(os.getenv("DISCORD_TOKEN"))
