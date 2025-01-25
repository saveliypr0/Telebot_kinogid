import tmdbsimple as tmdb
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
from init_token import BOT_TOKEN

bot = telebot.TeleBot(f'{BOT_TOKEN}')
new_mess_get = {}



def nazv_f(callback1, mess, page=1):
    search = tmdb.Search()
    response = search.movie(query=mess, language="ru", page=page)

    if not response['results']:
        bot.send_message(callback1.message.chat.id, 'По вашему запросу ничего не найдено')
        bot.register_next_step_handler(callback1.message, nazv_f)
    else:
        markup_nazv = InlineKeyboardMarkup(row_width=1)
        for result in response['results']:
            nazv = result['title']
            film_id = result['id']
            callback_data = f'movie_{film_id}'
            button = types.InlineKeyboardButton(text=nazv, callback_data=callback_data)
            markup_nazv.add(button)

        sp_ps = []
        if page > 1:
            pred = InlineKeyboardButton('<-', callback_data=f'nazvpage_{mess}_{page - 1}')
            sp_ps.append(pred)

        sled = InlineKeyboardButton('->', callback_data=f'nazvpage_{mess}_{page + 1}')
        sp_ps.append(sled)
        markup_nazv.row(*sp_ps)

        menu_btn = InlineKeyboardButton('Меню🏠︎', callback_data='nazad')
        markup_nazv.row(menu_btn)

        bot.edit_message_text(
            chat_id=callback1.message.chat.id,
            message_id=callback1.message.message_id,
            text=f"Вот что удалось найти (страница - {page})",
            reply_markup=markup_nazv
        )
