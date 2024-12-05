from django.db import models
from django.contrib.auth.models import User


class Entitys(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sectors', null=True, blank=True)
    
    def __str__(self):
        return self.name

class UserEntityPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entity_permissions")
    entity = models.ForeignKey(Entitys, on_delete=models.CASCADE, related_name="user_permissions")

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
    category = models.CharField(max_length=50, choices=CATEGORIES, default='staff')
    is_active = models.BooleanField(default=True)  # حقل نشط


    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text

class Surveys(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=Question.CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entities = models.ManyToManyField(Entitys, related_name="surveys", blank=True)

    


class Answer(models.Model):
    survey = models.ForeignKey(Surveys, related_name='answers', on_delete=models.CASCADE)
    entity = models.ForeignKey(Entitys, related_name='entity', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    choice_selected = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True, null=True)  # لإضافة الملاحظات
    
    
    

    def __str__(self):
        return f"{self.survey} for {self.entity}"

# New model to store user survey responses and summary
class SurveyResponse(models.Model):
    survey = models.ForeignKey(Surveys, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.TextField(blank=True, null=True)  # User's survey summary
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by {self.user} for {self.survey}"

# New model to store notes for each question within a survey response
class QuestionResponse(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='question_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)  # User's note for each question

    def __str__(self):
        return f"Note for {self.question} by {self.response.user}"
    


class SurveyEntityResponse(models.Model):
    survey = models.ForeignKey(Surveys, on_delete=models.CASCADE, related_name="responses")
    entity = models.ForeignKey(Entitys, on_delete=models.CASCADE, related_name="responses")
    # sector = models.ForeignKey(Sector, null=True, blank=True, on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)  # Store answers in JSON format
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        entity_name = self.entity.name
        sector_name = f" - {self.sector.name}" if self.sector else ""
        return f"Response for {self.survey.title} by {self.user} in {entity_name}{sector_name}"


