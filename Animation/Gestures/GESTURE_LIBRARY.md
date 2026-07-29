# Hand Gesture Library

## Introduction

For preschool audiences, gestures must be clear, readable, and slightly exaggerated. Children understand a character's intent through body language before they process dialogue. Every gesture in this library follows studio principles: playful, soft, rounded, easy to follow.

Gestures should:
- **Lead** — gesture starts 2–4 frames before the associated word or action
- **Show** — hand shapes are clear and held long enough to register (minimum 6 frames at peak)
- **Return** — hands return to neutral or resting position between gestures (not held indefinitely)

---

## Gesture Format

Every gesture documented with:

| Field          | Description                                  |
|----------------|----------------------------------------------|
| Frame count    | Total frames for complete gesture            |
| Arm position   | Where the arm(s) go                          |
| Hand shape     | Fingers open/closed, palm direction          |
| Body posture   | What the rest of the body does               |
| When to use    | Dialogue or situation context                |

---

## Gesture Library

### Wave (Hello / Goodbye)

| Field          | Details                                           |
|----------------|---------------------------------------------------|
| Frame count    | 12 frames per cycle (can repeat)                  |
| Arm position   | Arm raised to shoulder height, elbow bent ~90°    |
| Hand shape     | Open palm facing forward, fingers together         |
| Body posture   | Slight lean toward recipient, smile               |
| When to use    | Greeting, departing, getting attention             |

Motion: wrist rotates side-to-side (not whole arm waving). One cycle = left → right → center. Repeat for sustained waving.

---

### Point

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | Extend 8, hold variable, retract 6                  |
| Arm position   | Arm extends toward target, nearly straight           |
| Hand shape     | Index finger extended, other fingers curled in       |
| Body posture   | Lean slightly toward target, follow gaze direction   |
| When to use    | Directing attention, answering "where" questions     |

- Hold at extension minimum 8 frames for clarity
- Point at objects, not at other characters (preschool politeness)

---

### Thumbs Up

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 8 frames                                            |
| Arm position   | Arm raised, elbow bent, fist near chest or extended  |
| Hand shape     | Closed fist with thumb pointing up                   |
| Body posture   | Smile, slight head nod, chest slightly out           |
| When to use    | Approval, encouragement, "good job"                  |

---

### High Five

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 total (raise 4, slap 1, hold 1, lower 4)         |
| Arm position   | Arm raises to shoulder height, hand facing partner   |
| Hand shape     | Open palm, fingers together, slightly cupped         |
| Body posture   | Lean toward partner, smile, slight head forward      |
| When to use    | Celebration, greeting, accomplishment                |

- "Slap" frame: contact point with other character's hand
- Add a subtle bounce on contact

---

### Hug

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 16 total (arms open 4, close 4, hold 4, release 4)  |
| Arm position   | Phase 1: arms open wide to sides; Phase 2: arms wrap around |
| Hand shape     | Open, relaxed — gently grasping                      |
| Body posture   | Lean forward into hug, eyes soft or closed, smile    |
| When to use    | Greeting, comfort, affection, reunion                 |

- Hold phase: minimum 4 frames, can extend to 8–12 for emotional moments
- Release smoothly — don't drop arms instantly

---

### Clap

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 6 frames per clap                                   |
| Arm position   | Hands at chest height, elbows bent                   |
| Hand shape     | Hands slightly cupped, fingers together               |
| Body posture   | Smile, slight bounce, head may tilt                  |
| When to use    | Applause, celebration, song rhythm, excitement        |

- Repeat every 6 frames for sustained clapping
- For enthusiastic clapping: add body bounce and broader arm motion
- For gentle clapping: smaller motion, hands closer together

---

### Hold Object

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | Varies by object size and action duration             |
| Arm position   | Small object: one hand at waist/chest height          |
|                | Large object: both hands, arms wrapped around         |
| Hand shape     | Small: fingers curled around object; Large: palms supporting |
| Body posture   | Adjust based on object weight (slight lean if heavy)  |
| When to use    | Carrying, presenting, examining items                 |

- Objects should feel light (stylized physics)
- Hands should visibly contact the object surface

---

### Pick Up

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 12 total (reach 4, grasp 2, lift 4, hold 2)         |
| Arm position   | Reach down/toward object, then lift to natural hold  |
| Hand shape     | Reach: open; Grasp: closing around; Lift: secure grip |
| Body posture   | Bend slightly at waist for floor pickup               |
| When to use    | Retrieving any object from surface                    |

