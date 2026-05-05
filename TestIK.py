import ikpy.chain
import numpy as np
import math

# Load chain

chain = ikpy.chain.Chain.from_urdf_file(
"robot.urdf",
active_links_mask=[False, True, True, True, True, True]
)

# Joint state

current_joints = np.zeros(len(chain.links))

# Servo config

SERVO_LIMITS = [(0, 180)] * 5
SERVO_DIRECTIONS = [1, -1, 1, 1, -1]
SERVO_OFFSETS = [90, 90, 90, 90, 90]

# -----------------------------

# Forward kinematics

# -----------------------------

def forward_pos(joints):
    fk = chain.forward_kinematics(joints)
    return fk[:3, 3]

def get_end_effector_axes():
    fk = chain.forward_kinematics(current_joints)
    R = fk[:3, :3]


    # Columns of rotation matrix = local axes
    x_axis = R[:, 0]  # forward
    y_axis = R[:, 1]  # left/right
    z_axis = R[:, 2]  # up

    return x_axis, y_axis, z_axis

def get_base_yaw():
    fk = chain.forward_kinematics(current_joints)
    R = fk[:3, :3]


    # Project forward vector onto ground plane
    forward = R[:2, 0]  # x-axis projected to XY
    yaw = np.arctan2(forward[1], forward[0])

    return yaw




# -----------------------------

# Position Jacobian

# -----------------------------

def compute_jacobian_pos(joints):
    eps = 1e-5
    J = np.zeros((3, len(joints)))


    p0 = forward_pos(joints)

    for i in range(len(joints)):
        j_copy = joints.copy()
        j_copy[i] += eps

        p1 = forward_pos(j_copy)
        J[:, i] = (p1 - p0) / eps

    return J


# -----------------------------

# IK solver

# -----------------------------

def damped_least_squares(J, dx, damping=0.1):
    JT = J.T
    identity = np.eye(J.shape[0])
    inv = np.linalg.inv(J @ JT + (damping ** 2) * identity)
    return JT @ inv @ dx

def update_joints_from_velocity(target_velocity, dt=0.01):
    global current_joints


    J = compute_jacobian_pos(current_joints)

    # Only position part
    v = target_velocity[:3]

    dq = damped_least_squares(J, v)

    current_joints = current_joints + dq * dt

    return current_joints


# -----------------------------

# Manual joint control

# -----------------------------

def adjust_joint(index, delta):
    global current_joints
    current_joints[index] += delta

# -----------------------------

# Servo output

# -----------------------------

def get_servo_angles():
    angles = []


    for i, joint_angle in enumerate(current_joints[1:6]):
        deg = math.degrees(joint_angle)

        deg *= SERVO_DIRECTIONS[i]
        deg += SERVO_OFFSETS[i]

        min_lim, max_lim = SERVO_LIMITS[i]
        deg = max(min_lim, min(max_lim, deg))

        angles.append(int(deg))

    return angles

