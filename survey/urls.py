from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import AnswerViewSet, QuestionViewSet, SurveyViewSet, SurveyForUser, \
    create_user_answer, result_survey

router = SimpleRouter()
router.register('survey', SurveyViewSet)
router.register('question', QuestionViewSet)
router.register('answer', AnswerViewSet)
router.register('surveylist', SurveyForUser)

urlpatterns = [
    path('', include(router.urls)),
    path('useranswer/', create_user_answer),  # ответы на опросники
    path('result/', result_survey),  # результат опросника по авторизованному юзеру
    path('result/<int:user>', result_survey),  # результат опросника по анонимному пользователю
]
