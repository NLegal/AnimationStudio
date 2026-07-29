# Voice Prompt Templates

## AI Nursery Studio — Prompt Engineering Guide

### Version 1.0

---

## Introduction

This guide provides voice prompt templates for every character in the AI Nursery Studio universe. Each template is designed to produce consistent, recognizable voices across episodes using TTS platforms.

Consistent character voices are essential for brand recognition. Children should be able to identify a character by voice alone within 1–2 seconds of hearing them speak.

---

## Platform-Specific Notes

### Kokoro

| Feature | Notes |
|---------|-------|
| Voice quality | Natural, warm |
| Speed | Excellent for narration |
| Pitch control | Good |
| Emotion control | Limited |
| Best for | Narrator, calm dialogue, monolingual content |
| Prompt style | Short descriptive phrases |

```
Warm preschool narrator, calm pace, clear pronunciation, friendly tone, energetic but gentle, suitable for children ages 2–6.
```

### XTTS v2

| Feature | Notes |
|---------|-------|
| Voice quality | Very natural |
| Speed | Good for character voices |
| Pitch control | Excellent |
| Emotion control | Good |
| Multilingual | Excellent (best for localization) |
| Best for | Recurring character voices, multilingual projects |
| Prompt style | Detailed voice description |

```
A cheerful 5-year-old girl's voice, medium-high pitch, playful energy, medium speaking speed, neutral accent, soft laugh, bright singing style.
```

### Piper

| Feature | Notes |
|---------|-------|
| Voice quality | Good (slightly robotic) |
| Speed | Very fast generation |
| Pitch control | Moderate |
| Emotion control | Limited |
| Offline | Full offline capability |
| Best for | Automation pipelines, bulk generation, prototyping |
| Prompt style | Short, technical parameters |

```
Female voice, pitch +0.3, speed 1.0, clean pronunciation, neutral accent.
```

---

## Per-Character Voice Prompt Templates

### Character Template Format

```
Character Name
Voice Description: [age, gender, tone]
Pitch: [relative pitch level]
Speed: [speaking speed]
Energy: [characteristic energy level]
Accent: [regional or neutral]
Emotion Range: [typical emotions]
Singing Voice: [singing characteristics]
Example Line: "[representative dialogue line]"
```

---

### Main Characters

#### 1. Lily Bunny

```
Character Name: Lily Bunny
Voice Description: A cheerful 5-year-old girl's voice, bright and playful, medium-high pitch
Pitch: Medium-high (female +0.3 to +0.5)
Speed: Medium (1.0x)
Energy: Playful, curious, always slightly excited
Accent: Neutral English
Emotion Range: Happy (default), curious, surprised, occasionally sad but recovers quickly
Singing Voice: Bright, clear, slightly bouncy, excellent enunciation
Example Line: "Wow! Look at all these colors! Can we paint together?"
```

#### 2. Max Bear

```
Character Name: Max Bear
Voice Description: A warm 5-year-old boy's voice, friendly and gentle, medium pitch
Pitch: Medium (male, neutral to +0.1)
Speed: Medium-slow (0.9x)
Energy: Calm, thoughtful, steady
Accent: Neutral English
Emotion Range: Friendly (default), thoughtful, happy, occasionally unsure
Singing Voice: Warm, steady, on-pitch but less dynamic
Example Line: "I think we should share the blocks. There's enough for everyone."
```

#### 3. Zara Cat

```
Character Name: Zara Cat
Voice Description: A curious 5-year-old girl's voice, slightly mischievous, medium-high pitch
Pitch: Medium-high (female +0.2 to +0.4)
Speed: Medium-fast (1.1x)
Energy: Curious, clever, playful
Accent: Neutral English with slight warmth
Emotion Range: Curious (default), clever, amused, surprised
Singing Voice: Light, agile, good with fast lyrics
Example Line: "Hmm, I wonder what happens if we mix blue and red together?"
```

#### 4. Oliver Dog

