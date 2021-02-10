# coding: utf8

# Other modules
import numpy as np
from numpy import linalg as la
from math import pi

from .PD import PD

################
#  CONTROLLER ##
################ 

def control_fall(q, solo):
	return np.zeros((12,1))

def control_stand(q, qdot, solo, dt):
	qa = q[7:]
	qa_dot = qdot[6:]
	qa_ref = np.zeros((12, 1))  # target angular positions for the motors
	qa_dot_ref = np.zeros((12, 1))  # target angular velocities for the motors
	torque_sat = 3  # torque saturation in N.m
	torques_ref = np.zeros((12, 1))  # feedforward torques
	torques = PD(qa_ref, qa_dot_ref, qa, qa_dot, dt, 1, 1, torque_sat, torques_ref)
	return torques

def control_jump(q, qdot, solo, dt):
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
	if not control_jump.isCrouched:
		control_jump.isCrouched = la.norm(qa-q_crouch)<0.5
	if control_jump.isCrouched and not control_jump.inAir:
		control_jump.inAir = la.norm(qa-q_jump)<0.5

	if not control_jump.isCrouched:
		qa_ref = q_crouch
		KD = 1
		KP = 5
	else:
		qa_ref = q_jump
		KD = 0.5
		KP = 20
	
	if control_jump.inAir:
		qa_ref = q_air
		KD = 1
		KP = 10
	
	
	qa_dot_ref = np.zeros((12, 1))  # target angular velocities for the motors
	torque_sat = 3  # torque saturation in N.m
	torques_ref = np.zeros((12, 1))  # feedforward torques
	torques = PD(qa_ref, qa_dot_ref, qa, qa_dot, dt, KP, KD, torque_sat, torques_ref)

	return torques

control_jump.isCrouched = False
control_jump.inAir = False


def control_traj(solo, t, dt, q, qdot, traj):
	torque_sat = 3  # torque saturation in N.m
	torques_ref = np.zeros((12, 1))  # feedforward torques
	threshold = 0.3

	qa = q[7:]
	qa_dot = qdot[6:]

	# Reach the first position of the trajectory first
	if not control_traj.initialized :
		control_traj.offset = t

		qa_ref = traj.getElement('q', 0).reshape((12, 1))
		qadot_ref = traj.getElement('q_dot', 0).reshape((12, 1))

		torques = PD(qa_ref, qadot_ref, qa, qa_dot, dt, Kp=1, Kd=0.5, torque_sat=torque_sat, torques_ref=torques_ref)

		# If it is reached, continue
		if np.linalg.norm(qa_ref-qa) < threshold:
			print('Reached first state in {0:3.2f} s.'.format(t))
			control_traj.initialized = True
	
	# Then run the trajectory
	else:
		# Apply offset
		t = t-control_traj.offset

		# Get the current state in the trajectory
		if t>np.max(traj.getElement('t', -1)) and not control_traj.ended:
			print("End of trajectory. Staying in last state.")
			control_traj.ended = True

		qa_ref = traj.getElementAtTime('q', t).reshape((12, 1))
		qadot_ref = traj.getElementAtTime('q_dot', t).reshape((12, 1))
		torques_ref = traj.getElementAtTime('torques', t).reshape((12, 1))

		kp = traj.getElementAtTime('gains', t)[0]
		kd = traj.getElementAtTime('gains', t)[1]

		torques = PD(qa_ref, qadot_ref, qa, qa_dot, dt, Kp=kp, Kd=kd, torque_sat=torque_sat, torques_ref=torques_ref)
	
	return torques

control_traj.initialized = False
control_traj.ended = False
control_traj.offset = 0



####################
#  SECURITY CHECK ##
####################

def torque_check(torque, torque_threshold):
	for art in range(12):
		if torque(art)>torque_treshold:
			return false
	return true
