import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation, PillowWriter

# Parameters
L = 5.4
n_steps = 300
n_colloids = 2
n_polymers = 200
max_disp = 0.3

r_colloid = 0.5
r_polymer = 0.1

def pbc(x): 
    return x % L

def dist_pbc(r1, r2):
    delta = (r1 - r2 + L/2) % L - L/2
    return np.linalg.norm(delta)

def is_overlapping(new_pos, others, other_radii, new_radius):
    for pos, rad in zip(others, other_radii):
        if dist_pbc(new_pos, pos) < (rad + new_radius):
            return True
    return False


pos_colloids = [[0.75*L, 0.75*L],[0.5*L,0.5*L]]
pos_colloids = np.array(pos_colloids).reshape(n_colloids, 2)
pos_polymers = np.random.uniform(0, L, (n_polymers, 2))
for i in range(n_polymers):
    while is_overlapping(pos_polymers[i], pos_colloids, [r_colloid]*n_colloids, r_polymer):
        pos_polymers[i] = np.random.uniform(0, L, 2)

# Plot setup
fig, ax = plt.subplots(figsize=(4,4))
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_aspect('equal')

colloid_circles = [Circle(pos, r_colloid, facecolor='orange', edgecolor='black') for pos in pos_colloids]
polymer_circles = [Circle(pos, r_polymer, facecolor='cyan', edgecolor='black', alpha=0.6) for pos in pos_polymers]

for c in colloid_circles + polymer_circles:
    ax.add_patch(c)

def update(frame):
    global pos_colloids, pos_polymers

    # Move polymers randomly with overlap check
    for i in range(n_polymers):
        trial = pbc(pos_polymers[i] + np.random.uniform(-max_disp, max_disp, 2))
        if not is_overlapping(trial, pos_colloids, [r_colloid]*n_colloids, r_polymer):
            pos_polymers[i] = trial

    # Move only colloid 0 with overlap check
    i = 0
    trial = pbc(pos_colloids[i] + np.random.uniform(-max_disp, max_disp, 2))
    others = np.vstack((pos_polymers, pos_colloids[1:]))  # exclude moving colloid 0
    radii = [r_polymer]*n_polymers + [r_colloid]*(n_colloids - 1)
    if not is_overlapping(trial, others, radii, r_colloid):
        pos_colloids[i] = trial

    # Update patch positions
    for i, c in enumerate(colloid_circles):
        c.center = pos_colloids[i]
    for i, c in enumerate(polymer_circles):
        c.center = pos_polymers[i]

    return colloid_circles + polymer_circles

ani = FuncAnimation(fig, update, frames=n_steps, interval=30, blit=True)

# Save gif
ani.save("aoanimation.gif", writer=PillowWriter(fps=30))

# plt.show()