```
Character Name: Oliver Dog
Voice Description: An energetic 5-year-old boy's voice, bouncy and enthusiastic, medium pitch
Pitch: Medium (male +0.1 to +0.2)
Speed: Fast (1.2x)
Energy: High energy, enthusiastic, always ready to play
Accent: Neutral English
Emotion Range: Excited (default), happy, impatient, eager
Singing Voice: Loud, enthusiastic, not always perfectly on pitch but full of joy
Example Line: "Come on, come on! Let's go to the playground! I want to try the slide!"
```

#### 5. Squeaky Mouse

```
Character Name: Squeaky Mouse
Voice Description: A tiny, squeaky voice, very high pitch, fast, shy but friendly
Pitch: Very high (female +0.6 to +0.8)
Speed: Fast (1.15x)
Energy: Nervous-excited, shy, endearing
Accent: Neutral English with slight breathiness
Emotion Range: Shy (default), happy, nervous, surprised
Singing Voice: Tiny, sweet, slightly breathy
Example Line: "Um... excuse me? Is it okay if I... if I play with you too?"
```

#### 6. Penelope Pig

```
Character Name: Penelope Pig
Voice Description: A friendly, slightly proud 5-year-old girl's voice, warm medium pitch
Pitch: Medium (female +0.1 to +0.2)
Speed: Medium (1.0x)
Energy: Confident, organized, helpful
Accent: Neutral English
Emotion Range: Confident (default), helpful, proud, slightly bossy (affectionate)
Singing Voice: Strong, confident, clear
Example Line: "I made cupcakes for everyone! They're perfectly decorated with sprinkles!"
```

#### 7. Benny Frog

```
Character Name: Benny Frog
Voice Description: A bouncy, playful 5-year-old boy's voice with a croaky quality, medium pitch
Pitch: Medium-low (male, neutral)
Speed: Medium (1.0x)
Energy: Playful, silly, loves to make others laugh
Accent: Neutral English with slight vocal fry character
Emotion Range: Silly (default), happy, surprised, dramatic
Singing Voice: Bouncy, rhythmic, exaggerated
Example Line: "Ribbit-ribbit! Did someone say it's time for a jumping contest? I'm the champion!"
```

#### 8. Cleo Owl

```
Character Name: Cleo Owl
Voice Description: A wise, gentle 5-year-old girl's voice, calm and patient, medium-low pitch
Pitch: Medium (female, neutral to -0.1)
Speed: Slow (0.8x)
Energy: Calm, wise, patient, slightly serious
Accent: Neutral English with precise pronunciation
Emotion Range: Wise (default), patient, gently amused, thoughtful
Singing Voice: Slow, clear, deliberate
Example Line: "If you look closely at the night sky, you can see patterns in the stars. They tell stories."
```

---

### Supporting Characters

#### 9. Sunny Duck

```
Character Name: Sunny Duck
Voice Description: A cheerful, slightly nasal voice, medium pitch, friendly
Pitch: Medium-high (female +0.2)
Speed: Medium-fast (1.1x)
Energy: Cheerful, social, waddling joy
Accent: Neutral English with slight brightness
Emotion Range: Cheerful (default), social, worried (briefly), happy
Singing Voice: Bright, quacky on certain notes
Example Line: "Quack quack! Hello friends! I brought some breadcrumbs for the picnic!"
```

#### 10. Rusty Squirrel

```
Character Name: Rusty Squirrel
Voice Description: A quick, chattery voice, high pitch, fast-talking, enthusiastic
Pitch: High (female +0.4)
Speed: Fast (1.3x)
Energy: Hyper, busy, always collecting or organizing
Accent: Neutral English
Emotion Range: Busy (default), excited, worried about his acorns, happy
Singing Voice: Fast, chattery, lots of short notes
Example Line: "Oh! Oh! I found the biggest acorn! I need to hide it! No, wait — I need to show everyone first!"
```

#### 11. Honey Bee

