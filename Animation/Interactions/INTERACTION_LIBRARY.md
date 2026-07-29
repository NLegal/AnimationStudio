# Interaction Library

## Version 1.0 — AI Nursery Studio

---

## Introduction

Every interaction at AI Nursery Studio follows a consistent four-phase sequence:

1. **Approach** — Character moves toward the object/target
2. **Act** — The primary action occurs
3. **React** — Character shows response to the action
4. **Recover** — Character returns to neutral/idle state

This structure ensures every interaction reads clearly for preschool audiences. Frame counts are specified at 24 fps unless otherwise noted.

---

## Interaction Sequence

```
Approach ──→ Act ──→ React ──→ Recover
   ↑                              |
   └──────────────────────────────┘
         (loop if continuous)
```

---

## Interaction: Open Door

| Phase | Frames | Description |
|-------|--------|-------------|
| Reach | 3 | Arm extends toward handle, eyes lead the movement |
| Grasp | 1 | Fingers wrap around handle, subtle squeeze |
| Turn | 4 | Wrist rotates, handle turns with smooth resistance |
| Pull | 6 | Arm pulls door open, body leans back slightly, feet shift |
| Release | 2 | Fingers open, arm lowers to side |

**Total:** 16 frames

**Character Position:** Standing slightly to the hinge side, facing door panel

**Object Position:** Door at arm's length, handle at waist-to-chest height

**Body Mechanics:**
- Eyes track handle throughout reach
- Shoulder leads the reach, elbow follows
- Weight shifts from front to back foot during pull
- Head turns to look through opening during pull frames 4-6

**Hand Placement:** Palm facing down on reach, grips handle from top

---

## Interaction: Close Door

| Phase | Frames | Description |
|-------|--------|-------------|
| Reach | 2 | Arm extends toward door edge or handle |
| Grasp | 1 | Hand contacts door surface or handle |
| Push | 6 | Arm pushes door closed, body leans forward |
| Release | 3 | Hand lifts away from door |
| Step Back | 2 | Character steps backward to neutral position |

**Total:** 14 frames

**Character Position:** Standing on the open side of door, facing door

**Object Position:** Door already open 90 degrees

**Body Mechanics:**
- Shoulder leads push
- Front foot steps forward with push
- Eyes follow hand as it releases
- Subtle blink at contact frame

**Hand Placement:** Palm flat on door surface at chest height, or gripping handle

---

## Interaction: Open Book

| Phase | Frames | Description |
|-------|--------|-------------|
| Both Hands Out | 2 | Arms extend forward from idle, palms down |
| Grasp | 2 | Hands contact book cover edges, thumbs on top |
| Open Wide | 4 | Arms move apart, book opens, wrists rotate outward |
| Hold | 2 | Book held open, slight bobble settles, eyes scan pages |

**Total:** 10 frames

**Character Position:** Sitting or standing, book held at chest level

**Object Position:** Book centered in front of character

**Body Mechanics:**
- Elbows stay slightly bent throughout
- Head tilts down to look at pages during open phase
- Shoulders relaxed
- Subtle forward lean of torso

**Hand Placement:** Each hand on opposite edges of book cover, thumbs pressing lightly on top edges

---

## Interaction: Eat Apple

| Phase | Frames | Description |
|-------|--------|-------------|
| Hold Up | 2 | Arm lifts apple from waist to mouth height, eyes on apple |
| Bite | 2 | Arm brings apple to mouth, jaw opens, teeth close, head tilts slightly |
| Chew | 10 | Jaw moves in chewing cycle, cheeks bulge subtly, apple bobs |
| Swallow | 2 | Adam's apple moves (if visible), throat motion, apple lowers slightly |
| Lower | 4 | Arm lowers apple back to waist, eyes follow, swallow completes |

**Total:** 20 frames

**Character Position:** Standing or sitting, relaxed posture

**Object Position:** Apple held in hand, brought to mouth

**Body Mechanics:**
- Opposite arm hangs relaxed or rests on hip
- Chewing rhythm is steady and exaggerated for readability
- Eyes may look upward briefly during chewing
- Head tilts slightly back during bite

**Hand Placement:** Fingers wrapped around apple, thumb on top curve

---

## Interaction: Drink Water

