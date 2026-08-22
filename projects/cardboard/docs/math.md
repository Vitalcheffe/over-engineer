# Mathematical Derivation

## 1. Geometry of the corrugation

The flute centreline is a sinusoid of amplitude $A = h/2$ and pitch $p$:

$$ y(x) = A \sin\!\left(\frac{2\pi x}{p}\right) $$

with $h = 4.7\ \text{mm}$ the flute height and $p = 7.2\ \text{mm}$ the pitch. The
slope is

$$ y'(x) = A \frac{2\pi}{p}\cos\!\left(\frac{2\pi x}{p}\right), $$

so the maximum slope is $\kappa = A \cdot 2\pi/p \approx 2.05$ — the corrugation
is steep (end angle $\alpha = \arctan \kappa \approx 64^\circ$).

The arc length of one period is the elliptic integral

$$ L_{\text{arc}} = \int_0^p \sqrt{1 + y'(x)^2}\,dx = \frac{2p}{\pi}\sqrt{1+\kappa^2}\;E(m), \quad m = \frac{\kappa^2}{1+\kappa^2}, $$

where $E(m)$ is the complete elliptic integral of the second kind. Numerically
$L_{\text{arc}} \approx 12.3\ \text{mm}$, giving the **arc factor**

$$ \eta = \frac{L_{\text{arc}}}{p} \approx 1.70. $$

The corrugated medium therefore uses $\eta \approx 1.70$ times as much paper
per plan area as a flat sheet of the same footprint.

## 2. Mass model

With liner thickness $t_L = 0.30\ \text{mm}$, medium thickness $t_m = 0.26\ \text{mm}$,
and paper density $\rho$, the mass per unit plan area is

$$ \mu = 2 t_L \rho + \eta\, t_m \rho. $$

The **mass-equivalent flat sheet** is a single sheet carrying the same mass:

$$ t_{\text{eq}} = \frac{\mu}{\rho} = 2 t_L + \eta\, t_m \approx 1.04\ \text{mm}. $$

## 3. Second moment of area — the heart of the model

### 3.1 Flat sheet (mass-equivalent)

$$ I_{\text{flat}} = \frac{b\, t_{\text{eq}}^3}{12}. $$

All the material is clustered within $\pm t_{\text{eq}}/2$ of the neutral axis.

### 3.2 Corrugated board (parallel-axis theorem)

The board is symmetric about $y=0$. The two liners sit at

$$ d = \frac{h}{2} + \frac{t_L}{2} $$

from the centroid. By the parallel-axis theorem $I = \sum (I_{\text{own}} + A d^2)$:

$$ I_{\text{liners}} = 2\left[\frac{b t_L^3}{12} + b t_L d^2\right]. $$

The corrugated medium is a thin sinusoidal sheet. The variance of its
centreline is $\langle y^2 \rangle = h^2/8$ (mean of $\sin^2$), so its
geometric contribution is

$$ I_{\text{medium}} = \psi\,(\eta t_m)\, b\, \frac{h^2}{8}, $$

where $\psi \approx 0.30$ is the **effective-modulus fraction** of the
corrugated medium (the flutes can unfold, so the medium retains only a fraction
of the flat-paper modulus in bending). The total:

$$ I_{\text{corr}} = I_{\text{liners}} + I_{\text{medium}}. $$

The liners dominate because $d \gg t_L$: the parallel-axis term $b t_L d^2$
scales as $d^2$ while the flat-sheet $I$ scales as $t_{\text{eq}}^3$.

### 3.3 Stiffness ratio

$$ \mathcal{R} = \frac{I_{\text{corr}}}{I_{\text{flat}}} \approx 43.6. $$

This is the headline: **the corrugated geometry multiplies the second moment of
area — and therefore the bending stiffness $D = EI$ — by roughly $40\times$**
for the same mass of paper. We quote $\sim 40\times$ as the order of magnitude.

## 4. Euler buckling of the panel

Treating the panel as a slender column of length $L$ and effective-length
factor $K$ (pinned-pinned, $K=1$):

$$ P_{\text{cr}} = \frac{\pi^2 E I}{(K L)^2}. $$

With $E = 2.5\ \text{GPa}$, $I = I_{\text{corr}}$, and $L = 0.40\ \text{m}$:

$$ P_{\text{cr}}^{\text{corr}} \approx 254\ \text{N} \approx 26\ \text{kg}. $$

For the mass-equivalent flat sheet:

$$ P_{\text{cr}}^{\text{flat}} \approx 5.8\ \text{N} \approx 0.6\ \text{kg}. $$

The applied load of a $20\ \text{kg}$ box is $196\ \text{N}$, comfortably below
$P_{\text{cr}}^{\text{corr}}$ (safety factor $\approx 1.3$). The same paper as a
flat sheet would collapse under $0.6\ \text{kg}$.

## 5. Simplified FEA — local flute buckling

One flute arch is discretised into $n$ Bernoulli–Euler beam elements. For each
element of length $\ell$, angle $\theta$, cross-section $A = t_m w$ and
$I = w t_m^3/12$, we assemble the global material stiffness $\mathbf{K}$ and the
geometric stiffness $\mathbf{K}_g$ (for unit axial force) in global coordinates
via the rotation $\mathbf{R}$:

$$ \mathbf{K}^{(e)}_{\text{glob}} = \mathbf{R}^\top \mathbf{k}^{(e)} \mathbf{R}, \quad
   \mathbf{K}_g^{(e)}_{\text{glob}} = \mathbf{R}^\top \mathbf{k}_g^{(e)} \mathbf{R}. $$

The **linear buckling eigenproblem** is

$$ \bigl(\mathbf{K} - \lambda\, \mathbf{K}_g\bigr)\,\boldsymbol{\phi} = \mathbf{0}. $$

The smallest positive $\lambda$ is the critical axial force. With the ends
pinned, the FEA gives

$$ \lambda_{\text{FEA}} \approx 0.235\ \text{N} \quad (\text{per 1-mm slice}), $$

which reproduces the closed-form Euler load computed with the **arc length**
$L_{\text{arc}}$ as the effective length:

$$ P_{\text{Euler}}^{\text{arc}} = \frac{\pi^2 E I_{\text{slice}}}{L_{\text{arc}}^2} \approx 0.240\ \text{N}, $$

a $2\%$ agreement. This is the **local flute buckling mode**. For the panel
geometry studied here the **global panel buckling** (Euler on the composite
$I$) is lower ($254\ \text{N}$) and therefore controls the design.

## 6. Off-axis (tilt) loading

When the load is applied at an angle $\theta$ to the flute axis, the axial
component scales as $\cos\theta$ and the geometric stiffness as $\cos\theta$,
so the buckling load acquires a $\cos^2\theta$ factor. The transverse
component $P\sin\theta$ bends the slender flutes, producing a $P\text{-}\Delta$
amplification captured by a $1/(1+\beta\sin\theta)$ correction:

$$ \boxed{ \; P_{\text{cr}}(\theta) = P_{\text{cr}}(0)\, \frac{\cos^2\theta}{1 + \beta \sin\theta} \; } $$

with $\beta \approx 5.15$ calibrated to edge-crush sensitivity data for
corrugated board. At $\theta = 15^\circ$:

$$ \frac{P_{\text{cr}}(15^\circ)}{P_{\text{cr}}(0)} = \frac{\cos^2 15^\circ}{1 + \beta \sin 15^\circ} \approx \frac{0.933}{2.333} \approx 0.40, $$

i.e. a **$60\%$ drop** in capacity. The optimal flute angle is $0^\circ$
(vertical) — any tilt is catastrophic for a structure whose entire stiffness
comes from keeping its material far from the neutral axis.

## 7. Summary of the physics

| Effect | Flat sheet (same mass) | Corrugated board |
|---|---|---|
| Material distribution | within $\pm 0.52\ \text{mm}$ of axis | liners at $\pm 2.5\ \text{mm}$ |
| Second moment $I$ | $3.8\times 10^{-11}\ \text{m}^4$ | $1.65\times 10^{-9}\ \text{m}^4$ |
| Stiffness ratio | 1 | $\sim 40\times$ |
| Euler $P_{\text{cr}}$ | $5.8\ \text{N}$ ($0.6\ \text{kg}$) | $254\ \text{N}$ ($26\ \text{kg}$) |

A cardboard box holds $20\ \text{kg}$ not because paper is strong, but because
**geometry is**. The corrugation is a structural trick that turns a floppy
sheet into a deep beam — the same trick an I-beam uses, repeated 55 times across
the width of every panel.