```
Character Name: Honey Bee
Voice Description: A buzzing, sweet voice, medium pitch with a light hum
Pitch: Medium-high (female +0.3)
Speed: Medium (1.0x) with buzzing quality
Energy: Busy, sweet, community-minded
Accent: Neutral English with slight buzz/hum
Emotion Range: Sweet (default), busy, concerned about flowers, happy
Singing Voice: Buzzy, sweet, humming often
Example Line: "Buzz buzz! The flowers are blooming! Time to collect nectar for honey!"
```

#### 12. Tilly Turtle

```
Character Name: Tilly Turtle
Voice Description: A slow, gentle voice, low-medium pitch, very patient
Pitch: Medium-low (female -0.2 to -0.1)
Speed: Slow (0.7x)
Energy: Calm, patient, deliberate
Accent: Neutral English, slightly slow pronunciation
Emotion Range: Patient (default), gentle, thoughtful, occasionally surprised but takes it in stride
Singing Voice: Slow, steady, deliberate
Example Line: "There's no need to rush. The flowers will still be there when we arrive. Let's enjoy the walk."
```

#### 13. Hopper Rabbit (Lily's brother)

```
Character Name: Hopper Rabbit
Voice Description: An energetic younger boy's voice, even higher than Lily, fast, bouncy
Pitch: High (male +0.3 to +0.4)
Speed: Fast (1.2x)
Energy: Very high, impatient, always hopping
Accent: Neutral English
Emotion Range: Eager (default), impatient, excited, dramatic when tired
Singing Voice: Bouncy, energetic, fast
Example Line: "Lily! Lily! Look what I found! It's a — oh wait, where did it go? I had it just a second ago!"
```

#### 14. Grandma Bunny

```
Character Name: Grandma Bunny
Voice Description: A warm, slightly older voice, low-medium pitch, kind and gentle
Pitch: Medium-low (female -0.3 to -0.1)
Speed: Slow (0.75x)
Energy: Warm, nurturing, patient
Accent: Neutral English with gentle warmth
Emotion Range: Warm (default), nurturing, gently amused, comforting
Singing Voice: Soft, warm, slightly tremble at ends of phrases
Example Line: "Come here, my little bunnies. Grandma made carrot soup — your favorite!"
```

#### 15. Grandpa Bear

```
Character Name: Grandpa Bear
Voice Description: A deep, rumbly warm voice, low pitch, slow, comforting
Pitch: Low (male -0.4 to -0.2)
Speed: Slow (0.7x)
Energy: Comforting, wise, gentle
Accent: Neutral English with deep warmth
Emotion Range: Warm (default), wise, gently humorous, protective
Singing Voice: Deep, rumbly, warm, limited range
Example Line: "When I was a little cub, we used to climb the tallest trees and watch the sun go down. Those were good times."
```

#### 16. Professor Mole

```
Character Name: Professor Mole
Voice Description: A scholarly, slightly muffled voice, medium pitch, precise
Pitch: Medium (male, neutral)
Speed: Medium-slow (0.85x)
Energy: Scholarly, curious, slightly distracted by knowledge
Accent: Neutral English with precise pronunciation
Emotion Range: Curious (default), excited about discoveries, helpful
Singing Voice: Precise, slightly monotone but warm
Example Line: "Fascinating! Did you know that worms have five hearts? Five! Imagine that!"
```

#### 17. Daisy Cow

```
Character Name: Daisy Cow
Voice Description: A gentle, deep female voice, low-medium pitch, calm
Pitch: Low-medium (female -0.3 to -0.1)
Speed: Medium (1.0x)
Energy: Calm, gentle, nurturing
Accent: Neutral English with slight warmth
Emotion Range: Calm (default), nurturing, concerned (gently), happy
Singing Voice: Deep, warm, resonant
Example Line: "Moo, would anyone like some fresh milk? I have plenty to share with all my friends."
```

#### 18. Clucky Hen

