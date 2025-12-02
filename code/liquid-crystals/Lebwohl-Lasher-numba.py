import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import sys
from numba import jit, prange

@jit(nopython=True)
def p2(x):
    return 0.5 * (3 * x * x - 1)

@jit(nopython=True, parallel=True)
def delta_energy(theta, i, j, new_angle, epsilon):
    L = theta.shape[0]
    old_angle = theta[i, j]
    dE = 0.0
    neighbors = [((i+1) % L, j), ((i-1) % L, j), (i, (j+1) % L), (i, (j-1) % L)]
    for k in prange(4):
        ni, nj = neighbors[k]
        cos_old = np.cos(old_angle - theta[ni, nj])
        cos_new = np.cos(new_angle - theta[ni, nj])
        dE += -epsilon * (p2(cos_new) - p2(cos_old))
    return dE

@jit(nopython=True )
def run_simulation(theta, rands, new_angles, rs, epsilon, T):
    steps = rands.shape[0]
    for step in prange(steps):
        i, j = rands[step]
        new_angle = new_angles[step]
        dE = delta_energy(theta, i, j, new_angle, epsilon)
        if dE < 0 or rs[step] < np.exp(-dE / T):
            theta[i, j] = new_angle

L = 200
epsilon = 1.0
T = float(sys.argv[1]) if len(sys.argv) > 1 else 0.7
steps = 10000 * L * L

theta = np.random.uniform(0, np.pi, size=(L, L))
rands = np.random.randint(0, L, (steps, 2))
new_angles = np.random.uniform(0, np.pi, steps)
rs = np.random.uniform(0, 1, size=steps)

plt.ion()
fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(theta, cmap='hsv', vmin=0, vmax=np.pi, origin='lower')
cbar = plt.colorbar(im, ax=ax, label="angle $\\theta$")

# Run simulation in chunks and update plot
chunk_size = L * L
for step in range(0, steps, chunk_size):
    end_step = min(step + chunk_size, steps)
    run_simulation(theta, rands[step:end_step], new_angles[step:end_step], 
                    rs[step:end_step], epsilon, T)
    if step%100==0:
        im.set_data(theta)
        ax.set_title(f"Liquid Crystal Configuration (T={T}, MCSweep={step//(L*L)})")
        plt.pause(0.0001)

plt.ioff()
plt.show()