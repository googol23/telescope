import numpy as np

def LychDahlTheta0(beta, p, z, xX0):
    return 13.6 * z / (beta*p) * np.sqrt(xX0) * (1 + 0.038 * np.log(xX0 * z**2 / beta**2))

def LychDahlYrms(x, beta, p, z, xX0):
    return LychDahlTheta0(beta, p, z, xX0) * x / np.sqrt(3)
