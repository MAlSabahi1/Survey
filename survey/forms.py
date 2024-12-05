from django import forms
from .models import *
from django.forms import ModelForm, Textarea, RadioSelect, CheckboxSelectMultiple, Select


class EntitysForm(forms.ModelForm):
    class Meta:
        model = Entitys
        fields = ['name','description'] # الحقول التي ستظهر في النموذج
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),  # تخصيص واجهة المستخدم للحقل
            # 'parent': forms.Select(attrs={'class': 'form-control'}),  # تخصيص واجهة المستخدم للحقل
        }
        labels = {
            'name': 'اسم الكيان',
            'description': 'الوصف',
            # 'parent': 'القطاع الرئيسي',  # إذا كان الكيان هو قطاع فرعي
        }




class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
    

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text', 'choice_selected', 'note']
        widgets = {
            'answer_text': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'note': Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)

        # تخصيص الحقول بناءً على نوع السؤال
        if question:
            if question.question_type == 'yes_no':
                self.fields['answer_text'].widget = RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')])
            elif question.question_type in ['multiple_choice', 'radio']:
                self.fields['choice_selected'].queryset = question.choices.all()
                self.fields['choice_selected'].widget = RadioSelect()
            elif question.question_type == 'text':
                self.fields['choice_selected'].widget = forms.HiddenInput()
            else:
                self.fields['answer_text'].widget = forms.HiddenInput()
                self.fields['choice_selected'].widget = forms.HiddenInput()
