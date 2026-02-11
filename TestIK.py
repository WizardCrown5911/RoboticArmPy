import ikpy.chain
import ikpy.utils.plot as plot_utils

import ipywidgets

import matplotlib.pyplot as plt

import numpy as np
import time
import math

chain = ikpy.chain.Chain.from_urdf_file("robot.urdf", active_links_mask=[False, True, True, True, True, True])


def plot(ik1,target_position1):
    fig, ax = plot_utils.init_3d_figure()
    fig.set_figheight(9)
    fig.set_figwidth(13)
    chain.plot(ik1, ax, target=target_position1)
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    ax.set_zlim(0, 2)
    plt.show()


def IK(chain,target_position,target_orientation):

    ik = chain.inverse_kinematics(target_position, target_orientation, orientation_mode="Y")
    angles = list(map(lambda r: math.degrees(r), ik.tolist()))
    #print("The angles:", angles)

    computed_position = chain.forward_kinematics(ik)
    #print("Computed position: %s" % ["%.2f" % elem for elem in computed_position[:3, 3]])
    #plot(ik,computed_position)
    return angles

IK(chain,[0,0,3],[0,0,0])