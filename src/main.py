import numpy as np
import matplotlib.pyplot as plt

from boost_histogram import Histogram
from boost_histogram.axis import Regular

from layer import Layer
from setup import TelescopeSetup
from physics import LychDahlTheta0, LychDahlYrms

def smear_mc(x,y,z, err_x, err_y):
    """
    Smear the Monte Carlo hit with a Gaussian distribution
    """
    x_smear = np.random.normal(x, err_x)
    y_smear = np.random.normal(y, err_y)
    return x_smear, y_smear, z


setup = TelescopeSetup()
#               z    dz   xX0   err_x  err_y
setup.add(Layer(10, 0.0320, 0.038, 0.002, 0.002, True))
setup.add(Layer(15, 0.0320, 0.038, 0.002, 0.002, True))
setup.add(Layer(20, 0.0320, 0.038, 0.002, 0.002, True))
setup.add(Layer(30, 0.0320, 0.038, 0.002, 0.002, False))
setup.add(Layer(40, 0.0320, 0.038, 0.002, 0.002, True))
# setup.add(Layer(50, 0.0320, 0.038, 0.002, 0.002, True))
# setup.add(Layer(60, 0.0320, 0.038, 0.002, 0.002, True))
# setup.add(Layer(70, 0.0320, 0.038, 0.002, 0.002, True))
# setup.add(Layer(80, 0.0320, 0.038, 0.002, 0.002, True))

n_of_tracks = 1000
do_draw = n_of_tracks < 10
sigma_x0 = 0.0
sigma_y0 = 0.0
sigma_z0 = 0.0

h_res_x = Histogram(Regular(100, -0.1, +0.1))

for trk in range(n_of_tracks):
    """ Generate track """
    x_0, y_0, z_0 = np.random.normal(0, sigma_x0), np.random.normal(0, sigma_y0), np.random.normal(0, sigma_z0)
    t_x, t_y, t_z = 0, 0, 1 # Directional vector

    beta = 0.9
    p = 500 # Momentum MeV/c
    z = 1

    fig_size_x = 2*(len(setup.layers) + 1)
    if do_draw:
        plt.figure(figsize=(fig_size_x, 5))

        # Draw the layers
        max_resolution = 1e-5
        for layer in setup.layers:
            plt.axvline(x=layer.z, color='black', linewidth=3)
            max_resolution = max(max_resolution, layer.err_x, layer.err_y)
        plt.grid()
        plt.xlim( 0.0, setup.layers[-1].z + setup.layers[0].z)
        plt.ylim(-10*max_resolution, 10*max_resolution)

    mc_points = []
    reco_hits = []
    trck_data = []
    for layer in setup.layers:
        x_in = x_0 + t_x * (layer.z - z_0)
        y_in = y_0 + t_y * (layer.z - z_0)
        z_in = layer.z - 0.5 * layer.dz

        theta_rms = LychDahlTheta0(beta, p, z, layer.xX0)
        xy_rms = layer.dz * (1 / np.sqrt(3)) * theta_rms

        x_out = np.random.normal(0, xy_rms)
        y_out = np.random.normal(0, xy_rms)
        z_out = layer.z + 0.5 * layer.dz

        x_mc = 0.5*(x_in + x_out)
        y_mc = 0.5*(y_in + y_out)
        z_mc = 0.5*(z_in + z_out)

        mc_points.append((x_mc, y_mc, z_mc))
        reco_point = smear_mc(x_mc, y_mc, z_mc, layer.err_x, layer.err_y)
        reco_hits.append(reco_point)

        if layer.use_for_tracking:
            trck_data.append(reco_point)

        #  Update the track parameters
        t_x += np.tan(np.random.normal(0, theta_rms))
        t_y += np.tan(np.random.normal(0, theta_rms))
        x_0 = x_out
        y_0 = y_out
        z_0 = z_out

        # Draw directional vector
        # plt.quiver(z_mc, x_mc, t_z, t_x, color='green', angles='xy', scale_units='xy', scale=0.2)

    x_mc, y_mc , z_mc = zip(*mc_points)
    x_rc, y_rc , z_rc = zip(*reco_hits)
    x_tk, y_tk , z_tk = zip(*trck_data)

    # Fit the reconstructed track
    tx_fit, bx = np.polyfit(z_tk, x_tk, 1)
    ty_fit, by = np.polyfit(z_tk, y_tk, 1)

    res_x = [round(x - (tx_fit * z + bx), 4) for x, y, z in reco_hits]
    res_y = [round(x - (tx_fit * z + bx), 4) for x, y, z in reco_hits]

    h_res_x.fill(res_x[1])

    if do_draw:
        z_lin = np.linspace(0, z_rc[-1]+z_rc[1]-z_rc[0], 100)
        x_fit = [tx_fit * z + bx for z in z_lin]
        plt.plot(z_lin, x_fit, 'r--', label=f'Fit: x = {tx_fit:.2f}·z + {bx:.2f}')

        # plt.plot(z_mc, x_mc, 'go')
        plt.plot([0,*z_mc], [0,*x_mc], 'g-')

        plt.plot(z_rc, x_rc, 'bo')
        # plt.plot([0,*z_rc], [0,*x_rc], 'b--')

        plt.legend()
        plt.savefig("static/telescope.png")


from scipy.optimize import curve_fit

bin_centers = h_res_x.axes[0].centers
counts = h_res_x.view()

plt.figure(figsize=(8, 5))
plt.bar(h_res_x.axes[0].centers, h_res_x.view(), width=h_res_x.axes[0].widths)

def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean)**2) / (2 * stddev**2))

initial_guess = [max(counts), 0, 0.01]
popt, pcov = curve_fit(gaussian, bin_centers, counts, p0=initial_guess)

x_fit = np.linspace(bin_centers[0], bin_centers[-1], 500)
y_fit = gaussian(x_fit, *popt)
plt.plot(x_fit, y_fit, 'r-', label=f'Gaussian Fit\nμ = {popt[1]:.2f}, σ = {popt[2]:.2f}')

plt.xlabel(r'x_{rec} - x_{trk}')
plt.ylabel('Counts')
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.savefig("static/res_x.png")