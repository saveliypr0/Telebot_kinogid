import telebot
import random
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
import tmdbsimple as tmdb
import find_nameF
import news_parce
from init_token import BOT_TOKEN, API_TMDB
from find_film_kbb import find_f
from description_film_kbb import parce_desc
from engine import session
from models import User_favor


bot = telebot.TeleBot(f'{BOT_TOKEN}')
tmdb.API_KEY = f'{API_TMDB}'
login = None
password = None
name_position = {}
users_id = {}

class Globus: #Глобальные параметры
    nazad_btn = InlineKeyboardButton("Меню🏠︎", callback_data='nazad')
globus = Globus()

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


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, f'{random.randint(0, 10)}/10')


@bot.message_handler(commands=['website'])
def site(message):
    bot.send_message(message.chat.id, 'https://2016.kinofest.org')


@bot.message_handler(commands=['start'])
def main_s(message):
    try:
        msg = message.message
    except:
        msg = message

    inline_button = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Посмотреть расписание', callback_data='look_rasp')
    btn2 = InlineKeyboardButton('Личный календарь', callback_data='look_lk')
    btn3 = InlineKeyboardButton('Регистрация', callback_data='regi')
    btn4 = InlineKeyboardButton('Новости', callback_data='news_0')
    btn5 = InlineKeyboardButton('Найти фильм', callback_data='find_film')
    btn6 = InlineKeyboardButton('Заполнить форму', callback_data='FIO')
    btn7 = InlineKeyboardButton('Кинофестиваль', callback_data='kbb_films_0')
    inline_button.row(btn1, btn2)
    inline_button.row(btn3)
    inline_button.row(btn4)
    inline_button.row(btn5,btn7)
    inline_button.row(btn6)
    bot.send_message(msg.chat.id,f"Приветствую, {message.from_user.first_name}! 🎬 Добро пожаловать в мир кино! "
                                 f"Я ваш гид по миру кинематографа, готовый помочь выбрать фильм на любой вкус."
                                 f" Могу предложить новинки проката, лучшие фильмы разных жанров, "
                                 f"рассказать о последних премьерах и даже поделиться интересными фактами о мире кино. "
                                 f"Что бы вы хотели узнать?",
                                 reply_markup=inline_button)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('add_izbrKB_'))
def izbr_film(callback):
    film_id = int(callback.data.split('_')[2])
    new_favor = User_favor(id_user=callback.message.chat.id, favor=film_id)
    session.add(new_favor)
    session.commit()
    bot.send_message(callback.message.chat.id, "Успешно!")

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('film_'))
def kbb_film(callback):
    film_id = int(callback.data.split('_')[1])
    links_kbb = find_f()[1]
    text, img = parce_desc(links_kbb[film_id])

    exit_favor = InlineKeyboardMarkup()
    favor = InlineKeyboardButton('Добавить в избранное(пока не меняется)', callback_data=f'add_izbrKB_{film_id}')
    exit_favor.row(favor)
    exit_favor.row(globus.nazad_btn)

    bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    bot.send_photo(
        chat_id=callback.message.chat.id,
        caption=text,
        photo=img,
        reply_markup=exit_favor,
        parse_mode='MarkdownV2'
    )

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('zal_'))
def look_zal(callback):
    zal = int(callback.data.split('_')[1])

    inline_btn_rasp_text = InlineKeyboardMarkup()

    inline_btn_rasp_text.row(globus.nazad_btn)
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=data_zal.result_data[zal],
        reply_markup=inline_btn_rasp_text
    )

