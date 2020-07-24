"""
Auth test_services
"""
from .providers.facebook import FacebookAuth
from .providers.google import GoogleAuth
from .providers.spotify import SpotifyAuth
from .providers.vk import VKAuth


__all__ = [
    "FacebookAuth",
    "GoogleAuth",
    "SpotifyAuth",
    "VKAuth",
]
