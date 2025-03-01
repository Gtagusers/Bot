import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load the token from .env file
load_dotenv()
TOKEN = os.getenv("token")

# Set up intents to allow the bot to read message reactions and member updates
intents = discord.Intents.default()
intents.members = True  # To allow member updates (like reacting to messages)

# Set up the bot with a command prefix and the intents
bot = commands.Bot(command_prefix="+", case_sensitive=False, intents=intents)

# Remove the default help command
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    # Sync the commands (slash commands) with Discord
    await bot.tree.sync()

# Define a /ping slash command
@bot.tree.command(name="ping", description="Ping the bot to get its latency.")
async def ping(interaction: discord.Interaction):
    """Respond to the ping command and display bot's response time."""
    latency = round(bot.latency * 1000)  # Convert latency from seconds to milliseconds
    await interaction.response.send_message(f"Pong! 🏓 | Latency: {latency}ms")

# Giveaway Command (as it was earlier, adapted for slash commands)
@bot.tree.command(name="giveaway", description="Start a giveaway with a pre-selected winner and a duration.")
@app_commands.describe(winner="The winner of the giveaway", duration="Duration in seconds", msg="The prize message")
async def giveaway(interaction: discord.Interaction, winner: discord.Member, duration: int, msg: str):
    """Start a giveaway with a set winner, duration (in seconds), and message (prize)."""
    
    # Delete the user's command message
    await interaction.response.defer()  # Acknowledge the command, prevent timeout

    # Convert the duration from seconds to hours, minutes, and seconds for display
    int_dur = int(duration)
    dur_hrs = int_dur // 3600  # Convert to hours
    dur_mins = (int_dur % 3600) // 60  # Remaining minutes
    dur_secs = int_dur % 60  # Remaining seconds

    # Create an embed message for the giveaway
    giveaway_embed = discord.Embed()
    giveaway_embed.title = "Giveaway!!"
    giveaway_embed.description = f"""
    __{msg}__

    *Make sure to **react** with ⭐ to participate in this giveaway, ends in `{dur_hrs}` hours, `{dur_mins}` minutes, and `{dur_secs}` seconds.*

    ```Before participating, we recommend you check if this giveaway has any requirements before entering.```
    """
    
    # Send the giveaway message
    gw_msg = await interaction.channel.send(embed=giveaway_embed)

    # Add the ⭐ reaction to the giveaway message
    await gw_msg.add_reaction("⭐")

    # Wait for the duration of the giveaway
    await asyncio.sleep(int_dur)

    # Fetch all reactions to the message
    reaction = discord.utils.get(gw_msg.reactions, emoji="⭐")
    users = await reaction.users().flatten()

    # Remove the bot itself from the list of users
    users = [user for user in users if user != bot.user]

    # If there are no participants, send a message saying so
    if len(users) == 0:
        await interaction.followup.send(f"No one participated in the giveaway for `{msg}`.")
        return

    # Select the winner (the pre-selected winner in this case)
    winner_embed = discord.Embed()
    winner_embed.title = "Congratulations!!"
    winner_embed.description = f"<@{winner.id}> won `{msg}`"
    
    # Announce the winner
    await interaction.followup.send(f"Winner: <@{winner.id}>")
    await interaction.followup.send(embed=winner_embed)

# Run the bot with the token from the .env file
bot.run(TOKEN)
