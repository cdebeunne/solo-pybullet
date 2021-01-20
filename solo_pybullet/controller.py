# coding: utf8

# Other modules
import numpy as np
from numpy import linalg as la
# Pinocchio modules
import pinocchio as pin  # Pinocchio library
from math import pi

from .PD import PD

################
#  CONTROLLER ##
################
def stand(q, qdot, solo, dt):
    qa = q[7:]
    qa_dot = qdot[6:]
    qa_ref = np.zeros((12, 1))  # target angular positions for the motors
    qa_dot_ref = np.zeros((12, 1))  # target angular velocities for the motors
    torque_sat = 3  # torque saturation in N.m
    torques_ref = np.zeros((12, 1))  # feedforward torques
    torques = PD(qa_ref, qa_dot_ref, qa, qa_dot, dt, 1, 1, torque_sat, torques_ref)
    return torques

def jump(q, qdot, solo, dt, isCrouched, inAir):
    qa = q[7:]
    qa_dot = qdot[6:]
    qa_ref = np.zeros((12, 1))  # target angular positions for the motors
    
    # define the different configurations of the jump
    pos_crouch = np.array([[0, 0.9*pi/2, -0.9*pi], \
                        [0, 0.9*pi/2, -0.9*pi], \
                        [0, -0.9*pi/2, 0.9*pi], \
                        [0, -0.9*pi/2, 0.9*pi]])
    q_crouch = np.zeros((12,1))
    q_air = np.zeros((12,1))
    q_jump = np.zeros((12,1))
    for leg in range(4):
            for art in range(3):
                q_crouch[3*leg+art] = 0.8*pos_crouch[leg, art]
                q_air[3*leg+art] = 0.5*pos_crouch[leg,art]

    # check the step of the jump
    if not isCrouched:
        isCrouched = la.norm(qa-q_crouch)<0.5
    if isCrouched and not inAir:
        inAir = la.norm(qa-q_jump)<0.5

    if not isCrouched:
        qa_ref = q_crouch
        KD = 1
        KP = 5
    else:
        qa_ref = q_jump
        KD = 0.5
        KP = 20
    
    if inAir:
        qa_ref = q_air
        KD = 1
        KP = 10
    
    
    qa_dot_ref = np.zeros((12, 1))  # target angular velocities for the motors
    torque_sat = 3  # torque saturation in N.m
    torques_ref = np.zeros((12, 1))  # feedforward torques
    torques = PD(qa_ref, qa_dot_ref, qa, qa_dot, dt, KP, KD, torque_sat, torques_ref)

    return torques, isCrouched, inAir
    
def splineJump(q, qdot, solo, q_traj, qdot_traj, gains, step, dt):
	qa = q[7:]
	qa_dot = qdot[6:]
	if step < q_traj.shape[1]:
		KD = gains[0,step]
		KP = gains[1,step]
		qa_ref = q_traj[:, step].reshape(12,1)  # target angular positions for the motors
		qa_dot_ref = qdot_traj[:, step].reshape(12,1)  # target angular velocities for the motors
	else:
		KD = 1
		KP = 10
		qa_ref = q_traj[:, q_traj.shape[1]-1].reshape(12,1)
		qa_dot_ref = np.zeros((12, 1))
	torque_sat = 3  # torque saturation in N.m
	torques_ref = np.zeros((12, 1))  # feedforward torques
	torques = PD(qa_ref, qa_dot_ref, qa, qa_dot, dt, KP, KD, torque_sat, torques_ref)
	
	return torques
    
 
def fall(q, solo):
	return np.zeros((12,1))


####################
#  SECURITY CHECK ##
####################

def torque_check(torque, torque_threshold):
	for art in range(12):
		if torque(art)>torque_treshold:
			return false
	return true
