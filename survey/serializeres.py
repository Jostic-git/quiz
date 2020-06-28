from rest_framework import serializers
from .models import Survey, Question, Answer, UserAnswer, UserSession


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['pk', 'question', 'answertext', 'isCorrect']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['pk', 'survey', 'questtext', 'questtype', 'answers']


# ready
class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['pk', 'title', 'dateStart', 'dateEnd', 'description']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['pk', 'userSession', 'question', 'answer']


class UserSessionSerializer(serializers.ModelSerializer):
    class QuestionAnswersSer(serializers.ModelSerializer):
        question = QuestionSerializer()

        class Meta:
            model = UserAnswer
            fields = ['pk', 'userSession', 'question', 'answer']

    survey = SurveySerializer()
    question_answers = QuestionAnswersSer(many=True)

    class Meta:
        model = UserSession
        fields = ['survey', 'dateStart', 'dateEnd', 'userid', 'question_answers']
