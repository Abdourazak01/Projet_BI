import numpy as np
from scipy.optimize import linprog

c = [1, 1]
A_ub = [[-1, -2]]
b_ub = [-6]
A_eq = [[1, 1]]
b_eq = [4]
bounds = [(0, None), (0, None)]

# Solution 1 : méthode par défaut
print("Solution 1 (par défaut) :")
res1 = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
               bounds=bounds, method='highs')
print(f"x1 = {res1.x[0]}, x2 = {res1.x[1]}")
print(f"Z = {res1.fun}")
print()

# Solution 2 : avec point initial différent
print("Solution 2 (avec initialisation différente) :")
res2 = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
               bounds=bounds, method='highs',
               options={'presolve': False})  # Désactiver la pré-résolution
print(f"x1 = {res2.x[0]}, x2 = {res2.x[1]}")
print(f"Z = {res2.fun}")
print()

# Solution 3 : méthode simplex
print("Solution 3 (méthode simplex) :")
res3 = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
               bounds=bounds, method='simplex')
print(f"x1 = {res3.x[0]}, x2 = {res3.x[1]}")
print(f"Z = {res3.fun}")