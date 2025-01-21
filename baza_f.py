import telebot
import sqlite3

API_TOKEN = '8027072430:AAG-uhnAuXyr1VpRFSkGSpM49AEBq2Kilrs'

bot = telebot.TeleBot(API_TOKEN)
login = None

#ВОПРОС!!! правда что глобал переменные в боте это плохо, что при одновременном запросе к боту с логином может записать 2 в 1 или переменные типа глобал локальны и при одновременном запросе все будет ок
#ВОПРОС!!! как ограничить колво символов в логине и пароле, через Varchar не работает

@bot.message_handler(commands=['start'])
def start(message):
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

    bot.send_message(message.chat.id, 'Придумайте логин')
    bot.register_next_step_handler(message, handle_user_login)


def handle_user_login(message):
    global login
    login = message.text.strip()

    conn = sqlite3.connect('bazareg.bz')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users WHERE login=?', (login,))
    count = cursor.fetchone()[0]

    if count > 0:
        bot.send_message(message.chat.id, 'Такой логин уже занят. Придумайте другой.')
        bot.register_next_step_handler(message, handle_user_login)
    else:
        bot.send_message(message.chat.id, 'Придумайте пароль')
        bot.register_next_step_handler(message, handle_user_password)

    cursor.close()
    conn.close()


def handle_user_password(message):
    password = message.text.strip()

    conn = sqlite3.connect('bazareg.bz')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO users (login, pass) VALUES (?, ?)', (login, password))
    conn.commit()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('sps_users_dev', callback_data='users_sps'))
    bot.send_message(message.chat.id, f'Успешно!\nВаш логин: {login}\nВаш пароль: {password}', reply_markup=markup)
    cursor.close()
    conn.close()


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    conn = sqlite3.connect('bazareg.bz')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    info_au = ''
    for oneAU in all_users:
        info_au += f'Логин: {oneAU[1]}\nПароль: {oneAU[2]}\n\n'

    cursor.close()
    conn.close()

    bot.send_message(call.message.chat.id, f'Все пользователи:\n\n{info_au}')


bot.polling(none_stop=True)