from datetime import datetime
from discord import Embed
from discord.ext import commands
from .nhapi import NHApi
import logging
import sys

logger = logging.getLogger('nhentai')
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def get_args(args):
    parsed = {
        'query' : ''
    }
    for elem in args.split():
        if '=' in elem:
            arg = elem.split('=')
            parsed[arg[0]] = arg[1]
        else:
            parsed['query'] += elem + ' '
    return parsed

class NHentai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = NHApi()

    @commands.is_nsfw()
    @commands.command()
    async def get(self, ctx, id : int):
        """
Returns nhentai gallery information from given ID
Usage: get <id>
        """
        response = await self.api.get(id)
        await ctx.send(embed=self._build_embed(response))
        return True
    
    @get.error
    async def get_error(self, ctx, error):
        if isinstance(error, Exception):
            logger.exception(error)
            await ctx.send("{}".format(error))

    @commands.is_nsfw()
    @commands.command()
    async def search(self, ctx, *, query : get_args):
        """
Search nhentai by given query and parameters.
Usage: search <query> [ sort={ 'date' | 'popular' } ]
        """
        # basic check if the caller added a reaction
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in ('◀️','☑️','▶️')

        # handling if sort parameter is not passed
        try:
            sort = query['sort']
        except KeyError:
            sort = 'date'

        # get first response from API and deserialize
        response = await self.api.search(query['query'], sort=sort)
        results = response['result']
        num_pages = response['num_pages']
        page, index = 1, 0
        
        # send first entry
        try:
            entry = await ctx.send(embed=self._build_embed(results[0]))
        except IndexError:
            raise IndexError("No results...")
        while True:
            await entry.add_reaction('◀️')
            await entry.add_reaction('☑️')
            await entry.add_reaction('▶️')

            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)
            # TODO more unified exploring through lists.
            if reaction.emoji == '◀️':
                index -= 1
                try:
                    if index == -1:
                        raise IndexError
                except IndexError:
                    if page == 1:
                        page = num_pages
                    else:
                        page -= 1
                    response = await self.api.search(query['query'], sort=sort, page=page)
                    results = response['result']
                    index = len(results)-1

            if reaction.emoji == '▶️':
                index += 1
                try:
                    results[index]
                except IndexError:
                    if page < num_pages:
                        page += 1
                    else:
                        page = 1
                    response = await self.api.search(query['query'], sort=sort, page=page)
                    results = response['result']
                    index = 0

            if reaction.emoji == '☑️':
                break
            await entry.clear_reactions()
            await entry.edit(content="page {}/{}".format(page, num_pages), embed=self._build_embed(results[index]))
        await entry.clear_reactions()

    @search.error
    async def search_error(self, ctx, error):
        logger.exception(error)
        await ctx.send(error)

    @commands.is_nsfw()
    @commands.command()
    async def random(self, ctx):
        """
Returns random doujinshi from nhentai.
        """
        response = await self.api.random()
        await ctx.send(embed=self._build_embed(response))

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
        logger.debug('_build_embed - parsed tags: {}'.format(tags))
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
                    'value' : ', '.join(['[{0}]({1})'.format(tag['name'], self.api.get_url(tag['url'])) for tag in tags['language']]) if tags['language'] else 'None',
                    'inline' : 'true'
                },
                {
                    'name' : 'Categories',
                    'value' : ', '.join(['[{0}]({1})'.format(tag['name'], self.api.get_url(tag['url'])) for tag in tags['category']]) if tags['category'] else 'None',
                    'inline' : 'true'
                },
                {
                    'name' : 'Tags',
                    'value' : ', '.join([tag['name'] for tag in tags['tag']]) if tags['tag'] else 'None'
                }
            ],
            'footer' : {
                'text' : 'No. {}'.format(response['id'])
            }
        }
        logger.debug('_build_embed - embed payload: {}'.format(data))
        return(Embed.from_dict(data))

def setup(bot):
    bot.add_cog(NHentai(bot))