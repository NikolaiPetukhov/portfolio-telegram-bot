from django.contrib import admin
from .models import *


admin.site.register(BotUser)
admin.site.register(Quiz)
#admin.site.register(Question)
admin.site.register(QuestionOneAnswer)
admin.site.register(QuestionMultipleAnswers)
admin.site.register(QuestionAnyAnswers)

admin.site.register(Book)
admin.site.register(Page)