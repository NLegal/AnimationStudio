# Metadata System Guide

## Overview

Every asset in the Animation Studio is tagged with standardized metadata. This enables automated scene building, consistent rendering, physics simulation, and cross-episode reuse. Metadata is stored as YAML frontmatter in each asset's definition file.

## YAML Template

```yaml
Asset ID:
Category:
Subcategory:
Material:
Primary Color:
Secondary Color:
Scale:
Animation:
Interactive:
Child Safe:
Reusable:
```

## Field Descriptions

### Asset ID
Unique identifier following the naming convention:
- `PROP_[TYPE]_[ITEM]_[NNN]` for props
- `TOY_[TYPE]_[NNN]` for toys
- `FOOD_[ITEM]_[NNN]` for food
- `ANM_[ANIMAL]_[NNN]` for animals
- `VEH_[TYPE]_[NNN]` for vehicles
- `MUS_[INSTRUMENT]_[NNN]` for musical instruments
- `ENV_[TYPE]_[NNN]` for environment/world assets

**Valid values**: Alphanumeric, underscore-separated, 3-digit zero-padded number

### Category
The broad asset family.

**Valid values**: Toy, Food, Furniture, School, Nature, Animal, Holiday, Kitchen, Bathroom, Bedroom, LivingRoom, Playground, Sport, Musical, Medical, Occupation, Book

### Subcategory
More specific grouping within the category.

**Examples**: BuildingBlocks, ToyCars, StuffedAnimals (for Toys); Fruit, Dessert, Drink (for Food); Farm, Pet, Wildlife (for Animals)

### Material
Primary material the asset appears to be made from.

**Valid values**: Wood, Plastic, Metal, Fabric, Cotton, Rubber, Glass, Paper, Cardboard, Ceramic, Stone, Grass, Water, Snow, Ice, Sand, Leather, Wool, Foam, Silicone

### Primary Color
Dominant color of the asset.

**Valid values**: Red, Blue, Yellow, Green, Orange, Purple, Pink, White, Black, Brown, Gray, Gold, Silver, PastelBlue, PastelPink, PastelYellow, PastelGreen, Lavender, Peach, Mint, Coral, Teal

### Secondary Color
Second most prominent color (if applicable).

**Valid values**: Same as Primary Color. Use "None" if the asset is single-color.

### Scale
Size classification relative to the world.

**Valid values**: Tiny (under 5 cm), Small (5-20 cm), Medium (20-100 cm), Large (1-3 m), Huge (3-10 m), Massive (10+ m)

### Animation
How the asset can move or be animated.

**Valid values**: Static, Rolling, Spinning, Swinging, Bouncing, Sliding, Folding, Opening, Closing, Pouring, Stacking, Expanding, Collapsing, Floating, Flying, Walking, Running, Sitting, LyingDown, None

### Interactive
Whether characters can interact with this asset.

**Valid values**: Yes, No, Conditional

*Conditional* means the asset can be interacted with only in specific contexts (e.g., a stove that only turns on in cooking scenes).

### Child Safe
Whether the asset is safe for children in the fictional world.

**Valid values**: Yes, No

All assets in this library should be "Yes" unless the item is inherently adult-focused.

### Reusable
Whether the asset is designed for reuse across episodes.

**Valid values**: Yes, No

All library assets should be "Yes" unless it is a one-off prop.

## Example Filled Metadata

### Toy Train

```yaml
Asset ID: TOY_TRAIN_001
Category: Toy
Subcategory: ToyCars
Material: Wood
Primary Color: Red
Secondary Color: Yellow
Scale: Medium
Animation: Rolling
Interactive: Yes
Child Safe: Yes
Reusable: Yes
```

### Apple

```yaml
Asset ID: FOOD_APPLE_001
Category: Food
Subcategory: Fruit
Material: Wax
Primary Color: Red
Secondary Color: Green
Scale: Small
Animation: Static
Interactive: Yes
Child Safe: Yes
Reusable: Yes
```

### School Desk

```yaml
Asset ID: PROP_DESK_001
Category: School
Subcategory: Furniture
Material: Wood
Primary Color: PastelBlue
Secondary Color: White
Scale: Medium
Animation: Static
Interactive: Yes
Child Safe: Yes
Reusable: Yes
```

### Christmas Tree

```yaml
Asset ID: ENV_TREE_CHRISTMAS_001
Category: Holiday
Subcategory: Christmas
Material: Plastic
Primary Color: Green
Secondary Color: Red
Scale: Large
Animation: Static
Interactive: Conditional
Child Safe: Yes
Reusable: Yes
```

### Butterfly

```yaml
Asset ID: ANM_BUTTERFLY_001
Category: Nature
Subcategory: Insects
Material: None
Primary Color: Orange
Secondary Color: Blue
Scale: Tiny
Animation: Flying
Interactive: No
Child Safe: Yes
Reusable: Yes
```
