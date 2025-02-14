import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == "development":
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

CSRF_TRUSTED_ORIGINS = [ 'https://*' ]

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'django_htmx',
    'thq_home',
    'thq_users',
    'thq_chat',
    'thq_exams',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'thq_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'thq_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
if ENVIRONMENT == "development":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'postgres',
            'PORT': '5432',
        }
    }
else:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL', 'postgresql://'))
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = "{% url 'account_signup' %}?next={% url 'profile-onboarding' %}"

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

if ENVIRONMENT == "production":
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST ='smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = f'Hoccungminh {os.getenv("EMAIL_HOST_USER")}' 
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend"
)

# VNPAY CONFIG
VNPAY_RETURN_URL = os.getenv("VNPAY_RETURN_URL")
VNPAY_PAYMENT_URL = os.getenv("VNPAY_PAYMENT_URL")
VNPAY_API_URL = os.getenv("VNPAY_API_URL")
VNPAY_TMN_CODE = os.getenv("VNPAY_TMN_CODE")
VNPAY_HASH_SECRET_KEY = os.getenv("VNPAY_HASH_SECRET_KEY")

# Jazzmin settings
JAZZMIN_SETTINGS = {
    "site_title": "Administration",
    "site_header": "Hoc cung minh",
    "copyright": "Hoc cung minh",
    "welcome_sign": "Chào mừng đến Trang quản trị",
    "site_logo": "images/logo.png",
    "search_model": "auth.User",
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Users", "url": "admin:auth_user_changelist", "permissions": ["auth.view_user"]},
    ],
    "show_ui_builder": False,
    "navigation_expanded": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "solar",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}