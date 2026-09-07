import json

# Read the file
with open('data/scenes/ledras_scenes_v4.json', 'r') as f:
    data = json.load(f)

# Find scene 4 and update it
scene4 = None
for scene in data['scenes']:
    if scene['id'] == 4:
        scene4 = scene
        break

if scene4:
    scene4['description'] = "Amphitheater steps/tiers, 6 big tiers from down to top, 7th tier is wall. static stone structure. above the steps are sky. vertical stone panel at the top center. ancient cyprus style. Night desert sand gradually gives way to greenery and flourishing trees. The transformation reveals subtle water channels carved into stone, where twilight reflections create miniature oasis scenes within the amphitheater tiers."
    
    scene4['elements'] = [
        "amphitheater",
        "six stone tiers",
        "water channels",
        "twilight reflections",
        "ancient irrigation",
        "desert-to-garden transition",
        "flourishing trees",
        "stone aqueducts",
        "oasis within tiers",
        "night sky with stars",
        "wind-carved stone",
        "air currents",
        "subtle water flow"
    ]
    print("Scene 4 updated successfully")
else:
    print("Scene 4 not found")

# Write back
with open('data/scenes/ledras_scenes_v4.json', 'w') as f:
    json.dump(data, f, indent=2)
