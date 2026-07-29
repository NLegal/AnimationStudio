# Toy Negative Prompts

## Base Negative Prompt (All Assets)

```
broken,
dirty,
rust,
sharp edges,
blood,
weapon,
adult,
realistic wear,
dark,
horror,
graffiti,
blurry,
text,
logo,
watermark,
low quality
```

## Toy-Specific Negatives

### What to Avoid in Toys

- **Damage & Wear**: Toys in this world are always new, clean, and fully intact. Avoid any chips, cracks, scratches, or missing parts.
- **Texture Issues**: Avoid realistic fabric fraying, loose threads, torn stuffing, or worn surfaces.
- **Age Marks**: No yellowing plastic, faded colors, sticky residue, or sun damage.
- **Functional Problems**: Avoid missing buttons, stuck wheels, broken zippers, or torn seams.
- **Safety Hazards**: No small removable parts that could be choking hazards, sharp corners, or splinters.
- **Uncanny Elements**: Avoid human-like faces on toys, realistic eyes, or unsettling proportions.

### Extended Negative Prompt

```
chipped paint,
cracked plastic,
faded colors,
missing parts,
loose threads,
frayed fabric,
torn stuffing,
sticky residue,
yellowed plastic,
scratched surface,
dented metal,
broken wheel,
torn seam,
splintered wood,
sharp corner,
choking hazard,
realistic wear,
dirty fingerprints,
grimy,
rusty,
unsettling,
uncanny,
realistic human features,
dark theme,
scary,
adult content
```

### Usage Notes

Use the base negative prompt for every toy generation. Add the extended negative prompt when generating toys with fabric, wood, or small parts. Remove "text" and "logo" from negatives if the toy intentionally has printed text (e.g., alphabet blocks).
