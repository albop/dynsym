from dynsym.analyze import FormulaEvaluator
from dynsym.grammar import parser
from rich import print, inspect
fe = FormulaEvaluator()


def import_model(filename):

    txt = open(filename).read()
    tree = parser.parse(txt, start="free_block")

    fe = FormulaEvaluator()
    fe.visit(tree)

    fe.steady_state = True
    residuals = [fe.visit(eq) for eq in fe.equations]

    fe.steady_state = False

    variables = fe.variables

    print("variables: "+str.join(",", variables))

    exogenous = [v for v in variables if (v in fe.symbols['process']) or (v in fe.symbols['values']) ]
    endogenous = [v for v in variables if v not in exogenous]
    print("exogenous: "+str.join(",", exogenous))
    print("endogenous: "+str.join(",", endogenous))

    import copy
    def compute_residuals():
        pass

    def steady_state():
        y = [fe.symbol_table[f"{name}[~]"] for name in  (endogenous)]
        e = [fe.symbol_table[f"{name}[~]"] for name in  (exogenous)]
        return y,e


    from dynsym.analyze import DN
    def compute_derivatives(y2,y1,y0,e):

        for i,name in enumerate(endogenous):
            k0 = f"{name}[t-1]"
            fe.symbol_table[k0] = DN(y0[i], {k0: 1})
            k1 = f"{name}[t]"
            fe.symbol_table[k1] = DN(y1[i], {k1: 1})
            k2 = f"{name}[t+1]"
            fe.symbol_table[k2] = DN(y2[i], {k2: 1})
        for i,name in enumerate(exogenous):
            k0 = f"{name}[t]"
            fe.symbol_table[k0] = DN(e[i], {k0: 1})

        results = [fe.visit(eq) for eq in fe.equations]

        import numpy as np
        neq = len(results)
        nv = len(endogenous)
        ne = len(exogenous)

        r = np.array([el.value for el in results])
        A = np.zeros((neq,nv))
        B = np.zeros((neq,nv))
        C = np.zeros((neq,nv))
        J = [A,B,C]
        D = np.zeros((neq,ne))

        

        for n,eq in enumerate(results):
            for i,v in enumerate(endogenous):
                keys = [f"{v}[t+1]", f"{v}[t]", f"{v}[t-1]"]
                for (j,key) in enumerate(keys):
                    if key in eq.derivatives:
                        J[j][n,i] = eq.derivatives[key]

            for i,v in enumerate(exogenous):
                key = f"{v}[t]"
                if key in eq.derivatives:
                    D[n,i] = eq.derivatives[key]
        return r, A,B,C,D
        
    ys, es = steady_state()
    
    r, A, B, C, D = compute_derivatives(ys, ys, ys, es)

    return fe, ys, r, A, B, C, D


import time
# warm up
import_model("example.dyno")

t1 = time.time()
res = import_model("example.dyno")
t2 = time.time()
print(f"* Residuals: {res[1]}")

print(f"Elapsed: {t2 - t1}")

from rich import print, inspect