- Eyes should look at object 4–6 frames before reach begins (anticipatory gaze)
- Lift trajectory: smooth arc, not straight up

---

### Put Down

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 total (lower 4, release 2, withdraw 4)            |
| Arm position   | Lower from hold position to surface                   |
| Hand shape     | Lower: maintaining grip; Release: opening; Withdraw: relaxing |
| Body posture   | Lean forward slightly                                 |
| When to use    | Setting an object on a surface                        |

- Place gently — objects should not drop or land hard
- Hand lingers 2 frames after release before withdrawing

---

### Throw (Gentle)

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 12 total (wind up 4, release 2, follow through 6)   |
| Arm position   | Wind up: arm pulls back; Release: arm extends; Follow: arm continues arc |
| Hand shape     | Wind up: holding; Release: open, fingers extend; Follow: relaxed |
| Body posture   | Transfer weight back during wind up, forward on release |
| When to use    | Playing catch, tossing a ball, gentle underhand throw |

- Underhand throw is preferred (child-friendly)
- Overhand only for older characters or specific play contexts
- Never throw at another character — throw to a location or gently to hands

---

### Catch

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 8 total (arms out 2, close 2, hold 2, lower 2)      |
| Arm position   | Arms extend toward incoming object, then bring to chest |
| Hand shape     | Out: open palms forward; Close: fingers wrap; Hold: secure |
| Body posture   | Eyes track object, slight lean in direction of catch  |
| When to use    | Receiving a thrown object                             |

- Eyes follow the object trajectory throughout
- Small bounce/absorb motion on catch

---

### Open Book

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 total (hands out 2, grasp 2, open 4, hold 2)     |
| Arm position   | Both hands move to book edges, then spread outward   |
| Hand shape     | Out: open palms; Grasp: fingertips holding edges; Open: sliding apart |
| Body posture   | Look down at book, head centered                     |
| When to use    | Reading a book, showing pictures                     |

- For emphasis: one hand can hold the book while the other points to a page

---

### Turn Page

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 8 total (hand to corner 2, pinch 1, turn 3, release 2) |
| Arm position   | Hand moves to upper corner of page                    |
| Hand shape     | Pinch: thumb and forefinger together; Turn: sliding; Release: open |
| Body posture   | Head may tilt slightly to watch page                  |
| When to use    | Reading a book sequentially                           |

- Page turn is slow enough for children to see what was on the previous page
- Smooth arc: page lifts, crosses, settles

---

### Shake Head "No"

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 total (center to left 3, center to right 3, center 4) |
| Arm position   | Arms may be at sides or raised with palms out         |
| Hand shape     | Relaxed or palms facing outward                       |
| Body posture   | Head rotates on neck axis, shoulders stable           |
| When to use    | Disagreement, refusal, "no" response                  |

- Can add hand gestures alongside: palms out, pushing away
- Speed: faster for emphatic "no," slower for gentle refusal

---

### Nod "Yes"

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 8 total (down 3, up 3, hold 2)                      |
| Arm position   | Arms at rest or neutral                              |
| Hand shape     | Relaxed                                              |
| Body posture   | Chin drops toward chest, then rises                  |
| When to use    | Agreement, affirmation, understanding                |

- Single nod for simple agreement, 2–3 nods for enthusiastic yes
- Depth: deeper nod for more emphasis

---

### Shrug

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 12 total (shoulders up 4, hands open 2, hold 2, release 4) |
| Arm position   | Shoulders rise toward ears, arms relax at sides       |
| Hand shape     | Palms turn upward, open — "I don't know" shape        |
| Body posture   | Head may tilt, eyebrows raise                         |
| When to use    | Uncertainty, "I don't know," indifference             |

---

### Think

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 to achieve, hold as needed                        |
| Arm position   | One arm raises, hand approaches chin                  |
| Hand shape     | Fingers lightly touching chin or stroking lightly     |
| Body posture   | Head tilted up/to side, eyes looking up or away       |
| When to use    | Pondering a question, considering options             |

- Hold as needed (12–48 frames) for sustained thought
- Alternate with eye darts for active thinking

---