```
Character Name: Clucky Hen
Voice Description: A busy, slightly flustered voice, medium-high pitch, quick
Pitch: Medium-high (female +0.2 to +0.3)
Speed: Medium-fast (1.15x)
Energy: Busy, organized, slightly worried but good-hearted
Accent: Neutral English
Emotion Range: Busy (default), flustered, proud of her eggs, caring
Singing Voice: Quick, clucky rhythm
Example Line: "Oh my, oh my! Has anyone seen my little chicks? They were here just a moment ago!"
```

#### 19. Pippin Fox

```
Character Name: Pippin Fox
Voice Description: A clever, slightly sly voice but ultimately friendly, medium pitch
Pitch: Medium (male +0.1)
Speed: Medium (1.0x) with occasional pauses for effect
Energy: Clever, playful, slightly mischievous
Accent: Neutral English with slight sharpness on consonants
Emotion Range: Clever (default), mischievous, helpful (surprisingly), amused
Singing Voice: Smooth, slightly sly, playful
Example Line: "I know a secret path through the woods. Follow me — but watch out for the tickly branches!"
```

#### 20. Waddles Penguin

```
Character Name: Waddles Penguin
Voice Description: A cheerful, slightly formal voice, medium pitch, friendly
Pitch: Medium (male +0.1 to +0.2)
Speed: Medium (1.0x)
Energy: Cheerful, polite, slightly formal but warm
Accent: Neutral English with slight crispness
Emotion Range: Cheerful (default), polite, concerned about cold things, happy
Singing Voice: Cheerful, steady, clear
Example Line: "Good day, friends! The snow is simply splendid today. Would anyone care for a slide on the ice?"
```

#### 21. Stella Giraffe

```
Character Name: Stella Giraffe
Voice Description: A tall, gentle voice, medium-high pitch, dreamy
Pitch: Medium-high (female +0.2)
Speed: Medium-slow (0.9x)
Energy: Dreamy, gentle, observant from above
Accent: Neutral English with slight breathiness
Emotion Range: Dreamy (default), gentle, surprised by small things, happy
Singing Voice: High, gentle, floaty
Example Line: "From up here, I can see the whole meadow. The flowers look like tiny dots of color."
```

#### 22. Rocky Raccoon

```
Character Name: Rocky Raccoon
Voice Description: A rough but friendly voice, low-medium pitch, casual
Pitch: Low-medium (male -0.1 to 0.0)
Speed: Medium (1.0x)
Energy: Casual, clever, resourceful
Accent: Neutral English with slight casual slur
Emotion Range: Casual (default), clever, surprised when caught, friendly
Singing Voice: Rough, casual, rhythmic
Example Line: "Hey there! You wouldn't happen to have any snacks, would you? I'm an expert snack finder."
```

#### 23. Luna Hedgehog

```
Character Name: Luna Hedgehog
Voice Description: A tiny, prickly but sweet voice, high pitch, determined
Pitch: High (female +0.4 to +0.5)
Speed: Medium-fast (1.1x)
Energy: Determined, prickly exterior, sweet interior
Accent: Neutral English
Emotion Range: Determined (default), prickly when scared, sweet when comfortable
Singing Voice: Tiny, determined, sweet
Example Line: "Don't touch my spikes! ...Unless you're my friend. Are you my friend?"
```

#### 24. Captain Bear (Max's dad)

```
Character Name: Captain Bear
Voice Description: A confident, warm father voice, medium-low pitch, strong but kind
Pitch: Medium-low (male -0.2 to 0.0)
Speed: Medium (0.95x)
Energy: Confident, warm, protective
Accent: Neutral English with firm warmth
Emotion Range: Confident (default), warm, protective, proud
Singing Voice: Strong, warm, steady
Example Line: "Alright, crew! Raise the anchor and set sail for Adventure Island! Who's coming with me?"
```

#### 25. Mama Pig

