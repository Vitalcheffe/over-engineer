# Sandwich Panel Theory - Parallel-Axis Theorem

For a composite section symmetric about y=0, the second moment of area is

    I = sum_i [ I_own,i + A_i * d_i^2 ]

where d_i is the distance from the section centroid to element i's centroid.

For corrugated board:
- Two liners at d = h/2 + t_L/2 = 2.5 mm from centroid
- Liner own-I: b t_L^3 / 12 (negligible)
- Liner parallel-axis term: b t_L d^2 (DOMINATES)

The corrugated medium is a thin sinusoidal sheet. Variance of
y = (h/2) sin(...) over a period is <y^2> = h^2/8, so the medium contributes
A_medium * h^2 / 8 weighted by psi (effective modulus fraction).

Key insight: I scales as d^2 for the parallel-axis term but as t^3 for the
flat sheet. Since d ~ 2.5 mm >> t_eq ~ 1 mm, the ratio I_corr/I_flat ~
(d/t_eq)^2 * (t_L/t_eq) * 24 ~ 40x. That is the whole game.

Reference: Allen, "Analysis and Design of Structural Sandwich Panels" (1969).
