import yaml
examples = yaml.safe_load(open("tests/examples.yaml", "rt", encoding="utf-8").read())    

def test_parse_symbols():

    from dynsym.grammar import parser, str_expression
    for var in examples['symbols']:
        print("Parsing: ", var)
        tree = parser.parse(var, start="formula")
        s = str_expression(tree)
        print("String: ", s)
        assert s==var, f"Expected {var}, got {s}"
        ss = str_expression(tree, stringify_symbols=True)
        print("Stringified: ", ss)
        print("Pretty: ")

        print(tree.pretty())

        print("----")


def test_parse_equation():

    from dynsym.grammar import parser, str_expression
    
    var = examples['models']['dynamic_equations']

    print("Parsing: ", var)
    tree = parser.parse(var, start="equation_block")
    s = str_expression(tree)
    print("String: ", s)
    ss = str_expression(tree, stringify_symbols=True)
    print("Stringified: ", ss)
    print("Pretty: ")

    print(tree.pretty())

    print("----")




def test_parse_deep_parameters():

    from dynsym.grammar import parser, str_expression
    
    var = examples['models']['deep_parameters']

    print("Parsing: ", var)
    tree = parser.parse(var, start="assignment_block")
    s = str_expression(tree)
    print("String: ", s)
    ss = str_expression(tree, stringify_symbols=True)
    print("Stringified: ", ss)
    print("Stringified (2): ", ss)
    print("Pretty: ")

    print(tree.pretty())

    print("----")


def test_parse_free_block():

    from dynsym.grammar import parser, str_expression
    
    var = examples['models']['free_block']

    print("Parsing: ", var)
    tree = parser.parse(var, start="free_block")
    s = str_expression(tree)
    print("String: ", s)
    ss = str_expression(tree, stringify_symbols=True)
    print("Stringified: ", ss)
    print("Stringified (2): ", ss)
    print("Pretty: ")

    print(tree.pretty())

    print("----")


def test_analyze_free_block():

    from dynsym.grammar import parser, str_expression
    
    for model in ['neoclassical','rbc']:

        var = examples['models'][model]
        tree = parser.parse(var, start="free_block")

        from dynsym.analyze import Analyzer

        print(f"Working on model: {model}")


        # now time it !
        import time
        import numpy as np
        start = time.time()
        tree = parser.parse(var, start="free_block")
        an = Analyzer(steady_state=True, diff=False)
        res = an.evaluate(tree)
        end = time.time()
        print(res)
        print("Time: ", end-start)
        
        start = time.time()
        an = Analyzer(steady_state=False, diff=False)
        res = an.evaluate(tree)
        print(an.get_symbol_table())
        end = time.time()
        print(res)
        print('Time: (no ss)', end-start)

        start = time.time()
        an = Analyzer(steady_state=False, diff=True)
        res = an.evaluate(tree)
        print(an.get_symbol_table())
        end = time.time()
        print(res)
        print('Time: (no ss, diff)', end-start)

        print("----")
        print("----")
        print("----")
        print(res)
        print("----")
        print("----")
        print("----")

        variables = an.symbols['variables']
        print("Variables: ", variables)
        exogenous = an.symbols['exogenous']
        print("Exogenous: ", exogenous)
        constants = an.symbols['constants']
        print("Constants: ", constants)
        values = an.symbols['values']
        print("Values: ", values)
        print("----")
        print("Residuals: ", [r.value for r in res])
        
        start = time.time()
        endogenous = [v for v in variables if v not in exogenous]

        A = np.zeros((len(res), len(endogenous)))
        B = np.zeros((len(res), len(endogenous)))
        C = np.zeros((len(res), len(endogenous)))
        D = np.zeros((len(res), len(exogenous)))

        J = [A,B,C]
        for i,v in enumerate(endogenous):
            for k,_s in enumerate(["[t+1]", "[t]", "[t-1]"]):
                vfull = v+_s
                for n,r in enumerate(res):
                    if vfull not in r.derivatives:
                        continue
                    J[k][n,i] = r.derivatives[vfull]
        for i,v in enumerate(exogenous):
            vfull = v+"[t]"
            for n,r in enumerate(res):
                if vfull not in r.derivatives:
                    continue
                D[n,i] = r.derivatives[vfull]
        end = time.time()
        print('Time: (Jacobian)', end-start)
        print("Jacobian matrices: ")
        print(A)
        print(B)
        print(C)
        print(D)