| Phase | Frames | Description |
|-------|--------|-------------|
| Reach Cup | 2 | Hand extends toward cup on table |
| Grasp | 1 | Fingers wrap around cup handle or body |
| Lift | 4 | Arm raises cup to mouth, forearm rotates to tilt cup |
| Sip | 4 | Cup tilts, liquid enters mouth, throat moves, cup tilts back |
| Lower | 4 | Arm lowers cup back to table surface |
| Release | 1 | Fingers open, hand returns to neutral |

**Total:** 16 frames

**Character Position:** Sitting at table, chair pushed in

**Object Position:** Cup on table within easy reach

**Body Mechanics:**
- Eyes track cup throughout lift
- Other hand may rest on table
- Head tilts slightly forward during sip
- Lips purse slightly at cup rim
- Elbow bends to 90 degrees at sip

**Hand Placement:** Fingers wrapped around cup body, thumb opposite fingers

---

## Interaction: Kick Ball

| Phase | Frames | Description |
|-------|--------|-------------|
| Wind Up | 4 | Kicking leg pulls backward, standing leg bends slightly, arms balance |
| Kick | 1 | Leg swings forward, foot contacts ball |
| Follow-Through | 4 | Leg continues forward arc, body shifts forward |
| Land | 3 | Kicking foot returns to ground, balance restores, arms settle |

**Total:** 12 frames

**Character Position:** Standing behind ball, ball at feet distance

**Object Position:** Ball on ground in front of character

**Body Mechanics:**
- Arms counterbalance: opposite arm forward during kick
- Standing leg bends to absorb motion
- Eyes track ball through impact
- Torso leans forward slightly on follow-through
- Ankle locked on contact

**Hand Placement:** Arms out to sides for balance, palms open

---

## Interaction: Throw Ball

| Phase | Frames | Description |
|-------|--------|-------------|
| Reach Back | 3 | Throwing arm swings backward, torso rotates away, weight shifts to back foot |
| Forward | 3 | Arm swings forward, torso rotates toward target, weight shifts forward |
| Release | 1 | Fingers open, ball leaves hand at apex of arc |
| Follow Through | 5 | Arm continues downward arc, back foot steps forward, body settles |
| Settle | 2 | Arms lower, posture returns to neutral |

**Total:** 14 frames

**Character Position:** Standing sideways to target, feet shoulder-width apart

**Object Position:** Ball held in throwing hand at chest height initially

**Body Mechanics:**
- Opposite arm points toward target briefly
- Eyes track ball after release
- Step forward with opposite foot
- Underhand or overhand depending on distance

**Hand Placement:** Fingers spread across ball surface, thumb opposite, wrist loose

---

## Interaction: Catch Ball

| Phase | Frames | Description |
|-------|--------|-------------|
| Arms Out | 2 | Both arms extend forward, palms open and facing ball |
| Track | 4 | Eyes follow ball, head adjusts slightly, arms adjust position |
| Close | 2 | Hands close around ball as it arrives, fingers wrap |
| Hold | 2 | Arms absorb impact, pull ball slightly toward chest |
| Lower | 2 | Arms lower ball to waist level, eyes check ball |

**Total:** 12 frames

**Character Position:** Standing, facing direction ball comes from

**Object Position:** Ball approaches at chest-to-face height

**Body Mechanics:**
- Slight bend in knees to absorb
- Eyes locked on ball entire time
- Elbows bend during catch to cushion
- Small bounce settle after catch
- Feet stay planted or adjust slightly

**Hand Placement:** Palms open facing ball, fingers spread, thumbs almost touching

---

## Interaction: Build Blocks

| Phase | Frames | Description |
|-------|--------|-------------|
| Select | 4 | Eyes scan blocks, head turns, arm reaches toward chosen block |
| Grasp | 2 | Fingers wrap around block, confirm grip |
| Lift | 4 | Arm raises block from ground/table to placement height, eyes on target |
| Position | 4 | Arm moves block above stack, adjusts alignment, small wiggle |
| Place | 4 | Arm lowers block onto stack, fingers release |
| Release | 2 | Fingers open, arm pulls back slightly, check stability |

**Total:** 20 frames per block

**Character Position:** Sitting or kneeling near block pile, stack at comfortable distance

**Object Position:** Blocks scattered nearby, stack growing at center

