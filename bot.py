import discord
from nh import NHClient
import json
import sys

try:
    with open('settings.json', 'rb') as settings_file:
        settings_json = json.load(settings_file)
        token = settings_json['token']
except FileNotFoundError as file_error:
    print('Settings load error: {}'.format(file_error.strerror))
    sys.exit(file_error.errno)

client = discord.ext.commands.Bot(command_prefix='nh ', description='You wanted this, didn\'t you?')

@client.event
async def on_connect():
    print("Connected as " + client.user.name)

@client.event
async def on_ready():
    # TODO write proper presence for daily doujin
    await client.change_presence()
client.add_cog(NHClient(client))

if __name__ == "__main__":
    try:
        client.run(token)
    except KeyboardInterrupt:
        print("Discord client is closing...")
        client.close()