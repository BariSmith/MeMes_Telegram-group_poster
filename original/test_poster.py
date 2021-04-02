from bot import PostSender, ApiTelegramException
from config import TOKEN

if __name__ == '__main__':
    sender = PostSender(TOKEN)
    categories = sender.get_categories()
    for i, item in enumerate(categories):
        print(f'{i}. {item.name}')
    cat = int(input('Выберите категорию (число): '))
    limit = int(input('Введите сколько нужно постов: '))
    chat = input('Введите id или @юзернейм чата: ')
    for cat in categories:
        posts = sender.get_posts(cat, limit=5000)
        posts = [it for it in posts if it.likes >= 500]
        print(cat.name, len(posts))
    try:
        sender.publish_post(chat, posts[::-1])
        print('Успешно отправлено')
    except ApiTelegramException as e:
        print('Ошибка: ', e.result_json['description'])
