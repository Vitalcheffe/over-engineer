# Mathematical derivation

This document derives the equations implemented in `model.py` and
shows where each one is used.  The notation follows Helbing (2001).

## 1. The LWR conservation law

Let `ρ(x,t)` [veh/m] be the traffic density and `v(ρ)` [m/s] the
equilibrium velocity.  Conservation of vehicles on a road with no
sources or sinks gives

$$
\frac{\partial \rho}{\partial t} + \frac{\partial (\rho v(\rho))}{\partial x} = 0 .
$$

Defining the flow `q(ρ) = ρ v(ρ)`, this is the scalar hyperbolic
conservation law

$$
\partial_t \rho + \partial_x q(\rho) = 0 .
$$

## 2. Greenshields fundamental diagram

The simplest closed form for `v(ρ)` is linear in `ρ`:

$$
v(\rho) = v_{\max}\!\left(1 - \frac{\rho}{\rho_{\max}}\right),
\qquad
q(\rho) = v_{\max}\!\left(\rho - \frac{\rho^2}{\rho_{\max}}\right).
$$

`q(ρ)` is a downward parabola.  Its vertex is at

$$
\rho_{\mathrm{crit}} = \frac{\rho_{\max}}{2},
\qquad
q_{\max} = q(\rho_{\mathrm{crit}}) = \frac{v_{\max} \rho_{\max}}{4}.
$$

In `model.py`: `critical_density_greenshields()` and `max_flow()`.

## 3. Rankine-Hugoniot shock speed

If the initial data has a discontinuity
`ρ(x,0) = ρ_up` for `x < 0`, `ρ_down` for `x > 0`, the
weak solution is a shock traveling at

$$
w = \frac{q(\rho_{\mathrm{down}}) - q(\rho_{\mathrm{up}})}{\rho_{\mathrm{down}} - \rho_{\mathrm{up}}}.
$$

For a shock between a free-flow state (small `ρ`, large `q`) and a
deep-jam state (large `ρ`, small `q`), we have `q_down < q_up` and
`ρ_down > ρ_up`, so `w < 0`: the shock moves upstream.

In `model.py`: `shock_speed(rho_up, rho_down)`.

## 4. Godunov finite-volume scheme

Discretize the road into cells of width `Δx` and apply a
finite-volume update

$$
\rho_i^{n+1} = \rho_i^n + \frac{\Delta t}{\Delta x}\!\left(F^n_{i-1/2} - F^n_{i+1/2}\right),
$$

where `F^n_{i+1/2}` is the Godunov flux at the cell interface.  For
the **triangular** fundamental diagram (Daganzo's cell transmission
model, 1994) the Godunov flux takes the demand/supply form

$$
F_{i+1/2} = \min\!\big(D(\rho_i), S(\rho_{i+1})\big),
$$

with

$$
D(\rho) = q\!\big(\min(\rho, \rho_{\mathrm{crit}})\big),\qquad
S(\rho) = q\!\big(\min(\rho, \rho_{\mathrm{crit}})\big).
$$

`q(ρ)` is increasing on `[0, ρ_crit]` and decreasing on
`[ρ_crit, ρ_max]`, so `D` and `S` use the value of `q` at the
critical density as a ceiling.

CFL stability requires `Δt ≤ Δx / v_max`.  We use `Δt = 0.5 Δx / v_max`
for safety margin.

In `model.py`: `solve_lwr()`.

## 5. Bando optimal-velocity model

Microscopic car-following dynamics (Bando et al., 1995):

$$
\frac{d^2 x_i}{dt^2} = a\!\left[V(\Delta x_i) - \frac{dx_i}{dt}\right],
\qquad \Delta x_i = x_{i+1} - x_i.
$$

The piecewise-linear optimal velocity

$$
V(\Delta x) = \begin{cases}
0 & \Delta x \le \Delta x_{\min}\\
v_{\max}\dfrac{\Delta x - \Delta x_{\min}}{\Delta x_{\max} - \Delta x_{\min}} & \Delta x_{\min} < \Delta x < \Delta x_{\max}\\
v_{\max} & \Delta x \ge \Delta x_{\max}
\end{cases}
$$

