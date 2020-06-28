from datetime import datetime
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializeres import SurveySerializer, QuestionSerializer, AnswerSerializer, \
    UserAnswerSerializer, UserSessionSerializer
from .models import Survey, Question, Answer, UserSession, UserAnswer


@api_view(['GET'])
def result_survey(request, user=None):
    if is_anonimus := request.user.id == None:
        queryset = UserSession.objects.filter(userid=user, isAnonymous=is_anonimus)
    else:
        queryset = UserSession.objects.filter(userid=request.user.id, isAnonymous=is_anonimus)
    serializer = UserSessionSerializer(queryset, many=True)
    return Response(serializer.data)


class SurveyForUser(viewsets.ReadOnlyModelViewSet):
    queryset = Survey.objects.filter(dateEnd=None)
    serializer_class = SurveySerializer


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk=None):
        try:
            survey = Survey.objects.get(pk=pk)
        except (Survey.DoesNotExist, ValueError):
            return Response({'Survey not found'}, status=status.HTTP_404_NOT_FOUND)
        r_data = request.data.copy()
        r_data['dateStart'] = survey.dateStart
        serializer = SurveySerializer(survey, data=r_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            question = Question.objects.get(pk=request.data['question'])
        except (Question.DoesNotExist, ValueError):
            return Response({'Question not found'}, status=status.HTTP_404_NOT_FOUND)

        if question.questtype == 'TX':  # проверяем, есть ли уже ответ
            countAnswer = Answer.objects.filter(question=question).count()
            if countAnswer == 1:
                return Response({'Only one answer for this type'})

        elif (question.questtype == 'SC' and request.data['isCorrect'].lower() == 'true'.lower()):
            countAnswer = Answer.objects.filter(question=question, isCorrect=True).count()
            if countAnswer == 1:
                return Response({'Only one right answer for this type'})

        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_user_answer(request):
    # проверяем минимальные параметры входные
    if is_anonimus := request.user.id == None:  # неавторизованный лезет юзер
        if 'userid' not in request.data:
            return Response({'Login or provide used ID'})
        else:
            user_id = request.data['userid']
    else:
        user_id = request.user.id

    if 'survey' not in request.data:
        return Response({'Provide survey ID'})
    else:  # проверяем наличие открытой сессии
        try:
            survey = Survey.objects.get(pk=request.data['survey'])
        except (Survey.DoesNotExist, ValueError):
            return Response({'This Survey does not found'}, status=status.HTTP_404_NOT_FOUND)

        user_session = get_or_create_session_by_user(user_id, survey, is_anonimus)

    if 'answer' in request.data and 'question' in request.data:
        # проверим, относиться ли этот вопрос к нашему опроснику
        try:
            test_quest = Question.objects.get(pk=request.data['question'])
        except (Question.DoesNotExist, ValueError):
            return Response({'This Question does not found'}, status=status.HTTP_404_NOT_FOUND)
        if survey == test_quest.survey:
            r_data = request.data.copy()
            r_data['userSession'] = user_session.pk
            serializer = UserAnswerSerializer(data=r_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'This Question does not enter in this survey'},
                            status=status.HTTP_204_NO_CONTENT)

    # ищем неотвеченные вопросы из этого опросника и возвращаем их пользователю
    answer_quest = UserAnswer.objects.filter(userSession=user_session)
    question = Question.objects.filter(survey=user_session.survey_id).exclude(
        pk__in=list(q.question.id for q in answer_quest)).first()

    if question:
        serializer_quest = QuestionSerializer(question)
        if question.questtype == 'TX':
            serializer_quest.data['answers'][0]['answertext'] = '* * *'
        else:
            for i in range(len(serializer_quest.data['answers'])):
                serializer_quest.data['answers'][i]['isCorrect'] = '* * *'

        return Response(serializer_quest.data)
    else:
        user_session.dateEnd = datetime.now()
        user_session.save()
        return Response({'Вопросы закончились, можете просмотреть свои результаты'})


def get_or_create_session_by_user(userID, survey, isanonimus):
    user_session = UserSession.objects.filter(userid=userID, dateEnd=None, survey=survey,
                                              isAnonymous=isanonimus).first()
    if user_session:
        return user_session
    else:
        user_session = UserSession.objects.create(survey=survey, userid=userID,
                                                  isAnonymous=isanonimus)
        user_session.save()
        return user_session
