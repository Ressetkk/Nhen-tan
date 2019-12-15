import discord
from .nhapi import NHApi

class HentaiActivity(discord.Activity):
    def __init__(self, id : int = None):
        self.api = NHApi()
        self.id = id
        self.type = discord.ActivityType.playing
        self.state = "Lewding"
        self.update_hentai()
    
    def update_hentai(self):
        hentai = self.api.get(self.id)
        self.name = hentai['id']