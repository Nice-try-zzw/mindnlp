# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
CLIP Model
"""
from . import configuration_clap, modeling_clap, processing_clap, feature_extraction_clap

from .configuration_clap import *
from .modeling_clap import *
from .processing_clap import *
from .feature_extraction_clap import *

__all__ = []
__all__.extend(configuration_clap.__all__)
__all__.extend(modeling_clap.__all__)
__all__.extend(processing_clap.__all__)
__all__.extend(feature_extraction_clap.__all__)
