import json, datetime, random
from . import bot_pages, farfetchscrapper
from .utils import *
from .models import Quiz, Question, QuestionAnyAnswers, QuestionMultipleAnswers, QuestionOneAnswer, Book, Page
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

'''
All functions should receive kwargs with next arguments:
kwargs["telegram_bot"] = <telegram.Bot> object
kwargs["chat_id"] = <int> chat id
kwargs["message_id"] = <int> message id // is used to update message

All functions should return {"text": "some_text" }

bot_pages contains functions, each of it returns msg = {
    "text": " some text ",
    "reply_markup": <InlineKeyboardMarkup> OR <ReplyKeyboardMarkup> object
}

If you need to update the message, use message_update function
If you need to send new message, use telegram.Bot.sendMessage function
you can get telegram.Bot instance by kwargs.get("telegram_bot")
'''

user_answers = {}
user_items = {}

def unknown(*args, **kwargs):
    return {}

def start(*args, **kwargs):
    return main_menu(*args, **kwargs)

def main_menu(*args, **kwargs):
    print('callback_start')
    bot_user = kwargs.get("bot_user")
    global user_items
    user_items[str(bot_user.id)]=[]
    msg, error = bot_pages.main_menu_page()

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    if error:
        telegram_bot.sendMessage(448919113, str(error))
        telegram_bot.sendMessage(chat_id, "Sorry, some error ocured")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans

def submenu_1(*args, **kwargs):
    print('callback_submenu_1')

    msg = bot_pages.submenu_1()

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans

def show_quizes(*args, **kwargs):
    print('show_quizes')
    reply_markup = []
    quizes = Quiz.objects.all()

    for quiz in quizes:
        reply_markup.append([InlineKeyboardButton(text=quiz.name, callback_data=json.dumps({
            "comm": "show_quiz",
            "args": {
                "q_id": quiz.id,
            },
        }))])
    reply_markup.append([InlineKeyboardButton(text="назад", callback_data=json.dumps({
            "comm": "main_menu",
            "args": {},
        }))])
    msg = {
        "text": "Выберите тест из списка ниже",
        "reply_markup": InlineKeyboardMarkup(reply_markup),
    }

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans


def show_quiz(*args, **kwargs):
    print("im in show_quiz")
    quiz_id = int(kwargs.get("q_id"))
    quiz = Quiz.objects.get(pk=quiz_id)
    bot_user = kwargs.get("bot_user")
    reply_markup = [
        [InlineKeyboardButton(text="начать тест", callback_data=json.dumps({
            "comm": "start_quiz",
            "args": {
                "q_id": quiz.id,
                "u_id": bot_user.id,
            }
        }))],
        [InlineKeyboardButton(text="назад", callback_data=json.dumps({
            "comm": "show_quizes",
            "args": {},
        }))],
    ]
    msg = {
        "text": f"{quiz.name}\n{quiz.description}",
        "reply_markup": InlineKeyboardMarkup(reply_markup),
    }

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans

def start_quiz(*args, **kwargs):
    global user_answers
    user_id = kwargs.get("u_id")
    quiz_id = kwargs.get("q_id")
    user_answers[user_id] = {}
    user_answers[user_id][quiz_id] = {}
    kwargs.pop("u_id")
    kwargs["q_n"] = 1
    return show_question(*args, **kwargs)

def show_question(*args, **kwargs):
    print("im in show_question")
    quiz_id = int(kwargs.get("q_id"))
    question_number = int(kwargs.get("q_n"))
    bot_user = kwargs.get("bot_user")
    quiz = Quiz.objects.get(pk=quiz_id)
    question = Question.objects.filter(quiz=quiz, number=question_number).first()
    if not question:
        return end_quiz(*args, **kwargs)
    
    for subclass in Question.__subclasses__():
        try: question = subclass.objects.get(pk=question.id)
        except:
            pass
    
    global user_answers
    try:
        flagged = user_answers[bot_user.id][quiz_id][question_number]
    except:
        flagged = []
    
    return_button = {
        "text": "Назад",
        "comm": "main_menu",
        "args": {},
    }
    msg = bot_pages.get_question_page_by_type(type=question.show_type)(question, flagged, return_button=return_button)
    #msg = bot_pages.question_page_default(question, flagged)

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans


def save_answer(bot_user_id, quiz_id, question, answer):
    global user_answers
    if not bot_user_id in user_answers.keys():
        user_answers[bot_user_id] = {}
    if not quiz_id in user_answers[bot_user_id].keys():
        user_answers[bot_user_id][quiz_id] = {}
    if not question.id in user_answers[bot_user_id][quiz_id].keys():
        user_answers[bot_user_id][quiz_id][question.number] = ""
    
    if not question:
        return end_quiz()
    elif isinstance(question, QuestionOneAnswer):
        if user_answers[bot_user_id][quiz_id][question.number] == str(answer):
            user_answers[bot_user_id][quiz_id][question.number] = "0"
        else:
            user_answers[bot_user_id][quiz_id][question.number] = str(answer)
    elif isinstance(question, QuestionMultipleAnswers) or isinstance(question, QuestionAnyAnswers):
        current_user_answers = user_answers[bot_user_id][quiz_id][question.number]
        if str(answer) in current_user_answers.split():
            s = current_user_answers.split()
            s.remove(str(answer))
            s.sort()
            current_user_answers = ' '.join(s)
        else:
            s = current_user_answers.split()
            s.append(str(answer))
            s.sort()
            current_user_answers = ' '.join(s)
        user_answers[bot_user_id][quiz_id][question.number] = current_user_answers
    return True


