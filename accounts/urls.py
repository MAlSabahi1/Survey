from django.urls import path
from django.contrib.auth.views import LogoutView


from . import views


urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path('user/create/', views.create_user, name='create_user'),
    path('user/<int:user_id>/edit/', views.editUsers, name='edit_user'),
    path('user/list/', views.user_list, name='user_list'),  # Add this line for user list
    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('group/list/', views.group_list, name='group_list'),  # Add this line for group list
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/edit/<int:pk>/', views.edit_group, name='edit_group'),  # مسار التعديل
    path('groups/delete/<int:pk>/', views.delete_group, name='delete_group'),  # مسار الحذف


]

