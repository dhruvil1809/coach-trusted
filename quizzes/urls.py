from django.urls import path

from .views import FieldsListView
from .views import QuizCreateView

urlpatterns = [
    path("fields/", FieldsListView.as_view(), name="fields-list"),
    path("quiz/", QuizCreateView.as_view(), name="quiz-create"),
]
