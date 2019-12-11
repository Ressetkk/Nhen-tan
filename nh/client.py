import requests
from datetime import datetime
from discord import Embed
from discord.ext import commands

class NHClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.THUNBNAIL_API_URL = 'https://t.nhentai.net'
        self.IMAGES_API_URL = 'https://i.nhentai.net'
        self.API_URL = 'https://nhentai.net'
    
    @commands.command()
    async def get(self, ctx, id : int):
        try:
            response = self._get(id)
            await ctx.send(embed=self._buildEmbed(response))
            return True
        except requests.HTTPError as e:
            await ctx.send('nhentai.net returned an error: {0} {1}'.format(e.response.status_code, e.response.reason)) 
        finally:
            return False

    @commands.command()
    async def search(self, ctx, query : str):
        response = requests.get('{0}/api/galleries/search?query={1}'.format(self.API_URL, query))
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            return (error.errno)
        response = response.json()
        await ctx.send("Search is not implemented yet...")
        return (True)

    @commands.command()
    async def random(self, ctx):
        response = requests.get(self.API_URL + '/random')
        id = response.url.replace(self.API_URL, '').split('/')[2]
        await ctx.send(embed=self._buildEmbed(self._get(id)))

    def _get(self, id):
        response = requests.get('{0}/api/gallery/{1}'.format(self.API_URL, id))
        response.raise_for_status()
        return(response.json())

    def _buildEmbed(self, response):
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
            'url' : '{0}/g/{1}'.format(self.API_URL, response['id']),
            'timestamp' : datetime.utcfromtimestamp(response['upload_date']).isoformat(),
            'color' : 15208008,
            'thumbnail' : {
                'url' : '{0}/galleries/{1}/cover.jpg'.format(self.THUNBNAIL_API_URL, response['media_id']),
                'width' : 300 
            },
            'author' : {
                'url' : '{0}{1}'.format(self.API_URL, tags['artist'][0]['url']) if tags['artist'] else '',
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
                    'value' : ', '.join(['[{0}]({1})'.format(tag['name'], self.API_URL + tag['url']) for tag in tags['language']]),
                    'inline' : 'true'
                },
                {
                    'name' : 'Categories',
                    'value' : ', '.join(['[{0}]({1})'.format(tag['name'], self.API_URL + tag['url']) for tag in tags['category']]),
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