### Counting on Fingers

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 6 frames per number                                  |
| Arm position   | Hand raised to chest height, palm facing viewer       |
| Hand shape     | Fingers extend one by one: index, middle, ring, pinky, thumb |
| Body posture   | Eyes look at fingers, slight head tilt                |
| When to use    | Counting items, listing, showing age or quantity      |

- Each finger extension takes 4 frames, pause 2 frames
- For numbers 1–3: thumb holding pinky/ring down is natural
- For number 5: all fingers spread, palm open

---

### Blow a Kiss

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 total (hand to lips 3, kiss 1, blow 3, wave 3)   |
| Arm position   | Hand moves to mouth, then extends outward             |
| Hand shape     | Phase 1: fingertips at lips; Phase 2: open palm releasing |
| Body posture   | Slight lean forward, soft eyes                        |
| When to use    | Sending affection from a distance, goodbye            |

- Kiss sound optional but pairs naturally with the gesture
- Blow phase: hand moves outward with fingers opening

---

### Cover Mouth (Surprise)

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 6 frames                                            |
| Arm position   | Hand(s) move quickly to cover mouth area              |
| Hand shape     | Open palm or both hands flat over mouth               |
| Body posture   | Eyes wide (level 4–5), brows raised, head may pull back |
| When to use    | Surprise, shock, gasping, "oh my"                     |

- Hold covered for 6–12 frames, then lower hand slowly
- Eyes remain wide throughout

---

### Hands on Hips

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 8 frames                                            |
| Arm position   | Both arms bend, hands move to hip area                |
| Hand shape     | Palms resting on hips, fingers forward or slightly curled |
| Body posture   | Chest slightly out, chin up, feet shoulder-width      |
| When to use    | Confidence, impatience, scolding, determination       |

- Can be held as a stance (not just passing gesture)
- Often paired with foot tapping for impatience

---

### Arms Crossed

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 10 frames                                           |
| Arm position   | Both arms fold across chest, each hand on opposite upper arm |
| Hand shape     | Relaxed grip on own arms                             |
| Body posture   | Shoulders may hunch slightly, head may tilt           |
| When to use    | Defensiveness, stubbornness, disagreement, waiting    |

- Tension level varies: tight cross for upset, loose for casual waiting
- Hold as stance or passing gesture

---

### Fist Pump

| Field          | Details                                             |
|----------------|-----------------------------------------------------|
| Frame count    | 6 total (pull down 2, pump up 2, hold 2)            |
| Arm position   | Elbow bends, fist moves down then up                 |
| Hand shape     | Closed fist, thumb outside                          |
| Body posture   | Smile, slight body bounce, head may nod              |
| When to use    | Celebration, "yes!", success, victory                |

- Repeat for sustained celebration
- More restrained than adult fist pump — smaller motion, less aggressive

---

## Per-Character Gesture Notes

### Bunny
- Dainty, precise gestures — small hand movements, fingers together
- Hands often near face or chest height
- Ear tips bounce with arm movements (secondary motion)
- Avoid aggressive or wide gestures — Bunny is gentle

### Bear
- Big, broad gestures — arms fully extended, hands open
- Whole-body involvement — bear gestures often include shoulder and torso movement
- Heavy paws: hand shapes are chunky, fingers less distinct
- Grounded stance during gestures (feet shoulder-width)

### Pig
- Trotter-hands make finger separation minimal
- Gestures use whole-arm motion rather than wrist/finger detail
- Snout leads body direction for pointing gestures
- Clapping is round and soft (palms are padded)

### Owl
- Wings substitute for hands — limited finger articulation
- Wing tips can indicate direction (like pointing)
- Head swivels with gestures for emphasis
- Feathers ruffle during strong gestures (optional secondary motion)
- Cannot perform finger-based gestures (counting, thumbs up)

### Cat
- Fluid, precise gestures — grace and economy of motion
- Paws are rounded, claws never visible
- Batting motion for playful gestures (gentle paw swat)
- Tail swishes in rhythm with arm movements
- Sitting posture often paired with gestures (cats gesture from seated)

### Duck
- Wings are smaller — gestures are compact
- Wing flutters substitute for many hand gestures
- Head bobbing is primary emphasis (not hand motion)
- Cannot perform: thumbs up, pointing (individual finger), fist pump
- Can perform: wave (wing flap), hug (wing spread), shrug (wing lift), clap (wing slap)
