import telebot
from telebot import types
import random
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
import tmdbsimple as tmdb
#ВОПРОС!!! глобал переменные в боте это плохо? при одновременном запросе к боту с логином может записать 2 в 1 или переменные типа глобал локальны и при одновременном запросе все будет ок?
#ВОПРОС!!! почему ограничение символов через Varchar не работает?
bot = telebot.TeleBot("8027072430:AAG-uhnAuXyr1VpRFSkGSpM49AEBq2Kilrs")
tmdb.API_KEY = '03684a8a7594f223cb6c8416d6afbc25'
num_data_zal = None
login = None
password = None
name_position = {}

AllGenre = {
    'Боевик': 28,
    'Приключения': 12,
    'Мультфильм': 16,
    'Комедия': 35,
    'Криминал': 80,
    'Документальный': 99,
    'Драма': 18,
    'Семейный': 10751,
    'Фэнтези': 14,
    'История': 36,
    'Ужасы': 27,
    'Музыка': 10402,
    'Мистика': 9648,
    'Мелодрама': 10749,
    'Научная фантастика': 878,
    'Телевизионный фильм': 10770,
    'Триллер': 53,
    'Военный': 10752,
    'Вестерн': 37
}

user_data = {}

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, f'{random.randint(0,10)}/10')

@bot.message_handler(commands=['website'])
def site(message):
    bot.send_message(message.chat.id, 'https://2016.kinofest.org/program-2022')

@bot.message_handler(commands=['start', 'pickme'])
def main_s(message):
    #name_position[message.chat.id] = "MAIN"
    inline_button = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Посмотреть расписание', callback_data='look_rasp')
    btn2 = types.InlineKeyboardButton('Личный календарь', callback_data='look_lk')
    btn3 = types.InlineKeyboardButton('Регистрация', callback_data='regi')
    btn4 = types.InlineKeyboardButton('Новости', callback_data='news')
    btn5 = types.InlineKeyboardButton('Найти фильм', callback_data='find_film')
    inline_button.row(btn1, btn2)
    inline_button.row(btn3)
    inline_button.row(btn4)
    inline_button.row(btn5)
    bot.send_message(message.chat.id, f"Приветствую {message.from_user.first_name}! 🎬 Добро пожаловать в мир кино! Я ваш гид по миру кинематографа, готовый помочь выбрать фильм на любой вкус. Могу предложить новинки проката, лучшие фильмы разных жанров, рассказать о последних премьерах и даже поделиться интересными фактами о мире кино. Что бы вы хотели узнать?", reply_markup=inline_button)
    #bot.register_next_step_handler(message, menu)
@bot.callback_query_handler(func=lambda call: call.data.startswith('genre_'))
def show_genre_film(call):
    genre_id = int(call.data.split('_')[1])
    page = int(call.data.split('_')[3])

    discover = tmdb.Discover()
    response = discover.movie(with_genres=genre_id, language="ru", page=page)

    markup_res_genre = types.InlineKeyboardMarkup()
    for result in response['results']:
        nazv = result['title']
        movie_id = result['id']
        callback_data = f'movie_{movie_id}'
        btn = types.InlineKeyboardButton(text=nazv, callback_data=callback_data)
        markup_res_genre.row(btn)

    sp_btn = []
    next_page_callback = f'genre_{genre_id}_page_{page + 1}'
    load_btn = types.InlineKeyboardButton('->', callback_data=next_page_callback)
    sp_btn.append(load_btn)

    if page > 1:
        prev_page_callback = f'genre_{genre_id}_page_{page - 1}'
        prev_btn = types.InlineKeyboardButton('<-', callback_data=prev_page_callback)
        sp_btn.insert(0, prev_btn)

    reserv_AllGenre = {value: key for key, value in AllGenre.items()}
    markup_res_genre.row(*sp_btn)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Фильмы жанра {reserv_AllGenre[genre_id]} (страница {page}):',
        reply_markup=markup_res_genre
    )



