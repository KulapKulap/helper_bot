#https://openweathermap.org
#pip install requests+import requests

import telebot
import requests
import json
import math
from currency_converter import CurrencyConverter
from telebot import types

bot = telebot.TeleBot('6067689178:AAFe47z6gqKFTgEPCHBSYkQxxc-YP1de0ks')
API = '7f061594b3629ab634fd104c5c98f852'

currency = CurrencyConverter()

amount = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'How can I help you?')
    markup2 = types.InlineKeyboardMarkup(row_width=2)
    btn1_2 = types.InlineKeyboardButton('weather', callback_data='weather')
    btn2_2 = types.InlineKeyboardButton('currency', callback_data='currency')
    markup2.add(btn1_2, btn2_2)
    bot.send_message(message.chat.id, 'Choose an option:', reply_markup=markup2)

@bot.callback_query_handler(func=lambda call: call.data == 'weather')
def weather_query(call):
    bot.send_message(call.message.chat.id, "Please enter the city name:")
    bot.register_next_step_handler(call.message, getWeather)

@bot.callback_query_handler(func=lambda call: call.data == 'currency')
def currency_query(call):
    bot.send_message(call.message.chat.id, "Please enter the amount:")
    bot.register_next_step_handler(call.message, summ)

def getWeather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = math.trunc(data["main"]["temp"])
        bot.reply_to(message, f'Now the weather in {city.capitalize()} is: {temp}°C')

        image = 'sun.png' if temp > 15.0 else 'cloud.png'
        file = open('./img/' + image, 'rb')
        bot.send_photo(message.chat.id, file)
        start(message)
    else:
        bot.reply_to(message, f'No such city: {city.capitalize()}')
        start(message)

def summ(message):
    global amount

    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Only digits')
        bot.register_next_step_handler(message, summ)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Another', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Choose a currency pair:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Amount must be more than 0')
        bot.register_next_step_handler(message, summ)

@bot.callback_query_handler(func=lambda call: call.data != 'else' and '/' in call.data)
def currency_convert(call):
    global amount
    values = call.data.upper().split('/')
    try:
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Result: {round(res, 2)}. One more time? Enter amount:')
        bot.register_next_step_handler(call.message, summ)
    except Exception:
        bot.send_message(call.message.chat.id, 'Invalid currency pair. Please try again.')
        bot.register_next_step_handler(call.message, summ)

@bot.callback_query_handler(func=lambda call: call.data == 'else')
def currency_else(call):
    bot.send_message(call.message.chat.id, 'Enter a pair of currencies using "/" (e.g., USD/EUR):')
    bot.register_next_step_handler(call.message, my_currency)

def my_currency(message):
    global amount
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Result: {round(res, 2)}. One more time, please enter amount:')
        bot.register_next_step_handler(message, summ)
    except Exception:
        bot.send_message(message.chat.id, 'Enter correct currencies using "/"')
        bot.register_next_step_handler(message, my_currency)

bot.polling(none_stop=True)
