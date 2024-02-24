from django.urls import path
from url_shortner.views import URLShortnerListCreateView


urlpatterns = [
    path('', URLShortnerListCreateView.as_view(), name='url_shortner'),
]
