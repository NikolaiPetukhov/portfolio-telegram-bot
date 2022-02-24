from telegram import InputMediaPhoto


def message_update(TelegramBot, chat_id, message_id, msg, parse_mode=None):
    try:
        TelegramBot.edit_message_text(
            text=msg['text'],
            message_id=message_id,
            chat_id=chat_id,
            parse_mode=parse_mode,
        )
    except Exception as e:
        print('text exception: ', e)
    try:
        TelegramBot.edit_message_reply_markup(
            reply_markup=msg['reply_markup'],
            message_id=message_id,
            chat_id=chat_id,
        )
    except Exception as e:
        print('reply markup exception: ', e)
    return True