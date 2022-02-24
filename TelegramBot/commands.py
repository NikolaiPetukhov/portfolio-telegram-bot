from . import bot_pages 
from .utils import *
from telegram import ReplyKeyboardMarkup

'''
All functions should receive kwargs with next arguments:
kwargs["telegram_bot"] = <telegram.Bot> object
kwargs["chat_id"] = <int> chat id
kwargs["message_id"] = <int> message id // id of message, triggered the function. 
Can be used to reply or delete the message

Reuslt of function is not used, so it can return anything

bot_pages contains functions, each of it returns msg = {
    "text": " some text ",
    "reply_markup": <InlineKeyboardMarkup> OR <ReplyKeyboardMarkup> object
}

If you need to update the message, use message_update function
If you need to send new message, use telegram.Bot.sendMessage function
you can get telegram.Bot instance by kwargs.get("telegram_bot")
'''

def unknown(*args, **kwargs):
    print("unknown")

    reply_keyboard = [
        ['/menu', '/about'],
    ]
    msg = {
        "text": "Неизвестная команда",
        "reply_markup": ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    }

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    telegram_bot.sendMessage(chat_id, **msg)

def about(*args, **kwargs):
    print("about")

    msg = {
        "text": "About page",
    }

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    telegram_bot.sendMessage(chat_id, **msg)

def start(*args, **kwargs):
    msg = {
        "text": "Приветствую",
        "reply_markup": ReplyKeyboardMarkup([["/menu","/about"]], resize_keyboard=True),
    }
    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    telegram_bot.sendMessage(chat_id, **msg)
    return main_menu(*args, **kwargs)

def main_menu(*args, **kwargs):
    print('start')

    msg, error = bot_pages.main_menu_page()

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    telegram_bot.sendMessage(chat_id, **msg)
    if error:
        telegram_bot.sendMessage(448919113, str(error))
        telegram_bot.sendMessage(chat_id, "Sorry, some error ocured")

def menu(*args, **kwargs):
    return main_menu(*args, **kwargs)
