from django.db import models
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session for {self.user.username} from {self.login_time} to {self.logout_time if self.logout_time else 'Active'}"



class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'إضافة'),
        ('UPDATE', 'تعديل'),
        ('DELETE', 'حذف'),
        ('VIEW', 'عرض'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # المستخدم الذي قام بالفعل
    model_name = models.CharField(max_length=200)  # اسم النموذج (Entitys, Question, Surveys, إلخ)
    object_id = models.CharField(max_length=100)  # ID الكائن
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)  # نوع الحدث
    description = models.TextField(blank=True)  # وصف الحدث
    timestamp = models.DateTimeField(default=now)  # وقت الحدث

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} - {self.timestamp}"