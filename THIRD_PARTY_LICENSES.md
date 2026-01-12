# Third-Party Licenses

This document lists the third-party software packages used by OpenVTO and their respective licenses.

## Core Dependencies

The core `openvto` library has no mandatory runtime dependencies. All packages listed below are optional dependencies used for specific features.

---

## Image Processing

### Pillow (PIL Fork)

- **Package:** `pillow`
- **License:** Historical Permission Notice and Disclaimer (HPND)
- **Website:** https://python-pillow.org/
- **Usage:** Optional - used for image processing, resizing, and format conversion

```
The Python Imaging Library (PIL) is

    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh

Pillow is the friendly PIL fork. It is

    Copyright © 2010-2024 by Jeffrey A. Clark (Alex) and contributors.
```

---

## Google Cloud / Generative AI

### google-genai

- **Package:** `google-genai`
- **License:** Apache License 2.0
- **Website:** https://github.com/googleapis/python-genai
- **Usage:** Optional - Google Generative AI SDK for image and video generation

### google-auth

- **Package:** `google-auth`
- **License:** Apache License 2.0
- **Website:** https://github.com/googleapis/google-auth-library-python
- **Usage:** Optional - Authentication for Google Cloud services

```
Copyright 2016 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## Web Framework (FastAPI Example)

### FastAPI

- **Package:** `fastapi`
- **License:** MIT License
- **Website:** https://fastapi.tiangolo.com/
- **Usage:** Optional - Example API server implementation

### Hypercorn

- **Package:** `hypercorn`
- **License:** MIT License
- **Website:** https://github.com/pgjones/hypercorn
- **Usage:** Optional - ASGI server for FastAPI example

### python-dotenv

- **Package:** `python-dotenv`
- **License:** BSD 3-Clause License
- **Website:** https://github.com/theskumar/python-dotenv
- **Usage:** Optional - Environment variable management

### python-multipart

- **Package:** `python-multipart`
- **License:** Apache License 2.0
- **Website:** https://github.com/andrew-d/python-multipart
- **Usage:** Optional - Multipart form data parsing for file uploads

---

## Development Dependencies

### pytest

- **Package:** `pytest`
- **License:** MIT License
- **Website:** https://pytest.org/
- **Usage:** Development only - Testing framework

### pytest-cov

- **Package:** `pytest-cov`
- **License:** MIT License
- **Website:** https://github.com/pytest-dev/pytest-cov
- **Usage:** Development only - Coverage reporting

### Ruff

- **Package:** `ruff`
- **License:** MIT License
- **Website:** https://github.com/astral-sh/ruff
- **Usage:** Development only - Linting and formatting

---

## License Texts

### Apache License 2.0

The full text of the Apache License 2.0 can be found at:
https://www.apache.org/licenses/LICENSE-2.0

### MIT License

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### BSD 3-Clause License

```
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
```
