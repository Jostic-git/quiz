from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    dateStart = models.DateTimeField(verbose_name='Дата старта')
    dateEnd = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.title


class Question(models.Model):
    QUEST_TYPE = (
        ('TX', 'Ответ текстом'),
        ('SC', 'Ответ с выбором одного варианта'),
        ('MC', 'Множественный выбор')
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    questtext = models.TextField()
    questtype = models.CharField(max_length=3, choices=QUEST_TYPE, default='TX')

    def __str__(self):
        return self.questtext


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answertext = models.CharField(max_length=200, verbose_name='Текст ответа')
    isCorrect = models.BooleanField(default=False, verbose_name='Правильный ответ')

    def __str__(self):
        return self.answertext


class UserSession(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='UserSessions')
    dateStart = models.DateTimeField(auto_now_add=True)
    dateEnd = models.DateTimeField(null=True, blank=True)
    userid = models.IntegerField()
    isAnonymous = models.BooleanField(default=False)


class UserAnswer(models.Model):
    userSession = models.ForeignKey(UserSession, on_delete=models.CASCADE,
                                    related_name='question_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=50, blank=True, null=True, verbose_name='Правильный ответ')
