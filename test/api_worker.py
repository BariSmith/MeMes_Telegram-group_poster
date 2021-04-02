import requests
from typing import Optional, List
import logging


class IfunnyApiException(Exception):

    def __init__(self, resp_json):
        self.msg = f"Error_code: {resp_json['status']}. {resp_json['error_description']}"


class PostItem:

    def __init__(self, item_data: dict):
        self.type: str = item_data['type']
        self.url: str = item_data['url']
        self.title: str = item_data['title']

    def __repr__(self):
        return f'PostItem(type: {self.type}, url: {self.url}, title: {self.title}'


class Category:

    def __init__(self, category_data: dict):
        self.name = category_data['name']
        self.channel_id = category_data['id']

    def __repr__(self):
        return f'Category({self.name}, {self.channel_id})'


class ChanItems:

    def __init__(self, data: dict, channel_id: str, limit: int, likes: int, type: str):
        self.items_data = data['data']['content']['items']
        self.items = [PostItem(it) for it in self.items_data]
        data = data['data']['content']['paging']
        self.__prev_id = data['cursors']['prev'] if data['hasPrev'] else None
        self.__next_id = data['cursors']['next'] if data['hasNext'] else None
        self.__likes = data['data']['content']['likes'] if likes >= 500 else None #change
        self.__channel_id = channel_id
        self.__limit = limit
        self.__type = type
        self.__worker = ApiWorker()

    def get_next(self):
        if self.__next_id:
            return self.__worker.get_items(self.__channel_id, next_id=self.__next_id, limit=self.__limit)

    def get_prev(self):
        if self.__prev_id:
            return self.__worker.get_items(self.__channel_id, prev_id=self.__prev_id, limit=self.__limit)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        if isinstance(item, slice) or isinstance(item, int):
            return self.items[item]
        raise KeyError

    def __repr__(self):
        return f'ChanItems({len(self.items)} items)'


class ApiWorker:

    def __init__(self):
        self.__auth_key = 'MDIzNTYxMzY2NDYxMzY2MzMzMkQ2NDMyMzU2MzJEMzQ2MzY0NjQyRDM4Mzg2MzM1MkQzMDMyMzQzNjYyMzkzOTMxNjEzNjY2MzZfUHpuNEQxMnNvSzo5Nzg0ZjE2MzZlYzdhYjE4YmI5YzczNmNhZjg0MzY1Mzc3M2M5Y2Mz'
        self._headers = {
            'Accept': 'application/json,image/jpeg,image/webp,video/mp4',
            'iFunny-Project-Id': 'Russia',
            'Accept-Language': 'ru-RU',
            'Messaging-Project': 'idaprikol.ru:idaprikol-60aec',
            'ApplicationState': '1',
            'Authorization': f'Basic {self.__auth_key}',
            'Host': 'api.ifunny.mobi',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'iDaPrikol/6.15.4(1119163) Android/6.0 (Xiaomi; Redmi Note 4; Xiaomi)'
        }

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApiWorker, cls).__new__(cls)
        return cls.instance

    def __make_request(self, url: str) -> dict:
        try:
            resp = requests.get(url, headers=self._headers)
        except Exception:
            logging.exception()
            raise
        resp_json = resp.json()
        if resp_json['status'] == 200:
            return resp_json
        logging.error(f"request error: {resp_json['status']} {resp_json['error_description']}")
        raise IfunnyApiException(resp_json)

    def get_categories(self) -> List[Category]:
        response = self.__make_request(url='https://api.ifunny.mobi/v4/channels')
        return [Category(it) for it in response['data']['channels']['items']]

    def get_items(self, channel_id: str, limit: int = 1, likes: int = 1, next_id: Optional[str] = None,
                  prev_id: Optional[str] = None) -> ChanItems:
        params = []
        if limit and likes:
            params.append(f'limit={limit}')
            params.append(f'likes={500}')
        if next_id or prev_id:
            params.append(f'next={next_id}' if next_id else f'prev={prev_id}')
        url = f'https://api.ifunny.mobi/v4/channels/{channel_id}/items?{"&".join(params)}'
        return ChanItems(self.__make_request(url=url), channel_id, limit, likes, type)

    def get_recomendations(self, limit: int = 1, likes: int = 1) -> List[PostItem]:
        response = self.__make_request(url='https://api.ifunny.mobi/v4/feeds/featured')
        items = response['data']['content']['items']
        return [PostItem(it) for it in items]
