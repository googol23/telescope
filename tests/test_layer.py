from src.layer import Layer

from pytest import *

def test_layer_initialization():
    # Test initialization of Layer class
    layer = Layer(index=1, z=10.0, err_x=0.1, err_y=0.1, err_q=0.1, xX0=0.5)
    assert layer.index == 1
    assert layer.z == 10.0
    assert layer.err_x == 0.1
    assert layer.err_y == 0.1
    assert layer.err_q == 0.1
    assert layer.xX0 == 0.5

