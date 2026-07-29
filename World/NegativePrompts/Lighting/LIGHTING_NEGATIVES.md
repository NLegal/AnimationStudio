# LIGHTING NEGATIVES — Little Learning Town

Add these to the base negative when generating **lighting-specific** scenes.

---

## General Lighting Issues

harsh shadows, underexposed, overexposed, lens flare, glare, washed out, flat lighting, green tint, orange tint (unless golden hour), blue tint (unless night), red eye, dark spots, uneven lighting, flickering, strobe effect, blown out highlights, crushed blacks, clipped whites, muddy shadows, no contrast, too contrasty, unnatural lighting, unrealistic shadows, cast shadows in wrong direction, inconsistent light source, multiple conflicting light sources, shadowless, floating shadows, hard light (when soft needed), soft light (when hard needed), purple tint, yellow tint (unless warm lighting), magenta cast, cyan cast, color bleeding, light leak, vignette, lens distortion, chromatic aberration, blooming, god rays (unless intentional), volumetric fog (unless intentional)

## Time-of-Day Specific

### Morning
too dark, pre-dawn, still night, twilight darkness, harsh morning sun, long shadows, cold morning light, frost, dew (unless intentional)

### Noon
harsh overhead sun, squinting, extreme shadows, washed out sky, flat midday light, heat shimmer

### Afternoon
harsh shadows, squinting, heat, too bright, sun in eyes

### Golden Hour / Sunset
too dark, sunset already passed, orange so intense it burns, unrealistic colors, silhouette (unless intentional), blown out sky

### Evening / Night
too dark, cannot see details, pitch black, no light sources, unrealistic moonlight, flat night, no stars (when expected), light pollution, empty dark sky

## Advanced Lighting Issues

- rim light too strong
- backlight lost
- fill light missing
- key light too harsh
- practical light source inconsistency
- ambient occlusion missing
- global illumination artifacts
- caustics distracting
- sub-surface scattering missing (for character skin)
- specular highlights too strong
- diffuse lighting too flat
- indirect bounce light missing
- color temperature mismatch
- white balance off

## Color Temperature

too cool (blue), too warm (yellow), sickly green, unnatural magenta, clinical white, sterile lighting, hospital-like, fluorescent green, sodium orange (street lamp), mercury violet, mixed temperature confusion

## Usage

Combine with BASE_NEGATIVE and appropriate environment negative:

```
Negative: [BASE_NEGATIVE], [ENVIRONMENT_NEGATIVES], harsh shadows, underexposed, lens flare, green tint
```
