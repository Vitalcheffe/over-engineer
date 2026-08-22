# Over Engineer

> Modeling the mundane with disproportionate rigor.

**12 projects. 12 months. 2026.**

Each month, one everyday phenomenon — a traffic jam, a penalty kick, a raindrop on a window — modeled with the same mathematical rigor as a defense system. Not because it matters. Because the ability to formalize the everyday is what engineering is.

## The series

| # | Month | Phenomenon | Math | Key result |
|---|-------|-----------|------|------------|
| 01 | Jan | The Optimal Shower | Newton's Law of Cooling x Fanger PMV x Pareto | Optimal: 34.0C |
| 02 | Feb | Phantom Traffic Jams | LWR continuum + Bando OVM stability | rho_crit = 30 veh/km |
| 03 | Mar | The Penalty Kick Game | Zero-sum game theory + Nash via LP | Goal rate: 75% |
| 04 | Apr | Elevator Dispatching | M/M/c queueing + SCAN/LOOK | LOOK 48% faster |
| 05 | May | The Queue Paradox | M/M/1 + Little's Law + serpentine | Variance -67% |
| 06 | Jun | Raindrop Racing | Stokes drag + coalescence | r* = 1.5mm |
| 07 | Jul | The Blind Bartender | 1-D Kalman filter + sensor fusion | RMSE 0.104m |
| 08 | Aug | Flocking Dynamics | Reynolds boids (1987) + Vicsek psi | psi: 0.03->0.94 |
| 09 | Sep | The Optimal Paper Airplane | Aerodynamics + L/D optimization | L/D = 3.1:1 |
| 10 | Oct | The Self-Balancing Tray | Slosh dynamics + LQR control | Peak 18->4 deg |
| 11 | Nov | The Strength of Cardboard | FEA + Euler buckling | 278,000x stiffer |
| 12 | Dec | Sorting Algorithms as Music | Sonification + spectral entropy | Quick: 0.79 entropy |

## Structure

```
over-engineer/
├── README.md                    # This file
├── projects/
│   ├── shower/                  # P.01
│   │   ├── model.py
│   │   ├── tests/
│   │   └── README.md
│   ├── traffic/                 # P.02
│   ├── penalty/                 # P.03
│   ├── ...
│   └── sorting-music/           # P.12
└── portfolio/                   # Live portfolio site
```

Each project folder contains:
- `model.py` — the mathematical implementation
- `tests/` — pytest suite verifying mathematical invariants
- `README.md` — the question, the model, the result, the limitations
- `data/results.json` — numerical output

## Run all projects

```bash
for d in projects/*/; do
  cd "$d"
  python3 model.py
  python3 -m pytest tests/ -q
  cd ..
done
```

## Stats

- **90 tests passing** across 12 projects (0 failures)
- **Python + NumPy + SciPy** — no external simulation libraries
- **MIT License** — open source, reproducible

## Philosophy

The model says 34C. The human says 40C. The gap is the point.

The world is formalizable. This repo proves it, one mundane phenomenon at a time.

---

*Amine Harch El Korane - 2026*
