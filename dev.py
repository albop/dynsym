import dynsym

    
def print_an(self):

    print(self.steady_state)
    print(self.symbols)

block = """
alpha := 0.3
beta := 0.96
rho := 0.5

# endogenous parameters
r := 1/beta

# steady-state values
a[~] := alpha/2

# exogenous values
e[0] := 0.1
e[1] := 0.05
e[2] := 0.01

# exogonous variables
epsilon[t] := N(0, 0.01)

# equations
a[t] = rho*a[t-1]
"""

from dynsym.grammar import parser
from dynsym.analyze import FormulaEvaluator

tree = parser.parse(block, start="free_block")

# res = an.evaluate(tree)
# ev = an.evaluator

from rich import print
# print(ev.symbols)
# print(ev.symbol_table)
# print(ev.function_table)
# print(ev.steady_state)
# print(ev.diff)

##%


from dynsym.analyze import FormulaEvaluator, ReadAssignments

def sort_statements(tree, deep_parameters={}):
    
    context = deep_parameters.copy()

    an = ReadAssignments()
    # an.visit(tree)

    # TODO: could be done by the first parser (but cheap anyway)

    # sort all statements in a free block

    # definitions = dict(
    #     deep_parameters = [],
    #     parameters = [],
    #     values = []
    # # )
    equations = []

    n = 0
    for ch in tree.children:
        if ch.data == "equality":
            n += 1
            equations.append( ch )
        else: #its an assignement
            # continue
            print(ch)
            an.visit(ch)

    # res = []
    # for eq in equations:
    #     res.append(an.visit(eq))
    return an, equations

an,eqs = sort_statements(tree, deep_parameters={"beta": 0.96})

print(an.symbols)


