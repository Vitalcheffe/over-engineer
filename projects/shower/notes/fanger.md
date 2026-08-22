# Fanger PMV Notes

PMV = 0.303 * exp(-0.036*M) + 0.028) * L

Where L = (R - C - E_k - E_sw - E_res)

Variables:
- M: metabolic rate (W/m²)
- R: radiation heat loss
- C: convection heat loss  
- E_k: conductive heat loss
- E_sw: sweat evaporation
- E_res: respiration heat loss

ISO 7730 says comfort is |PMV| < 0.5

For a shower:
- M = 80 W (standing, light activity)
- Clothing = 0 clo (nude)
- Humidity = 95% (near saturation)
- Air velocity = 0.5 m/s

Need to find h_water for convective coefficient.