**Body Mechanics:**
- Tongue may stick out slightly during positioning (optional character trait)
- Head tilts to check alignment
- Breath held briefly during placement, exhale on release
- Leans forward during selection, sits back during placement

**Hand Placement:** Fingers grip block sides, thumbs on top

---

## Interaction: Draw Picture

| Phase | Frames | Description |
|-------|--------|-------------|
| Hold Pencil | — | Continuous grip on pencil or crayon |
| Stroke | 8 | Arm moves pencil across paper, wrist guides, eyes follow tip |
| Lift | 2 | Pencil lifts from paper, arm repositions |
| Reposition | 6 | Arm moves to new starting position, eyes check reference |

**Total:** 16 frames (looping)

**Character Position:** Sitting at table or at easel

**Object Position:** Paper centered, pencil in dominant hand

**Body Mechanics:**
- Non-dominant hand holds paper steady
- Shoulder drives long strokes, wrist for detail
- Tongue or lip movement may accompany concentration
- Sits back periodically to admire work
- Varied strokes: circles, lines, scribbles

**Hand Placement:** Pencil held in tripod grip, fingers near tip, thumb on side

---

## Interaction: Brush Teeth

| Phase | Frames | Description |
|-------|--------|-------------|
| Hold Brush | 2 | Hand lifts brush to mouth, toothpaste visible on bristles |
| Brush Motion | 18 | Arm moves brush in gentle circles across teeth, head tilts |
| Rinse | 4 | Hand lowers brush, mouth fills with water, swish, spit |

**Total:** 24 frames per cycle

**Character Position:** Standing at sink, facing mirror

**Object Position:** Toothbrush held at mouth height

**Body Mechanics:**
- Brushing direction: small circles, top teeth then bottom
- Head tilts to expose different areas
- Cheeks puff during rinse
- Mirror visible in background for reference
- Other hand rests on sink edge or holds cup

**Hand Placement:** Toothbrush handle gripped in palm, thumb along top, fingers wrapped

---

## Interaction: Wash Hands

| Phase | Frames | Description |
|-------|--------|-------------|
| Turn Water | 3 | Hand reaches to faucet handle, twists, water begins flowing |
| Wet | 3 | Both hands position under water stream, palms up |
| Soap | 6 | Hand reaches for soap pump, presses 1-2 times, rubs soap between palms |
| Scrub | 12 | Hands rub together in circular motion, fingers interlace, thumbs rotate |
| Rinse | 4 | Hands return under water, rub to remove soap |
| Dry | 2 | Hands reach for towel or air dryer, rub together to dry |

**Total:** 30 frames

**Character Position:** Standing at sink, comfortable height for child

**Object Position:** Sink at waist height, soap dispenser within reach

**Body Mechanics:**
- Eyes check water temperature (optional)
- Singing or humming may accompany scrubbing phase
- Water splashes softly (stylized)
- Posture relaxed, feet slightly apart
- Wiggle fingers during rinse

**Hand Placement:** Varies by sub-phase — palms together during scrub, under faucet during rinse

---

## Interaction: Plant Flower

| Phase | Frames | Description |
|-------|--------|-------------|
| Dig | 12 | Small shovel or hands dig hole in soil, scooping motion |
| Place Seed | 4 | Hand holds seed, lowers into hole, releases carefully |
| Cover | 8 | Hands push soil over seed, pat down gently |
| Water | 12 | Watering can lifts, tilts, water pours, can lowers |
| Stand | 4 | Character stands up, brushes hands on pants, smiles |

**Total:** 40 frames

**Character Position:** Kneeling or squatting near flower pot or garden patch

**Object Position:** Flower pot at ground level or table height

**Body Mechanics:**
- Knees bent, weight on haunches
- Leans forward for ground work
- Arm movements are deliberate and careful
- Breath visible as effort (gentle puffs)
- Wipe brow on standing if desired

**Hand Placement:** Digging with fist-grip on shovel, fingers together for seed, cupped for water

---

## Interaction: Feed Animal

| Phase | Frames | Description |
|-------|--------|-------------|
| Hold Food | 2 | Hand lifts food from container (seed, hay, pellet) |
| Offer | 6 | Arm extends toward animal, palm open, food visible |
| Animal Eats | 6 | Animal approaches, takes food gently, character watches |
| Lower | 2 | Arm lowers, character smiles, may pet animal |

