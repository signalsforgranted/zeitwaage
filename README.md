This project aims to provide interop testing of NTP version 5 and NTS. We do handle time protocols and interoperation here, however accuracy and precision are deliberately not in scope.

"Zeitwaage" is German for "timegrapher", a machine which measures the accuracy of a time keeping device. Which is slightly ironic given how I just said we weren't going to measure that.

## Environment Setup
You'll need Docker with docker-compose as well as
[Poetry](https://python-poetry.org) installed. To get started, clone this
repository using the `--recurse-submodules` argument, then run:

```bash
poetry env activate;
poetry install;
```
> [!TIP]
> If you forgot to bring in the submodules, run `git submodule update --init --recursive`
> to bring all the implementations.

To build each of the implementations, run:
```bash
poetry run build
```

## Running

```bash
poetry run zeitwaage
```

## Licence

Copyright 2026-

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
