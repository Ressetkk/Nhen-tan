import requests

class NHApi(object):
    def __init__(self):
        self.THUNBNAIL_API_URL = 'https://t.nhentai.net'
        self.IMAGES_API_URL = 'https://i.nhentai.net'
        self.API_URL = 'https://nhentai.net'
    
    def get(self, id):
        response = requests.get('{0}/api/gallery/{1}'.format(self.API_URL, id))
        response.raise_for_status()
        return(response.json())
    
    def random(self):
        response = requests.get(self.API_URL + '/random')
        id = response.url.replace(self.API_URL, '').split('/')[2]
        return(self.get(id))

    def search(self, query : str, sort : str = 'date', page : int = 1):
        if sort not in ('date', 'popular'):
            raise ValueError("You can only sort by 'date' and 'popular'")

        response = requests.get('{0}/api/galleries/search?query={1}&sort={2}&page={3}'.format(
            self.API_URL,
            query,
            sort,
            page
        ))
        response.raise_for_status()
        return(response.json())

    def get_cover_thumbnail(self, media_id : int):
        return('{0}/galleries/{1}/cover.jpg'.format(self.THUNBNAIL_API_URL, media_id))

    def get_gallery_url(self, id : int):
        return('{0}/g/{1}'.format(self.API_URL, id))

    def get_url(self, url):
        return(self.API_URL + url)