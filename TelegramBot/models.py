from django.db import models
from . import farfetchscrapper
import json


class BotUser(models.Model):
    username = models.CharField(verbose_name="Username", max_length=1024, blank=True, null=True)
    first_name = models.CharField(verbose_name="Name", max_length=1024, blank=True, null=True)
    last_name = models.CharField(verbose_name="Surname", max_length=1024, blank=True, null=True)
    chat_id = models.IntegerField(verbose_name="Id of a chat", unique=True)
    is_admin = models.BooleanField(verbose_name="Admin", default=False)

    def __str__(self):
        return f"{self.username}"

    @staticmethod
    def get_or_create_from_chat(chat):
        obj, created = BotUser.objects.get_or_create(
            chat_id=chat.id
        )
        obj.username = chat.username
        obj.last_name = chat.last_name
        obj.first_name = chat.first_name
        obj.save()
        return obj, created

    @staticmethod
    def get_by_chat_id(chat_id):
        try: 
            obj = BotUser.objects.get(chat_id=chat_id)
        except:
            obj = None
        return obj


class Quiz(models.Model):
    name = models.CharField(max_length = 128)
    description = models.CharField(max_length = 1024)
    number_of_questions = models.IntegerField(blank=True, null=True)
    result_interpretation = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def interpret_result(self, score):
        try:
            r_i = self.result_interpretation
            for key in r_i.keys():
                bottom, upper = int(key.split("-")[0]), int(key.split("-")[1])
                if (score>=bottom and score<=upper):
                    return r_i[key]
        except Exception as e:
            return ""


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE)
    number = models.IntegerField()
    text = models.CharField(max_length = 1024)
    # answers = {
    #   "1": "first answer",
    #   "2": "second answer",
    # }
    answers = models.JSONField(max_length=1024)
    points = models.IntegerField(default=1)
    show_type = models.IntegerField(default=1)

    def set_answers_from_dict(self, dictionary):
        self.answers = dictionary
        self.save()

    def get_points(self, answer):
        return self.points


class QuestionOneAnswer(Question):
    right_answer = models.IntegerField()

    def set_right_answer(self, answer):
        self.right_answer = answer
        self.save()

    def get_result(self, answer):
        return True if answer == self.right_answer else False

    def get_points(self, answer):
        return self.points if int(answer) == self.right_answer else 0


class QuestionMultipleAnswers(Question):
    right_answers = models.CharField(max_length = 32)

    def set_right_answers(self, answers_list):
        self.right_answers = ' '.join(answers_list)
        self.save()

    def get_result(self, answers_list):
        return True if self.right_answers == ' '.join(answers_list.sort()) else False

    def get_points(self, answers):
        return self.points if answers == self.right_answers else 0
    

class QuestionAnyAnswers(Question):
    # answer_points = {
    #   "1": "1",
    #   "2": "0",
    # }
    answers_points = models.JSONField(max_length = 64)

    def set_answers_points_from_dict(self, dictionary):
        self.answer_points = dictionary
        self.save()

    def get_result(self, answers):
        points = self.answers_points
        result = 0
        for i in answers:
            try: result = result + int(points[str(i)])
            except:
                pass
        return result

    def get_points(self, answers):
        return self.points*self.get_result(answers.split())


class Book(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1024)
    cover = models.ImageField(upload_to='books/covers/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_pages(self):
        total = 0
        pages = Page.objects.filter(book=self)
        for page in pages:
            if page.number > total: total=page.number
        return total


class Page(models.Model):
    number = models.IntegerField()
    text = models.TextField(max_length=4096)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.book.name+". page: "+str(self.number)