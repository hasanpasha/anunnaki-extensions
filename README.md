# anunnaki extensions

### How to create a new source
In order to create a new source you have to implement the following file tree:
```bash
lang
└── package_name
    ├── source_class.py
    ├── icon.png
    ├── __init__.py
    └── metadata.json
```

- `__init__`.py: contains one function `get_source_class` which accepts two optional arguments `session: aiohttpSession` and `headers: Dict[str, Any]`.
- `source_class.py`: contains the implementation of one of the source classes, This is the heart of the source.
- `icon.png`: The icon of the source.
- `metadata.json`: Contains the necessary information for the extensions repo, which is: [see also](#how-to-generate-an-id-for-your-source)
```json
{
    "name": "source_name",
    "package_name": "source_pkg_name",
    "lang": "source_lang",
    "id": 0123456789101214,
    "base_url": "...",
    "version": "0.0.0"
}
```

#### How to generate an `id` for your source
the `id` should be 16 digits
```python
import hashlib

int(hashlib.sha1(f"{ext_lang}_{ext_pkg}".encode("utf-8")).hexdigest(), 16) % (10 ** 16)

```