class NewsPage:
    page = 0

    def __init__(self):
        self.message = None
        self.data = None

    @bot.callback_query_handler(func=lambda callback: callback.data.startswith('news_'))
    def news_page(callback):
        NewsPage.page = int(callback.data.split('_')[1])
        bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

        news_markup = InlineKeyboardMarkup()
        next = InlineKeyboardButton('>>>', callback_data=f'news_{NewsPage.page + 1}')
        back = InlineKeyboardButton('<<<', callback_data=f'news_{NewsPage.page - 1}')
        if NewsPage.page > 0:
            news_markup.row(back, next)
        else:
            news_markup.row(next)
        news_markup.row(globus.nazad_btn)

        photo_news, text_news = news_parce.show_news(NewsPage.page)

        bot.send_photo(
            photo=photo_news,
            caption=text_news,
            chat_id=callback.message.chat.id,
            reply_markup=news_markup,
            parse_mode="HTML"
        )


class DataZal:
    result_data = None

    def __init__(self):
        self.message = None
        self.data = None

    @bot.callback_query_handler(func=lambda callback: callback.data.startswith('data_'))
    def osnova(callback):
        check_site_programs = requests.get('https://2016.kinofest.org/program-2022')
        n_data = int(callback.data.split('_')[1])
        inline_btn_data = InlineKeyboardMarkup()
        btnz1 = InlineKeyboardButton('Зал 1', callback_data='zal_0')
        btnz2 = InlineKeyboardButton('Зал 2', callback_data='zal_1')
        btnz3 = InlineKeyboardButton('Зал 3', callback_data='zal_2')

        inline_btn_data.row(btnz1, btnz2, btnz3)
        inline_btn_data.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Выберите зал",
            reply_markup=inline_btn_data
        )
        if check_site_programs.status_code == 200:
            html_site = check_site_programs.text
            soup = BeautifulSoup(html_site, 'lxml')
            find_zal = soup.find_all('td', class_="prog-table-33")
            final_zal = [find_zal[item].text.replace('\n\n', '\n').replace('/', '\n') for item in range(len(find_zal))]

            sp_infi = list(zip(*[iter(final_zal)] * 3))

            DataZal.result_data = sp_infi[n_data]

data_zal = DataZal()

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('nazvpage_'))
def show_nazv_film(callback):
    page = int(callback.data.split('_')[2])
    mess = callback.data.split('_')[1]
    find_nameF.nazv_f(callback, mess, page)


@bot.callback_query_handler(func=lambda call: call.data.startswith('genre_'))
def show_genre_film(call):
    genre_id = int(call.data.split('_')[1])
    page = int(call.data.split('_')[3])

    discover = tmdb.Discover()
    response = discover.movie(with_genres=genre_id, language="ru", page=page)

    markup_res_genre = InlineKeyboardMarkup()
    for result in response['results']:
        nazv = result['title']
        movie_id = result['id']
        callback_data = f'movie_{movie_id}'
        btn = InlineKeyboardButton(text=nazv, callback_data=callback_data)
        markup_res_genre.row(btn)

    sp_btn = []
    next_page_callback = f'genre_{genre_id}_page_{page + 1}'
    load_btn = InlineKeyboardButton('>>>', callback_data=next_page_callback)
    sp_btn.append(load_btn)

    if page > 1:
        prev_page_callback = f'genre_{genre_id}_page_{page - 1}'
        prev_btn = InlineKeyboardButton('<<<', callback_data=prev_page_callback)
        sp_btn.insert(0, prev_btn)

    reserv_all_genre = {value: key for key, value in AllGenre.items()}

    markup_res_genre.row(*sp_btn)
    markup_res_genre.row(globus.nazad_btn)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Фильмы жанра {reserv_all_genre[genre_id]} (страница {page}):',
        reply_markup=markup_res_genre
    )


