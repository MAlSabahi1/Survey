from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from .forms import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from survey.models import *
from django.contrib.auth import logout, login
from django.views.decorators.csrf import csrf_exempt
import json


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def logout_view(request):
    # تسجيل الخروج
    logout(request)
    # تنظيف الجلسة بشكل كامل
    request.session.flush()
    # إعادة التوجيه إلى صفحة تسجيل الدخول
    return redirect('login')


def is_admin(user):
    return user.is_authenticated and user.is_staff



@login_required
@permission_required('survey.add_user', raise_exception=True)
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        
        if form.is_valid():
            user = form.save()  # حفظ المستخدم
            
            # حفظ الكيانات المرتبطة
            entities = form.cleaned_data['entities']
            for entity in entities:
                UserEntityPermission.objects.create(user=user, entity=entity)
            
            # إرسال استجابة نجاح عبر JSON
            return JsonResponse({
                'success': True,
                'message': 'تم إنشاء المستخدم بنجاح!',
                'redirect_url': '/accounts/user/list/'  # قم بتعديل هذا الـ URL بناءً على التطبيق الخاص بك
            })
        else:
            # إذا كانت هناك أخطاء في النموذج، يتم إرجاعها في استجابة JSON
            errors = {field: form.errors.get(field) for field in form.errors}
            return JsonResponse({
                'success': False,
                'errors': errors
            })
    
    else:
        form = UserForm()
    
    return render(request, 'registration/create_user.html', {'form': form})



@login_required
@permission_required('survey.change_user', raise_exception=True)
def editUsers(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            # تحديث الكيانات المرتبطة
            entities = form.cleaned_data['entities']
                
            # حذف الكيانات القديمة فقط إذا كانت موجودة
            UserEntityPermission.objects.filter(user=user).delete()
            # إضافة الكيانات الجديدة
            for entity in entities:
                UserEntityPermission.objects.create(user=user, entity=entity)
            
            user.save()
            form.save_m2m()  # حفظ العلاقات الأخرى (مثل groups وpermissions)
            return redirect('user_list')
    else:
        form = UserForm(instance=user)

    return render(request, 'registration/edit_user.html', {'form': form, 'user': user})

# views.py
@login_required
@permission_required('survey.view_group', raise_exception=True)
def group_list(request):
    groups = Group.objects.all()  # جلب جميع المجموعات
    
    if request.method == 'POST':
        # معالجة الطلب وحفظ التحديثات
        for group in groups:
            form = GroupPermissionForm(request.POST, instance=group, prefix=str(group.id))
            if form.is_valid():
                # هنا يمكننا حفظ الصلاحيات كما ترغب. مثلاً تخزينها في قاعدة بيانات
                # أو تعديل الحقول المناسبة بناءً على التطبيق الخاص بك
                pass  # يمكن استبدال هذا بحفظ المعلومات في قاعدة البيانات أو تعديل الحقول
        return redirect('group_permissions')  # إعادة توجيه بعد الحفظ
    forms = [GroupPermissionForm(instance=group, prefix=str(group.id)) for group in groups]  # إنشاء نموذج لكل مجموعة
    return render(request, 'registration/group_permissions.html', {'forms': forms})



@login_required
@permission_required('survey.add_group', raise_exception=True)
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            # إذا كان الطلب AJAX، قم بإرجاع JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'تم إنشاء المجموعة بنجاح!',
                    'redirect_url': '/accounts/groups/'  # المسار المحدث لإعادة التوجيه
                })
            # إذا لم يكن AJAX، قم بإعادة التوجيه
            return redirect('group_list')
        else:
            # إذا كان الطلب AJAX مع خطأ في النموذج، قم بإرجاع الأخطاء
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = GroupForm()
    return render(request, 'registration/create_group.html', {'form': form})




@login_required
@permission_required('survey.change_group', raise_exception=True)
def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk)  # جلب المجموعة المحددة أو عرض 404 إذا لم تكن موجودة

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)  # استخدام النموذج الحالي لتعديل المجموعة
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'تم حفظ التعديلات بنجاح!',
                'redirect_url': '/accounts/groups/'  # أو المسار المناسب لعرض المجموعات
            })
        else:
            # إذا كان هناك أخطاء في النموذج، أرسل الأخطاء إلى الـ AJAX
            return JsonResponse({
                'success': False,
                'errors': {field: form.errors.get(field) for field in form.errors}
            })
    else:
        form = GroupForm(instance=group)

    return render(request, 'registration/edit_group.html', {'form': form, 'group': group})



@login_required
@permission_required('survey.delete_group', raise_exception=True)
@csrf_exempt  # تأكد من أن الطلبات من نوع POST تعمل بشكل صحيح
def delete_group(request, pk):
    if request.method == "POST":
        group = get_object_or_404(Group, pk=pk)
        group.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
@permission_required('survey.view_user', raise_exception=True)
def user_list(request):
    users = User.objects.all()  # Get all users
    return render(request, 'registration/user_list.html', {'users': users})


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/')  # التحقق من أن المستخدم مشرف
@csrf_exempt  # السماح بمعالجة طلبات Ajax
def delete_user(request, id):
    if request.method == "POST":
        try:
            user = User.objects.get(id=id)
            user.delete()
            return JsonResponse({"message": "تم حذف المستخدم بنجاح."}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "المستخدم غير موجود."}, status=404)
    return JsonResponse({"error": "طلب غير صالح."}, status=400)


@login_required
@permission_required('survey.view_group', raise_exception=True)
def group_list(request):
    groups = Group.objects.all()  # Get all groups
    return render(request, 'registration/group_list.html', {'groups': groups})


@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active  # Toggle the active status
    user.save()
    return redirect('user_list')

@login_required
@permission_required('survey.change_user', raise_exception=True)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'registration/edit_user.html', {'form': form, 'user': user})
