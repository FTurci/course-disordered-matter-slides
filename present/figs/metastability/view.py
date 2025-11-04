import os
from ovito.io import import_file
from ovito.vis import Viewport, TachyonRenderer
import ovito

from ovito.modifiers import ComputePropertyModifier
# Create an OVITO virtual viewport.
vp = Viewport(type=Viewport.Type.Perspective, camera_dir=(2, 1, -1))

# Import a trajectory and add the model to the visualization scene.
pipeline = import_file('dump.melt.lammpstrj')

modifier = ComputePropertyModifier(output_property='Radius', expressions=['0.5'])
pipeline.modifiers.append(modifier)
# Set particle color (RGB values 0-1)
color_modifier = ComputePropertyModifier(
    output_property='Color', 
    expressions=['0.0', '0.72', '1.0']  # Red color
)
pipeline.modifiers.append(color_modifier)
pipeline.add_to_scene()

# Adjust viewport camera to show the entire scene.
vp.zoom_all()
print(pipeline.source.num_frames)

for frame in range(pipeline.source.num_frames):
    # print(frame)
    vp.render_image(filename=f"f{frame}.png", frame=frame,renderer=TachyonRenderer(),)
