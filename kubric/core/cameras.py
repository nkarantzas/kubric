# Copyright 2020 The Kubric Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import traitlets as tl

from kubric.core import base
from kubric.core import objects

__all__ = ("Camera", "UndefinedCamera", "PerspectiveCamera", "OrthographicCamera")


class Camera(objects.Object3D):
  pass


class UndefinedCamera(Camera, base.Undefined):
  pass


class PerspectiveCamera(Camera):
  focal_length = tl.Float(50)
  sensor_width = tl.Float(36)

  @property
  def field_of_view(self):
    return 2*np.arctan(self.sensor_width/2./self.focal_length)


class OrthographicCamera(Camera):
  orthographic_scale = tl.Float(6.0)
