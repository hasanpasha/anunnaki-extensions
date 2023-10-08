from .cinemana import Cinemana
from aiohttp import ClientSession
from typing import Any, Dict



def get_source_class(session: ClientSession = None, headers: Dict[str, Any] = None):
    return Cinemana(session=session, headers=headers)
