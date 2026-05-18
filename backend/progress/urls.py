from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.SessionCreateView.as_view(), name='session-create'),
    path('sessions/<int:pk>/next/', views.SessionNextQuestionView.as_view(), name='session-next'),
    path('sessions/<int:pk>/answers/', views.SessionAnswerView.as_view(), name='session-answer'),
    path('sessions/<int:pk>/results/', views.SessionResultsView.as_view(), name='session-results'),
    path('sessions/<int:pk>/complete/', views.SessionCompleteView.as_view(), name='session-complete'),
    path('progress/', views.ProgressOverviewView.as_view(), name='progress-overview'),
    path('progress/domains/', views.DomainProgressView.as_view(), name='progress-domains'),
    path('progress/objectives/', views.ObjectiveProgressView.as_view(), name='progress-objectives'),
]