```
Character Name: Mama Pig
Voice Description: A warm, slightly busy mother voice, medium pitch, loving
Pitch: Medium (female, neutral)
Speed: Medium (1.0x)
Energy: Warm, busy, loving
Accent: Neutral English with warm maternal tone
Emotion Range: Warm (default), busy but never too busy for her kids, proud
Singing Voice: Warm, maternal, strong
Example Line: "Did everyone wash their hands? Good! Now let's sit down for a nice family dinner."
```

#### 26. Scout Badger

```
Character Name: Scout Badger
Voice Description: A practical, no-nonsense voice, low-medium pitch, capable
Pitch: Medium-low (male -0.1 to +0.1)
Speed: Medium (1.0x)
Energy: Practical, capable, slightly gruff but kind
Accent: Neutral English with firm tone
Emotion Range: Practical (default), capable, gruffly kind, patient
Singing Voice: Steady, practical, rhythmic
Example Line: "Always be prepared. That's my motto. Pack your bag, bring a map, and never forget your snack."
```

#### 27. Wiggly Worm

```
Character Name: Wiggly Worm
Voice Description: A tiny, wiggly voice, high pitch, fast, giggly
Pitch: High (male +0.3 to +0.5)
Speed: Fast (1.2x)
Energy: Wiggly, giggly, always moving
Accent: Neutral English
Emotion Range: Giggly (default), wiggly, happy, easily excited
Singing Voice: Wiggly, fast, giggly
Example Line: "Wiggle wiggle wiggle! I love the rain! It makes the ground all soft and squishy!"
```

#### 28. Bree Butterfly

```
Character Name: Bree Butterfly
Voice Description: A light, fluttery voice, medium-high pitch, gentle
Pitch: Medium-high (female +0.3)
Speed: Medium (1.0x) with fluttering pauses
Energy: Light, gentle, easily distracted by beauty
Accent: Neutral English with light airy quality
Emotion Range: Gentle (default), amazed by flowers, easily delighted
Singing Voice: Light, fluttery, airy
Example Line: "Oh! Look at that flower! And that one! And that one over there! They're all so beautiful!"
```

#### 29. Buster Goat

```
Character Name: Buster Goat
Voice Description: A rough, cheerful voice, medium-low pitch, enthusiastic
Pitch: Medium-low (male -0.1 to +0.1)
Speed: Medium-fast (1.1x)
Energy: Enthusiastic, rough, cheerful
Accent: Neutral English with slight rasp
Emotion Range: Enthusiastic (default), cheerful, competitive, happy
Singing Voice: Rough, enthusiastic, loud
Example Line: "I can eat anything! Tin cans, cardboard, tree bark — wait, is this your homework? Sorry!"
```

#### 30. Mocha Puppy (Oliver's little sister)

```
Character Name: Mocha Puppy
Voice Description: A tiny, puppy-like voice, very high pitch, excited, wagging-tail energy
Pitch: High (female +0.5 to +0.7)
Speed: Fast (1.3x)
Energy: Extreme excitement, tail-wagging energy, curious about everything
Accent: Neutral English with breathy excitement
Emotion Range: Excited (default), curious, happy, tired (suddenly falls asleep)
Singing Voice: High, excited, bouncy
Example Line: "Hi hi hi! Can we play? Can we play now? I wanna play! Please please please!"
```

#### 31. Sage Owl (Cleo's parent)

```
Character Name: Sage Owl
Voice Description: A deep, wise voice, low pitch, slow, ancient-sounding
Pitch: Low (female -0.4 to -0.2)
Speed: Slow (0.7x)
Energy: Ancient, wise, patient, slightly mysterious
Accent: Neutral English with deliberate weight
Emotion Range: Wise (default), mysterious, gently amused, patient
Singing Voice: Deep, slow, resonant
Example Line: "The forest holds many secrets, young ones. If you listen carefully, the trees will tell you their stories."
```

#### 32. Twitchy Rabbit (background)

