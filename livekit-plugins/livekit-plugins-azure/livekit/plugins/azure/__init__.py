# Copyright 2024 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LiveKit Azure AI Services Plugin

This plugin provides integration with Azure AI Services for LiveKit Agents,
including support for Azure Live Interpreter API for real-time speech translation.
"""

from . import realtime
from .version import __version__

__all__ = [
    "realtime",
    "__version__",
]

# Hide non-exported symbols from documentation
__pdoc__ = {name: False for name in dir() if name not in __all__}
