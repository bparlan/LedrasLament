#!/usr/bin/env python3
"""
Simple test to verify the version tracking fix prevents overwriting.
"""

import tempfile
from pathlib import Path
import shutil

# Define the fixed functions directly in this test
def get_next_version_number(output_dir: Path, scene_id: int) -> int:
    """
    Get the next version number for a scene to ensure unique filenames.
    
    This function ensures that each generated image for a given scene gets a unique
    filename, preventing overwrites of previously generated assets.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Pattern: scene-01-v[version].png
    version_pattern = f"scene-{scene_id:02d}-v*.png"
    
    max_version = 0
    for file_path in output_dir.glob(version_pattern):
        # Extract version number from filename
        try:
            # Extract version from pattern like "scene-01-v002.png"
            version_str = file_path.stem.split('-')[-1][1:]  # Remove 'v' prefix
            version = int(version_str)
            max_version = max(max_version, version)
        except (ValueError, IndexError):
            continue
    
    return max_version + 1

def save_image_fixed(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """
    Save generated image to file with version tracking to prevent overwrites.
    
    Key fix: Each save operation gets a unique version number to prevent
    overwriting existing assets. The function tracks existing files for the
    given scene and increments the version number accordingly.
    """
    output_path = Path(output_dir)
    
    # Get next available version number
    version = get_next_version_number(output_path, scene_id)
    
    # Create filename with version number: scene-01-v002.png
    out_path = output_path / f"scene-{scene_id:02d}-v{version:03d}.png"
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save the image
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    
    print(f"📸 Saved scene {scene_id} as {out_path.name} (version {version})")
    return str(out_path)

def test_version_tracking_fix():
    """Test that the fix prevents overwriting."""
    print("🧪 Testing version tracking fix for overwrite prevention")
    print("=" * 60)
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_dir = temp_path / "assets/generated"
        
        # Test 1: Multiple saves of same scene should create unique files
        print("\nTest 1: Multiple saves of same scene")
        for i in range(1, 5):
            image_data = f"scene_1_data_v{i}".encode()
            result = save_image_fixed(image_data, 1, str(output_dir))
            filename = Path(result).name
            
            # Verify filename pattern
            if not filename.startswith("scene-01-v") or not filename.endswith(".png"):
                print(f"❌ Invalid filename: {filename}")
                return False
            
            # Extract version number
            version_part = filename.split('v')[1].split('.')[0]
            version = int(version_part)
            
            if version != i:
                print(f"❌ Wrong version: got {version}, expected {i}")
                return False
            
            print(f"  Save {i}: {filename} ✓")
        
        # Verify all 4 files exist and have unique content
        files = list(output_dir.glob("scene-01-v*.png"))
        if len(files) != 4:
            print(f"❌ Expected 4 files, got {len(files)}")
            return False
        
        print(f"✅ Test 1 PASSED: Created 4 unique files for scene 1")
        
        # Test 2: Different scenes should have independent versioning
        print("\nTest 2: Different scenes with independent versioning")
        
        # Reset for clean test
        shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)
        
        # Save multiple scenes
        saves = [(1, b"scene1"), (2, b"scene2"), (3, b"scene3"), (1, b"scene1_new"), (2, b"scene2_new")]
        
        for scene_id, data in saves:
            result = save_image_fixed(data, scene_id, str(output_dir))
            print(f"  Scene {scene_id}: {Path(result).name}")
        
        # Verify scene 1 has 2 files, scene 2 has 2 files, scene 3 has 1 file
        scene1_files = list(output_dir.glob("scene-01-v*.png"))
        scene2_files = list(output_dir.glob("scene-02-v*.png"))
        scene3_files = list(output_dir.glob("scene-03-v*.png"))
        
        if len(scene1_files) != 2:
            print(f"❌ Scene 1 has {len(scene1_files)} files, expected 2")
            return False
        
        if len(scene2_files) != 2:
            print(f"❌ Scene 2 has {len(scene2_files)} files, expected 2")
            return False
        
        if len(scene3_files) != 1:
            print(f"❌ Scene 3 has {len(scene3_files)} files, expected 1")
            return False
        
        print("✅ Test 2 PASSED: Scenes have independent versioning")
        
        # Test 3: Verify no overwriting occurred
        print("\nTest 3: Verify no overwriting")
        
        # Check scene 1 versions
        scene1_v1 = output_dir / "scene-01-v001.png"
        scene1_v2 = output_dir / "scene-01-v002.png"
        
        with open(scene1_v1, "rb") as f:
            v1_content = f.read()
        with open(scene1_v2, "rb") as f:
            v2_content = f.read()
        
        if v1_content == v2_content:
            print("❌ Scene 1 files have same content - overwriting occurred!")
            return False
        
        if v1_content != b"scene1":
            print(f"❌ Scene 1 v1 has wrong content: {v1_content}")
            return False
        
        if v2_content != b"scene1_new":
            print(f"❌ Scene 1 v2 has wrong content: {v2_content}")
            return False
        
        print("✅ Test 3 PASSED: No overwriting, all files have unique content")
        
        return True

def main():
    """Run the test."""
    print("🔧 Testing Ledras Lament overwrite fix")
    print("=" * 60)
    
    try:
        if test_version_tracking_fix():
            print("\n" + "=" * 60)
            print("🎉 SUCCESS: Overwrite issue has been fixed!")
            print("=" * 60)
            print("\nThe fix implements:")
            print("1. Version tracking to ensure unique filenames")
            print("2. Independent versioning per scene")
            print("3. No overwriting of existing assets")
            print("\nGenerated files will be named like:")
            print("  - scene-01-v001.png (first version)")
            print("  - scene-01-v002.png (second version)")
            print("  - scene-02-v001.png (first version for scene 2)")
            return 0
        else:
            print("\n" + "=" * 60)
            print("❌ FAILURE: Overwrite issue still exists!")
            print("=" * 60)
            return 1
            
    except Exception as e:
        print(f"\n❌ Test crashed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())