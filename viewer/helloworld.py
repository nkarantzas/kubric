# Copyright 2020 Google LLC
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
""" Helloworld for 3D visualization.

Inspired by https://threejs.org/docs/#manual/en/introduction/Creating-a-scene.

WARNING: this needs to be executed in either of two ways
  1) Via the python REPL inside blender as `blender -noaudio --background --python helloworld.py`
  2) Via `pip install bpy` via https://wiki.blender.org/wiki/Building_Blender/Other/BlenderAsPyModule
"""

# TODO: user proper imports once project name is defined
import sys; sys.path.append("../")

import argparse
import trimesh
import mathutils
import numpy as np
from google.cloud import storage
import viewer.blender as THREE  # selects blender as the standard backend

# --- parse arguments
import sys
FLAGS = argparse.Namespace()
if "--" in sys.argv:
  parser = argparse.ArgumentParser(prog="helloworld")
  parser.add_argument("--output", type=str, default="helloworld.png", help="output path")
  FLAGS = parser.parse_args(sys.argv[sys.argv.index("--")+1:])


# --- renderer & scene
renderer = THREE.Renderer()
renderer.set_size(200,200)
scene = THREE.Scene()
scene.frame_start = 0
scene.frame_end = 10

# --- camera
camera = THREE.OrthographicCamera(left=-.5, right=+.5, top=.5, bottom=-.5)
camera.position = (2, 2, 2)
camera.look_at(0, 0, .25)

# --- ambient light
amb_light = THREE.AmbientLight(color=0x030303)
scene.add(amb_light)

# --- sunlight
dir_light = THREE.DirectionalLight(color=0xFFFFFF, intensity=2)
dir_light.position = (.5, -.5, 2)
dir_light.look_at(0,0,0)
scene.add(dir_light)

# --- instantiate object
geometry = THREE.BoxGeometry()
material = THREE.MeshFlatMaterial()
cube = THREE.Mesh(geometry, material)
cube.scale = (.1, .1, .1)
cube.position = (0, .2, .05)
cube.keyframe_insert("position", 0)
cube.position = (0, .5, .25)
cube.keyframe_insert("position", 10)
scene.add(cube)

# --- raw mesh object
url = "https://storage.googleapis.com/tensorflow-graphics/public/spot.ply"
mesh = trimesh.load_remote(url)
faces = np.array(mesh.faces)
vertices = np.array(mesh.vertices)
# --- mesh from vertices/faces
geometry = THREE.BufferGeometry()
geometry.set_index(faces)
geometry.set_attribute("position", THREE.Float32BufferAttribute(vertices,3))
material = THREE.MeshPhongMaterial()
spot = THREE.Mesh(geometry, material)
spot.position = (-0.14, 0.22, 0)
spot.scale = (.5, .5, .5)
spot.quaternion = mathutils.Quaternion((1, 0, 0), np.pi/2) 
scene.add(spot)

# --- Invisible ground
geometry = THREE.PlaneGeometry()
material = THREE.ShadowMaterial()
floor = THREE.Mesh(geometry, material)
floor.scale = (2, 2, 2)
scene.add(floor)

def on_render_write(rendered_file: str):
  bucket = storage.Client().bucket("kubric")  #< gs://kubric
  bucket.blob(rendered_file).upload_from_filename(rendered_file)

# --- render to PNG or save .blend file (according to extension)
# renderer.render(scene, camera, path="helloworld.blend")
# renderer.render(scene, camera, path="helloworld.png")
# renderer.render(scene, camera, path="helloworld.mov")
# renderer.render(scene, camera, path="helloworld/frame_")
renderer.render(scene, camera, path=FLAGS.output, on_render_write=on_render_write)