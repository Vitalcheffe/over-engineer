# Corrugated Board Geometry

Standard single-wall corrugated board (FEFCO specs):

- Flute type: B-flute (common for small boxes)
- Flute height h: 4.7 mm
- Flute pitch p: 7.2 mm
- Flutes per metre: ~140

Liner: kraft paper, two layers
Medium: corrugated kraft, one layer (sinusoidal)

The flute is well approximated by a sinusoid y = (h/2) sin(2 pi x / p).
End slope = (h/2)(2 pi / p) = 2.05 -> end angle ~64 deg.

Arc length per period is an elliptic integral; numerically ~12.3 mm,
giving arc factor eta = L_arc / p ~ 1.70.

The corrugated medium uses ~1.70x as much paper per plan area as a flat
sheet of the same footprint. This is the mass penalty of corrugation.
