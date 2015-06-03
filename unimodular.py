# -*- coding: utf-8 -*-

import sympy as sp
import numpy as np
import symb_tools as st
import non_commutative_tools as nct

from IPython import embed

def prepare_example():
    # Symbole fuer y
    global yy
    yy = sp.Matrix(sp.symbols('y1, y2', commutative=False))
    global s
    s = sp.Symbol('s', commutative=False)
    yyd1 = st.perform_time_derivative(yy, yy, order=1, commutative=False)
    yyd2 = st.perform_time_derivative(yy, yy, order=2, commutative=False)
    yyd3 = st.perform_time_derivative(yy, yy, order=3, commutative=False)
    yyd4 = st.perform_time_derivative(yy, yy, order=4, commutative=False)

    # Hilfssymbole zur Konstruktion von Gleichungen
    global a1, a2, aa
    a1, a2 = aa = sp.symbols('a1:3')

    # Funktionen der Zeit
    global t
    t = nct.t
    yyf = st.symbs_to_func(yy, yy, nct.t)
    yyfd1 = yyf.diff(t, 1)
    yyfd2 = yyf.diff(t, 2)
    yyfd3 = yyf.diff(t, 3)
    yyfd4 = yyf.diff(t, 4)

    global yyaf
    yyaf = st.row_stack(yyf, yyfd1, yyfd2, yyfd3, yyfd4)

    global yya
    yya = st.row_stack(yy, yyd1, yyd2, yyd3, yyd4)


    st.makeGlobal(yya, 1)
    #return yyaf, yya

def generate_example():
    # einfacheres Beispiel:
    # ich konstruiere mir zweistufig eine integrallos umkehrbare Trafo
    # 1. Stufe
    z1 = y1*ydot2
    z2 = y2
    ZZ = ZZ1 = sp.Matrix([z1, z2])

    # 2. Stufe
    xi1 = z1
    xi2 = z2 * st.perform_time_derivative(z1, yya, commutative=False)

    # damit wird weitergerechnet
    ZZ = ZZ2 = sp.Matrix([xi1, xi2])

    # Umkehrung (Konsistenz-Probe):
    Z1 = xi1
    Z2 = xi2/st.perform_time_derivative(xi1, yya, commutative=False)

    Y1 = Z1/st.perform_time_derivative(Z2, yya, commutative=False)
    Y2 = Z2

    YY = sp.Matrix([Y1, Y2])
    assert YY == yy

    # Zu dieser Abbildung möchte ich die Jacobi-Matrix bestimmen und für
    # einen generischen Punkt prüfen, ob sie unimodular ist.
    yya.reshape(5, 2)

    P = lie_baecklund_jacobi_matrix(ZZ, yya, 2)

    J1 = lie_baecklund_jacobi_matrix(ZZ1, yya, 2)
    J2 = lie_baecklund_jacobi_matrix(ZZ2, yya, 2) # J2==P -> True

    # diese matrix sollte unimodular sein. d.h. sie sollte eine polynommatirx
    # in s als inverse haben --> mit der determinante kann man das scheinbar
    # nicht zeigen

    # neues Fazit: Ich muss Unimodularität anders überprüfen
    # Aussage von Prof. Rudolph: Dann kann man Unimodularität hier nicht mit
    # der Determinante testen
    return P, J1, J2

def lie_baecklund_jacobi_matrix(ZZ, yya, ny):
    """ jacobi matrix of lie-baecklund-transformations
    """
    # ny is the number of scalar components of y

    # determine the number of derivatives
    N = len(yya)*1.0/ny
    assert int(N) == N
    #print N

    P = sp.zeros(ny, ny)
    # yya is a col vector  -> convert to matrix
    # each row contains one derivative oder
    yyam = yya.reshape(int(N), ny)
    #print(yyam)

    # now convert to list of rows    
    for i, vv in enumerate( yyam.tolist() ):
        #print vv, i
        P+=ZZ.jacobian(vv) *s**i
    return P

def create_parameter_inverse():
    n = 2
    I0 = st.symbMatrix(n,n, 'a', commutative=False)
    I1 = st.symbMatrix(n,n, 'b', commutative=False)
    I2 = st.symbMatrix(n,n, 'c', commutative=False)

    M = I0 + I1*s + I2*s**2
    return M, I0, I1, I2

def is_square_matrix(matrix):
    """ duplicate from algorithmus_franke.py
    """
    m, n = matrix.shape
    return True if (m==n) else False

def is_zero_matrix(matrix):
    """ duplicate from algorithmus_franke.py
    """
    m_rand = st.subs_random_numbers(matrix)

    for i in xrange(len(m_rand)):
        if not np.allclose(float(m_rand[i]), 0):
            return False
    return True

def is_unit_matrix(matrix):
    """ duplicate from algorithmus_franke.py
    """
    assert is_square_matrix(matrix), "Matrix is not a square matrix."

    m, n = matrix.shape
    matrix_rand = st.subs_random_numbers(matrix)

    for i in xrange(len(matrix_rand)):
        if i%(m+1)==0:
            if not np.allclose(float(matrix_rand[i]), 1):
                return False
        elif not np.allclose(float(matrix_rand[i]), 0):
                return False
    return True