def a_p(*args, **kwargs):
    return answer_pressed(*args, **kwargs)

def answer_pressed(*args, **kwargs):
    quiz_id = kwargs.get("q_id")
    question_number = int(kwargs.get("q_n"))
    answer_number = int(kwargs.get("a_n"))
    bot_user = kwargs.get("bot_user")
    global user_answers
    quiz = Quiz.objects.get(pk=quiz_id)
    question = Question.objects.filter(quiz=quiz, number=question_number).first()
    if not question:
        return end_quiz()
    
    for subclass in Question.__subclasses__():
        try: question = subclass.objects.get(pk=question.id)
        except:
            pass
    
    # Saving answer
    save_answer(bot_user.id, quiz.id, question, answer_number)

    # After saving the answer we view same question to the user
    #flag = 1 if next_question else 0
    next_question = question.show_type == 2
    kwargs["q_n"] = question.number + (1 if next_question else 0)
    return show_question(*args, **kwargs)


def calculate_score(bot_user, quiz):
    global user_answers
    score = 0
    questions = Question.objects.filter(quiz=quiz)
    for question in questions:
        for subclass in Question.__subclasses__():
            try: question = subclass.objects.get(pk=question.id)
            except:
                pass
        try: 
            answer = user_answers[bot_user.id][quiz.id][question.number]
        except: answer = "0"
        score += question.get_points(answer)
    return score


def end_quiz(*args, **kwargs):
    bot_user = kwargs.get("bot_user")
    quiz_id = kwargs.get("q_id")
    quiz = Quiz.objects.get(pk=quiz_id)

    score = calculate_score(bot_user, quiz)
    result = quiz.interpret_result(score)

    msg = bot_pages.quiz_ended_page(score, result)

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans


def show_books(*args, **kwargs):
    print('show_books')
    reply_markup = []
    books = Book.objects.all()

    for book in books:
        reply_markup.append([InlineKeyboardButton(text=book.name, callback_data=json.dumps({
            "comm": "show_book",
            "args": {
                "b_id": book.id,
            },
        }))])
    reply_markup.append([InlineKeyboardButton(text="назад", callback_data=json.dumps({
            "comm": "main_menu",
            "args": {},
        }))])
    msg = {
        "text": "Выберите книгу из списка ниже",
        "reply_markup": InlineKeyboardMarkup(reply_markup),
    }

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans

def start_read_book(*args, **kwargs):
    print("im in start_read_book")
    return book_page(*args, **kwargs)


def show_book(*args, **kwargs):
    print("im in show_book")
    book_id = int(kwargs.get("b_id"))
    book = Book.objects.get(pk=book_id)
    bot_user = kwargs.get("bot_user")
    reply_markup = [
        [InlineKeyboardButton(text="читать книгу", callback_data=json.dumps({
            "comm": "start_read_book",
            "args": {
                "b_id": book_id,
                "p_n": 1,
            }
        }))],
        [InlineKeyboardButton(text="назад", callback_data=json.dumps({
            "comm": "show_books",
            "args": {},
        }))],
    ]
    msg = {
        "text": f"{book.name}\n{book.description}",
        "reply_markup": InlineKeyboardMarkup(reply_markup),
    }

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans

def book_page(*args, **kwargs):
    print("im in book_page")
    book_id = kwargs.get("b_id")
    page_number = kwargs.get("p_n")
    book = Book.objects.get(pk=book_id)
    page = Page.objects.filter(book=book, number=page_number).first()
    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")

    msg = bot_pages.book_page(book, page)

    message_id = kwargs.get("message_id")
    message_update(telegram_bot, chat_id, message_id, msg)
    ans = {
        "text": "loading..."
    }
    return ans


def farfetch(*args, **kwargs):
    print("im in farfetch")
    bot_user = kwargs.get("bot_user")
    size = kwargs.get("size", 5)
    scrap()
    try:
        with open(f'items.json', 'r', encoding='utf-8') as f:
            items = random.choices(json.load(f)["listingItems"]["items"], k=size)
    except:
        items = []
    global user_items
    user_items[str(bot_user.id)] = items
    return farfetch_page(*args, **kwargs)


def farfetch_page(*args, **kwargs):
    print("im in farfetch_page")
    bot_user = kwargs.get("bot_user")
    global user_items
    items = user_items.get(str(bot_user.id))
    page = kwargs.get("page", 1)
    
    #items = farfetchscrapper.get_listings()["listingItems"]["items"][:size]
    
    msg, error = bot_pages.catalogue_page(items, page)
    parse_mode = msg.get("parse_mode", None)

    telegram_bot = kwargs.get("telegram_bot")
    chat_id = kwargs.get("chat_id")
    message_id = kwargs.get("message_id")
    if error:
        telegram_bot.sendMessage(448919113, str(error))
        telegram_bot.sendMessage(chat_id, "Sorry, some error ocured")
    message_update(telegram_bot, chat_id, message_id, msg, parse_mode=parse_mode)
    ans = {
        "text": "loading..."
    }
    return ans

def scrap(filename="items"):
    print("im in scrap")
    try:
        with open(f'{filename}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            date = datetime.datetime.strptime(data.get("date"), "%Y-%m-%d").date()
        if date+datetime.timedelta(days=7) < datetime.date.today():
            print("doing request to farfetch")
            farfetchscrapper.print_to_file("items")
    except Exception as e:
        print(e)
        print("doing request to farfetch from except")
        farfetchscrapper.print_to_file("items")