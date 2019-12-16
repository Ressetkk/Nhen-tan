from datetime import datetime
from discord import Embed
from discord.ext import commands
from .nhapi import NHApi
import argparse

def get_args(args):
    print(args)
    return

class NHentai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = NHApi()
    
    @commands.command()
    async def get(self, ctx, id : int):
        """
Returns nhentai gallery information from given ID
Example: nh get 177013
        """
        response = self.api.get(id)
        await ctx.send(embed=self._build_embed(response))
        return True
    
    @get.error
    async def get_error(self, ctx, error):
        if isinstance(error, Exception):
            await ctx.send("{}".format(error))

    @commands.command()
    async def search(self, ctx, *, query : str):
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in ('◀️','☑️','▶️')
        results = self.api.search("vanilla")['result']
        entry = await ctx.send(embed=self._build_embed(results[0]))
        while True:
            await entry.add_reaction('◀️')
            await entry.add_reaction('☑️')
            await entry.add_reaction('▶️')
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)
            
            if reaction.emoji == '◀️':
                await entry.edit(embed=self._build_embed(results[0]))
            if reaction.emoji == '▶️':
                await entry.edit(embed=self._build_embed(results[1]))
            if reaction.emoji == '☑️':
                break
            await entry.clear_reactions()
        await entry.clear_reactions()

    @commands.command()
    async def random(self, ctx):
        await ctx.send(embed=self._build_embed(self.api.random()))

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
    bot.add_cog(NHentai(bot))