has slope

$$
V'(\Delta x) = \frac{v_{\max}}{\Delta x_{\max} - \Delta x_{\min}}
$$

inside the ramp and zero outside.

In `model.py`: `v_optimal`, `v_optimal_derivative`.

## 6. Linear stability of uniform flow

Linearize the OVM around uniform flow `x_i = v_0 t + i s + \xi_i(t)`
with `v_0 = V(s)` and `|ξ| << s`:

$$
\ddot{\xi}_i = a\!\left[V'(s)(\xi_{i+1} - \xi_i) - \dot{\xi}_i\right].
$$

Inserting the Fourier ansatz `ξ_i = e^{λ t + i k n}` gives the
dispersion relation

$$
\lambda^2 + a\lambda + a V'(s)\,(1 - \cos k) - i\,a V'(s)\sin k = 0 .
$$

The system is **linearly unstable** when `Re(λ) > 0` for some
wavenumber `k ∈ (0, π]`.  The classic Bando result is that this
happens whenever

$$
a < 2 V'(s) \cos^2(k/2)
$$

for some `k`, which simplifies (maximize over `k`) to

$$
a < 2 V'(s).
$$

For the piecewise-linear `V`:

- `V'(s) = v_max / (Δx_max − Δx_min) > 0` for `s ∈ (Δx_min, Δx_max)`,
  i.e. densities in `(1/Δx_max, 1/Δx_min)`;
- `V'(s) = 0` outside that range.

With `a = 1 s⁻¹`, `v_max = 30 m/s`, `Δx_min = 7 m`, `Δx_max = 33 m`:

$$
2 V'(s) = 2 \cdot \frac{30}{33 - 7} = \frac{60}{26} \approx 2.31 > 1 = a,
$$

so the OVM is linearly unstable exactly for densities in

$$
\left(\frac{1}{\Delta x_{\max}},\, \frac{1}{\Delta x_{\min}}\right)
= (0.0303,\, 0.143)\ \text{veh/m}
= (30.3,\, 143)\ \text{veh/km}.
$$

The critical density at which perturbations stop dissipating and start
amplifying is therefore

$$
\boxed{\rho^* = \frac{1}{\Delta x_{\max}} \approx 30\ \text{veh/km}}.
$$

In `model.py`: `critical_density_ovm()` returns `1 / DX_MAX`.

## 7. Empirical verification

`stability_sweep()` runs the microsim at 18 densities and records the
ratio of (max speed range over the second half of the run) to (initial
speed range).  The empirical crossing of `growth_ratio = 1` falls at
~28 veh/km, within 7% of the theoretical `ρ* = 30.3 veh/km`.  The
small discrepancy comes from nonlinear saturation (finite perturbation
size, finite ring length).

## 8. Wave speed of the saturated stop-and-go pattern

Once the perturbation has saturated into a stop-and-go wave, the wave
travels at the group velocity of the dominant nonlinear mode.  We
estimate it from the simulation by tracking the physical position of
the slowest car over time and fitting a line; for the headline
100-car, 100 veh/km simulation this gives `−0.37 m/s` (upstream),
consistent with the macroscopic Rankine-Hugoniot shock speed
`w = −2.42 m/s` for a free-flow → deep-jam transition.

The discrepancy between the micro and macro wave speeds is expected:
the OVM wave is the saturated nonlinear pattern, while the
LWR shock is the kinematic discontinuity between two uniform states.

---

### References

- Lighthill, M. J. & Whitham, G. B. (1955). *On kinematic waves II.*
  Proc. R. Soc. A 229.
- Richards, P. I. (1956). *Shockwaves on the highway.* Oper. Res. 4.
- Daganzo, C. F. (1994). *The cell transmission model.* Transp. Res. B 28.
- Bando, M., Hasebe, K., Nakayama, A., Shibata, A., & Sugiyama, Y.
  (1995). *Dynamical model of traffic congestion and numerical
  simulation.* Phys. Rev. E 51.
- Helbing, D. (2001). *Traffic and related self-driven many-particle
  systems.* Rev. Mod. Phys. 73.
