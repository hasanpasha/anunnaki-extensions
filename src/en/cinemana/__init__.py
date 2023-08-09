from anunnaki_source.loader import Extension
from .cinemana import Cinemana


def load_extension():
    ext = Cinemana()
    return Extension(
        name=ext.name,
        id=ext.id,
        version="0.1.0"
        ext=ext,
        is_online=True
    )
