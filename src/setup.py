from layer import Layer

class TelescopeSetup:
    """
    A class to set up the telescope simulation environment.
    """
    def __init__(self, layers = None):
        if layers is None:
            layers = []
        self.layers = layers

    def add(self, layer):
        """
        Add up the layers of the telescope.
        """
        self.layers.append(layer)