@bot.callback_query_handler(func=lambda call: call.data.startswith('movie_'))
def show_film(call):
    def escape_markdown_v2(text): #Экранирует специальные символы для поддержки MarkdownV2
        special_characters = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in special_characters else char for char in text)

    movie_id = int(call.data.split('_')[1])
    movie = tmdb.Movies(movie_id).info(language="ru")
    poster_path = movie.get('poster_path')
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    else:
        poster_url = None

    genres = ', '.join([genre['name'] for genre in movie['genres']]) or 'Нет жанра'
    overview = movie.get('overview') or 'Описание отсутствует.'
    release_date = movie.get('release_date') or 'Дата выхода неизвестна.'

    text_f = f"""*Название:* {escape_markdown_v2(movie['title'])}
*Жанры:* {escape_markdown_v2(genres)}
*Дата выхода:* {escape_markdown_v2(release_date)}
*Рейтинг:* {escape_markdown_v2(str(movie['vote_average']))} / 10
*Описание:*
    {escape_markdown_v2(overview)}"""

    markup_izbr = InlineKeyboardMarkup()
    markup_izbr_del = InlineKeyboardMarkup()
    markup_izbr.add(InlineKeyboardButton('Добавить в избранное', callback_data='add_izbr'))
    markup_izbr_del.add(InlineKeyboardButton('Удалить из избранного', callback_data='del_izbr'))

    user_data[call.message.chat.id] = {
        'text_f': text_f,
        'markup_izbr': markup_izbr,
        'markup_izbr_del': markup_izbr_del
    }

    if poster_url:
        bot.send_photo(call.message.chat.id, photo=poster_url, caption=text_f, parse_mode='MarkdownV2', reply_markup=markup_izbr)
    else:
        bot.send_message(call.message.chat.id, text=text_f, parse_mode='MarkdownV2', reply_markup=markup_izbr)



