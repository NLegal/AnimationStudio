# Seasons & Holiday Planning Guide

> **Version:** 1.0
> **Purpose:** Coordinate episode themes across the calendar year

## Philosophy

Seasonal planning ensures:
- Holiday episodes are ready on time (never reactive)
- Curriculum variety across the year
- Weather/location diversity matches real seasons
- Special episodes feel special (not random)

## Annual Calendar

| Month | Season | Holidays | Curriculum Focus |
|-------|--------|----------|------------------|
| January | Winter | New Year | Numbers, Shapes |
| February | Winter | Valentine's Day | Emotions, Friendship |
| March | Spring | Easter Prep | Colors, Nature |
| April | Spring | Easter | Animals, Growth |
| May | Spring | Mother's Day | Family, Music |
| June | Summer | Summer Start | Weather, Outdoors |
| July | Summer | Independence Day (gentle) | Community Helpers |
| August | Summer | Back to School Prep | Alphabet, Readiness |
| September | Autumn | First Day of School | School, Numbers |
| October | Autumn | Halloween (friendly) | Imagination, Costumes |
| November | Autumn | Thanksgiving | Gratitude, Food |
| December | Winter | Christmas, New Year | Giving, Traditions |

## Season Themes

| Season | Color Palette | Typical Weather | Typical Activities |
|--------|---------------|-----------------|-------------------|
| Spring | Pink, Green, Yellow | Rain, Rainbow, Sunny | Planting, Picnics, Puddles |
| Summer | Blue, Yellow, Orange | Sunny, Hot, Thunder | Beach, Swimming, Ice Cream |
| Autumn | Orange, Brown, Red | Cool, Windy, Leafy | Harvest, Hiking, Baking |
| Winter | White, Blue, Silver | Snow, Cold, Frost | Sledding, Snowman, Warm Cocoa |

## Holiday Episode Allocation

| Holiday | Episodes | Song Type | Decorations |
|---------|----------|-----------|-------------|
| Valentine's Day | 2-3 | Love/friendship songs | Hearts, pink, red |
| Easter | 3-4 | Spring/egg songs | Eggs, baskets, pastels |
| Halloween | 2-3 | Silly/fun songs | Pumpkins, friendly ghosts |
| Thanksgiving | 2 | Gratitude songs | Autumn leaves, feast |
| Christmas | 4-5 | Holiday songs | Tree, lights, stockings |
| New Year | 1 | Celebration songs | Confetti, midnight (noon) |
| Birthdays | As needed | Birthday songs | Cake, balloons, gifts |

## Series Planning

The SeriesPlanner in `src/story_engine/planner.py` provides:
- `plan_season(season_number, episode_count)` — creates a full season plan
- Automatic curriculum progression across seasons
- Holiday episode reservation

### Season Curriculum Mapping

| Season | Title | Curriculum Focus |
|--------|-------|------------------|
| 1 | Meet the Characters | Social skills, emotions |
| 2 | Learning Colors | Colors, art, creativity |
| 3 | Learning Numbers | Counting, math, shapes |
| 4 | Animal Adventures | Animals, nature, science |
| 5 | School Time | Alphabet, community, friendship |
| 6 | Science Fun | Weather, space, discovery |

## Diversity Rules

- No two consecutive episodes use the same season
- Holiday episodes should be spaced at least 2 weeks apart in-universe
- Each season gets at least 3 non-holiday episodes before a holiday is used
- Weather should match the season (no snow in summer episodes)

## Quality Checklist

- [ ] Holidays are planned at least one season in advance
- [ ] Curriculum progression is logical across seasons
- [ ] Each season has weather-appropriate locations
- [ ] Holiday episodes have appropriate decorations/assets
- [ ] No season is overused (balance across 12 months)
- [ ] Special episodes are clearly marked in the metadata
