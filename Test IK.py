import ikpy.chain
import ikpy.utils.plot as plot_utils

import ipywidgets

import matplotlib.pyplot as plt

import numpy as np
import time
import math

chain = ikpy.chain.Chain.from_urdf_file("robot.urdf", active_links_mask=[False, True, True, True, True, True])

target_position = [2, 0, 0]

target_orientation = [0, 0, -1]

ik = chain.inverse_kinematics(target_position,target_orientation,orientation_mode="Y")
print("The angles:", list(map(lambda r: math.degrees(r), ik.tolist())))

computed_position = chain.forward_kinematics(ik)
print("Computed position: %s" % [ "%.2f" % elem for elem in computed_position[:3, 3]])

fig, ax = plot_utils.init_3d_figure()
fig.set_figheight(9)
fig.set_figwidth(13)
chain.plot(ik, ax, target=target_position)
plt.xlim(-2, 2)
plt.ylim(-2, 2)
ax.set_zlim(0, 2)
plt.show()
