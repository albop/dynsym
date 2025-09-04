#!/usr/bin/env python3

"""Test script for dual number math functions."""

import math
from dynsym.autodiff import DNumber, sin, cos, exp, log, sqrt, dabs, dmax, dmin

def test_math_functions():
    """Test math functions with both floats and dual numbers."""
    
    print("Testing math functions with floats:")
    x_float = 1.0
    print(f"sin({x_float}) = {sin(x_float)}")
    print(f"cos({x_float}) = {cos(x_float)}")
    print(f"exp({x_float}) = {exp(x_float)}")
    print(f"log({x_float}) = {log(x_float)}")
    print(f"sqrt({x_float}) = {sqrt(x_float)}")
    print(f"abs(-{x_float}) = {dabs(-x_float)}")
    
    print("\nTesting math functions with dual numbers:")
    # Create a dual number with respect to variable 'x'
    x_dual = DNumber(1.0, {'x': 1.0})
    
    print(f"x = {x_dual}")
    
    # Test trigonometric functions
    sin_result = sin(x_dual)
    print(f"sin(x) = {sin_result}")
    print(f"  Value: {sin_result.value}, Derivative: {sin_result.derivatives}")
    
    cos_result = cos(x_dual)
    print(f"cos(x) = {cos_result}")
    print(f"  Value: {cos_result.value}, Derivative: {cos_result.derivatives}")
    
    # Test exponential and logarithm
    exp_result = exp(x_dual)
    print(f"exp(x) = {exp_result}")
    print(f"  Value: {exp_result.value}, Derivative: {exp_result.derivatives}")
    
    log_result = log(exp_result)  # log(exp(x)) should give us x back
    print(f"log(exp(x)) = {log_result}")
    print(f"  Value: {log_result.value}, Derivative: {log_result.derivatives}")
    
    # Test square root
    x2_dual = DNumber(4.0, {'x': 1.0})
    sqrt_result = sqrt(x2_dual)
    print(f"sqrt(4) = {sqrt_result}")
    print(f"  Value: {sqrt_result.value}, Derivative: {sqrt_result.derivatives}")
    
    # Test absolute value
    x_neg = DNumber(-2.0, {'x': 1.0})
    abs_result = dabs(x_neg)
    print(f"abs(-2) = {abs_result}")
    print(f"  Value: {abs_result.value}, Derivative: {abs_result.derivatives}")
    
    # Test max and min
    y_dual = DNumber(3.0, {'y': 1.0})
    max_result = dmax(x_dual, y_dual)
    print(f"max(1, 3) = {max_result}")
    print(f"  Value: {max_result.value}, Derivatives: {max_result.derivatives}")
    
    min_result = dmin(x_dual, y_dual)
    print(f"min(1, 3) = {min_result}")
    print(f"  Value: {min_result.value}, Derivatives: {min_result.derivatives}")
    
    print("\nTesting composite functions:")
    # f(x) = sin(x^2) + exp(x)
    x_comp = DNumber(0.5, {'x': 1.0})
    x_squared = x_comp * x_comp
    composite_result = sin(x_squared) + exp(x_comp)
    print(f"f(x) = sin(x^2) + exp(x) at x=0.5:")
    print(f"  Value: {composite_result.value}")
    print(f"  Derivative: {composite_result.derivatives}")
    
    # Manual calculation for verification
    x_val = 0.5
    expected_value = math.sin(x_val**2) + math.exp(x_val)
    expected_derivative = 2 * x_val * math.cos(x_val**2) + math.exp(x_val)
    print(f"  Expected value: {expected_value}")
    print(f"  Expected derivative: {expected_derivative}")

if __name__ == "__main__":
    test_math_functions()
