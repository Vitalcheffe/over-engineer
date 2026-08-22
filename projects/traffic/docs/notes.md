# Lighthill-Whitham-Richards — research notes

## Source equations

Lighthill & Whitham (1955), *On kinematic waves II*:
```
∂ρ/∂t + ∂(ρv)/∂x = 0
```

Richards (1956) independently:
```
∂ρ/∂t + ∂q(ρ)/∂x = 0
```

Both assumed an equilibrium relation q(ρ).  This is the scalar
hyperbolic conservation law of traffic flow.

## Greenshields fundamental diagram

Greenshields (1935) fit a linear v(ρ):
```
v(ρ) = v_max (1 − ρ/ρ_max)
```
So q(ρ) is a parabola:
```
q(ρ) = ρ v(ρ) = v_max (ρ − ρ²/ρ_max)
```
Peak at ρ = ρ_max/2, q_max = v_max ρ_max / 4.

Real fundamental diagrams are skewed (more capacity preserved on the
free-flow side, sharper drop into jam).  Greenshields over-estimates
ρ_crit.  Use triangular for the macro side.

## Triangular fundamental diagram (Daganzo CTM)

q(ρ) = min(v_max ρ, w (ρ_max − ρ))
where w = v_max ρ_crit / (ρ_max − ρ_crit) is the congestion-wave speed.

For ρ_crit = 0.030 veh/m, ρ_max = 0.143 veh/m:
```
w = 30 × 0.030 / (0.143 − 0.030) = 0.90 / 0.113 ≈ 7.96 m/s
```

## Rankine-Hugoniot

For initial data with a discontinuity ρ_up | ρ_down, the shock
travels at:
```
w = (q_down − q_up) / (ρ_down − ρ_up)
```

Upstream shock: ρ_down > ρ_up (jam denser than free-flow), and
q_down < q_up (jam has lower flow because it's on the right of the
parabola past the peak).  Both conditions together ⇒ w < 0.

Concrete example: ρ_up = 0.05 veh/m (free side, q = 0.97 veh/s),
ρ_down = 0.13 veh/m (deep jam, q = 0.36 veh/s).
```
w = (0.36 − 0.97) / (0.13 − 0.05) = −7.6 m/s  (upstream)
```

## Bando OVM stability

Bando et al. (1995):
```
d²x_i/dt² = a [V(Δx_i) − dx_i/dt]
```

Linear stability around uniform flow x_i = v_0 t + i s:
```
λ² + aλ + aV'(s)(1 − cos k) − i aV'(s) sin k = 0
```

Stability criterion: a ≥ 2 V'(s) (after maximizing over k).

For piecewise-linear V with slope v_max/(Δx_max − Δx_min) inside
the ramp and 0 outside, instability appears exactly for densities
in (1/Δx_max, 1/Δx_min).

With v_max=30, Δx_max=33, Δx_min=7:
```
ρ_crit = 1/Δx_max = 1/33 = 0.0303 veh/m = 30.3 veh/km  ✓
```

This matches the task's stated critical density of ~30 veh/km.

## Implementation pitfalls (recorded after debugging)

1. **Sorted-order maintenance.**  The OVM is a car-following model:
   each car's update uses the gap to its leader.  After enough time,
   the position array's "natural" order gets scrambled because the
   ring wraparound breaks the sortedness assumption.  The fix is to
   argsort the position array at every timestep before computing
   gaps.

2. **No-overtake clamp.**  Without it, the OVM lets cars pass each
   other in tight jams, which produces unphysical "superposition"
   events.  Clamp v_i so that v_i·dt ≤ gap_i − 0.5 m.

3. **Wave-speed detection.**  Tracking argmin(speeds) over time and
   fitting a line is brittle when the wave is noisy.  Cross-correlation
   of the speed profile across frames would be more robust but slower.
   For the chosen parameters the linear fit is sufficient.

4. **Perturbation metric.**  Reporting "final speed range / initial
   speed range" is wrong: in saturated nonlinear regimes the wave
   can return to uniform at the final frame by coincidence.  Use
   the MAX range over the second half of the run, divided by the
   initial range.