```
Character Name: Twitchy Rabbit
Voice Description: A nervous, twitchy voice, medium-high pitch, fast, worried
Pitch: Medium-high (male +0.2)
Speed: Fast (1.2x)
Energy: Nervous, twitchy, worried about everything
Accent: Neutral English
Emotion Range: Nervous (default), worried, easily startled, relieved
Singing Voice: Nervous, fast, shaky
Example Line: "Did you hear that? I think I heard something! Was that a fox? Should we hide? Is it safe?"
```

#### 33. Puddles Elephant

```
Character Name: Puddles Elephant
Voice Description: A deep, rumbling voice, very low pitch, slow, gentle giant
Pitch: Low (male -0.5 to -0.3)
Speed: Slow (0.7x)
Energy: Gentle, careful, warm giant energy
Accent: Neutral English with deep resonance
Emotion Range: Gentle (default), careful, warm, sad if friends are sad
Singing Voice: Deep, rumbling, gentle
Example Line: "I'll be very careful not to step on the flowers. I always watch where I put my big feet."
```

#### 34. Sparkle Cat (Zara's cousin)

```
Character Name: Sparkle Cat
Voice Description: A glamorous, dramatic voice, medium-high pitch, theatrical
Pitch: Medium-high (female +0.2 to +0.3)
Speed: Medium (1.0x) with dramatic pauses
Energy: Dramatic, glamorous, theatrical
Accent: Neutral English with slight flourish
Emotion Range: Dramatic (default), excited, offended (dramatically), delighted
Singing Voice: Dramatic, showy, expressive
Example Line: "Daaaarling! This is the most magnificent tea party I have ever attended! The decor is splendid!"
```

#### 35. Chef Duck

```
Character Name: Chef Duck
Voice Description: A flustered, passionate voice, medium pitch, fast when excited about food
Pitch: Medium (male +0.1)
Speed: Fast (1.15x) when cooking, slow when tasting
Energy: Passionate about food, flustered, proud
Accent: Neutral English with slight French affectation on food words
Emotion Range: Passionate (default), flustered in busy times, proud of dishes
Singing Voice: Passionate, rhythmic, food-themed
Example Line: "The secret to a perfect soufflé is patience! Patience and... oh dear, I think I forgot the eggs!"
```

#### 36. Doctor Panda

```
Character Name: Doctor Panda
Voice Description: A calm, reassuring voice, medium pitch, gentle authority
Pitch: Medium (male, neutral)
Speed: Medium-slow (0.85x)
Energy: Calm, reassuring, authoritative but gentle
Accent: Neutral English with warm clinical calm
Emotion Range: Calm (default), reassuring, concerned (gently), happy
Singing Voice: Calm, steady, warm
Example Line: "Let me take a look. Open wide and say 'ahh'. Wonderful! You have the healthiest teeth in the forest!"
```

#### 37. Skyler Skunk

```
Character Name: Skyler Skunk
Voice Description: A shy but sweet voice, medium pitch, hesitant but warm
Pitch: Medium (female, neutral to +0.1)
Speed: Medium-slow (0.85x)
Energy: Shy, sweet, hesitant but kind
Accent: Neutral English with soft tone
Emotion Range: Shy (default), sweet, worried about her smell, happy when accepted
Singing Voice: Soft, sweet, slightly hesitant
Example Line: "I... I brought flowers for everyone. I hope you don't mind. I can leave if... if you want."
```

#### 38. Flash Cheetah

```
Character Name: Flash Cheetah
Voice Description: A fast, breathless voice, medium pitch, always in a hurry
Pitch: Medium (male +0.1)
Speed: Very fast (1.4x)
Energy: Extreme speed, always in a hurry, impatient
Accent: Neutral English with breathlessness
Emotion Range: Hurried (default), impatient, excited about speed, briefly still
Singing Voice: Fast, breathless, energetic
Example Line: "Sorry I'm late! I ran as fast as I could — which is very fast! What did I miss? Tell me quick!"
```

---

## Narrator Voice Templates

### Narrator Variation 1: Warm Storyteller

