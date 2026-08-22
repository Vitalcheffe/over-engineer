# Bando OVM — stability analysis

Bando et al. (1995):
  d²x_i/dt² = a [V(Δx_i) − dx_i/dt]

Linear stability around uniform flow gives the criterion
  a < 2 V'(s)  ⟹  unstable.

For a piecewise-linear V(Δx) with slope v_max/(Δx_max − Δx_min)
inside [Δx_min, Δx_max] and zero outside, instability appears exactly
for densities ρ ∈ (1/Δx_max, 1/Δx_min).

So the critical density is ρ_crit = 1/Δx_max.

If Δx_max = 33 m, ρ_crit = 30.3 veh/km — matches the empirical
phantom-jam threshold from Sugiyama et al. (2008) ring experiment.
