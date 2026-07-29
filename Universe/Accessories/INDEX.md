# Accessory Library

> **Version:** 1.0
> **Architecture:** Standalone library with per-character defaults + episode overrides

## Architecture

```
Accessory Library
        │
        ▼
Reusable Asset
        │
        ▼
Character Default Loadout
        │
        ▼
Episode Overrides
```

**Principle:** Characters own identity; accessories are reusable assets.

## Categories

| Category | Subdirectories | Description |
|----------|---------------|-------------|
| Clothing | Bows, Hairbands, Hair Clips, Scarves, Gloves, Socks, Belts, Suspenders, Aprons, Capes | Clothing accessories |
| Bags | Backpacks, School Bags, Lunch Bags, Shopping Bags, Picnic Baskets, Travel Bags | Bags and carriers |
| Jewelry | Watches, Bracelets, Necklaces, Rings, Friendship Bracelets, Badges | Wearable decorations |
| Eyewear | Reading Glasses, Sunglasses, Swimming Goggles, Safety Goggles | Eye accessories |
| Musical | Guitar Straps, Microphones, Headphones, Music Stands | Music-related |
| School | Pencil Cases, Notebooks, Clipboards, Calculators, Name Tags | School supplies |
| Medical | Bandages, Stethoscopes, Face Masks, First Aid Kits | Medical gear |
| Occupation | Chef Hats, Fire Helmets, Police Badges, Construction Helmets, Tool Belts, Gardening Gloves | Job gear |
| Holiday | Santa Hats, Bunny Ears, Birthday Crowns, Party Hats, Fairy Wings, Witch Hats | Seasonal |
| Fantasy | Magic Wands, Crowns, Wizard Hats, Fairy Wands, Dragon Wings, Pirate Hats, Treasure Maps | Imaginative play |
| Sports | Soccer Balls, Basketballs, Tennis Rackets, Helmets, Shin Guards, Baseball Gloves | Sports gear |
| Hats | All headwear not covered by other categories | General hats |

## Asset Metadata Template

```yaml
Accessory ID: ACC_{CATEGORY}_{NAME}_{VARIANT}_{NNN}
Category: {Category}
Subcategory: {Subcategory}
Material: {Material}
Primary Color: {Color}
Secondary Color: {Color}
Compatible Characters: [All / Specific list]
Animation: [Hanging, Swinging, etc.]
Physics: [Soft Body, Rigid, etc.]
Season: [All, Spring, Summer, Fall, Winter]
Reusable: Yes
```

## Usage Pattern

### Per-Character Default Loadout (in character bio)

```yaml
Default Accessories:
  - ACC_BOW_BLUE_001
  - ACC_BACKPACK_PINK_002

Optional Accessories:
  - ACC_RAIN_BOOTS_001
  - ACC_SUN_HAT_003
  - ACC_BIRTHDAY_CROWN_001
```

### Episode Overrides (in episode script)

```
Christmas Episode → Lily switches Pink Backpack → Santa Hat + Gift Bag
Beach Episode → Lily switches Pink Dress → Sun Hat + Sunglasses + Beach Towel
```

## Benefits

1. **No duplication** — one Red Backpack asset, all characters can use it
2. **Consistency** — update once, every character benefits
3. **Better LoRA training** — AI learns Character + Accessory = Final Image
4. **Massive reuse** — Doctor Kit used by Lily, Ben, Charlie, Teacher, Doctor, Firefighter

---

*Part of the AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