class User:
    user_data = {}
    text_f = None
    def __init__(self):
        self.message = None
        self.data = None

    def escape_markdown_v2(text):
        special_characters = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in special_characters else char for char in text)

    @staticmethod
    def get_info(movie):
        genres = ', '.join([genre['name'] for genre in movie['genres']]) or 'Нет жанра'
        overview = movie.get('overview') or 'Описание отсутствует.'
        release_date = movie.get('release_date') or 'Дата выхода неизвестна.'

        User.text_f = f"""*Название:* {User.escape_markdown_v2(movie['title'])}
*Жанры:* {User.escape_markdown_v2(genres)}
*Дата выхода:* {User.escape_markdown_v2(release_date)}
*Рейтинг:* {User.escape_markdown_v2(str(movie['vote_average']))} / 10
*Описание:*
    {User.escape_markdown_v2(overview)}"""

    @bot.callback_query_handler(func=lambda call: call.data.startswith('movie_'))
    def show_film(call):
        movie_id = int(call.data.split('_')[1])
        movie = tmdb.Movies(movie_id).info(language="ru")
        poster_path = movie.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            poster_url = None

        markup_izbr = InlineKeyboardMarkup()
        markup_izbr_del = InlineKeyboardMarkup()
        markup_izbr.add(InlineKeyboardButton('Добавить в избранное', callback_data='add_izbr'))
        markup_izbr_del.add(InlineKeyboardButton('Удалить из избранного', callback_data='del_izbr'))
        User.user_data[call.message.chat.id] = {
            'markup_izbr': markup_izbr,
            'markup_izbr_del': markup_izbr_del,
            'm_id' : movie_id
        }

        User.get_info(movie)

        markup_izbr.row(globus.nazad_btn)
        markup_izbr_del.row(globus.nazad_btn)

        user = session.query(User_favor).filter_by(id_user=call.message.chat.id).filter(User_favor.favor == movie_id).first()
        if user is not None:
            bot.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            if poster_url:
                bot.send_photo(call.message.chat.id,
                               photo=poster_url,
                               caption=User.text_f,
                               parse_mode='MarkdownV2',
                               reply_markup=markup_izbr_del)
            else:
                bot.send_message(call.message.chat.id,
                                 text=User.text_f,
                                 parse_mode='MarkdownV2',
                                 reply_markup=markup_izbr_del)
        else:
            if poster_url:
                bot.send_photo(call.message.chat.id,
                               photo=poster_url,
                               caption=User.text_f,
                               parse_mode='MarkdownV2',
                               reply_markup=markup_izbr)
            else:
                bot.send_message(call.message.chat.id,
                                 text=User.text_f,
                                 parse_mode='MarkdownV2',
                                 reply_markup=markup_izbr)

