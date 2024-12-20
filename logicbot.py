import telebot
from telebot import types
import random
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup
import time

bot = telebot.TeleBot("8027072430:AAG-uhnAuXyr1VpRFSkGSpM49AEBq2Kilrs")
num_data_zal = None
name_position = {}

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    complimet = ['Классная фотка', 'Неплохо', 'Нормис', 'Убежище']
    bot.reply_to(message, complimet[random.randint(0,3)])

@bot.message_handler(commands=['website'])
def site(message):
    bot.send_message(message.chat.id, 'https://2016.kinofest.org/program-2022')

@bot.message_handler(commands=['start', 'pickme'])
def main_s(message):
    #name_position[message.chat.id] = "MAIN"
    inline_button = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Посмотреть расписание', callback_data='look_rasp')
    btn2 = types.InlineKeyboardButton('Личный календарь', callback_data='look_lk')
    inline_button.row(btn1, btn2)
    bot.send_message(message.chat.id, f"Приветствую {message.from_user.first_name}! 🎬 Добро пожаловать в мир кино! Я ваш гид по миру кинематографа, готовый помочь выбрать фильм на любой вкус. Могу предложить новинки проката, лучшие фильмы разных жанров, рассказать о последних премьерах и даже поделиться интересными фактами о мире кино. Что бы вы хотели узнать?", reply_markup=inline_button)
    #bot.register_next_step_handler(message, menu)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    check_site = requests.get('https://2016.kinofest.org/program-2022')
    if callback.data == 'look_rasp':
        #name_position[callback.message.chat.id] = "RASP"

        if check_site.status_code == 200:
            html = check_site.text
            soup = BeautifulSoup(html, 'lxml')
            element = soup.find_all('p', attrs={'style': 'color: #800080; font-size: 20px; font-family: verdana, geneva; text-align: center;'})
        else:
            bot.send_message(callback.message.chat.id, f'Ошибка при запросе: {check_site.status_code}')

        inline_btn_rasp = types.InlineKeyboardMarkup()
        btnr4 = types.InlineKeyboardButton(f'1.  {element[3].text}', callback_data='data4')
        inline_btn_rasp.row(btnr4)
        btnr3 = types.InlineKeyboardButton(f'2.  {element[2].text}', callback_data='data3')
        inline_btn_rasp.row(btnr3)
        btnr2 = types.InlineKeyboardButton(f'3.  {element[1].text}', callback_data='data2')
        inline_btn_rasp.row(btnr2)
        btnr1 = types.InlineKeyboardButton(f'4.  {element[0].text}', callback_data='data1')
        inline_btn_rasp.row(btnr1)

        sled_btn = types.InlineKeyboardButton('След.', callback_data='sled_sps')
        pred_btn = types.InlineKeyboardButton('Пред.', callback_data='pred_sps')
        inline_btn_rasp.row(pred_btn, sled_btn)
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        inline_btn_rasp.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Ближайшие мероприятия",
            reply_markup=inline_btn_rasp
        )

    def osnova():
        inline_btn_data = types.InlineKeyboardMarkup()
        btnz1 = types.InlineKeyboardButton('Зал 1', callback_data='zal1')
        btnz2 = types.InlineKeyboardButton('Зал 2', callback_data='zal2')
        btnz3 = types.InlineKeyboardButton('Зал 3', callback_data='zal3')
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        inline_btn_data.row(btnz1, btnz2, btnz3)
        inline_btn_data.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Выберите зал",
            reply_markup=inline_btn_data
        )

    if check_site.status_code == 200:
        html_site = check_site.text
        soup = BeautifulSoup(html_site, 'lxml')
        find_zal = soup.find_all('td', class_="prog-table-33")
        sp_infi = [[], [], [], []]
        s = 0
        sc_dz = 0
        for datazal in range(len(find_zal)):
            sp_infi[s].append(find_zal[datazal].text)
            sc_dz += 1
            if sc_dz == 3:
                sc_dz = 0
                s += 1

    global num_data_zal

    if callback.data == 'data1':
        #name_position[callback.message.chat.id] = "DATA1"
        osnova()
        num_data_zal = 0

    if callback.data == 'data2':
        #name_position[callback.message.chat.id] = "DATA2"
        osnova()
        num_data_zal = 1

    if callback.data == 'data3':
        #name_position[callback.message.chat.id] = "DATA3"
        osnova()
        num_data_zal = 2

    if callback.data == 'data4':
        #name_position[callback.message.chat.id] = "DATA4"
        osnova()
        num_data_zal = 3

    if callback.data == 'zal1':
        inline_btn_rasp_text = InlineKeyboardMarkup()
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        inline_btn_rasp_text.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=sp_infi[num_data_zal][0],
            reply_markup=inline_btn_rasp_text
        )

    if callback.data == 'zal2':
        inline_btn_rasp_text = InlineKeyboardMarkup()
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        inline_btn_rasp_text.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=sp_infi[num_data_zal][1],
            reply_markup=inline_btn_rasp_text
        )

    if callback.data == 'zal3':
        inline_btn_rasp_text = InlineKeyboardMarkup()
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        inline_btn_rasp_text.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=sp_infi[num_data_zal][2],
            reply_markup=inline_btn_rasp_text
        )

    if callback.data == 'look_lk':
        #name_position[callback.message.chat.id] = "LK"
        inline_btn_l_k = types.InlineKeyboardMarkup()
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        btn_izbr = types.InlineKeyboardButton('Избранное', callback_data='like_films_mp')
        inline_btn_l_k.row(btn_izbr)
        btn_rec = types.InlineKeyboardButton('Рекомендации', callback_data='rec')
        inline_btn_l_k.row(btn_rec)
        btn_sms = types.InlineKeyboardButton('Уведомления', callback_data='sms')
        inline_btn_l_k.row(btn_sms)
        inline_btn_l_k.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='тут будет текст после нажатия ЛК',
            reply_markup=inline_btn_l_k
        )
    if callback.data == 'like_films_mp':
        #name_position[callback.message.chat.id] = "lIKE"
        inline_btn_like = types.InlineKeyboardMarkup()
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        btn_mplike = types.InlineKeyboardButton('Мероприятия', callback_data='mp_rec')
        btn_filmslike = types.InlineKeyboardButton('Фильмы', callback_data='films_rec')
        inline_btn_like.row(btn_mplike, btn_filmslike)
        inline_btn_like.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='после нажатия Л_МиФ тут будет либо текст с кнопками, либо только кнопки',
            reply_markup=inline_btn_like
        )
    if callback.data == 'rec':
        #name_position[callback.message.chat.id] = "REC"
        inline_btn_rec = types.InlineKeyboardMarkup()
        nazad_btn = types.InlineKeyboardButton('Назад', callback_data='nazad')
        btn_mprec = types.InlineKeyboardButton('Мероприятия', callback_data='mp_rec')
        btn_filmsrec = types.InlineKeyboardButton('Фильмы', callback_data='films_rec')
        inline_btn_rec.row(btn_mprec,btn_filmsrec)
        inline_btn_rec.row(nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='пока тут пусто',
            reply_markup= inline_btn_rec
        )

    if callback.data == 'nazad':
        try:
            bot.delete_message(callback.message.chat.id, callback.message.id)
        except Exception as e:
            print(e)
        #if name_position[callback.message.chat.id] == "RASP":
        main_s(callback.message)


@bot.message_handler(commands=['help'])
def main_h(message):
    commands = (
        "/start - запустить бота\n"
        "/help - все команды бота\n"
        "/website - Открыть наш сайт КиноГид \"Кино без барьеров\""
    )
    bot.send_message(message.chat.id, f'Что умеет бот:\n{commands}')

@bot.message_handler()
def any_message(message):
    bot.send_message(message.chat.id, 'Возможно ты ошибся в команде, напиши /help для просмотра доступных команд')

bot.polling(none_stop=True)
