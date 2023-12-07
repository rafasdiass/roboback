# settings.py

import os

# Construa caminhos dentro do projeto assim: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Aviso de segurança: mantenha a chave secreta usada em produção em segredo!
SECRET_KEY = '^b3nrlks94qpdgm-m=ebqc-1+#$n4v9*e&&zb3rxlah9(u4x2@'

# Aviso de segurança: não execute com o modo debug ativado em produção!
DEBUG = True

ALLOWED_HOSTS = []

# Definição da aplicação

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # Adicione 'channels' às apps instaladas
    'automacao',  # Substitua pelo nome do seu app Django
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'robotrader.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'robotrader.wsgi.application'
ASGI_APPLICATION = 'robotrader.asgi.application'  # Definição do ASGI para Django Channels

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'alexiatrade',  # Nome do banco de dados no MongoDB Atlas
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://rafasdiasdev:EDmesf8y66x3MyzE@cluster0.rkaertv.mongodb.net/?retryWrites=true&w=majority'
        }
    }
}

# Validação de senha
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

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Arquivos estáticos (CSS, JavaScript, Imagens)
STATIC_URL = '/static/'
