import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Line3DCollection

def generate_fcc_lattice(n_cells, lattice_const):
    basis = np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]])
    pos = []
    for x in range(n_cells):
        for y in range(n_cells):
            for z in range(n_cells):
                origin = np.array([x,y,z]) * lattice_const
                for b in basis:
                    pos.append(origin + b * lattice_const)
    return np.array(pos)

def sphere(center, radius, resolution=10):
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
    return x, y, z

def has_overlap(positions, radius, box_length):
    # Compute all pairwise differences
    delta = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    
    # Apply minimum image convention for PBC
    delta -= np.round(delta / box_length) * box_length

    # Compute pairwise distances
    dist_squared = np.sum(delta**2, axis=-1)

    # Mask out self-comparisons
    np.fill_diagonal(dist_squared, np.inf)

    # Check for any overlaps
    return np.any(dist_squared < (2 * radius)**2)

def monte_carlo_step(positions, radius, box_length, delta=0.1, fixed_idx=0):
    N = len(positions)
    idx = np.random.randint(N)
    if idx == fixed_idx:
        return  0 # skip moving the fixed particle
    move = (2 * np.random.rand(3) - 1) * delta
    old_pos = positions[idx].copy()
    positions[idx] = (positions[idx] + move) % box_length
    if has_overlap(positions, radius, box_length):
        positions[idx] = old_pos
        return 0
    else:
        return 1

def Monte_Carlo_traj(packing_fraction, box_length,sigma=1.0,  nsteps=100, freq = 10):
    vp = np.pi/6*sigma**3
    N = int(packing_fraction/vp*box_length**3)
    # number of cells needed to get enough fcc lattice points
    n_cells = int(np.ceil((N/4)**(1/3)))
    eps = 0.05
    positions = generate_fcc_lattice(n_cells, lattice_const=sigma*np.sqrt(2)+eps)
    positions = positions[:N]
    assert len(positions) == N, f"positions {positions.shape}, {N}, {n_cells}"

    vol_box = box_length ** 3
    vol_spheres_total = packing_fraction * vol_box
    vol_sphere = vol_spheres_total / N
    radius = sigma*0.5

    # Recalculate actual packing fraction for verification
    actual_pf = N * (4/3) * np.pi * radius**3 / vol_box
    if not np.isclose(actual_pf, packing_fraction, rtol=1e-1):
        raise ValueError(f"Packing fraction mismatch: requested {packing_fraction}, got {actual_pf}")

    trajectory = []
    accepted  = 0
    for _ in range(nsteps):
        # print(_)
        trial = monte_carlo_step(positions, radius, box_length, delta=0.1)
        accepted += trial 
        if _ %freq ==0:
            trajectory.append(positions.copy())

    return trajectory, accepted/nsteps
