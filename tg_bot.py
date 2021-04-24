import hashlib
import uuid

from requests import post
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler

TOKEN = '1773431202:AAEQ-JoWlUCJ1OjR8kFBWd44PJWUSdYQ_Fk'


def start(update, context):
    markup = ReplyKeyboardMarkup([['наш сайт', 'создать анонимный пост']],
                                 one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Привет! Я могу создавать анонимные посты.",
        reply_markup=markup
    )


def show_site(update, context):
    site = 'https://...'
    update.message.reply_text(f'Наш сайт: {site}')


def input_title(update, context):
    update.message.reply_text('Введите название поста')
    return 1


def input_content(update, context):
    context.user_data['title'] = update.message.text
    update.message.reply_text('Введите текст')
    return 2


def add_post(update, context):
    context.user_data['content'] = update.message.text
    link = hashlib.sha512(f"{context.user_data['title']}"
                          f"{uuid.uuid4().hex}".encode()).hexdigest()[:12]
    response = post(f'http://localhost:5000/api/anonim_posts', json={
        'title': context.user_data['title'],
        'content': context.user_data['content'],
        'link': link
    }).json()
    if 'success' in response:
        update.message.reply_text("Анонимный пост успешно создан")
        update.message.reply_text('https://...' + link)
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('создать анонимный пост'),
                                     input_title, pass_user_data=True)],

        states={
            1: [MessageHandler(Filters.text,
                               input_content, pass_user_data=True)],
            2: [MessageHandler(Filters.text,
                               add_post, pass_user_data=True)],
        },

        fallbacks=[]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('наш сайт'),
                                  show_site))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