**Total:** 16 frames

**Character Position:** Standing or crouching near animal enclosure

**Object Position:** Food held in open palm at animal mouth height

**Body Mechanics:**
- Crouch if animal is small
- Eyes track animal approach
- Smile and gentle expression throughout
- Hand stays very still during animal eating
- Other hand may hold container at side

**Hand Placement:** Palm flat, food resting in center, fingers together, thumb tucked

---

## Interaction: Pet Dog

| Phase | Frames | Description |
|-------|--------|-------------|
| Reach | 2 | Arm extends toward dog's head/back |
| Stroke Forward | 4 | Hand moves from head toward tail along back |
| Stroke Back | 4 | Hand returns from tail toward head |
| Lift | 2 | Hand lifts away, arm returns to neutral |

**Total:** 12 frames

**Character Position:** Sitting or crouching beside dog

**Object Position:** Dog sitting or standing beside character

**Body Mechanics:**
- Eyes on dog, soft expression
- Other hand may rest on knee
- Body angled slightly toward dog
- Gentle pressure in hand (no heavy patting)
- Dog may wag tail in response

**Hand Placement:** Palm open, fingers together, hand follows contour of dog's body

---

## Interaction: Pet Dog (Loop)

| Phase | Frames | Description |
|-------|--------|-------------|
| Stroke Forward | 4 | Hand moves from head toward tail |
| Stroke Back | 4 | Hand returns from tail toward head |

**Total:** 8 frames (continuous loop)

**Character Position:** Sitting or crouching beside dog, settled posture

**Object Position:** Dog in comfortable position

**Body Mechanics:**
- Continuous gentle rhythm
- Head may tilt slightly with stroke motion
- Dog may lean into petting
- Occasional blink

**Hand Placement:** Open palm, gentle contact throughout loop

---

## Interaction: Ride Bicycle

| Phase | Frames | Description |
|-------|--------|-------------|
| Pedal Cycle | 24 per revolution | Legs alternate pushing pedals, handlebars held steady |

**Total:** 24 frames per pedal cycle

**Character Position:** Seated on bike, hands on handlebars

**Object Position:** Bicycle moving forward

**Body Mechanics:**
- Upper body stays relatively stable
- Gentle side-to-side sway with pedal rhythm
- Head faces forward, eyes scanning path
- Knees rise and fall in alternating pattern
- Feet stay flat on pedals

**Hand Placement:** Both hands on handlebars, elbows slightly bent, fingers wrapped

---

## Interaction: Pick Up Toy

| Phase | Frames | Description |
|-------|--------|-------------|
| Bend | 3 | Hips and knees bend, torso lowers toward toy |
| Reach | 2 | Arm extends toward toy, fingers preparing to grasp |
| Grasp | 1 | Fingers wrap around toy, confirm grip |
| Lift | 2 | Arm raises toy, body begins to straighten |
| Stand | 2 | Hips and knees extend, character returns to full height |

**Total:** 10 frames

**Character Position:** Standing near toy on ground

**Object Position:** Toy on floor in front of character

**Body Mechanics:**
- Eyes on toy throughout
- Back stays relatively straight (bend at hips and knees)
- Opposite arm balances at side
- Knees bend deeply — not a back-bend
- Toy is held at waist height after lift

**Hand Placement:** Fingers wrap around toy according to shape, thumb opposite

---

## Interaction: Put Away Toy

| Phase | Frames | Description |
|-------|--------|-------------|
| Hold | 2 | Character stands holding toy at waist level |
| Bend | 2 | Hips and knees bend, torso lowers toward shelf/box |
| Reach | 2 | Arm extends toy toward target location |
| Place | 2 | Toy is set down, fingers release |
| Release | 2 | Fingers open, hand pulls back |
| Stand | 2 | Hips and knees extend, character returns to full height |

**Total:** 12 frames

**Character Position:** Standing near toy box or shelf

**Object Position:** Toy storage container at ground or knee height

**Body Mechanics:**
- Eyes guide placement
- Gentle release — no dropping
- Satisfied expression after release
- Hands may pat toy once placed

**Hand Placement:** Toy held in palm, fingers wrapped around

---

