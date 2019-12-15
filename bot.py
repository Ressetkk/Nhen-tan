import discord
from nh import NHClient, HentaiActivity
import json
import sys

try:
    with open('settings.json', 'rb') as settings_file:
        settings_json = json.load(settings_file)
        token = settings_json['token']
except FileNotFoundError as file_error:
    print('Settings load error: {}'.format(file_error.strerror))
    sys.exit(file_error.errno)

bot = discord.ext.commands.Bot(command_prefix='nh ', description=r"You wanted this, didn't you?")

@bot.event
async def on_connect():
    print("Connected as {} - {}".format(bot.user, bot.description))

bot.add_cog(NHClient(bot))

if __name__ == "__main__":
    bot.run(token)