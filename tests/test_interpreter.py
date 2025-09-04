#!/usr/bin/env python3
"""
Simple test script to verify the interpreter functionality.
"""

from dynsym.grammar import parser
from dynsym.analyze import FormulaEvaluator, Analyzer

def test_basic_arithmetic():
    """Test basic arithmetic operations"""
    print("Testing basic arithmetic operations...")
    
    evaluator = FormulaEvaluator()
    
    # Test simple expressions
    test_cases = [
        ("2 + 3", 5),
        ("10 - 4", 6),
        ("3 * 4", 12),
        ("15 / 3", 5),
        ("2^3", 8),
        ("2**3", 8),
        ("-5", -5),
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
    ]
    
    for expr, expected in test_cases:
        tree = parser.parse(expr, start="formula")
        result = evaluator.visit(tree)
        print(f"{expr} = {result} (expected: {expected})")
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"
    
    print("✓ Basic arithmetic tests passed!\n")

def test_symbols():
    """Test symbol evaluation"""
    print("Testing symbol evaluation...")
    
    # Create evaluator with some symbols
    symbol_table = {
        'α': 0.36,
        'σ': 2,
        'c[t]': 10,
        'y[t]': 15,
        'y[t+1]': 20,
        'k': 0.5,
    }
    
    evaluator = FormulaEvaluator(symbol_table)
    
    test_cases = [
        ("α", 0.36),
        ("σ", 2),
        ("c[t]", 10),
        ("y[t+1]", 20),
        ("α * σ", 0.72),
        ("y[t+1] - y[t]", 5),
        ("k * (y[t+1] - y[t])", 2.5),
    ]
    
    for expr, expected in test_cases:
        tree = parser.parse(expr, start="formula")
        result = evaluator.visit(tree)
        print(f"{expr} = {result} (expected: {expected})")
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"
    
    print("✓ Symbol evaluation tests passed!\n")

def test_functions():
    """Test function calls"""
    print("Testing function calls...")
    
    evaluator = FormulaEvaluator()
    
    test_cases = [
        ("sin(0)", 0),
        ("cos(0)", 1),
        ("exp(0)", 1),
        ("sqrt(4)", 2),
        ("abs(-5)", 5),
    ]
    
    for expr, expected in test_cases:
        tree = parser.parse(expr, start="formula")
        result = evaluator.visit(tree)
        print(f"{expr} = {result} (expected: {expected})")
        assert abs(result - expected) < 1e-10, f"Expected {expected}, got {result}"
    
    print("✓ Function call tests passed!\n")

def test_assignments():
    """Test assignments"""
    print("Testing assignments...")
    
    evaluator = FormulaEvaluator()
    
    # Test assignment
    assign_expr = "σ <- 2"
    tree = parser.parse(assign_expr, start="assignment_block")
    result = evaluator.visit(tree)
    print(f"Assignment result: {result}")
    
    # Check that the symbol was added to the table
    assert 'σ' in evaluator.symbol_table
    assert evaluator.symbol_table['σ'] == 2
    print(f"Symbol table after assignment: {evaluator.symbol_table}")
    
    # Test using the assigned symbol
    formula_expr = "σ * 3"
    tree = parser.parse(formula_expr, start="formula")
    result = evaluator.visit(tree)
    print(f"{formula_expr} = {result} (expected: 6)")
    assert result == 6
    
    print("✓ Assignment tests passed!\n")

def test_analyzer_convenience_class():
    """Test the Analyzer convenience class"""
    print("Testing Analyzer convenience class...")
    
    analyzer = Analyzer()
    
    # Add some symbols
    analyzer.add_symbol('x', 5)
    analyzer.add_symbol('y', 3)
    
    # Test evaluation with string input
    result = analyzer.evaluate("x + y")
    print(f"x + y = {result} (expected: 8)")
    assert result == 8
    
    # Test evaluation with complex expression
    result = analyzer.evaluate("x^2 + y^2")
    print(f"x^2 + y^2 = {result} (expected: 34)")
    assert result == 34
    
    print("✓ Analyzer tests passed!\n")

if __name__ == "__main__":
    test_basic_arithmetic()
    test_symbols()
    test_functions()
    test_assignments()
    test_analyzer_convenience_class()
    print("🎉 All tests passed!")
