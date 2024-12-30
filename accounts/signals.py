from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.dispatch import receiver
from django.contrib import messages
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.models import ContentType
from .models import ActionLog
from django.contrib.auth.models import User, Group, Permission
from survey.models import *  # إضافة النماذج المستهدفة فقط
from axes.signals import user_login_failed
from .models import LoginAttempt
from user_agents import parse


#------------------------------   منع دخول المستخدم بحساب واحد في اكثر من جلسه   ------------------------------------

@receiver(user_logged_in)
def prevent_multiple_logins(sender, request, user, **kwargs):
    # احصل على جميع الجلسات النشطة
    sessions = Session.objects.filter(expire_date__gte=now())

    # البحث عن الجلسات المرتبطة بالمستخدم
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):  # تحقق من ID المستخدم
            # إذا كانت الجلسة الحالية هي الجلسة الجديدة (الجهاز الثاني)
            if session.session_key != request.session.session_key:  
                # تخزين الرسالة في الجلسة الحالية قبل حذف الجلسة القديمة
                messages.warning(request, "تم تسجيل خروج جهاز آخر كان مسجلًا بنفس الحساب بسبب تسجيل الدخول من جهاز جديد.")
                session.delete()  # بعد إرسال الرسالة، نقوم بحذف الجلسة القديمة
                break  # بعد حذف الجلسة القديمة، توقف عن البحث

    # الجلسة الحالية (الجهاز الذي تم تسجيل الدخول منه) ستبقى نشطة فقط
    request.session.save()
#--------------------------------------------------------------------------------------

#---------------------------------   سجل الاحداث التي يقوم بها المستخدم   -------------
@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    # تحديد النماذج المستهدفة فقط
    if sender not in [Entitys, Question, Surveys, Answer, User, Group, Permission, Choice ]:
        return  # إذا لم يكن النموذج من النماذج المستهدفة، لا تفعل شيئًا

    # الحصول على المستخدم الحالي (إذا كنت تستخدم middleware)
    from .middleware import get_current_user
    user = get_current_user()

    # تسجيل الإضافة أو التعديل
    action = "CREATE" if created else "UPDATE"
    description = f"تم {'إضافة' if created else 'تعديل'} عنصر في {sender._meta.verbose_name} (ID: {instance.id})"

    ActionLog.objects.create(
        user=user,
        model_name=sender._meta.verbose_name,
        object_id=str(instance.id),
        action=action,
        description=description
    )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    # تحديد النماذج المستهدفة فقط
    if sender not in [Entitys, Question, Surveys, Answer, User, Group, Permission, Choice]:
        return  # إذا لم يكن النموذج من النماذج المستهدفة، لا تفعل شيئًا

    # الحصول على المستخدم الحالي (إذا كنت تستخدم middleware)
    from .middleware import get_current_user
    user = get_current_user()

    # تسجيل الحذف
    description = f"تم حذف عنصر في {sender._meta.verbose_name} (ID: {instance.id})"

    ActionLog.objects.create(
        user=user,
        model_name=sender._meta.verbose_name,
        object_id=str(instance.id),
        action="DELETE",
        description=description
    )

#-------------------------------------------------------------------------------------


#---------------------------------   محاولات تسجيل الدخول الخاطئ   -----------------------
@receiver(user_login_failed)
def log_failed_attempt(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # تحليل نوع المتصفح
    parsed_user_agent = parse(user_agent)
    browser = parsed_user_agent.browser.family
    os = parsed_user_agent.os.family

    # البحث عن سجل موجود بنفس المستخدم وعنوان الـ IP
    attempt, created = LoginAttempt.objects.get_or_create(
        ip_address=ip,
        username=credentials.get('username', None),
        defaults={
            'user_agent': user_agent,
            'browser': browser,
            'os': os,
            'failures_since_start': 1,
        }
    )

    # إذا كان السجل موجودًا، تحديث عدد المحاولات ووقت المحاولة
    if not created:
        attempt.failures_since_start += 1
        attempt.attempt_time = now()
        attempt.save()

#---------------------------------------------------------------------------