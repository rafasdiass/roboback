from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('automacao/', include('automacao.urls')),  # Inclui as URLs do app 'automacao'
]
