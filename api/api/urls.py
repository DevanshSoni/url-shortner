from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('url-shortner/', include('url_shortner.urls')),
]
