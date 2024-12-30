from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path('user/create/', views.create_user, name='create_user'),
    path('user/<int:user_id>/edit/', views.editUsers, name='edit_user'),
    path('user/list/', views.user_list, name='user_list'),  # Add this line for user list
    path('user/delete/<int:id>/', views.delete_user, name='delete_user'),
    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('group/list/', views.group_list, name='group_list'),  # Add this line for group list
    path('logout/', views.logout_view, name='logout'),
    path('user/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/edit/<int:pk>/', views.edit_group, name='edit_group'),  # مسار التعديل
    path("groups/delete/<int:pk>/", views.delete_group, name="delete_group"),
    # إذا كنت ترغب في إضافة صفحة خاصة بعرض الحظر (كما تم ذكره في المثال السابق):
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logs/', views.logs_view, name='logs'),
    path('logs/clear/', views.clear_logs, name='clear_logs'),
    path('user-sessions/', views.user_sessions, name='user_sessions'),
    path('delete-session/<int:session_id>/', views.delete_session, name='delete_session'),
    path('delete-all-sessions/', views.delete_all_sessions, name='delete_all_sessions'),
    path('logs-events/', views.logs_events, name='logs_events'),
    path('logs-events/delete/', views.delete_all_logs, name='delete_all_logs'),
]

