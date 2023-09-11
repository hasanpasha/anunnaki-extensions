# anunnaki extensions

### How to generate id for your source
the `id` should be 16 digits
```python
import hashlib

int(hashlib.sha1(f"{ext_lang}_{ext_pkg}".encode("utf-8")).hexdigest(), 16) % (10 ** 16)

```