@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.message.chat.id in user_data:
        film_data = user_data[callback.message.chat.id]
        if callback.data == 'add_izbr':
            bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=film_data['text_f'],
                reply_markup=film_data['markup_izbr_del']
            )
        elif callback.data == 'del_izbr':
            bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=film_data['text_f'],
                reply_markup=film_data['markup_izbr']
            )
    #else:
     #   bot.send_message(callback.message.chat.id, "Ошибка: данные фильма не найдены.")

    if callback.data == 'genre':
        markup_genre = InlineKeyboardMarkup(row_width=1)
        for genres in AllGenre:
            markup_genre.add(InlineKeyboardButton(genres, callback_data=f'genre_{AllGenre[genres]}_page_1'))
        bot.send_message(callback.message.chat.id, 'Список жанров', reply_markup=markup_genre)

    if callback.data == 'nazv':
        def nazv_f(message):
            search = tmdb.Search()
            response = search.movie(query=message.text, language="ru")

            if not response['results']:
                bot.send_message(callback.message.chat.id, 'По вашему запросу ничего не найдено')
                bot.send_message(callback.message.chat.id, 'Попробуйте ещё раз')
                bot.register_next_step_handler(callback.message, nazv_f)
            else:
                markup_nazv = InlineKeyboardMarkup(row_width=1)
                for result in response['results']:
                    nazv = result['title']
                    film_id = result['id']
                    callback_data = f'movie_{film_id}'
                    button = types.InlineKeyboardButton(text=nazv, callback_data=callback_data)
                    markup_nazv.add(button)
                bot.send_message(message.chat.id, "Вот несколько подходящих вариантов:", reply_markup=markup_nazv)

        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Напишите название фильма",
            reply_markup=None
        )
        bot.register_next_step_handler(callback.message, nazv_f)

    if callback.data == 'find_film':
        markup_genre_nazv = InlineKeyboardMarkup()
        nazv_btn = InlineKeyboardButton('Названию', callback_data='nazv')
        genre_btn = InlineKeyboardButton('Жанру', callback_data='genre')
        markup_genre_nazv.row(nazv_btn,genre_btn)
        bot.send_message(callback.message.chat.id, 'Поиск по', reply_markup=markup_genre_nazv)


    if callback.data == 'news':
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Последние новости:",
            reply_markup=None
        )
        with open('news_r.mp4', 'rb') as rvideo:
            bot.send_video(callback.message.chat.id, rvideo, supports_streaming=True)
    if callback.data == 'regi':
        def user_login(message):
            global login
            bot.delete_message(message.chat.id, message.message_id)
            if len(message.text) > 20:
                bot.send_message(callback.message.chat.id, 'Нет, так не пойдет, логин должен быть менее 20 символов')
                time.sleep(1.4)
                bot.send_message(callback.message.chat.id, 'Давай сначала')
                time.sleep(0.7)
                bot.send_message(callback.message.chat.id, 'Придумайте логин')
                bot.register_next_step_handler(message, user_login)
            else:
                login = message.text.strip()

                conn = sqlite3.connect('bazareg.bz')
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) FROM users WHERE login=?', (login,))
                count = cursor.fetchone()[0]

                if count > 0:
                    bot.send_message(message.chat.id, 'Такой логин уже занят. Придумайте другой.')
                    bot.register_next_step_handler(message, user_login)
                else:
                    bot.send_message(message.chat.id, 'Придумайте пароль')
                    bot.register_next_step_handler(message, user_password)

                cursor.close()
                conn.close()

        conn = sqlite3.connect('bazareg.bz')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                                           login VARCHAR(25) UNIQUE,
                                           pass VARCHAR(50)
                                       )''')
        conn.commit()
        cursor.close()
        conn.close()

        bot.send_message(callback.message.chat.id, 'Придумайте логин')
        bot.register_next_step_handler(callback.message, user_login)

        def user_password(message):
            bot.delete_message(message.chat.id, message.message_id)

            global password
            if len(message.text) > 30:
                bot.send_message(callback.message.chat.id, 'Эй, эй, куда столько много? 30 символов хватит')
                time.sleep(1.4)
                bot.send_message(callback.message.chat.id,'Давай сначала')
                time.sleep(0.7)
                bot.send_message(callback.message.chat.id,'Придумайте Пароль')
                bot.register_next_step_handler(message, user_password)
            else:
                password = message.text.strip()

                conn = sqlite3.connect('bazareg.bz')
                cursor = conn.cursor()

                cursor.execute('INSERT INTO users (login, pass) VALUES (?, ?)', (login, password))
                conn.commit()

                cursor.close()
                conn.close()

                markup = telebot.types.InlineKeyboardMarkup()
                btn_dev = types.InlineKeyboardButton('Пользователи(админ)', callback_data='users_sps')
                markup.add(btn_dev)
                #btn_continue = types.InlineKeyboardButton('Подтвердить', callback_data='continue')
                #markup.row(btn_continue)

                bot.send_message(message.chat.id, f'Круто!\nТеперь ваш логин такой: {login}\nА пароль такой: {password}', reply_markup=markup)

    '''if callback.data == 'continue':
        conn = sqlite3.connect('bazareg.bz')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (login, pass) VALUES (?, ?)', (login, password))
        conn.commit()

        cursor.close()
        conn.close()

        callback_data='nazad'
        callback_message(callback)'''

    if callback.data == 'users_sps':
        conn = sqlite3.connect('bazareg.bz')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users')
        all_users = cursor.fetchall()
        info_au = ''
        for oneAU in all_users:
            info_au += f'Логин: {oneAU[1]}\nПароль: {oneAU[2]}\n\n'

        cursor.close()
        conn.close()

        bot.send_message(callback.message.chat.id, f'Все пользователи:\n\n{info_au}')


    check_site = requests.get('https://2016.kinofest.org/program-2022')

    def lookraspf():
        if check_site.status_code == 200:
            html = check_site.text
            soup = BeautifulSoup(html, 'lxml')
            element = soup.find_all('p', attrs={'style': 'color: #800080; font-size: 20px; font-family: verdana, geneva; text-align: center;'})
        else:
            bot.send_message(callback.message.chat.id, f'Ошибка при запросе: {check_site.status_code}')

        inline_btn_rasp = types.InlineKeyboardMarkup()
        btnr4 = types.InlineKeyboardButton(f'1.  {element[e+3].text}', callback_data='data4')
        inline_btn_rasp.row(btnr4)
        btnr3 = types.InlineKeyboardButton(f'2.  {element[e+2].text}', callback_data='data3')
        inline_btn_rasp.row(btnr3)
        btnr2 = types.InlineKeyboardButton(f'3.  {element[e+1].text}', callback_data='data2')
        inline_btn_rasp.row(btnr2)
        btnr1 = types.InlineKeyboardButton(f'4.  {element[e].text}', callback_data='data1')
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

    if callback.data == 'look_rasp':
        e = 0
        lookraspf()

    '''if callback.data == 'sled':
        e += 3
        callback_data='look_rasp'
        callback_message(callback)'''


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