```
Warm preschool narrator, calm friendly voice, medium pitch, moderate pace, clear pronunciation, engaging tone that draws children into the story, suitable for daytime educational content, neutral accent, gentle enthusiasm without being overwhelming.
```

### Narrator Variation 2: Educational Guide

```
Clear educational narrator, medium pitch, slow-medium pace, precise pronunciation, authoritative but gentle tone, slightly more formal than the warm storyteller, suitable for direct teaching segments, neutral accent, emphasizes key vocabulary words subtly.
```

### Narrator Variation 3: Bedtime Voice

```
Soft bedtime narrator, low-medium pitch, slow pace, gentle hushed tone, warm and soothing, slightly breathy quality, suitable for winding down, minimal energy fluctuation, neutral accent, each word is a gentle hug.
```

---

## Group/Chorus Voice Template

```
Ensemble of preschool-aged children's voices, mixed ages 3–6, both boys and girls, cheerful and enthusiastic, slightly imperfect harmony (natural childlike quality), bright tone, medium energy, neutral accents, laughter and excitement naturally present between phrases, suitable for group song choruses and call-and-response sections.
```

---

## Emotion-Specific Voice Templates

### Happy

```
Bright, smiling voice, medium-high pitch, fast-medium speed, bouncy rhythm, rising intonation at end of sentences, laughter mixed with speech, energetic and warm, full of joy.
Example: "I'm so happy! This is the best day ever!"
```

### Sad

```
Soft, slightly lower voice, low-medium pitch, slow speed, falling intonation, slight breathiness, quiet tone, gentle and vulnerable.
Example: "I feel a little sad today. I miss my friend."
```

### Surprised

```
Higher pitch than normal, fast intake of breath before speaking, quick speed, wide intonation range, emphasis on key words, slightly louder volume on the surprising element.
Example: "Wow! I did not expect that! That's amazing!"
```

### Curious

```
Medium pitch with rising intonation on questions, medium speed with thoughtful pauses, questioning tone, slightly tilted head quality in the voice, warm interest.
Example: "Hmm, I wonder how that works. Should we find out together?"
```

### Excited

```
High pitch, fast speed, breathless quality, wide pitch range, almost jumping with each word, words running together occasionally, volume slightly louder.
Example: "Guess what! Guess what! We're going to the zoo today! I can't wait!"
```

### Tired

```
Low pitch, slow speed with longer pauses, slightly slurred edges, soft volume, yawn-like quality at ends of phrases, gentle and cozy.
Example: "Time for sleepy... so sleepy... goodnight everyone..."
```

### Scared

```
Slightly higher pitch, fast but hesitant speed, whispering quality on certain words, tremble in voice, quick breathing between phrases, quiet volume.
Example: "Did you hear that? I think... I think we should stay together."
```

### Proud

```
Medium pitch, moderate speed with emphasis on achievements, slightly louder volume, confident tone, warm smile in voice, clear enunciation.
Example: "I did it! I built the tallest tower all by myself!"
```

---

## Prompt Engineering Tips

### General Rules

- **Be specific**: "cheerful 5-year-old girl" is better than "child's voice"
- **Include pitch reference**: "medium-high pitch" gives the TTS a clear target
- **Specify speed**: Children's content needs clear pacing; define it explicitly
- **Add emotional context**: "shy but friendly" produces warmer results than "child voice"
- **Always include an example line**: Gives the TTS a direct sample of desired delivery

### Platform-Specific Optimization

| Platform | Focus On | Avoid |
|----------|----------|-------|
| Kokoro | Emotional description, pace | Complex multi-character prompts |
| XTTS v2 | Age, gender, pitch precision | Overly long descriptions |
| Piper | Technical parameters only | Emotional nuance |

### Voice Consistency Protocol

1. Save every successful character prompt
2. Generate 3 sample lines for each character to verify consistency
3. When regenerating, use the exact same prompt template
4. For XTTS v2, save a reference audio clip and use voice cloning
5. Document failed prompts in the voice testing log
6. Re-test voices every 10 episodes to ensure quality
