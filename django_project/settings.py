from datetime import timedelta
from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-bekb+5+!#s&*jjb5!701ztl^0otie+$s@)kbd^z(bh$(q9g^mc"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "accounts",  # new
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "survey",  # new
    "widget_tweaks",  # new
    'axes',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.NoCacheMiddleware", 
    "axes.middleware.AxesMiddleware",
    'accounts.middleware.CurrentUserMiddleware',

]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # new
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]




WSGI_APPLICATION = "django_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # يتحقق من أن كلمة المرور لا تتشابه مع اسم المستخدم أو بريد إلكتروني المستخدم.
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # الحد الأدنى لطول كلمة المرور.
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # الحد الأدنى للطول (12 حرفًا على الأقل)
        }
    },
    # يتحقق من أن كلمة المرور ليست من الكلمات الشائعة.
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # يتحقق من أن كلمة المرور ليست مكونة بالكامل من أرقام فقط.
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # أضف هذا
    'django.contrib.auth.backends.ModelBackend',  # لا تنسَ تضمين نظام المصادقة الافتراضي
]



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/


# في settings.py
LANGUAGES = [
    ('ar', 'Arabic'),
    # اللغات الأخرى التي ترغب في دعمها
]

LANGUAGE_CODE = 'ar'  # تعيين اللغة العربية


# LANGUAGE_CODE = "en-us"


TIME_ZONE = 'Asia/Riyadh'  # تأكد من أنها المنطقة الزمنية المناسبة

USE_I18N = True

USE_TZ = True


SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # حفظ الجلسات في قاعدة البيانات

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"  # new
LOGOUT_REDIRECT_URL = "login"  # new

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# # إعدادات الجلسة
# # SESSION_COOKIE_SECURE = True  # استخدام HTTPS فقط للجلسات
SESSION_COOKIE_HTTPONLY = True  # منع الوصول للجلسة عبر JavaScript
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # انتهاء الجلسة عند إغلاق المتصفح
SESSION_COOKIE_AGE = 600 
# # # # # # # # # # # # # # # # # # # #

# # الحماية من XSS
SECURE_BROWSER_XSS_FILTER = True

# # الحماية من CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# # الحماية من Clickjacking
X_FRAME_OPTIONS = 'DENY'

# SECURE_SSL_REDIRECT = True  # إعادة التوجيه إلى HTTPS
SECURE_HSTS_SECONDS = 3600  # تمكين HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# # إعدادات الكوكيز
SECURE_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


AXES_ENABLE_ADMIN = True  


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'axes': {
            'handlers': ['console'],
            'level': 'INFO',  # يمكن تغييرها إلى DEBUG لمزيد من التفاصيل
        },
    },
}


# الحد الأقصى لعدد المحاولات الفاشلة
AXES_FAILURE_LIMIT = 5  # عدد المحاولات الفاشلة التي يُسمح بها قبل الحظر

# مدة الحظر بعد المحاولات الفاشلة (هنا دقيقة واحدة)
AXES_COOLOFF_TIME = timedelta(seconds=60)  # أو timedelta(minutes=1) لمدة دقيقة واحدة

# إزالة المحاولات القديمة بعد الحظر
AXES_REMOVE_OLD_LOCKOUTS = False  # تنظيف المحاولات الفاشلة القديمة بعد فترة من الزمن

AXES_LOCKOUT_TEMPLATE = 'registration/login_locked.html'  # المسار إلى القالب الذي أنشأته

# إعدادات django-axes
AXES_ENABLED = True
# AXES_PERSISTENCE = True
AXES_RESET_ON_SUCCESS = False
