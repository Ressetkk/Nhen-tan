import discord
from nh import NHClient
import json

client = discord.ext.commands.Bot(command_prefix='nh ', description='You wanted this, didn\'t you?')
client.add_cog(NHClient(client))

if __name__ == "__main__":
    client.run()