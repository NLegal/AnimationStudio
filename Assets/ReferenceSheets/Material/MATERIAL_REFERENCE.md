# Material Reference Guide

## Overview

Materials define how surfaces look, feel, and react to light. Consistent materials ensure assets render predictably across scenes and maintain the signature Animation Studio visual style. This guide details approved materials, their rendering properties, and per-asset recommendations.

---

## How Materials Affect Rendering

Every material in the 3D pipeline has three key properties:

- **Shininess**: How much the surface reflects light (glossy vs matte)
- **Roughness**: How textured the surface feels to light (smooth vs bumpy)
- **Transparency**: How much light passes through the material (opaque vs clear)

Balancing these properties creates the distinctive Pixar/Cocomelon-style look: clean, readable, and child-friendly.

---

## Material Properties Guide

### Wood
| Property | Value |
|---|---|
| Shininess | Low (satin finish) |
| Roughness | Medium |
| Transparency | Opaque |
| Notes | Subtle grain texture, no splinters or knots |

**Subtypes**: Warm Oak (medium brown), Light Maple (pale yellow-brown), Dark Walnut (rich dark brown)

### Plastic
| Property | Value |
|---|---|
| Shininess | Medium-High |
| Roughness | Low |
| Transparency | Usually opaque, some translucent variants |
| Notes | Smooth surface, slight specular highlight, no fingerprints |

**Subtypes**: Hard Plastic (glossy, toys), Soft Plastic (matte, utensils), Translucent Plastic (semi-clear, bottles)

### Metal
| Property | Value |
|---|---|
| Shininess | High |
| Roughness | Very Low |
| Transparency | Opaque |
| Notes | Clean reflections, no rust or tarnish, brushed or polished |

**Subtypes**: Polished (mirror-like), Brushed (satin), Colored Metal (painted metal surfaces)

### Fabric
| Property | Value |
|---|---|
| Shininess | Very Low |
| Roughness | High |
| Transparency | Opaque |
| Notes | Soft fuzz, no loose threads, uniform weave |

**Subtypes**: Cotton (matte, soft), Wool (textured, fuzzy), Fleece (plush, soft), Denim (woven, slightly rough)

### Glass
| Property | Value |
|---|---|
| Shininess | Very High |
| Roughness | Very Low |
| Transparency | Clear or lightly tinted |
| Notes | Crystal clear, slight refraction, no bubbles or smudges |

### Rubber
| Property | Value |
|---|---|
| Shininess | Low |
| Roughness | Medium |
| Transparency | Opaque |
| Notes | Matte surface, slight grip texture, flexible appearance |

### Paper
| Property | Value |
|---|---|
| Shininess | Very Low |
| Roughness | Medium |
| Transparency | Opaque |
| Notes | Slightly textured, matte finish, no tears or creases |

### Cardboard
| Property | Value |
|---|---|
| Shininess | Very Low |
| Roughness | Medium-High |
| Transparency | Opaque |
| Notes | Corrugated edge texture visible, brown surface, rigid |

### Ceramic
| Property | Value |
|---|---|
| Shininess | Medium-High |
| Roughness | Low |
| Transparency | Opaque |
| Notes | Glossy glazed surface, smooth, slight specular |

### Stone
| Property | Value |
|---|---|
| Shininess | Low |
| Roughness | Medium-High |
| Transparency | Opaque |
| Notes | Smooth pebbles or flat surfaces, no sharp edges |

### Water
| Property | Value |
|---|---|
| Shininess | High |
| Roughness | Very Low (surface) |
| Transparency | Semi-transparent to clear |
| Notes | Still or gently rippling, blue tint, no murkiness |

---

## Material Combination Rules

### Compatible Pairings (Do Combine)
- Wood + Fabric (chair with cushion)
- Plastic + Metal (toy with metal axles)
- Glass + Ceramic (cup on saucer)
- Paper + Cardboard (book with cardboard cover)
- Wood + Glass (picture frame)
- Fabric + Foam (stuffed toy)
- Plastic + Rubber (wheel on toy car)

### Incompatible Pairings (Don't Combine)
- Water + Paper (destroys paper)
- Glass + Stone (too hard, fragile combination)
- Metal + Ceramic (scratching risk — avoid direct contact surfaces)
- Fabric + Water (soggy fabric is not child-friendly)

### Material Hierarchy
When an asset uses multiple materials, follow this visual importance order:
1. Primary visible surface (outer material)
2. Functional surface (seat, handle, tabletop)
3. Decorative elements (accents, trim)
4. Internal components (visible only when opened)

---

## Per-Asset Material Recommendations

### Toys
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Building Blocks | Wood or Hard Plastic | None |
| Toy Cars | Hard Plastic | Rubber (wheels) |
| Stuffed Animals | Fleece or Cotton | Plastic (eyes) |
| Puzzles | Cardboard | Paper (surface print) |
| Doll House | Wood | Plastic (windows) |
| Train Set | Wood | Metal (wheels) |
| Doctor Kit | Plastic | Fabric (bag) |

### Food
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Apple | Wax (simulated) | None |
| Cake | Foam (simulated sponge) | Wax (frosting) |
| Ice Cream | Soft Plastic (simulated) | Wafer = Cardboard-styled |
| Pizza | Cardboard (crust) | Soft Plastic (toppings) |
| Cookie | Hard Foam (simulated) | None |
| Juice | Translucent Plastic (bottle) | Paper (label) |

### Furniture
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Chair | Wood | Fabric (cushion) |
| Sofa | Fabric | Wood (legs) |
| Bed | Wood | Fabric (mattress) |
| Table | Wood | None |
| Bookshelf | Wood | None |
| Lamp | Ceramic (base) | Fabric (shade) |

### School Supplies
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Pencil | Wood | Rubber (eraser) |
| Backpack | Fabric | Plastic (zippers) |
| Crayons | Wax | Paper (wrapper) |
| Whiteboard | Plastic (frame) | Ceramic (board) |
| Globe | Plastic | Metal (stand) |

### Nature
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Tree | Soft Plastic (leaves) | Wood (trunk) |
| Flower | Soft Plastic (petals) | Plastic (stem) |
| Rock | Stone | None |
| Cloud | Soft Foam (simulated) | None |
| Butterfly | Soft Plastic (wings) | None |

### Animals
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Cow | Fabric (fur) | Plastic (hooves) |
| Pig | Fabric (fur) | Plastic (snout) |
| Dog | Fabric (fur) | Plastic (nose) |
| Cat | Fabric (fur) | Plastic (whiskers) |
| Elephant | Fabric (fur) | Plastic (toenails) |

### Holidays
| Asset | Recommended Material | Secondary Material |
|---|---|---|
| Christmas Tree | Plastic (needles) | Metal (tinsel) |
| Easter Egg | Plastic (shell) | None |
| Pumpkin | Hard Plastic (shell) | None |
| Gift Box | Paper (wrap) | Fabric (ribbon) |
| Balloons | Rubber (latex) | None |

---

## Material Checklist

- [ ] Material matches the asset type (wood for blocks, fabric for stuffed animals)
- [ ] Shininess/roughness values are consistent across similar assets
- [ ] Material combinations follow the compatible pairings guide
- [ ] No conflicting materials that would look wrong in the same scene
- [ ] Material is recorded in the asset's metadata
- [ ] Material variants (color changes) use the same material type
