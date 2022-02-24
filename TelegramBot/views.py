import os, logging, json
# just a test
from django.views.generic import View
from django.http.response import JsonResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Get rid of this in the future. 
# We should take bot token from environment variables
from django.conf import settings

import telegram
from telegram import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from .models import BotUser
from . import commands, callback_commands

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", settings.TELEGRAM_BOT_TOKEN)
TelegramBot = telegram.Bot(telegram_bot_token)
logger = logging.getLogger("telegram.bot")


def get_callback_command(callback_data):
    data = json.loads(callback_data)
    command_name = data.get("comm", "unknown")
    args = data.get("args", {})
    for name, val in callback_commands.__dict__.items():
        if (name == command_name and callable(val)):
            return val, args
    return callback_commands.unknown, args

def get_command(message_text):
    try:
        command_name = message_text.split()[0].lower()
        if command_name[0] == '/': command_name = command_name[1:]
        args = message_text.split()[1:]
    except:
        command_name = "unknown"
    for name, val in commands.__dict__.items():
        if (name == command_name and callable(val)):
            return val, args
    return commands.unknown, args

class CommandReceiveView(View):
    def post(self, request, bot_token):
        if bot_token != telegram_bot_token:
            return HttpResponseForbidden("Invalid token")

        raw = request.body.decode("utf-8")
        logger.info(raw)
        data = json.loads(raw)

        is_edit_message = data.get("edited_message", False)
        is_callback_query = data.get("callback_query", False)
        is_my_chat_member = data.get("my_chat_member", False)

        if is_my_chat_member:
            pass

        elif is_edit_message:
            pass

        elif is_callback_query:
            callback_query = CallbackQuery.de_json(data["callback_query"], TelegramBot)
            bot_user = BotUser.get_by_chat_id(callback_query.from_user.id)
            callback_data = callback_query.data
            print(callback_data)

            func, args = get_callback_command(callback_data)
            args["telegram_bot"] = TelegramBot
            args["bot_user"] = bot_user
            args["chat_id"] = callback_query.message.chat_id
            args["message_id"] = callback_query.message.message_id
            
            answer = func(**args)

            answer["callback_query_id"] = callback_query.id
            try: 
                TelegramBot.answer_callback_query(
                **answer
            )
            except:
                pass

        else:
            message = Message.de_json(data["message"], TelegramBot)
            bot_user, created = BotUser.get_or_create_from_chat(message.chat)
            message_text = message.text
            print(message_text)
            
            func, args = get_command(message_text)
            kwargs = {}
            kwargs["telegram_bot"] = TelegramBot
            kwargs["bot_user"] = bot_user
            kwargs["chat_id"] = message.chat_id
            kwargs["message_id"] = message.message_id

            func(*args, **kwargs)
        return JsonResponse({}, status=200)

    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
