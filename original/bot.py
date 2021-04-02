import time

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from typing import Union, List
from api_worker import ApiWorker, PostItem, Category
import logging

logging.basicConfig(
    filename='poster.log',
    format='%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
    level=logging.INFO
)


class PostSender:

    def __init__(self, token: str):
        self.__bot = TeleBot(token)
        self.__api_worker = ApiWorker()

    def get_categories(self) -> List[Category]:
        return self.__api_worker.get_categories()

    def get_posts(self, category: Union[Category, str], limit: int = 1):
        if isinstance(category, Category):
            category = category.channel_id
        return self.__api_worker.get_items(category, limit=limit)

    def get_recomendation(self, limit=1):
        return self.__api_worker.get_recomendations(limit=limit)

    def __send_post(self, chat_id: Union[str, int], post_item: PostItem) -> bool:
        if post_item:
            try:
                if post_item.type in ('pic', 'mem'):
                    self.__bot.send_photo(chat_id, photo=post_item.url, caption=post_item.title)
                elif post_item.type == 'gif_caption':
                    self.__bot.send_animation(chat_id, animation=post_item.url, caption=post_item.title)
                elif post_item.type == 'video_clip':
                    self.__bot.send_video(chat_id, data=post_item.url, caption=post_item.title)
            except ApiTelegramException as e:
                logging.error(f"Bot can't send message error_code: {e.error_code} - {e.result_json['description']}")
                if e.error_code == 429:
                    print('timeout ', e.result_json['parameters']['retry_after'])
                    time.sleep(e.result_json['parameters']['retry_after'])
                    return self.__send_post(chat_id, post_item)
                raise
            return True

    def _check_chat(self, chat_id) -> bool:
        try:
            self.__bot.get_chat(chat_id)
            return True
        except ApiTelegramException as e:
            logging.error(f'bad chat {chat_id}: {e.result_json["description"]}')
            raise

    def publish_post(self, chat_id: Union[int, str], post_items: Union[PostItem, List[PostItem]]) -> Union[bool, List[bool]]:
        if self._check_chat(chat_id):
            if isinstance(post_items, PostItem):
                return self.__send_post(chat_id, post_items)
            else:
                for it in post_items:
                    self.__send_post(chat_id, it)
                    time.sleep(1)
