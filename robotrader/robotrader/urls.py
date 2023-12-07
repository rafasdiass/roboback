# robotrader/robotrader/urls.py

from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclua URLs de outros apps aqui, se necessário, usando path ou include
    # Exemplo: path('app/', include('app.urls')),
]
