# The Optimal Shower

What water temperature minimizes heat loss while maximizing thermal comfort?

## Model

Newton's Law of Cooling (dQ/dt = hA(T_water - T_air)) combined with Fanger's
Predicted Mean Vote (ISO 7730) — the international standard for thermal comfort.

The Pareto front reveals the trade-off: at 34°C, PMV = 0.000 (perfectly neutral)
and heat loss is 2863 kJ. Above 34°C, comfort rises marginally but heat loss
climbs steeply. Below 34°C, heat loss drops but comfort collapses.

**The model says 34°C. Nobody showers at 34°C. The gap is the point.**

## Run

```bash
python3 model.py       # writes data/results.json
pytest tests/           # 6 tests
```

## Results

- Optimal temperature: 34.0°C
- PMV at optimal: 0.000 (thermally neutral)
- Energy used: 2863 kJ
- Real human shower temp: ~40°C
- Gap: 6°C (psychological, not physical)
