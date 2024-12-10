from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('entity_list', views.entity_list, name='entity_list'),
    path('update_entity/<int:entity_id>/', views.update_entity, name='update_entity'),
    path('delete_entity/<int:entity_id>/', views.delete_entity, name='delete_entity'),
    path('report/question/', views.question_report, name='question_report'),
    path('answer_report/', views.answer_report, name='answer_report'),
    path('edit_survey/<int:survey_id>/', views.edit_survey, name='edit_survey'),
    path('get_choices/<int:question_id>/', views.get_choices, name='get_choices'),
    path('creates/', views.create_entitys, name='create_entitys'),
    path('create-sector/', views.create_sector, name='create_sector'),
    path('categories/<str:pk>/', views.show_categories, name='categories'),  # pk مشفر
    path('submit/<str:category>/<str:pk>/', views.submit_survey, name='submit_survey'),  # pk مشفر
    path('survey/<int:survey_id>/', views.show_survey, name='view_survey'),
    path('delete_survey/<int:survey_id>/<str:entity_id>/', views.delete_survey, name='delete_survey'),  # entity_id مشفر
    path('questions/<str:category>/<str:pk>/', views.show_questions_by_category, name='show_questions_by_category'),  # pk مشفر 
    path('add-question/', views.add_question, name='add_question'),
    path('questions-list/', views.questions_list, name='questions_list'),  # الرابط لعرض جدول الأسئلة
    path('update_question/<int:question_id>/', views.update_question, name='update_question'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
  
]