dataizb = User()
#бешенством заражаются, как правило, от укуса собаки, так что будьте аккуратны и не кусайте кого попало

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data.startswith('kbb_films_'):
        all_films_kbb = InlineKeyboardMarkup()
        films_kbb = find_f()[0]
        p = int(callback.data.split('_')[2])
        for index, item in enumerate(films_kbb[p:p+6]):
            btn_film = InlineKeyboardButton(f'{item}', callback_data=f'film_{index}')
            all_films_kbb.row(btn_film)
        
        next = InlineKeyboardButton('>>>', callback_data=f'kbb_films_{p+6}')
        if p > 0:
            back = InlineKeyboardButton('<<<', callback_data=f'kbb_films_{p-6}')
            all_films_kbb.row(back, next)
        else:
            all_films_kbb.row(next)
        
        all_films_kbb.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Эксклюзивные фильмы которые вы найдете только у нас',
            reply_markup=all_films_kbb
        )

    if callback.data == 'send_fio':
        markup_exit = InlineKeyboardMarkup()

        markup_exit.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Успешно!',
            reply_markup=markup_exit
        )

    if callback.data == 'FIO':
        def input_name(mess):
            name = mess.text
            bot.send_message(callback.message.chat.id, 'Введите вашу фамилию')
            bot.register_next_step_handler(callback.message, lambda msg: input_surname(msg, name))

        def input_surname(mess, name):
            surname = mess.text
            markup_send = InlineKeyboardMarkup()
            markup_send.row(InlineKeyboardButton('Отправить', callback_data='send_fio'))
            bot.send_message(callback.message.chat.id, f'Ваше имя:{name}\nВаша фамилия:{surname}', reply_markup=markup_send)

        bot.send_message(callback.message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(callback.message, input_name)


    if callback.data == 'add_izbr':
        film_data = dataizb.user_data[callback.message.chat.id]
        new_favor = User_favor(id_user=callback.message.chat.id, favor=film_data['m_id'])
        session.add(new_favor)
        session.commit()

        bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=User.text_f,
            reply_markup=film_data['markup_izbr_del'],
            parse_mode='MarkdownV2'
        )

    if callback.data == 'del_izbr':
        film_data = dataizb.user_data[callback.message.chat.id]
        user = session.query(User_favor).filter_by(favor=film_data['m_id']).first()
        session.delete(user)
        session.commit()

        bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=User.text_f,
            reply_markup=film_data['markup_izbr'],
            parse_mode='MarkdownV2'
        )


    if callback.data == 'genre':
        markup_genre = InlineKeyboardMarkup(row_width=1)
        for genres in AllGenre:
            markup_genre.add(InlineKeyboardButton(genres, callback_data=f'genre_{AllGenre[genres]}_page_1'))


        markup_genre.row(globus.nazad_btn)

        bot.send_message(callback.message.chat.id, 'Список жанров', reply_markup=markup_genre)

    if callback.data == 'nazv':
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Напишите название фильма",
            reply_markup=None
        )
        bot.register_next_step_handler(callback.message, lambda msg: find_nameF.nazv_f(callback, msg.text))

    if callback.data == 'find_film':
        markup_genre_nazv = InlineKeyboardMarkup()

        nazv_btn = InlineKeyboardButton('Названию', callback_data='nazv')
        genre_btn = InlineKeyboardButton('Жанру', callback_data='genre')
        markup_genre_nazv.row(nazv_btn, genre_btn)
        markup_genre_nazv.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Поиск по',
            reply_markup=markup_genre_nazv
        )



        # bot.edit_message_text(
        #     chat_id=callback.message.chat.id,
        #     message_id=callback.message.message_id,
        #     text="Последние новости:",
        #     reply_markup=None
        # )
        # with open('news_r.mp4', 'rb') as rvideo:
        #     bot.send_video(callback.message.chat.id, rvideo, supports_streaming=True)

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

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,login VARCHAR(1) UNIQUE,pass VARCHAR(10))''')
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
                bot.send_message(callback.message.chat.id, 'Давай сначала')
                time.sleep(0.7)
                bot.send_message(callback.message.chat.id, 'Придумайте Пароль')
                bot.register_next_step_handler(message, user_password)
            else:
                password = message.text.strip()

                conn = sqlite3.connect('bazareg.bz')
                cursor = conn.cursor()

                cursor.execute('INSERT INTO users (login, pass) VALUES (?, ?)', (login, password))
                conn.commit()

                cursor.close()
                conn.close()

                markup = InlineKeyboardMarkup()

                btn_dev = InlineKeyboardButton('Пользователи(админ)', callback_data='users_sps')
                markup.row(btn_dev)
                markup.row(globus.nazad_btn)
                # btn_continue = InlineKeyboardButton('Подтвердить', callback_data='continue')
                # markup.row(btn_continue)

                bot.send_message(message.chat.id, f'Круто!\nВаш логин такой: {login}\nА пароль такой: {password}',
                                 reply_markup=markup)

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


    if callback.data == 'look_rasp':
        check_site_programs = requests.get('https://2016.kinofest.org/program-2022')
        if check_site_programs.status_code == 200:
            html = check_site_programs.text
            soup = BeautifulSoup(html, 'lxml')
            element = soup.find_all('p', attrs={
                'style': 'color: #800080; font-size: 20px; font-family: verdana, geneva; text-align: center;'})
        else:
            bot.send_message(callback.message.chat.id, f'Ошибка при запросе: {check_site_programs.status_code}')

        inline_btn_rasp = InlineKeyboardMarkup()
        btnr4 = InlineKeyboardButton(f'1.  {element[3].text}', callback_data='data_3')
        inline_btn_rasp.row(btnr4)
        btnr3 = InlineKeyboardButton(f'2.  {element[2].text}', callback_data='data_2')
        inline_btn_rasp.row(btnr3)
        btnr2 = InlineKeyboardButton(f'3.  {element[1].text}', callback_data='data_1')
        inline_btn_rasp.row(btnr2)
        btnr1 = InlineKeyboardButton(f'4.  {element[0].text}', callback_data='data_0')
        inline_btn_rasp.row(btnr1)

        # sled_btn = InlineKeyboardButton('След.', callback_data='sled_sps')
        # pred_btn = InlineKeyboardButton('Пред.', callback_data='pred_sps')
        # inline_btn_rasp.row(pred_btn, sled_btn)

        inline_btn_rasp.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Ближайшие мероприятия",
            reply_markup=inline_btn_rasp
        )
#*приходит на свадьбу, жмет руку невесте*
#-я пришел к вам с пустыми руками, но не с пустыми яйцами
    '''if callback.data == 'sled':
        e += 3
        callback_data='look_rasp'
        callback_message(callback)'''

    if callback.data == 'look_lk':
        inline_btn_l_k = InlineKeyboardMarkup()

        btn_izbr = InlineKeyboardButton('Избранное', callback_data='like_films_mp')
        inline_btn_l_k.row(btn_izbr)
        btn_rec = InlineKeyboardButton('Рекомендации', callback_data='rec')
        inline_btn_l_k.row(btn_rec)
        btn_sms = InlineKeyboardButton('Уведомления', callback_data='sms')
        inline_btn_l_k.row(btn_sms)
        inline_btn_l_k.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Настройки уведомлений,\nпросмотр избранного,\nрекомендации — всё это находится здесь.',
            reply_markup=inline_btn_l_k
        )

    if callback.data == 'like_films_mp':
        inline_btn_like = InlineKeyboardMarkup()

        btn_mplike = InlineKeyboardButton('Мероприятия', callback_data='mp_like')
        btn_filmslike = InlineKeyboardButton('Фильмы', callback_data='films_like')
        inline_btn_like.row(btn_mplike, btn_filmslike)
        inline_btn_like.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Любимые фильмы и события',
            reply_markup=inline_btn_like
        )

    if callback.data == 'rec':
        inline_btn_rec = InlineKeyboardMarkup()

        btn_mprec = InlineKeyboardButton('Мероприятия', callback_data='mp_rec')
        btn_filmsrec = InlineKeyboardButton('Фильмы', callback_data='films_rec')
        inline_btn_rec.row(btn_mprec, btn_filmsrec)
        inline_btn_rec.row(globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Здесь вы можете найти фильмы и мероприятия по вашим предпочтениям.',
            reply_markup=inline_btn_rec
        )

    if callback.data == 'films_like':
        user = session.query(User_favor).filter_by(id_user=callback.message.chat.id).all()
        makrup_favor = InlineKeyboardMarkup()
        for info_user in user:
            movie_id = info_user.favor
            try:
                movie = tmdb.Movies(movie_id).info(language="ru")
                film_btn = InlineKeyboardButton(movie['title'], callback_data=f'movie_{movie_id}')
            except:
                film_btn = InlineKeyboardButton(find_f()[0][int(movie_id)], callback_data=f'film_{movie_id}')

            makrup_favor.row(film_btn)
        makrup_favor.row(Globus.nazad_btn)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Ваши любимые фильмы',
            reply_markup=makrup_favor
        )

    if callback.data == 'nazad':
        try:
            bot.delete_message(callback.message.chat.id, callback.message.id)
        except Exception as e:
            print(e)
        main_s(callback)

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
