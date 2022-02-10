from .base import MEDIA_ROOT
from .base import *

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Take environment variables from .env file
environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Open API Keys
EXIM_BANK_API_KEY = env('EXIM_BANK_API_KEY')
UPBIT_ACCESS_KEY = env('UPBIT_ACCESS_KEY')
UPBIT_SECRET_KEY = env('UPBIT_SECRET_KEY')
KSD_API_KEY = env('KSD_API_KEY')
LOCAL_IP_ADDRESS = env('LOCAL_IP_ADDRESS')