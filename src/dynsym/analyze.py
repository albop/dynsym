from lark.visitors import Transformer, Interpreter
from lark.tree import Tree
from lark.lexer import Token
import math
from typing import Dict, Any, Callable, Union, List
from .autodiff import DNumber as DN

class FormulaEvaluator(Interpreter):
    """
    An interpreter that evaluates mathematical formulas as defined by the grammar.
    
    This class can evaluate:
    - Basic arithmetic operations (add, sub, mul, div, pow, neg)
    - Numbers and symbols (constants, values, variables)
    - Function calls
    - Assignments and equations
    """
    
    def __init__(self, symbol_table: Dict[str, Any] = None, function_table: Dict[str, Callable] = None, steady_state=False, diff=False):
        """
        Initialize the evaluator.
        
        Args:
            symbol_table: Dictionary mapping symbol names to their values
            function_table: Dictionary mapping function names to callable functions
            steady_state: If True, evaluates variables at their steady state (only the name of the symbol is taken into account)
        """
        super().__init__()
        self.symbol_table = symbol_table or {}
        self.function_table = function_table or {}
        self.steady_state = steady_state
        self.diff = diff
        self.symbols = {
            'constants': [],
            'values': [],
            'variables': [],
            'exogenous': []
        }
        self.equations = {}
        self.time_set = False

        # Add default mathematical functions
        from .autodiff import MATH_FUNCTIONS
        self.function_table.update(MATH_FUNCTIONS)
        # self.function_table.update({
        #     'sin': math.sin,
        #     'cos': math.cos,
        #     'tan': math.tan,
        #     'exp': math.exp,
        #     'log': math.log,
        #     'sqrt': math.sqrt,
        #     'abs': abs,
        #     'max': max,
        #     'min': min,
        # })
    
    def add_symbol(self, name: str, value: Any):
        """Add a symbol to the symbol table."""
        self.symbol_table[name] = value
    
    def add_function(self, name: str, func: Callable):
        """Add a function to the function table."""
        self.function_table[name] = func
    
    # Arithmetic operations
    def add(self, tree):
        """Handle addition: a + b"""
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        return left + right
    
    def sub(self, tree):
        """Handle subtraction: a - b"""
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        return left - right
    
    def mul(self, tree):
        """Handle multiplication: a * b"""
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        return left * right
    
    def div(self, tree):
        """Handle division: a / b"""
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        if right == 0:
            raise ZeroDivisionError("Division by zero")
        return left / right
    
    def pow(self, tree):
        """Handle exponentiation: a ^ b or a ** b"""
        base = self.visit(tree.children[0])
        exponent = self.visit(tree.children[1])
        return base ** exponent
    
    def neg(self, tree):
        """Handle negation: -a"""
        value = self.visit(tree.children[0])
        return -value
    
    # Numbers and literals
    def number(self, tree):
        """Handle numeric literals"""
        value = tree.children[0].value
        # Try to parse as int first, then float
        try:
            return int(value)
        except ValueError:
            return float(value)
    
    # Symbols
    def constant(self, tree):
        """Handle constants (symbols without time indexing)"""
        name = str(tree.children[0].children[0])
        if name in self.symbol_table:
            return self.symbol_table[name]
        else:
            raise ValueError(f"Undefined constant: {name}")
    
    def value(self, tree):
        """Handle values with specific time: name[time]"""
        name = str(tree.children[0].children[0])
        time = int(tree.children[1].children[0])

        # Create a key for the symbol table
        if self.steady_state:
            key = name
        else:
            key = f"{name}[{time}]"
            ### TODO: revisit this part
        if key in self.symbol_table:
            return self.symbol_table[key]
        else:
            raise ValueError(f"Undefined value: {key}")
    
    def variable(self, tree):
        """Handle variables with time indexing: name[t+shift]"""
        name = str(tree.children[0].children[0])
        index = str(tree.children[1].children[0])  # Usually 't'
        shift = int(tree.children[2].children[0])
        
        # TODO deal with index ~
        vars = self.symbols['variables']
        if name not in vars:
            vars.append(name)
        
        if self.time_set:
            time = self.symbol_table['t'] + shift
            key = f"{name}[{time}]"
        elif self.steady_state:
            # from rich import print
            key = f"{name}[~]"
        else:

            # Create a key for the symbol table
            if shift == 0:
                key = f"{name}[{index}]"
            elif shift > 0:
                key = f"{name}[{index}+{shift}]"
            else:
                key = f"{name}[{index}{shift}]"

        if key in self.symbol_table:
            return self.symbol_table[key]
        else:
            raise ValueError(f"Undefined variable: {key}")
    
    # Function calls
    def call(self, tree):
        """Handle function calls: func_name(arg)"""
        func_name = tree.children[0].children[0].value
        arg = self.visit(tree.children[1])
        
        if func_name in self.function_table:
            return self.function_table[func_name](arg)
        else:
            raise ValueError(f"Undefined function: {func_name}")
    
    # Equations and assignments
    def equality(self, tree):
        """Handle equations: left = right. Returns the difference (should be 0 for equality)"""
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        return right - left  # Return difference for equation solving
    
    def assignment(self, tree):
        """Handle assignments: symbol := value or symbol <- value"""
        symbol_tree = tree.children[0]
        value = self.visit(tree.children[1])
        
        name = str(symbol_tree.children[0].children[0])
        
        # if self.steady_state:
        #     key = name
        #     if self.diff and symbol_tree.data in ("variable", 'value'):
        #         value = DN(value, {key: 1.0})
        #     self.symbol_table[key] = value
        # else:
            # Extract symbol name based on symbol type
        if symbol_tree.data == "constant":
            key = name
            if name in self.symbols['constants']:
                print(f"Warning: constant {name} redefined")
            else:
                self.symbols['constants'].append(name)
            self.symbol_table[key] = value
        elif symbol_tree.data == "value":
            if name not in self.symbols['values']:
                self.symbols['values'].append(name)
            time = int(symbol_tree.children[1].children[0])
            key = f"{name}[{time}]"
            self.symbol_table[key] = value

        elif symbol_tree.data == "variable":
            index = str(symbol_tree.children[1].children[0])
            shift = int(symbol_tree.children[2].children[0])
            

            if index=='~':
                key = f"{name}[~]"
                self.symbol_table[key] = value
            else:
                if name in self.symbols['exogenous']:
                    print(f"Warning: invalid redefinition of variable {name}.")
                else:
                    self.symbols['exogenous'].append(name)
                assert shift == 0
                if shift == 0:
                    key = f"{name}[{index}]"
                elif shift > 0:
                    key = f"{name}[{index}+{shift}]"
                else:
                    key = f"{name}[{index}{shift}]"
                self.symbol_table[key] = value
                # we set the steady state value as well
                ss_key = f"{name}[~]"
                self.symbol_table[ss_key] = value

        return value
    
    def quantified_assignment(self, tree):
        bounds = tree.children[0]
        assert(bounds.data == 't_double_bound')
        lower = self.visit(bounds.children[0])
        upper = self.visit(bounds.children[1])
        try:
            assert( isinstance(lower,int) and isinstance(upper, int) and lower<upper)
        except:
            raise ValueError(f"Invalid bounds in quantified assignment: {lower}, {upper}")
        from rich import print, inspect
        print("Lower:", lower, "Upper:", upper)
        dates = range(lower, upper)
            # if name in self.symbols['exogenous']:
            #     print(f"Warning: invalid redefinition of variable {name}.")
            # else:
            #     self.symbols['exogenous'].append(name)
        t_val = self.symbol_table.get('t', None)
        self.time_set = True

        for d in dates:

            symbol_tree = tree.children[1]
            self.symbol_table['t'] = d
            value = self.visit(tree.children[2])
            
            name = str(symbol_tree.children[0].children[0])
            index = str(symbol_tree.children[1].children[0])
            shift = int(symbol_tree.children[2].children[0])
            assert index=='t' and shift==0
            key = f"{name}[{d}]"
            self.symbol_table[key] = value

        if t_val is not None:
            self.symbol_table['t'] = t_val
        else:
            self.symbol_table.pop('t')
        self.time_set = False
            # # we set the steady state value as well
            # ss_key = f"{name}[~]"
            # self.symbol_table[ss_key] = value

    # Block handling
    def assignment_block(self, tree):
        """Handle a block of assignments"""
        results = []
        for child in tree.children:
            if hasattr(child, 'data'):  # Skip newlines
                result = self.visit(child)
                results.append(result)
        return results
    
    def equation_block(self, tree):
        """Handle a block of equations"""
        results = []
        for child in tree.children:
            if hasattr(child, 'data'):  # Skip newlines
                result = self.visit(child)
                results.append(result)
        return results
    
    def free_block(self, tree):
        """Handle a mixed block of equations and assignments"""
        results = []
        for i,child in enumerate(tree.children):
            if hasattr(child, 'data'):  # Skip newlines
                result = self.visit(child)
                if child.data in ('equality', 'formula'):
                    results.append(result)
                    self.equations[len(results)] = child
                # results.append(result)
        return results


