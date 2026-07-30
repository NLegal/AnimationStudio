# Curriculum Engine Guide

## Purpose

The Curriculum Engine determines **what children should learn**. It is the first layer of the Story Engine pipeline and ensures that every episode serves a meaningful educational purpose. The engine maintains balanced educational coverage across hundreds of episodes so that no single area is overrepresented.

---

## Curriculum Areas

| # | Area | Description |
|---|---|---|
| 1 | Alphabet | Letter recognition, phonics, letter sounds, alphabetical order |
| 2 | Numbers | Counting, number recognition, basic arithmetic, quantities |
| 3 | Shapes | Shape identification, shape properties, sorting by shape |
| 4 | Colors | Color recognition, color mixing, identifying colors in the world |
| 5 | Animals | Animal names, sounds, habitats, characteristics |
| 6 | Science | Basic scientific concepts, observation, cause and effect |
| 7 | Space | Sun, moon, stars, planets, space travel concepts |
| 8 | Ocean | Sea creatures, ocean environments, water concepts |
| 9 | Farm | Farm animals, crops, farm life, where food comes from |
| 10 | Healthy Habits | Brushing teeth, washing hands, eating well, exercise, sleep |
| 11 | Friendship | Sharing, taking turns, helping, being kind, making friends |
| 12 | Emotions | Identifying feelings, expressing emotions, empathy |
| 13 | Problem Solving | Critical thinking, finding solutions, asking for help |
| 14 | Motor Skills | Clapping, jumping, dancing, drawing, building |
| 15 | Music | Rhythm, instruments, singing, musical concepts |
| 16 | Dance | Movement, coordination, following dance patterns |
| 17 | Language | Vocabulary building, sentence structure, communication |
| 18 | Seasons | Spring, summer, fall, winter — characteristics and changes |
| 19 | Weather | Rain, sun, snow, wind, clouds, weather observation |
| 20 | Community Helpers | Firefighters, doctors, teachers, police, mail carriers |
| 21 | Transportation | Cars, buses, trains, planes, boats — how we move |
| 22 | Geography | Maps, places, near and far, land and water |
| 23 | Nature | Plants, trees, flowers, gardening, outdoor exploration |
| 24 | Music & Rhythm | Beat, tempo, rhythm patterns, musical instruments |
| 25 | Daily Routines | Morning routine, bedtime, mealtime, getting dressed |

---

## Balanced Educational Coverage

The Curriculum Engine tracks how many episodes have been produced in each curriculum area. When selecting a new area, it prefers those with the fewest episodes to maintain balance.

**Algorithm:**
1. Count episodes per curriculum area
2. Identify areas with the lowest count
3. Apply soft preference — area with lowest count gets higher priority
4. Check theme compatibility — ensure available themes match the selected area
5. Check recent episodes — avoid same area twice in a row
6. Final selection

---

## Example Learning Objectives per Area

| Curriculum Area | Example Objectives |
|---|---|
| Alphabet | Recognize letter A, Learn the letter B sound, Sing the Alphabet Song |
| Numbers | Count to five, Count to ten, Recognize number 3, Count backwards |
| Shapes | Identify circles, Find triangles, Sort shapes by color |
| Colors | Recognize blue, Mix red and yellow, Find green in nature |
| Animals | Learn duck sounds, Name farm animals, Identify animal habitats |
| Science | Explore sinking and floating, Learn about magnets, Observe plant growth |
| Healthy Habits | Brush teeth properly, Wash hands before eating, Eat colorful foods |
| Friendship | Share toys with friends, Take turns on the swing, Help a friend in need |
| Emotions | Name feeling happy, Recognize sad face, Say "I feel angry" |
| Seasons | Describe spring changes, Identify winter weather, Talk about fall leaves |

---

## Integration with Difficulty Scaling

The Curriculum Engine works with the Vocabulary Engine to scale difficulty:

| Age | Curriculum Complexity | Vocabulary Level |
|---|---|---|
| 2 | Single concept, concrete objects | One-word phrases |
| 3 | Basic identification, simple actions | Two-word phrases |
| 4 | Concept application, simple reasoning | Simple sentences |
| 5 | Understanding, prediction | Longer conversations |
| 6 | Explanation, connection between concepts | Complex sentences |

A "Count to Five" episode for age 2 uses visual counting with one-word responses. For age 5, it incorporates simple addition word problems within the count.
