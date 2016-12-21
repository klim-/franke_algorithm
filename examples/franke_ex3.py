# -*- coding: utf-8 -*-
# enable true divison

import sympy as sp
import symbtools as st

x1, x2, x3 = sp.symbols("x1, x2, x3")
vec_x = sp.Matrix([x1, x2, x3])

vec_xdot = st.time_deriv(vec_x, vec_x)
xdot1, xdot2, xdot3 = vec_xdot

F_eq = sp.Matrix([xdot1*x3 - x2*x3 - x1*xdot3])


#P1i = sp.Matrix([ [x3, 0, -x1] ])
#P0i = sp.Matrix([ [-xdot3, -x3, -x2+xdot1] ])
