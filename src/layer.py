import numpy as np

class Layer:
    """
    Base class for detector layers
    """
    def __init__(self, z, dz, xX0, err_x, err_y, use_for_tracking = True):
        self.z = z
        self.dz = dz
        self.xX0 = xX0
        self.err_x = err_x
        self.err_y = err_y
        self.use_for_tracking = use_for_tracking

