from django.urls import path
from . import views

urlpatterns = [
    path('domains/', views.DomainListView.as_view(), name='domain-list'),
    path('domains/<int:pk>/objectives/', views.ObjectiveListView.as_view(), name='objective-list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('questions/', views.QuestionListView.as_view(), name='question-list'),
]
