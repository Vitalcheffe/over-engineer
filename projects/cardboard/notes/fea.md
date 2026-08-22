# Beam Element FEA - Eigenvalue Buckling

For a 2D Bernoulli-Euler beam element with nodes i, j (6 DOFs total),
the local material stiffness k_e (6x6) and geometric stiffness k_g (6x6)
are standard (see e.g. Hughes, "The Finite Element Method", Ch. 6).

For eigenvalue (linear) buckling we solve

    (K - lambda * K_g) phi = 0

where K and K_g are the assembled global matrices and lambda is the load
multiplier. K_g is assembled for unit axial force, so lambda = critical
axial force directly.

For the corrugated flute arch:
- Discretise one sinusoidal period into n beam elements
- Each element: cross-section A = t_m * w, I = w * t_m^3 / 12
- Boundary conditions: pin both ends (fix u, v; rotation free)
- Smallest positive eigenvalue -> local flute buckling load

The curved arch has effective length = arc length (~12.3 mm), not the
chord (7.2 mm). The FEA should therefore reproduce Euler with L = L_arc,
NOT L = pitch. This is the validation check.
