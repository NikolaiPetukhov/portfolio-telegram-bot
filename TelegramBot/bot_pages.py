import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from . import farfetchscrapper
from telegram.utils.helpers import escape_markdown


def main_menu_page(error=None):   
    reply_keyboard = [
        [InlineKeyboardButton(text="Викторины/Тесты", callback_data=json.dumps({
            "comm": "show_quizes",
            "args": {}
        }))],
        [InlineKeyboardButton(text="Книги", callback_data=json.dumps({
            "comm": "show_books",
            "args": {}
        }))],
        [InlineKeyboardButton(text="Farfetch", callback_data=json.dumps({
            "comm": "farfetch",
            "args": {}
        }))],
        [InlineKeyboardButton(text="Заказать бота", url='tg://user?id=448919113')],
    ]
    msg = {
        "text": "Это главное меню бота.\n\nНиже вы можете ознакомиться с функционалом.\n\n\
Раздел Викторины/Тесты - Викторины или тесты с любым количеством вопросов и ответов,\
    в том числе с вводом ответа пользователем. Или психологические тесты с интерпретацией результата теста.\n\n\
Раздел Книги - Постраничный вывод данных \n\n\
Раздел Farfetch - Парсит сайт Farfetch.com и выводит товары в виде каталога", 
        "reply_markup": InlineKeyboardMarkup(reply_keyboard),
    }
    return msg, error

def submenu_1():
    reply_keyboard = [
        [InlineKeyboardButton(text="Назад", callback_data=json.dumps({
            "comm": "main_menu",
            "args": {}
        }))],
    ]
    msg = {
        "text": "This is the submenu_1",
        "reply_markup": InlineKeyboardMarkup(reply_keyboard),
    }
    return msg


def get_question_page_by_type(type):
    question_pages = {
        1: question_page_default,
        2: question_page_type_2,
    }
    return question_pages.get(type)

def question_page_type_2(question, flagged=[], emoji="✅", return_button=None):
    reply_keyboard = []
    for i, answer in question.answers.items():
        reply_keyboard.append([InlineKeyboardButton(text=emoji+answer if i in flagged else answer, callback_data=json.dumps({
            "comm": "a_p",
            "args": {
                "q_id": question.quiz.id,
                "q_n": question.number,
                "a_n": i,
            },
        }))])
    if return_button:
        reply_keyboard.append([InlineKeyboardButton(text=return_button["text"], callback_data=json.dumps({
            "comm": return_button["comm"],
            "args": return_button["args"],
        }))])
    msg = {
        "text": f"{question.number}/{question.quiz.number_of_questions}\n{question.text}",
        "reply_markup": InlineKeyboardMarkup(reply_keyboard),
    }
    return msg

def question_page_default(question, flagged=[], emoji="✅", return_button=None):
    reply_keyboard = []
    for i, answer in question.answers.items():
        reply_keyboard.append([InlineKeyboardButton(text=emoji+answer if i in flagged else answer, callback_data=json.dumps({
            "comm": "a_p",
            "args": {
                "q_id": question.quiz.id,
                "q_n": question.number,
                "a_n": i,
            },
        }))])
    buttons = []
    if question.number > 1:
        buttons.append(InlineKeyboardButton(text="<<", callback_data=json.dumps({
            "comm": "show_question",
            "args": {
                "q_id": question.quiz.id,
                "q_n": question.number-1,
            }
        })))
    #if question.number < question.quiz.number_of_questions:
    if True:
        buttons.append(InlineKeyboardButton(text=">>", callback_data=json.dumps({
            "comm": "show_question",
            "args": {
                "q_id": question.quiz.id,
                "q_n": question.number+1,
            }
        })))
    reply_keyboard.append(buttons)

    if return_button:
        reply_keyboard.append([InlineKeyboardButton(text=return_button["text"], callback_data=json.dumps({
            "comm": return_button["comm"],
            "args": return_button["args"],
        }))])
    msg = {
        "text": f"{question.number}/{question.quiz.number_of_questions}\n{question.text}",
        "reply_markup": InlineKeyboardMarkup(reply_keyboard),
    }
    return msg


