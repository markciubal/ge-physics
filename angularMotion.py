# Description: This file contains the functions for angular motion calculations.
# Original Author: Mark Ciubal
# i@markciubal.com

# Theta: Angular Position
def angularPosition(angularVelocity, time):
    return angularVelocity * time

# Delta Theta: Angular Displacement
def angularDisplacement(angularPositionInitial, angularPositionFinal):
    return angularPositionInitial - angularPositionFinal

# Omega: Angular Velocity
def angularVelocity(angularDisplacement, time):
    return angularDisplacement / time

# Alpha: Angular Acceleration
def angularAcceleration(alpha):
    return alpha

# Eta: Angular Jerk
def angularJerk(eta, time):
    return eta / time

def angularKineticEnergy(I, omega):
    return 0.5 * I * omega**2

def angularMomentum(I, omega):
    return I * omega

def torque(I, alpha):
    return I * alpha

# Rotational Mass
def rotationalMass(m, r):
    return m * r**2

# Angular Motion
# Time in Seconds
time = .5
angularPositionInitial = 0
angularPositionFinal = 4*3.14159
angularDisplacementValue = angularDisplacement(angularPositionInitial, angularPositionFinal)
angular_velocity = angularVelocity(angularDisplacementValue, time)
angular_position = angularPosition(angular_velocity, time)
angular_jerk = angularJerk(angular_velocity, time)
print("Angular Motion")
print("Angular Position: ", angular_position)
print("Angular Displacement: ", angular_displacement)
print("Angular Velocity: ", angular_velocity)