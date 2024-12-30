from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group

from django_project import settings
from .forms import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from survey.models import *
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView
from axes.models import AccessAttempt, AccessLog
from django.utils.timezone import now
from axes.handlers.proxy import AxesProxyHandler

from user_agents import parse

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserSession


from .models import ActionLog

@login_required
def logs_events(request):
    logs = ActionLog.objects.all().order_by('-timestamp')  # ترتيب السجلات من الأحدث إلى الأقدم
    return render(request, 'registration/log_events.html', {'logs': logs})

from django.contrib import messages

@login_required
def delete_all_logs(request):
    if not request.user.is_superuser:
        return redirect('logs_events')

    ActionLog.objects.all().delete()
    # messages.success(request, "تم حذف جميع السجلات بنجاح.")
    return redirect('logs_events')


@receiver(user_logged_in)
def create_user_session(sender, request, user, **kwargs):
    # إنشاء جلسة جديدة عند تسجيل الدخول
    UserSession.objects.create(user=user)

@receiver(user_logged_out)
def update_user_session(sender, request, user, **kwargs):
    # تحديث وقت الخروج عند تسجيل الخروج
    try:
        session = UserSession.objects.filter(user=user, logout_time__isnull=True).latest('login_time')
        session.logout_time = timezone.now()
        session.save()
    except UserSession.DoesNotExist:
        pass

def user_sessions(request):
    # استخراج User-Agent من الطلب
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    # استخراج معلومات المتصفح ونظام التشغيل
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os = f"{user_agent.os.family} {user_agent.os.version_string}"
    
    # يمكنك عرض البيانات في السجلات إذا لزم الأمر (للاختبار)
    print(f"Browser: {browser}, OS: {os}")
    
    # جلب السجلات
    sessions = UserSession.objects.all().order_by('-login_time')[:30]
    
    # إضافة معلومات المتصفح ونظام التشغيل للـ context
    return render(request, 'registration/user_sessions.html', {
        'sessions': sessions,
        'browser': browser,
        'os': os
    })
@login_required
def delete_session(request, session_id):
    # الحصول على السجل بناءً على المعرف
    session = get_object_or_404(UserSession, id=session_id)

    # حذف السجل
    session.delete()

    # إعادة توجيه إلى صفحة سجلات الجلسات
    return redirect('user_sessions')  # التأكد من اسم الـ URL الذي يعرض سجلات الجلسات

@login_required
def delete_all_sessions(request):
    if request.method == "POST":
        # حذف جميع سجلات الجلسات
        UserSession.objects.all().delete()
        return redirect('user_sessions')  # إعادة توجيه إلى صفحة سجلات الجلسات بعد الحذف
    return HttpResponse(status=405)  # في حال كانت الطريقة غير صحيحة

def logs_view(request):
    # استرجاع سجلات محاولات الدخول الفاشلة من django-axes
    axes_logs = AccessAttempt.objects.all().order_by('-attempt_time')[:30]  # عرض آخر 30 محاولة

    # إضافة نوع المتصفح إلى كل سجل
    for log in axes_logs:
        user_agent = parse(log.user_agent)
        log.browser = user_agent.browser.family  # نوع المتصفح (مثل Chrome, Firefox)
        log.os = user_agent.os.family  # نوع نظام التشغيل (مثل Windows, Linux)
    
    return render(request, 'registration/logs.html', {
        'axes_logs': axes_logs,
    })


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # مسار صفحة تسجيل الدخول الخاصة بك

    def dispatch(self, request, *args, **kwargs):
        # تحقق مما إذا كان المستخدم محظورًا
        if AxesProxyHandler.is_locked(request):
            # إعادة توجيه المستخدم إلى صفحة الحظر
            return render(request, 'registration/login_locked.html')
        return super().dispatch(request, *args, **kwargs)



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
