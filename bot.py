import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

# Load the token from .env file
load_dotenv()
TOKEN = os.getenv("token")

# Set up the bot with a command prefix
bot = commands.Bot(command_prefix="+", case_sensitive=False)

# Remove the default help command
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

# Giveaway Command
@bot.command()
@commands.has_permissions(administrator=True)
async def gw(ctx, winner: discord.Member, duration: int, *, msg: str):
    """Start a giveaway with a set winner, duration (in seconds), and message (prize)."""
    
    # Delete the user's command message
    await ctx.message.delete()

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
    gw_msg = await ctx.send(embed=giveaway_embed)

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
        await ctx.send(f"No one participated in the giveaway for `{msg}`.")
        return

    # Select the winner (the pre-selected winner in this case)
    winner_embed = discord.Embed()
    winner_embed.title = "Congratulations!!"
    winner_embed.description = f"<@{winner.id}> won `{msg}`"
    
    # Announce the winner
    await ctx.send(f"Winner: <@{winner.id}>")
    await ctx.send(embed=winner_embed)

    # Optionally, you can also DM the winner or log it in a channel if needed.

# Ping Command
@bot.command()
async def ping(ctx):
    """Respond to the ping command."""
    await ctx.send("Pong! 🏓")

# Run the bot with the token from the .env file
bot.run(TOKEN)
