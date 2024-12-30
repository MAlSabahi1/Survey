from django.db import models
from django.contrib.auth.models import User


class Entitys(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sectors', null=True, blank=True)
    
    class Meta:
        verbose_name = "الكيانات"
    
    def __str__(self):
        return self.name

class UserEntityPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entity_permissions")
    entity = models.ForeignKey(Entitys, on_delete=models.CASCADE, related_name="user_permissions")

    class Meta:
        verbose_name = "صلاحية المستخدم على الكيان"
        
    def __str__(self):
        return f"{self.user.username} - {self.entity.name}"





class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'نص'),
        ('yes_no', 'نعم/لا'),
        ('multiple_choice', 'اختيارات متعددة'),
        ('radio', 'اختيار واحد'),  # New question type
    )
    CATEGORIES = (
        ('staff', 'الكادر'),
        ('infrastructure', 'البنية التحتية'),
        ('systems', 'الأنظمة'),
    )
    
    text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='systems')
    is_active = models.BooleanField(default=True)  # حقل نشط
    
    class Meta:
        verbose_name = "الاسئلة"


    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    class Meta:
        verbose_name = "الاختيارات المتعددة"

    def __str__(self):
        return self.text

class Surveys(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=Question.CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entities = models.ManyToManyField(Entitys, related_name="surveys", blank=True)

    class Meta:
        verbose_name = "الاستبيانات"
    


class Answer(models.Model):
    survey = models.ForeignKey(Surveys, related_name='answers', on_delete=models.CASCADE)
    entity = models.ForeignKey(Entitys, related_name='entity', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    choice_selected = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True, null=True)  # لإضافة الملاحظات
    
    class Meta:
        verbose_name = "الاجابات"
    

    def __str__(self):
        return f"{self.survey} for {self.entity}"



    



