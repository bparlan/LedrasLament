import re

with open('/Users/bparlan/devcode/ledraslament/fal_generate.py', 'r') as f:
    content = f.read()

# Fix the generate_image method to add API key authentication
old_pattern = r'(\s+print\(f"🤖 Calling fal\.run\(\) API\.\.\."\)\s+result = fal_run\(self\.config\.fal_model, arguments=fal_params\))'

new_code = '''            print(f"🤖 Calling fal.run() API...")
            # Add API key authentication for fal.run()
            api_key = os.environ.get('FAL_API_KEY')
            if not api_key:
                print(f"⚠️  WARNING: FAL_API_KEY not set. Image generation may fail.")
            
            # Make authenticated API call
            result = fal_run(self.config.fal_model, arguments=fal_params, headers={"Authorization": f"Bearer {api_key}"} if api_key else {})'''

# Apply the fix
fixed_content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

with open('/Users/bparlan/devcode/ledraslament/fal_generate.py', 'w') as f:
    f.write(fixed_content)

print("✅ Authentication fix applied successfully!")
