import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv("token")

# Create intents object
intents = discord.Intents.default()  # Default intents
intents.messages = True  # Enable message intents (adjust based on your needs)
intents.members = True   # Enable member intents (adjust based on your needs)

# Initialize the bot with intents
bot = commands.Bot(command_prefix="+", case_sensitive=False, intents=intents)

# Remove the default help command
bot.remove_command("help")

# Bot event when it is ready
@bot.event
async def on_ready():
    print("Bot logged in")

# Example command for giveaway
@bot.command()
@commands.has_permissions(administrator=True)
async def gw(ctx, winner: discord.Member, duration, *, msg):
    await ctx.message.delete()
    int_dur = int(duration)
    dur_mins = int_dur / 60
    dur_hrs = dur_mins / 60
    giveaway_embed = discord.Embed()
    giveaway_embed.title = "Giveaway!!"
    giveaway_embed.description = f"""__{msg}__

    *Make sure to **react** with ⭐ to participate in this giveaway, ends in `{dur_hrs}` hours,*

    ```Before participating we recommend you check if this giveaway has any requirements before entering.```
    """
    gw_msg = await ctx.send(embed=giveaway_embed)
    await gw_msg.add_reaction("⭐")
    await asyncio.sleep(int_dur)
    winner_embed = discord.Embed()
    winner_embed.title = "Congratulations!!"
    winner_embed.description = f"<@{winner.id}> won `{msg}`"
    await ctx.send(f"Winner: <@{winner.id}>")
    await ctx.send(embed=winner_embed)

# Run the bot with the token
bot.run(TOKEN)
