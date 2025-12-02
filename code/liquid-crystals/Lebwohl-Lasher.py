import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
from numba import jit

@jit(nopython=True)
def p2(x):
    return 0.5 * (3 * x * x - 1)

@jit(nopython=True)
def delta_energy(theta, i, j, new_angle, epsilon):
    L = theta.shape[0]
    old_angle = theta[i, j]
    dE = 0.0
    neighbors = [((i+1) % L, j), ((i-1) % L, j), (i, (j+1) % L), (i, (j-1) % L)]
    for k in range(4):
        ni, nj = neighbors[k]
        cos_old = np.cos(old_angle - theta[ni, nj])
        cos_new = np.cos(new_angle - theta[ni, nj])
        dE += -epsilon * (p2(cos_new) - p2(cos_old))
    return dE

@jit(nopython=True)
def run_simulation(theta, rands, new_angles, rs, epsilon, T):
    steps = rands.shape[0]
    for step in range(steps):
        i, j = rands[step]
        new_angle = new_angles[step]
        dE = delta_energy(theta, i, j, new_angle, epsilon)
        if dE < 0 or rs[step] < np.exp(-dE / T):
            theta[i, j] = new_angle

L = 64*2
epsilon = 1.0
T = float(sys.argv[1]) if len(sys.argv) > 1 else 0.7
steps = 20000 * L * L

theta = np.random.uniform(0, np.pi, size=(L, L))
rands = np.random.randint(0, L, (steps, 2))
new_angles = np.random.uniform(0, np.pi, steps)
rs = np.random.uniform(0, 1, size=steps)

plt.ion()
fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(theta, cmap='hsv', vmin=0, vmax=np.pi, origin='lower')
cbar = plt.colorbar(im, ax=ax, label="angle $\\theta$")

# Collect frames for animation
frames = []

# Run simulation in chunks and update plot
chunk_size = L * L
for step in range(0, steps, chunk_size):
    end_step = min(step + chunk_size, steps)
    run_simulation(theta, rands[step:end_step], new_angles[step:end_step], 
                    rs[step:end_step], epsilon, T)
    if step % 100 == 0:
        im.set_data(theta)
        ax.set_title(f"Liquid Crystal Configuration (T={T}, MCSweep={step//(L*L)})")
        plt.pause(0.0001)
        # Capture frame every 100 sweeps
        if step % (200 * chunk_size) == 0:
            frames.append(theta.copy())

# Save animation to GIF
print("Saving animation to GIF...")
fig_anim, ax_anim = plt.subplots(figsize=(8, 7))
im_anim = ax_anim.imshow(frames[0], cmap='hsv', vmin=0, vmax=np.pi, origin='lower')
cbar_anim = plt.colorbar(im_anim, ax=ax_anim, label="angle $\\theta$")

def update_frame(frame_num):
    im_anim.set_data(frames[frame_num])
    ax_anim.set_title(f"Liquid Crystal Configuration (T={T}, MCSweep={frame_num*100})")
    return [im_anim]

anim = animation.FuncAnimation(fig_anim, update_frame, frames=len(frames), 
                               interval=50, blit=True)
anim.save(f'liquid_crystal_T{T}.gif', writer='pillow', fps=20)
print(f"Animation saved as liquid_crystal_T{T}.gif")

plt.ioff()
plt.show()