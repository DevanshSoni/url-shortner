from django.db import models
from django.http import Http404
from django.core.cache import cache

import redis
import os
import rsa
import base64

redis_instance = redis.StrictRedis(
    host=os.environ.get('REDIS_HOST', '127.0.0.1'),
    port=os.environ.get('REDIS_PORT', '6379'),
    db=1
)

# Create your models here.
class URL(models.Model):
    RSA_PUBLIC_KEY = ''
    RSA_PRIVATE_KEY = ''
    ORIGINAL_URL_CACHE_KEY = 'original_'
    SHORTEN_URL_CACHE_KEY = 'shorten_'
    RSA_PUBLIC_KEY = os.environ.get('RSA_PUBLIC_KEY', 'a1b2c3')
    RSA_PRIVATE_KEY = os.environ.get('RSA_PRIVATE_KEY', 'x1y2z3')

    original_url = models.TextField(db_index=True)
    short_url = models.TextField(db_index=True)

    def __str__(self):
        return self.original_url_alias

    @property
    def original_url_alias(self):
        return self.original_url[:20] + '...'

    @classmethod
    def initialize_secret_keys(cls):
        public_key, private_key = rsa.newkeys(512)
        cls.RSA_PUBLIC_KEY = public_key
        cls.RSA_PRIVATE_KEY = private_key

        return

    @classmethod
    def encrypt_url(cls, url: str):
        return str(rsa.encrypt(url.encode(), cls.RSA_PUBLIC_KEY))

    @classmethod
    def decrypt_url(cls, encrypted_url):
        return str(rsa.decrypt(encrypted_url, cls.RSA_PRIVATE_KEY).decode())

    @classmethod
    def encrypt_base64(cls, raw_string: str):
        encoded_url = raw_string.encode("ascii")
        base64_bytes = base64.b64encode(encoded_url)
        return base64_bytes.decode("ascii")

    @classmethod
    def decrypt_base64(cls, encoded_string: str):
        base64_bytes = encoded_string.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        return sample_string_bytes.decode("ascii")

    @classmethod
    def _shorten_url(cls, url):
        encrypted_url = cls.encrypt_url(url)
        shorten_url = cls.encrypt_base64(encrypted_url)
        return shorten_url[:4] + shorten_url[-4:]

    @classmethod
    def shorten_and_persist_url(cls, original_url):
        shorter_url = cls._shorten_url(original_url)
        url_instance = cls.objects.create(
            original_url=original_url,
            short_url=shorter_url
        )
        original_url_cache_key = cls.ORIGINAL_URL_CACHE_KEY + cls.encrypt_base64(original_url)
        shorten_url_cache_key = cls.SHORTEN_URL_CACHE_KEY + cls.encrypt_base64(shorter_url)

        RedisService.set(original_url_cache_key, shorter_url)
        RedisService.set(shorten_url_cache_key, original_url)

        return url_instance

    @classmethod
    def fetch_original_url(cls, url):
        try:
            cache_key = cls.SHORTEN_URL_CACHE_KEY + cls.encrypt_base64(url)
            cache_data = RedisService.get(cache_key)
            if cache_data:
                return cache_data
            else:
                url_instance = cls.objects.get(original_url=url)
                RedisService.set(cache_key, url_instance.short_url)
                return url_instance
        except cls.DoesNotExist:
            raise Http404

    @classmethod
    def fetch_shorten_url(cls, url):
        try:
            cache_key = cls.ORIGINAL_URL_CACHE_KEY + cls.encrypt_base64(url)
            cache_data = RedisService.get(cache_key)
            if cache_data:
                return cache_data
            else:
                url_instance = cls.objects.get(short_url=url)
                RedisService.set(cache_key, url_instance.original_url)
                return url_instance
        except cls.DoesNotExist:
            raise Http404


class RedisService:
    @classmethod
    def set(cls, key: str, value: any):
        return cache.set(key, value)

    @classmethod
    def get(cls, key: str):
        return cache.get(key)
