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

# Giveaway command
@bot.command()
@commands.has_permissions(administrator=True)
async def gw(ctx, winner: discord.Member, duration, *, msg):
    await ctx.message.delete()
    int_dur = int(duration)
    dur_mins = int_dur / 60
    dur_hrs = dur_mins / 60
    
    # Embed for the giveaway
    giveaway_embed = discord.Embed()
    giveaway_embed.title = "Giveaway!!"
    giveaway_embed.description = f"""__{msg}__

    *Make sure to **react** with ⭐ to participate in this giveaway, ends in `{dur_hrs}` hours,*

    ```Before participating we recommend you check if this giveaway has any requirements before entering.```
    """
    
    # Send the giveaway message
    gw_msg = await ctx.send(embed=giveaway_embed)
    await gw_msg.add_reaction("⭐")
    
    # Wait for the duration
    await asyncio.sleep(int_dur)
    
    # Embed for the winner
    winner_embed = discord.Embed()
    winner_embed.title = "Congratulations!!"
    winner_embed.description = f"<@{winner.id}> won `{msg}`"
    
    # Announce the winner
    await ctx.send(f"Winner: <@{winner.id}>")
    await ctx.send(embed=winner_embed)

# Run the bot
bot.run(TOKEN)
