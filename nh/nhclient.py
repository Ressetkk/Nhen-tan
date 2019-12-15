from datetime import datetime
from discord import Embed
from discord.ext import commands
from .nhapi import NHApi

class NHClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = NHApi()
    
    @commands.command()
    async def get(self, ctx, id : int):
        response = self.api.get(id)
        await ctx.send(embed=self._build_embed(response))
        return True

    @commands.command()
    async def search(self, ctx, query : str):
        self.api.search(query)
        await ctx.send("Search is not implemented yet...")
        return (True)

    @commands.command()
    async def random(self, ctx):
        await ctx.send(embed=self._build_embed(self.api.random()))

    # TODO custom embed model for Hentai
    def _build_embed(self, response):
        tags = {
            'language' : [],
            'tag' : [],
            'artist' : [],
            'category': []
        }
        for tag in response['tags']:
            try:
                tags[tag['type']].append(tag)
            except KeyError:
                continue
        data = {
            'title' : response['title']['english'],
            'description' : response['title']['japanese'],
            'url' : self.api.get_gallery_url(response['id']),
            'timestamp' : datetime.utcfromtimestamp(response['upload_date']).isoformat(),
            'color' : 15208008,
            'thumbnail' : {
                'url' : self.api.get_cover_thumbnail(response['media_id']),
                'width' : 300 
            },
            'author' : {
                'url' : self.api.get_url(tags['artist'][0]['url']) if tags['artist'] else '',
                'name' : tags['artist'][0]['name'] if tags['artist'] else '',
            },
            'fields' : [
                {
                    'name' : 'Pages',
                    'value' : response['num_pages'],
                    'inline' : 'true'
                },
                {
                    'name' : 'Languages',
                    'value' : ', '.join(['[{0}]({1})'.format(tag['name'], self.api.get_url(tag['url'])) for tag in tags['language']]),
                    'inline' : 'true'
                },
                {
                    'name' : 'Categories',
                    'value' : ', '.join(['[{0}]({1})'.format(tag['name'], self.api.get_url(tag['url'])) for tag in tags['category']]),
                    'inline' : 'true'
                },
                {
                    'name' : 'Tags',
                    'value' : ', '.join([tag['name'] for tag in tags['tag']])
                }
            ],
            'footer' : {
                'text' : 'No. {}'.format(response['id'])
            }
        }
        return(Embed.from_dict(data))

def setup(bot):
    bot.add_cog(NHClient(bot))