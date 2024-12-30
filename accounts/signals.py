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