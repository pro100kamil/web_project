import uuid
import hashlib

from requests import post
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler

from data.config import TG_TOKEN as TOKEN, SITE


def start(update, context):
    markup = ReplyKeyboardMarkup([['наш сайт', 'создать анонимный пост']],
                                 one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Привет! Я могу создавать анонимные посты.",
        reply_markup=markup
    )


def show_site(update, context):
    update.message.reply_text(f'Наш сайт: {SITE}')


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
    try:
        response = post(f'{SITE}/api/anonim_posts', json={
            'title': context.user_data['title'],
            'content': context.user_data['content'],
            'link': link
        }).json()
        if 'success' in response:
            update.message.reply_text("Анонимный пост успешно создан")
            update.message.reply_text(f'{SITE}/anonim_posts/{link}')
    except Exception as e:
        update.message.reply_text('Произошла ошибка')
        print(e)
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
