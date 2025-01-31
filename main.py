import json
import os
from functools import wraps
from random import choice

from telebot import TeleBot
from telebot.types import Message

TOKEN = '7066186948:AAHYaKGd5gkAgDpUkHkGMhipRXi2ms3Q_Do'
bot = TeleBot(TOKEN)


with open('telebot2/cities.txt', 'r', encoding='utf-8') as f:
    # cities = []
    # for line in f.readlines():
    #     cities.append(line.strip().lower())
    cities = [word.strip().lower() for word in f.readlines()]
    
if os.path.exists("user_data.json"):
    with open('user_data.json', 'r', encoding='utf-8') as file:
        user_data = json.load(file)
else:
    user_data = {}

def save_user_data():
    with open('user_data.json', 'w', encoding='utf-8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)    

def user_action(func):
    @wraps(func)
    def wrapper(message:Message, *args, **kwargs):
        user_id = str(message.from_user.id)
        name = message.from_user.username
        if user_id not in user_data:
            user_data[user_id] = {
                "name": name,
                "used_words": [],
                "letter": "", 
                "points": 0
            }
        save_user_data()
        return func(message, *args, **kwargs)
    return wrapper

def select_letter(text: str) -> str:
    i = 1
    while text[-1 * i] in ["ы", "ь", "ъ", "й"]:
        i += 1
    return text[-1 * i]

@bot.message_handler(commands=['start'])
@user_action
def start(message: Message):
    bot.send_message(message.chat.id, 
        f"Привет {message.from_user.username}! Я бот, играющий в города. \
        \n Чтобы начать, нажми /goroda")

@bot.message_handler(commands=['goroda'])
@user_action
def start_game(message: Message):
    user_id = str(message.from_user.id)
    city = choice(cities)
    user_data[user_id]["letter"] = select_letter(city)
    user_data[user_id]["used_words"].append(city)
    save_user_data()
    bot.send_message(message.chat.id, city)

@bot.message_handler()
@user_action
def play(message: Message):
    user_id = str(message.from_user.id)
    user_info = user_data[user_id]
    
    if not user_info["letter"]:
        bot.send_message(message.chat.id, "Игра ещё не начата! Нажми /goroda чтобы начать.")
        return
    text = message.text.lower()
    if text in user_info["used_words"]:
        bot.send_message(message.chat.id, "Город уже назывался!")
        return
    if text[0] != user_info["letter"]:
        bot.send_message(message.chat.id, "Не та буква!") 
        return
    if text in cities:
        user_info["used_words"].append(text)
        user_info["points"] += 1
        user_info["letter"] = select_letter(text)
        
        for city in cities:
            if city[0] == user_info["letter"] and city not in user_info["used_words"]:
                user_info["used_words"].append(city)
                user_info["letter"] = select_letter(city)
                save_user_data()
                bot.send_message(message.chat.id, city)
                return
        bot.send_message(message.chat.id, "Я проиграл!")
        user_info["letter"] = ""
        save_user_data()
    else:
        bot.send_message(message.chat.id, "Такого города не существует!")    


bot.polling(non_stop= True)
