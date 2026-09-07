import re

with open('/Users/bparlan/devcode/ledraslament/fal_generate.py', 'r') as f:
    content = f.read()

# Update the main execution to use scene 4
old_main_pattern = r'print\(f"🎨 Generating scene \d+\.\.\."\)\s*scenes = generator\.generate_specific_images\(\[\d+, \d+\], "intro"\)'
new_main_code = '''        # Generate the requested scene
        print(f"🎨 Generating scene 4...")
        scenes = generator.generate_specific_images([4], "intro")

        print()
        print("✅ SUCCESS: Scene 4 generated successfully!")
        print(f"📊 Generated: {len(scenes)} scenes")'''

# Use a more specific pattern
main_pattern = r'(\s*# Generate the requested scene\s*\n\s*print\(f"🎨 Generating scene \d+\.\.\."\)\s*\n\s*scenes = generator\.generate_specific_images\(\[\d+, \d+\], "intro"\)\s*\n\s*\n\s*print\(\)\s*\n\s*print\("✅ SUCCESS: Scene \d+ generated successfully!"\))'

# Find and replace using line numbers approach
lines = content.split('\n')

# Find the line with "Generate the requested scene"
for i, line in enumerate(lines):
    if '# Generate the requested scene' in line:
        start_line = i
        print(f"Found target section at line {i+1}")
        
        # Find the end of the section (look for the success print line)
        for j in range(i, min(i+20, len(lines))):
            if '✅ SUCCESS:' in lines[j]:
                end_line = j
                print(f"Found success message at line {j+1}")
                
                # Replace the section
                new_lines = lines[:start_line] + [
                    '# Generate the requested scene',
                    '        print(f"🎨 Generating scene 4...")',
                    '        scenes = generator.generate_specific_images([4], "intro")',
                    '',
                    '        print()',
                    '        print("✅ SUCCESS: Scene 4 generated successfully!")',
                    '        print(f"📊 Generated: {len(scenes)} scenes")'
                ] + lines[end_line+1:]
                
                new_content = '\n'.join(new_lines)
                
                with open('/Users/bparlan/devcode/ledraslament/fal_generate.py', 'w') as f:
                    f.write(new_content)
                
                print("✅ Main execution updated successfully!")
                break
        break
else:
    print("❌ Could not find target section to update")
