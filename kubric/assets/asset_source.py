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

import json
import logging
import tarfile
import tempfile

import pandas as pd
import tensorflow as tf
import tensorflow_datasets.public_api as tfds
from tensorflow_datasets.core.utils.type_utils import PathLike

from typing import Optional

from kubric.core import objects


class AssetSource(object):
  def __init__(self, path: PathLike, scratch_dir: Optional[PathLike] = None):
    self.remote_dir = tfds.core.as_path(path)
    name = self.remote_dir.name
    logging.info("Adding AssetSource '%s' with URI='%s'", name, self.remote_dir)

    self.local_dir = tfds.core.as_path(tempfile.mkdtemp(prefix="assets", dir=scratch_dir))

    manifest_path = self.remote_dir / "manifest.json"
    if manifest_path.exists():

      self.db = pd.read_json(tf.io.gfile.GFile(manifest_path, "r"))
      logging.info("Found manifest file. Loaded information about %d assets", self.db.shape[0])
    else:
      assets_list = [p.name[:-7] for p in manifest_path.iterdir() if p.name.endswith('.tar.gz')]
      self.db = pd.DataFrame(assets_list, columns=["id"])
      logging.info("No manifest file. Found %d assets.", self.db.shape[0])

  def create(self, asset_id: str, **kwargs) -> objects.FileBasedObject:
    assert asset_id in self.db["id"].values, kwargs
    sim_filename, vis_filename, properties = self.fetch(asset_id)

    for pname in ["mass", "friction", "restitution", "bounds"]:
      if pname in properties and pname not in kwargs:
        kwargs[pname] = properties[pname]

    return objects.FileBasedObject(asset_id=asset_id,
                                   simulation_filename=str(sim_filename),
                                   render_filename=str(vis_filename),
                                   **kwargs)

  def fetch(self, object_id):
    remote_path = self.remote_dir / (object_id + '.tar.gz')
    local_path = self.local_dir / (object_id + '.tar.gz')
    if not local_path.exists():
      logging.debug("Copying %s to %s", str(remote_path), str(local_path))
      tf.io.gfile.copy(remote_path, local_path)

      with tarfile.open(local_path, "r:gz") as tar:
        tar.extractall(self.local_dir)
        logging.debug("Extracted %s", repr([m.name for m in tar.getmembers()]))

    json_path = self.local_dir / object_id / "data.json"
    with open(json_path, "r") as f:
      properties = json.load(f)
      logging.debug("Loaded properties %s", repr(properties))

    # paths
    vis_path = self.local_dir / object_id / properties["paths"]["visual_geometry"][0]
    urdf_path = self.local_dir /object_id / properties["paths"]["urdf"][0]

    return urdf_path, vis_path, properties

