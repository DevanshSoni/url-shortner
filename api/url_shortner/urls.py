from django.urls import path
from url_shortner.views import URLShortnerView


urlpatterns = [
    path('', URLShortnerView.as_view(), name='url_shortner'),
    path('<short_url>/', URLShortnerView.as_view(), name='url_shortner'),
]
