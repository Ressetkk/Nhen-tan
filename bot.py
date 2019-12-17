import discord
from nh import NHentai, HentaiActivity
import json
import sys
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

try:
    with open('settings.json', 'rb') as settings_file:
        settings_json = json.load(settings_file)
        token = settings_json['token']
except FileNotFoundError as file_error:
    print('Settings load error: {}'.format(file_error.strerror))
    sys.exit(file_error.errno)

bot = discord.ext.commands.Bot(command_prefix=discord.ext.commands.when_mentioned, description=r"You wanted this, didn't you?")

# TODO add dynamic cog loading at boot
bot.add_cog(NHentai(bot))

if __name__ == "__main__":
    bot.run(token)