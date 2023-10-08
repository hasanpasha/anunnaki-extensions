# anunnaki extensions

### How to create new source
In order to create a new source you have to implement the following files tree:
```
lang/
    source_pkg_name/
        __init__.py
        source_class.py
        icon.png
        metadata.json
```
- `__init__`.py: contains one function `get_source_class` which accept to optional arguments `session: aiohttpSession` and `headers: Dict[str, Any]`.
- `source_class.py`: contains the implementation of one of the source classess, This is the heart of the source.
- `icon.png`: The icon of the source.
- `metadata.json`: Contains the necessary information for extensions repo, which is:
```json
    {
        "name": "source_name",
        "package_name": "source_pkg_name",
        "lang": "source_lang",
        "id": integer unique number, see [how to](#How-to-generate-id-for-your-source).
        "base_url": "...",
        "version": "0.0.0"
    }
```

#### How to generate id for your source
the `id` should be 16 digits
```python
import hashlib

int(hashlib.sha1(f"{ext_lang}_{ext_pkg}".encode("utf-8")).hexdigest(), 16) % (10 ** 16)

```