class Analyzer:
    """
    A convenience class for analyzing and evaluating parsed expressions.
    """
    
    def __init__(self, symbol_table: Dict[str, Any] = None, function_table: Dict[str, Callable] = None, steady_state=False, diff=True):
        self.evaluator = FormulaEvaluator(symbol_table, function_table, steady_state=steady_state, diff=diff)
    
    def evaluate(self, tree: Union[Tree, str]) -> Any:
        """
        Evaluate a parsed tree or parse and evaluate a string.
        
        Args:
            tree: Either a parsed Lark Tree or a string to parse and evaluate
            
        Returns:
            The evaluated result
        """
        if isinstance(tree, str):
            from .grammar import parser
            tree = parser.parse(tree, start="formula")
        
        return self.evaluator.visit(tree)
    
    def add_symbol(self, name: str, value: Any):
        """Add a symbol to the evaluator's symbol table."""
        self.evaluator.add_symbol(name, value)
    
    def add_function(self, name: str, func: Callable):
        """Add a function to the evaluator's function table."""
        self.evaluator.add_function(name, func)
    
    def get_symbol_table(self) -> Dict[str, Any]:
        """Get the current symbol table."""
        return self.evaluator.symbol_table.copy()

    @property
    def symbols(self) -> Dict[str, List[str]]:
        """Get the current symbol table."""
        return self.evaluator.symbols.copy()
