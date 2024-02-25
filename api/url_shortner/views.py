from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView
from url_shortner.models import URL

import os


class URLShortnerView(APIView):
    def post(self, request):
        host_url = os.environ.get('API_SERVER_HOST_URL', 'https://127.0.0.1:8000')
        original_url = request.data.get('url')
        URL.initialize_secret_keys()
        url_instance = URL.shorten_and_persist_url(original_url)

        return Response({ 'url': host_url+ '/' +url_instance.short_url })

    def get(self, request, short_url: str):
        original_url = URL.fetch_original_url(short_url)
        return Response({ 'url': original_url.decode() })
