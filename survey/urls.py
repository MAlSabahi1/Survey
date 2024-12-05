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
    # path('edit_survey/<str:survey_id>/', views.edit_survey, name='edit_survey'),
    path('get_choices/<int:question_id>/', views.get_choices, name='get_choices'),
    path('creates/', views.create_entitys, name='create_entitys'),
    path('create-sector/', views.create_sector, name='create_sector'),
    # عرض جميع الاستبيانات حسب التصنيف
    path('categories/<str:pk>/', views.show_categories, name='categories'),  # pk مشفر
    path('submit/<str:category>/<str:pk>/', views.submit_survey, name='submit_survey'),  # pk مشفر
    path('survey/<int:survey_id>/', views.show_survey, name='view_survey'),
    path('delete_survey/<int:survey_id>/<str:entity_id>/', views.delete_survey, name='delete_survey'),  # entity_id مشفر
    path('questions/<str:category>/<str:pk>/', views.show_questions_by_category, name='show_questions_by_category'),  # pk مشفر 
    path('add-question/', views.add_question, name='add_question'),
    path('questions-list/', views.questions_list, name='questions_list'),  # الرابط لعرض جدول الأسئلة
    path('update_question/<int:question_id>/', views.update_question, name='update_question'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('get_questions/', views.get_questions, name='get_questions'),
    # path('lists/', views.survey_list, name='survey_list'),  # Rename to 'survey_list'
    # path('survey/<int:survey_id>/', views.view_survey, name='view_survey'),
    # path('surveys/', views.survey_list, name='survey_list_all'),
    # path('surveys/<int:survey_id>/delete/', views.delete_survey, name='delete_survey'),
    # path('surveys/<int:survey_id>/edit/', views.edit_survey, name='edit_survey'),

    # path('survey/<int:survey_id>/answers/', views.view_survey_answers, name='view_survey_answers'),
    # path('choose-answers/', views.choose_survey_for_answers, name='choose_survey_for_answers'),
    # path('survey/<int:survey_id>/delete/', views.delete_survey, name='delete_survey'),
    # path('survey/report/', views.survey_report, name='survey_report'),  # Without ID
    # path('survey/report/<int:survey_id>/', views.survey_report, name='survey_report_with_id'),  # With ID

    # path('survey/<int:survey_id>/', views.view_survey, name='view_survey'),
    # path('select-entity-sector/', views.entity_sector_selection, name='entity_sector_selection'),
    # path('select-entity-sector/surveys/', views.entity_sector_selection, name='entity_sector_surveys'),

    # path('survey/<int:survey_id>/summary/', views.survey_summary_report, name='survey_summary_report'),
    # path('survey/<int:survey_id>/question_analysis/', views.question_analysis_report, name='question_analysis_report'),
    # path('survey/<int:survey_id>/demographic/', views.demographic_report, name='demographic_report'),
    # path('survey/<int:survey_id>/time_trend/', views.time_trend_report, name='time_trend_report'),
    # path('survey/<int:survey_id>/completion/', views.completion_analysis, name='completion_analysis'),
    # path('survey/<int:survey_id>/satisfaction/', views.satisfaction_report, name='satisfaction_report'),
    # path('survey/<int:survey_id>/export/', views.export_survey_data, name='export_survey_data'),

    # path('link-survey/<int:survey_id>/', views.link_survey_to_entity_sector, name='link_survey_to_entity_sector'),
    # path('get-sectors/', views.get_sectors, name='get_sectors'), 



    # path('survey/<int:survey_id>/report/', views.survey_report, name='survey_report'),
    # path('survey/dynamic_report/', views.dynamic_report, name='dynamic_report'),  # URL for dynamic report view 
    # path('survey/survey_summary/', views.dynamic_report, name='survey_summary'),
    # path('survey/<int:survey_id>/summary/', views.survey_summary, name='survey_summary'),
# 
    # path('create-entity/', views.create_entity, name='create_entity'),  # URL for creating an entity


    # path('survey-link-list/', views.survey_link_list, name='survey_link_list'),
    # path('entities/', views.entity_list, name='entity_list'),  
    # path('survey/<int:survey_id>/update_answers/', views.update_survey_answers, name='update_survey_answers'),




    # other URL patterns...

  # URL for dynamic report view 
    # path('thank-you/', views.thank_you, name='thank_you'),



    # apis
        # path('api/get-sectors/', views.get_sectors, name='get_sectors'),

]