## Interaction: Tie Shoelaces

| Phase | Frames | Description |
|-------|--------|-------------|
| Bend | 4 | Hips and knees bend, torso lowers, hands reach toward shoes |
| Cross | 4 | Laces crossed over, one end pulled under |
| Loop | 8 | One lace folded into loop, held between thumb and finger |
| Pull | 4 | Second loop pulled through the crossed section |
| Second Loop | 12 | Second lace folded into loop, crossed in front |
| Tie | 8 | Both loops pulled tight, knot forms |
| Straighten | 8 | Loops adjusted, laces straightened, knot centered |
| Stand | 12 | Hands lift off shoes, back straightens, knees extend |

**Total:** 60 frames

**Character Position:** Sitting on ground or small chair, one foot extended

**Object Position:** Shoe on foot, laces loose

**Body Mechanics:**
- Head angled down throughout
- Concentration expression (furrowed brow, slight tongue out)
- Breath held during critical knot pull
- Satisfied exhale on completion
- Other foot may bounce slightly during process

**Hand Placement:** Fingers manipulate laces with precision, thumbs holding loops in place

---

## Interaction: Blow Out Candle

| Phase | Frames | Description |
|-------|--------|-------------|
| Lean In | 4 | Torso leans forward toward candle, hands may rest on table |
| Big Breath | 2 | Shoulders rise, chest expands, mouth opens wide, inhale audible |
| Blow | 4 | Lips purse, air expelled, flame flickers and extinguishes, small smoke curl |
| Clap | 4 | Hands clap together in celebration, smile |
| Lean Back | 2 | Torso returns to neutral, satisfied expression |

**Total:** 16 frames

**Character Position:** Standing or sitting at table with cake

**Object Position:** Cake with candle centered on table

**Body Mechanics:**
- Eyes focused on flame throughout
- Cheeks puff during big breath
- Head tilts slightly forward on blow
- Flame animation: flicker 1 frame, extinguish 1 frame, smoke 2 frames
- Joyful expression after successful blow

**Hand Placement:** Resting on table edge or clasped together

---

## Per-Character Interaction Notes

### Lily Bunny
- Ears follow head movement with 3-frame delay
- Nose twitches on concentration phases (grasp, position, tie)
- Tail gives small bounce on completion of interaction
- Uses both hands for delicate tasks (book, blocks, shoelaces)

### Oliver Dog
- Tail wags during interactions involving play (ball, pet, feed)
- Sniffs objects briefly before grasping on first encounter
- Head tilts when curious about unfamiliar objects
- More energetic wind-up on throw and kick

### Mia Cat
- Paws (hands) move with precision economy — minimal unnecessary motion
- Blinks slowly during waiting phases
- Tail curls and uncurls during concentration
- Tends to sit rather than stand for ground-level interactions

### Benny Bear
- Larger wind-up motions for all reaching actions
- Sways on standing interactions due to broader build
- Blinks more frequently (every 12-16 frames)
- After interaction completes, often touches belly contentedly

---

## Frame Count Reference (24 fps)

| Interaction | Total Frames | Duration (seconds) |
|-------------|-------------|-------------------|
| Open Door | 16 | 0.67 |
| Close Door | 14 | 0.58 |
| Open Book | 10 | 0.42 |
| Eat Apple | 20 | 0.83 |
| Drink Water | 16 | 0.67 |
| Kick Ball | 12 | 0.50 |
| Throw Ball | 14 | 0.58 |
| Catch Ball | 12 | 0.50 |
| Build Blocks (per block) | 20 | 0.83 |
| Draw Picture (loop) | 16 | 0.67 |
| Brush Teeth (per cycle) | 24 | 1.00 |
| Wash Hands | 30 | 1.25 |
| Plant Flower | 40 | 1.67 |
| Feed Animal | 16 | 0.67 |
| Pet Dog | 12 | 0.50 |
| Pet Dog (loop) | 8 | 0.33 |
| Ride Bicycle (per pedal) | 24 | 1.00 |
| Pick Up Toy | 10 | 0.42 |
| Put Away Toy | 12 | 0.50 |
| Tie Shoelaces | 60 | 2.50 |
| Blow Out Candle | 16 | 0.67 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-29 | Initial interaction library with 20+ standardized interactions |
