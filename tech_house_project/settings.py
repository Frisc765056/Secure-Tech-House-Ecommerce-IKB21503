from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- MANUAL .ENV LOADER (Requirement B.7 / Configuration Security) ---
# This function reads the .env file line by line without needing 'python-dotenv'.
def load_env_file(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                # Ignore empty lines and comments
                if line.strip() and not line.startswith('#'):
                    # Split key and value, then remove extra quotes or spaces
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip("'").strip('"')

# Load your .env file from the root directory
load_env_file(BASE_DIR / '.env')

# --- CONFIGURATION SECURITY (Requirement B.7) ---
# Secrets are now pulled from the .env file instead of being hardcoded.
SECRET_KEY = os.getenv('SECRET_KEY')

# DEBUG is pulled from .env; converts the string 'False' to the boolean False.
DEBUG = os.getenv('DEBUG') == 'True'

# --- SECURE API KEY SLOTS (Requirement B.7) ---
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
PAYMENT_GATEWAY_TOKEN = os.getenv('PAYMENT_GATEWAY_TOKEN')

# Essential for running locally with Debug=False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store', 
]

MIDDLEWARE = [
    # --- CUSTOM SECURITY MIDDLEWARE (Forces CSP Header) ---
    # This replaces the standard library to GUARANTEE the header appears on every response.
    'tech_house_project.middleware.ForceSecurityHeadersMiddleware',
    # ------------------------------------------------------

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tech_house_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tech_house_project.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- PASSWORD HASHING  ---
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}}, 
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- SESSION & COOKIE SECURITY ---
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 900            
SESSION_EXPIRE_AT_BROWSER_CLOSE = True 
SESSION_SAVE_EVERY_REQUEST = True    

# --- OWASP A6: SENSITIVE DATA PROTECTION (HTTPS & COOKIES) ---
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# --- BROWSER SECURITY HEADERS ---
X_FRAME_OPTIONS = 'DENY'             
SECURE_BROWSER_XSS_FILTER = True     
SECURE_CONTENT_TYPE_NOSNIFF = True   

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' 
STATICFILES_DIRS = [BASE_DIR / 'static']

# --- LOGIN REDIRECTS ---
LOGIN_URL = 'login'               
LOGIN_REDIRECT_URL = 'product_list' 
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONTENT SECURITY POLICY (CSP) ---
CSP_DEFAULT_SRC = ("'self'",) 
CSP_STYLE_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")

# --- CUSTOM ERROR HANDLING FOR CSRF  ---
CSRF_FAILURE_VIEW = 'store.views.custom_403'