def get_homogeneous_equation(eq, pars_c):
    # Homogene gleichungen rausfinden
    eq_0 = eq.subs(st.zip0(pars_c))

    # indices:
    inhom_idcs = st.np.where(st.to_np(eq_0) != 0)[0]
    hom_idcs = st.np.where(st.to_np(eq_0) == 0)[0]

    # Homogene und Inhomogene Gleichungen trennen
    eq4 = sp.Matrix(st.np.array(eq)[hom_idcs])
    eq5 = sp.Matrix(st.np.array(eq)[inhom_idcs])

    # Probe
    assert eq4.subs(st.zip0(pars_c)) == eq4*0

    return eq4, eq5

def is_system_solvable(eq4, pars_c):
    # lösbarkeitstest
    JEh = eq4.jacobian(pars_c)
    JEh = JEh.expand()
    kk = st.nullspaceMatrix(JEh)
    k1, k2 = st.col_split(kk)

    return k1, k2

def get_homogeneous_indices_from_eq(eq):
    hom_idcs = st.np.where(st.to_np(eq) == 0)[0]
    return hom_idcs

def get_inhomogeneous_indices_from_eq(eq):
    inhom_idcs = st.np.where(st.to_np(eq) != 0)[0]
    return inhom_idcs

def solve_system_of_equations(eq):
    pass

def is_unimodular(jacobi_matrix):
    # konstruktion einer inversen
    global inv_ansatz
    inv_ansatz, I0, I1, I2 = create_parameter_inverse()

    # Gleichung die die Inverse definiert
    R = nct.nc_mul(inv_ansatz, J2).subs(zip(yya, yyaf)) - sp.eye(inv_ansatz.shape[0])
    eq = list(R)

    # test
    assert is_zero_matrix( inv_ansatz*J2 - nct.nc_mul(inv_ansatz, J2) ), "Gleichungsansatz scheint falsch zu sein."

    # wofür ist K?
    K = sp.Symbol('K')

    # s überall nach rechts schieben
    eq2 = [nct.right_shift_all(e, s, t) for e in eq]

    back_subs = list(reversed(zip(yyaf, yya)))

    eq1_symb = [e.subs(back_subs) for e in eq]
    eq2_test = sp.Matrix([nct.right_shift_all(e, s, t, yya) for e in eq1_symb])

    # Funktionen wieder durch Symbole ersetzen
    eq2 = sp.Matrix(eq2).subs(back_subs)

    w = eq2-eq2_test
    w.simplify()
    assert is_zero_matrix(w), "w should be zero-matrix"

    # Gleichungen für die einzelnen s-Potenzen aufstellen
    eq3 = st.row_stack(eq2.subs(s,0), eq2.diff(s).subs(s,0), eq2.diff(s, 2).subs(s,0), eq2.diff(s, 3).subs(s,0) )

    # jetzt spielt Nicht-Kommutativität keine Rolle mehr
    eq3, st_c_nc = nct.make_all_symbols_commutative(eq3)

    # Parameter alle in einem Vektor zusammenfassen
    global pars
    pars = sp.Matrix(list(I0) + list(I1) + list(I2))

    pars_c, st_cnc_pars = nct.make_all_symbols_commutative(pars)

    JE = eq3.jacobian(pars_c)

    # Vermutung: ich habe mehr Gleichungen als Variablen. Weil die
    # allermeisten Gleichungen aber homogen sind, ist das kein
    # prinzipielles Problem... am besten wäre es, wenn in den
    # inhomogenen Gleichungen Koeffizienten auftauchen, die die sonst
    # nirgendwo auftauchen

    eq4, eq5 = get_homogeneous_equation(eq3, pars_c)

    k1, k2 = is_system_solvable(eq4, pars_c)

    # Hoffnung: ich kann jetzt auch noch das inhomogene GS erfüllen
    K = a1*k1 + a2*k2
    eq6 = eq5.subs(zip(pars_c, K))
    eq6.simplify()

    sol = sp.solve(eq6, aa)

    tmp = eq6.subs(sol)
    tmp.simplify()
    assert tmp == eq6*0

    KK = K.subs(sol)
    KK.simplify()

    # KK enthält die Lösung für den Parameter Vektor (kommutative Variablen)
    # Jetzt fehlt noch dir Rücksubstitution auf nichtkommutative Variablen

    KK_nc = KK.subs(st_c_nc)
    
    return test_unimodularity(KK, KK_nc, pars_c)


def test_unimodularity(KK, KK_nc, pars_c):
    """ probe ob tatsächlich M*A gleich der einheitsmatrix entspricht
    """
    sol_c = zip(pars_c, KK)
    sol_nc = zip(pars, KK_nc)
    Inv = inv_ansatz.subs(sol_nc)
    Invf = Inv.subs(zip(yya, yyaf))
    J2f = J2.subs(zip(yya, yyaf))

    rr = nct.nc_mul(J2f, Invf)
    rr2 = nct.right_shift_all(rr)
    # sollte einheitsmatrix sein
    if not is_unit_matrix(st.subs_random_numbers(rr2)):
        return False

    ww = nct.nc_mul(Invf, J2f)
    ww2 = nct.right_shift_all(ww)
    # sollte ebenfalls einheitsmatrix sein
    if not is_unit_matrix(st.subs_random_numbers(ww2)):
        return False

    r = nct.nc_mul(J2, Inv)
    r2 = nct.right_shift_all(r, s, t, yy)
    # sollte auch einheitsmatrix sein
    if not is_unit_matrix(st.subs_random_numbers(r2)):
        return False

    return [Invf, J2f]

prepare_example()
P, J1, J2 = generate_example()
value = is_unimodular(J2)

print "finished!" 
if type(value) != bool:
    print "J2 is unimodular. its inverse is" 
    sp.pprint(value[0])
else:
    print "J2 is not unimodular!" 