def quiz_ended_page(score, result):
    msg = {
        "text": f"Congratulations! quiz is ended.\nYour score: {score}!\n{result}"
    }
    return msg


def book_page(book, page):
    reply_keyboard = [
        [
        ]
    ]
    pages = book.get_pages()
    if pages <= 5:
        for p in range(pages):
            s = f"-{page}-" if page==p+1 else str(p+1)
            reply_keyboard[0].append(InlineKeyboardButton(text=s, callback_data=json.dumps({
            "comm": "book_page",
            "args": {
                "b_id": book.id,
                "p_n": p+1,
            }
        })),)
    else:
        if page.number>2:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(1), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": 1,
                }
            })),)
        if page.number>=pages-1:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(pages-3), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": pages-3,
                }
            })))
        if page.number>=pages:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(pages-2), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": pages-2,
                }
            })))
        if page.number>1:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(page.number-1), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": page.number-1,
                }
            })),)
        reply_keyboard[0].append(InlineKeyboardButton(text=f"-{page.number}-", callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": page.number,
                }
            })))
        if page.number<book.get_pages(): 
            reply_keyboard[0].append(InlineKeyboardButton(text=str(page.number+1), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": page.number+1,
                }
            })))
        if page.number<2:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(3), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": 3,
                }
            })))
        if page.number<3:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(4), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": 4,
                }
            })))
        if page.number<book.get_pages()-1:
            reply_keyboard[0].append(InlineKeyboardButton(text=str(book.get_pages()), callback_data=json.dumps({
                "comm": "book_page",
                "args": {
                    "b_id": book.id,
                    "p_n": book.get_pages(),
                }
            })),)

    reply_keyboard.append([InlineKeyboardButton(text="назад", callback_data=json.dumps({
        "comm": "show_books",
        "args": {}
    }))])
    msg = {
        "text": f"{book.name}\n{page.text}",
        "reply_markup": InlineKeyboardMarkup(reply_keyboard),
    }

    return msg

def error_page(*args, **kwargs):
    return main_menu_page()

def catalogue_page(items, page):
    try: item = items[page-1]
    except Exception as e: 
        return error_page(str(e))
    text = item.get('shortDescription', 'Нет описания')
    brand = item.get('brand', {}).get('name', "Неизвестный бренд")
    img_url = item.get('images', {}).get('cutOut', "")
    product_url = f"http://farfetch.com{item.get('url')}"
    gender = item.get("gender", "Уточните в магазине")
    price = item.get('priceInfo', {}).get('finalPrice', "Уточните в магазине")
    try:
        availabe_sizes = [str(size.get("size")) for size in item.get("availableSizes", [])]
    except:
        availabe_sizes = []
    sizes = ", ".join(availabe_sizes) if availabe_sizes else "Уточните в магазине"

    reply_markup = [
        []
    ]
    if page>1:
        reply_markup[0].append(InlineKeyboardButton(text='<<', callback_data=json.dumps({
            "comm": "farfetch_page",
            "args": {
                "page": page-1
            }
        })))
    reply_markup.append([InlineKeyboardButton(text='в магазин', url=product_url)])
    if page<len(items):
        reply_markup[0].append(InlineKeyboardButton(text='>>', callback_data=json.dumps({
            "comm": "farfetch_page",
            "args": {
                "page": page+1
            }
        })))
    reply_markup.append([InlineKeyboardButton(text='return', callback_data=json.dumps({
        "comm": "main_menu",
        "args": {}
    }))])
    msg = {
        "text": f"{page}/{len(items)}\n{text}<a href='{img_url}'>{'&#8288'}</a>\nПол: {gender}\nBrand: {brand}\nSizes: {sizes}\n{price} RUB",
        "reply_markup": InlineKeyboardMarkup(reply_markup),
        "parse_mode": "html"
    }
    return msg, None