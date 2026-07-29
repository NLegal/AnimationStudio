# Asset Composition Guide

## Overview

Consistent composition ensures every asset is captured in a standardized, usable format. This guide defines how to frame, light, and present individual assets for the library. Following these rules guarantees assets can be dropped into any scene and composited seamlessly.

---

## How to Frame Individual Assets

### General Framing Rules

1. **Centered**: Asset occupies the center 60-70% of the frame
2. **Padding**: 15% padding on all sides (no cropping)
3. **Straight-on**: Primary view is straight-on at eye level (character eye level, ~40 cm)
4. **Neutral Background**: Soft gradient background (#E8F0FE to #FFFFFF)
5. **No Shadows**: Clean shadowless presentation for the primary capture
6. **One Asset Per Frame**: Never group multiple different assets in the same capture

### Background / Staging for Isolated Assets

| Context | Background | Notes |
|---|---|---|
| Catalog shot | Gradient (#E8F0FE to #FFFFFF) | Default presentation |
| Scene context | Transparent (alpha channel) | For compositing into scenes |
| Size reference | Grid background (10 cm squares) | Only for scale verification |
| Turnaround | Solid #D4D4D4 gray | Consistent across all angles |

---

## Ideal Angles by Asset Type

### Toys
| Angle | Purpose | Notes |
|---|---|---|
| Front (0°) | Primary ID | Shows the toy as a child would see it |
| 3/4 View (45°) | Depth demonstration | Shows volume and dimensionality |
| Top (90°) | Plan view | For puzzles, board games, flat toys |
| Side (90°) | Profile | For vehicles, to show wheels and length |
| Bottom (optional) | Underside | Only if interactive from below |

### Food
| Angle | Purpose | Notes |
|---|---|---|
| 3/4 View (45°) | Primary ID | Shows volume, texture, and shape |
| Front (0°) | Serving view | Shows the food as presented |
| Top (90°) | Plating view | For pizza, pancakes, decorated items |
| Cross-section | Internal view | For cakes, sandwiches, fruit |

### Furniture
| Angle | Purpose | Notes |
|---|---|---|
| Front (0°) | Primary ID | Shows the front face |
| 3/4 View (45°) | Depth | Shows depth and perspective |
| Side (90°) | Profile | Shows depth/thickness |
| Top (90°) | Plan | Shows surface area and layout |

### School Supplies
| Angle | Purpose | Notes |
|---|---|---|
| 3/4 View (45°) | Primary ID | Shows front and side details |
| Front (0°) | Face view | For books, notebooks, whiteboards |
| Top (90°) | Contents | For open items, tool sets |

### Nature
| Angle | Purpose | Notes |
|---|---|---|
| Front (0°) | Primary ID | For trees, clouds, large items |
| 3/4 View (45°) | Depth | For flowers, mushrooms, bushes |
| Top (90°) | Pattern | For leaves, snowflakes, water features |

### Animals
| Angle | Purpose | Notes |
|---|---|---|
| 3/4 View (45°) | Primary ID | Shows face and body |
| Front (0°) | Face | For character interactions |
| Side (90°) | Profile | Shows full body shape |
| Back (180°) | Rear | For full turnaround |

### Holidays
| Angle | Purpose | Notes |
|---|---|---|
| Front (0°) | Primary ID | For trees, pumpkins, stockings |
| 3/4 View (45°) | Depth | For ornaments, decorations |
| Top (90°) | Arrangement | For baskets, displays |

---

## Lighting Setup for Asset Photography

### Standard Three-Point Lighting

| Light | Position | Intensity | Color |
|---|---|---|---|
| Key Light | 45° left, 30° above | 70% | Warm white (4500K) |
| Fill Light | 45° right, 30° above | 30% | Cool white (5500K) |
| Rim Light | Behind, 45° above | 40% | Warm white (4500K) |

### Lighting Rules

1. **Soft Shadows**: Use area lights with soft shadow maps — no hard shadows
2. **No Hot Spots**: Maximum brightness should not clip to pure white
3. **Ambient Occlusion**: Subtle AO for depth without darkening the cheerful mood
4. **Consistent Intensity**: All assets use the same light intensity settings
5. **No Colored Lights**: Only white/warm lights (no red/blue/gel lighting)
6. **HDRI**: Use a soft studio HDRI (not an outdoor or environment HDRI)

### Lighting by Mood (Alternative)

| Mood | Key Light | Fill Light | Notes |
|---|---|---|---|
| Default Studio | 70% warm | 30% cool | Standard catalog shot |
| Warm/Cozy | 80% warm | 20% warm | For stuffed animals, bedtime items |
| Bright/Playful | 80% warm | 40% cool | For toys, playground items |
| Fresh/Clean | 60% cool | 40% warm | For food, bathroom items |
| Magical | 70% warm | 30% cool + rim | For holidays, fantasy items |

---

## Turnaround Requirements

Every asset requires a standardized set of views for complete documentation.

### Standard Turnaround Set (All Assets)

```
Front (0°)     →   3/4 Right (45°)    →   Side Right (90°)    →   3/4 Back (135°)    →   Back (180°)
```

### Minimum Turnaround (Essential)

1. **Front (0°)**: Head-on view
2. **3/4 View (45°)**: Slight rotation showing front and side
3. **Side (90°)**: Profile view
4. **Top (90°)**: Looking straight down

### Optional Views (When Needed)

- **Bottom**: If the underside has detail
- **Inside**: If the asset opens (doll house, backpack)
- **Cross-section**: If internal structure matters (food, layered items)
- **Exploded view**: If the asset has multiple separable parts

### Turnaround Rules

1. All views use the same lighting setup
2. All views use the same background color
3. Asset rotates, camera stays fixed
4. Even spacing between angles (45° increments minimum)
5. Asset maintains consistent scale across all views

---

## Composition Checklist

- [ ] Asset is centered in the frame with 15% padding
- [ ] Primary angle is appropriate for the asset type
- [ ] Three-point lighting is configured correctly
- [ ] Background matches the staging guide (catalog, scene, or grid)
- [ ] Turnaround includes all required views
- [ ] No hard shadows, hot spots, or colored lighting
- [ ] Asset is framed at character eye level (~40 cm height)
- [ ] Single asset per frame (no grouping)
- [ ] Alpha channel or clean background for compositing
