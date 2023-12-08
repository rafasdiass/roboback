from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('automacao/', include('automacao.urls')),  # Substitua 'meuapp' pelo nome do seu aplicativo
    # Adicione mais URLs de outros apps aqui, se necessário
]
