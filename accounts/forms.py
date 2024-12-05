# forms.py
from django import forms
from django.contrib.auth.models import User, Group, Permission
from survey.models import *
from django.contrib.auth.forms import UserCreationForm



class GroupPermissionForm(forms.ModelForm):
    can_add = forms.BooleanField(required=False, label='إضافة')
    can_delete = forms.BooleanField(required=False, label='حذف')
    can_edit = forms.BooleanField(required=False, label='تعديل')

    class Meta:
        model = Group
        fields = ['name', 'can_add', 'can_delete', 'can_edit']

class UserForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='المجموعات'
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label='أذونات المستخدم'
    )
    entities = forms.ModelMultipleChoiceField(
        queryset=Entitys.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="الكيانات المسموحة"
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'groups', 'user_permissions', 'entities']
        labels = {
            'username': 'اسم المستخدم',
            'password': 'كلمة المرور',
            'email': 'البريد الإلكتروني',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if user:
            # تحديد الكيانات المرتبطة بالمستخدم
            user_entities = UserEntityPermission.objects.filter(user=user).values_list('entity_id', flat=True)
            self.fields['entities'].initial = user_entities  # ضبط القيم المحددة

            

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            self.save_m2m()
        return user

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)
    #     if user:
    #         # تعيين الكيانات التي يمتلكها المستخدم كقيم مبدئية
    #         self.fields['entities'].initial = Entitys.objects.filter(
    #             user_permissions__user=user
    #         )
# forms.py
class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

    class Meta:
        model = Group
        fields = ['name', 'permissions']
