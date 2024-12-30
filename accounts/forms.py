# forms.py
from django import forms
from django.contrib.auth.models import User, Group, Permission
from survey.models import *
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password



class GroupPermissionForm(forms.ModelForm):
    can_add = forms.BooleanField(required=False, label='إضافة')
    can_delete = forms.BooleanField(required=False, label='حذف')
    can_edit = forms.BooleanField(required=False, label='تعديل')

    class Meta:
        model = Group
        fields = ['name', 'can_add', 'can_delete', 'can_edit']
forms.ModelMultipleChoiceField



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), validators=[validate_password])
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_('المجموعات')
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label=_('أذونات المستخدم'),
   
    )
    entities = forms.ModelMultipleChoiceField(
        queryset=Entitys.objects.all(),
        required=False,
        label=_("الكيانات المسموحة")
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'groups', 'user_permissions', 'entities']
        labels = {
            'username': _('اسم المستخدم'),
            'password': _('كلمة المرور'),
            'email': _('البريد الإلكتروني'),
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        

        # ترجمة أسماء الصلاحيات إلى العربية
        translated_permissions = {}
        for perm in Permission.objects.all():
            model_class = perm.content_type.model_class()  # الحصول على النموذج المرتبط
            if model_class:
                model_verbose_name = model_class._meta.verbose_name  # الحصول على verbose_name
            else:
                model_verbose_name = perm.content_type.model  # إذا كان غير موجود نستخدم اسم النموذج الافتراضي

            if "add" in perm.codename:
                translated_permissions[perm.id] = f"إضافة {model_verbose_name}"
            elif "change" in perm.codename:
                translated_permissions[perm.id] = f"تعديل {model_verbose_name}"
            elif "delete" in perm.codename:
                translated_permissions[perm.id] = f"حذف {model_verbose_name}"
            elif "view" in perm.codename:
                translated_permissions[perm.id] = f"عرض {model_verbose_name}"
            else:
                translated_permissions[perm.id] = perm.name  # الافتراضي إذا لم يكن هناك حالة محددة

        # إعادة تسمية أسماء الصلاحيات في الحقل
        self.fields['user_permissions'].queryset = Permission.objects.all()
        self.fields['user_permissions'].label_from_instance = lambda obj: translated_permissions.get(obj.id, obj.name)

        if user:
            # تحديد الكيانات المرتبطة بالمستخدم
            user_entities = UserEntityPermission.objects.filter(user=user).values_list('entity_id', flat=True)
            self.fields['entities'].initial = user_entities  # ضبط القيم المحددة

    # تخصيص عرض أسماء الأذونات
        def custom_permission_label(permission):
            # الوصول إلى النموذج المرتبط والحصول على verbose_name
            model_class = permission.content_type.model_class()
            if model_class:
                model_verbose_name = model_class._meta.verbose_name
            else:
                model_verbose_name = permission.content_type.model  # إذا لم يكن النموذج موجودًا

            codename = permission.codename  # اسم الصلاحية (add, change, delete, view)

            # ترجمة نوع الصلاحية
            if codename.startswith('add'):
                action = _("إضافة")
            elif codename.startswith('change'):
                action = _("تعديل")
            elif codename.startswith('delete'):
                action = _("حذف")
            elif codename.startswith('view'):
                action = _("عرض")
            else:
                action = codename  # الافتراضي

            # إرجاع النص مع verbose_name فقط بدون اسم التطبيق
            return f"{action} {model_verbose_name}"

        # تخصيص النصوص المعروضة للأذونات
        self.fields['user_permissions'].label_from_instance = custom_permission_label

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ترجمة أسماء الأذونات إلى العربية
        translated_permissions = {}
        for perm in Permission.objects.all():
            model_class = perm.content_type.model_class()  # الحصول على النموذج المرتبط
            if model_class:
                model_verbose_name = model_class._meta.verbose_name  # الحصول على verbose_name
            else:
                model_verbose_name = perm.content_type.model  # إذا كان النموذج غير موجود نستخدم اسم النموذج الافتراضي

            if "add" in perm.codename:
                translated_permissions[perm.id] = f"إضافة {model_verbose_name}"
            elif "change" in perm.codename:
                translated_permissions[perm.id] = f"تعديل {model_verbose_name}"
            elif "delete" in perm.codename:
                translated_permissions[perm.id] = f"حذف {model_verbose_name}"
            elif "view" in perm.codename:
                translated_permissions[perm.id] = f"عرض {model_verbose_name}"
            else:
                translated_permissions[perm.id] = perm.name  # الافتراضي إذا لم يكن هناك حالة محددة

        # إعادة تسمية الأذونات
        self.fields['permissions'].label_from_instance = lambda obj: translated_permissions.get(obj.id, obj.name)
