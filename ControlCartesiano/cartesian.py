#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Librería 'cartesian.py', para control cartesiano de un robot SCARA INACAP.
# Versión 1.0 - Sólo para uso educativo
# Autor: Claudio Morales Díaz 
# Santiago, Chile, 2023.
# 
import sympy
import time

# Definimos una función para construir las matrices de transformación
# en forma simbóĺica a partir de los parámetros D-H

def MatrixfromDH(theta, d, a, alpha):
    # theta y alpha en radianes
    # d y a en metros
    Rz = sympy.Matrix([[sympy.cos(theta), -sympy.sin(theta), 0, 0],
                   [sympy.sin(theta), sympy.cos(theta), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    tz = sympy.Matrix([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 1, d],
                   [0, 0, 0, 1]])
    ta = sympy.Matrix([[1, 0, 0, a],
                   [0, 1, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    Rx = sympy.Matrix([[1, 0, 0, 0],
                   [0, sympy.cos(alpha), -sympy.sin(alpha), 0],
                   [0, sympy.sin(alpha), sympy.cos(alpha), 0],
                   [0, 0, 0, 1]])
    return Rz*tz*ta*Rx


def matrixFromPose(pose):
    # pose = [x, y, z, alpha, beta, gamma]
    # x, y, z en metros
    # alpha, beta, gamma en radianes
    x, y, z = pose[0], pose[1], pose[2]
    alpha, beta, gamma = pose[3], pose[4], pose[5]
    Ra = sympy.Matrix([[1, 0, 0, 0],
                   [0, sympy.cos(alpha), -sympy.sin(alpha), 0],
                   [0, sympy.sin(alpha), sympy.cos(alpha), 0],
                   [0, 0, 0, 1]])
    Rb = sympy.Matrix([[sympy.cos(beta), 0, sympy.sin(beta), 0],
                   [0, 1, 0, 0],
                   [-sympy.sin(beta), 0, sympy.cos(beta), 0],
                   [0, 0, 0, 1]])
    Rc = sympy.Matrix([[sympy.cos(gamma), -sympy.sin(gamma), 0, 0],
                   [sympy.sin(gamma), sympy.cos(gamma), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    T = Ra*Rb*Rc
    T[0,3] = x
    T[1,3] = y
    T[2,3] = z
    return T


def direct_kinematics_scara():
    q1, q2, q3 = sympy.symbols(['q1', 'q2', 'q3'])
    j1_T_j2 = MatrixfromDH(q1, 0.13, 0, 0)
    j2_T_j3 = MatrixfromDH(0, q2, 0.2, 0)
    j3_T_conn = MatrixfromDH(q3, -0.052, 0.2, sympy.pi)
    conn_T_tip = MatrixfromDH(0, 0.068, 0.013, sympy.pi)
    j1_T_tip = sympy.simplify(j1_T_j2 * j2_T_j3 * j3_T_conn * conn_T_tip)
    return j1_T_tip


def position_vector_scara(dk_matrix):
    T = matrixFromPose([dk_matrix[3], dk_matrix[7], dk_matrix[11], 0, 0, 0])
    return T[:3, 3]


def jacobian_scara():
    q1, q2, q3 = sympy.symbols(['q1', 'q2', 'q3'])
    return sympy.Matrix([[-0.2*sympy.sin(q1) - 0.213*sympy.sin(q1 + q3), 0, -0.213*sympy.sin(q1 + q3)], 
                         [0.2*sympy.cos(q1) + 0.213*sympy.cos(q1 + q3), 0, 0.213*sympy.cos(q1 + q3)], 
                         [0, 1, 0]])


def delta_q(q, delta_x):
    J = jacobian_scara()
    dx = sympy.Matrix(delta_x)
    J0 = J.evalf(subs={sympy.symbols('q1'):q[0], 
                       sympy.symbols('q2'):q[1], 
                       sympy.symbols('q3'):q[2]})
    Jinv = J0.inv()
    dq = Jinv * dx
    return dq
    
    