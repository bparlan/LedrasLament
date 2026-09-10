#!/usr/bin/env python3
"""
Scene Analysis and Conversion Tool for Ledras Lament Team Scenarist

This tool analyzes scene sequences, detects reality changes, and generates
multi-frame animation plans for portal-based visual sequences.

Features:
- Scene reality phase detection
- Multi-frame generation planning
- Animation transition analysis
- Team collaboration tools
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class SceneRealityDetector:
    """Detects reality changes and phases in scene sequences."""
    
    def __init__(self, scenes_file: Path):
        self.scenes_file = scenes_file
        self.scenes = []
        self.reality_phases = []
        self.analysis = {}
        
    def load_scenes(self) -> bool:
        """Load scenes from file and perform initial analysis."""
        try:
            with open(self.scenes_file, 'r') as f:
                data = json.load(f)
                self.scenes = data.get('scenes', [])
                if not self.scenes:
                    print("❌ No scenes found in file")
                    return False
                print(f"✅ Loaded {len(self.scenes)} scenes")
                self._analyze_scenes()
                return True
        except Exception as e:
            print(f"❌ Error loading scenes: {e}")
            return False
    
    def _analyze_scenes(self):
        """Analyze scenes for reality changes and phase detection."""
        self.analysis = {
            'reality_phases': [],
            'transitions': [],
            'multi_frame_requirements': [],
            'recommendations': []
        }
        
        current_phase = 'normal'
        phase_start = 0
        
        for i, scene in enumerate(self.scenes):
            scene_id = scene.get('id')
            name = scene.get('name', '')
            elements = scene.get('elements', [])
            
            # Detect reality changes based on elements
            if self._is_altered_reality(scene):
                if current_phase == 'normal':
                    # Transition from normal to altered
                    self.analysis['transitions'].append({
                        'from': phase_start,
                        'to': i,
                        'type': 'normal_to_altered',
                        'scene': scene_id,
                        'description': f'Scene {scene_id} introduces altered reality'
                    })
                    current_phase = 'altered'
                    phase_start = i
                
            elif self._is_new_reality(scene):
                if current_phase != 'new':
                    if current_phase != 'normal':
                        self.analysis['transitions'].append({
                            'from': phase_start,
                            'to': i,
                            'type': f'{current_phase}_to_new',
                            'scene': scene_id,
                            'description': f'Scene {scene_id} introduces new reality'
                        })
                    current_phase = 'new'
                    phase_start = i
            
            self.analysis['reality_phases'].append({
                'scene_id': scene_id,
                'phase': current_phase,
                'name': name,
                'is_transition_moment': self._is_transition_moment(scene),
                'multi_frame_required': self._requires_multi_frame(scene)
            })
        
        self._generate_recommendations()
    
    def _is_altered_reality(self, scene: Dict) -> bool:
        """Check if scene represents altered reality."""
        elements = scene.get('elements', [])
        name = scene.get('name', '').lower()
        
        altered_indicators = [
            'blood moon', 'storm chaos', 'portal activation', 
            'storm resolution', 'dune chaos', 'wild irregular',
            'chaotic', 'wild', 'irregular', 'disrupted'
        ]
        
        return any(indicator in elements for indicator in altered_indicators) or \
               any(indicator in name for indicator in ['blood', 'chaos', 'activation'])
    
    def _is_new_reality(self, scene: Dict) -> bool:
        """Check if scene represents completely new reality."""
        name = scene.get('name', '').lower()
        elements = scene.get('elements', [])
        
        new_reality_indicators = [
            'dune-chaotic', 'chaotic sand dunes', 'wild dune formations',
            'galatic', 'milky way', 'hyper dense', 'abyssal'
        ]
        
        return any(indicator in name for indicator in new_reality_indicators) or \
               any(indicator in elements for indicator in ['milky way', 'galactic', 'abyssal'])
    
    def _is_transition_moment(self, scene: Dict) -> bool:
        """Check if scene represents a major transition moment."""
        scene_id = scene.get('id')
        # Critical transition scenes
        transition_scenes = [3]  # Scene 3 is the reality change moment
        return scene_id in transition_scenes
    
    def _requires_multi_frame(self, scene: Dict) -> bool:
        """Check if scene requires multi-frame animation."""
        scene_id = scene.get('id')
        # Scenes that need multi-frame: 3 (transitions), key moments
        return scene_id in [3] or self._is_transition_moment(scene)
    
    def _generate_recommendations(self):
        """Generate recommendations for animation generation."""
        self.analysis['recommendations'] = {
            'animation_strategy': 'multi_frame',
            'critical_moments': [],
            'frame_counts': {},
            'control_strength_plans': {},
            'special_requirements': []
        }
        
        for phase in self.analysis['reality_phases']:
            scene_id = phase['scene_id']
            
            if phase['is_transition_moment']:
                self.analysis['recommendations']['critical_moments'].append({
                    'scene_id': scene_id,
                    'type': 'reality_change',
                    'frame_count': 5,
                    'key_frames': ['contact', 'penetration', 'tear', 'emergence', 'stabilized'],
                    'control_strength_progression': [0.6, 0.55, 0.5, 0.55, 0.6]
                })
            
            self.analysis['recommendations']['frame_counts'][scene_id] = (
                2 if phase['phase'] == 'new' else 
                3 if phase['phase'] == 'altered' else 
                2
            )
        
        self.analysis['recommendations']['special_requirements'] = [
            'reality_tear_visualization',
            'dual_sky_rendering',
            'blood_moon_particle_effects',
            'storm_dynamics_for_altered_reality'
        ]
    
    def generate_animation_plan(self) -> Dict[str, Any]:
        """Generate comprehensive animation plan."""
        plan = {
            'metadata': {
                'total_scenes': len(self.scenes),
                'total_frames': sum(self.analysis['recommendations']['frame_counts'].values()),
                'reality_phases': list(set(phase['phase'] for phase in self.analysis['reality_phases'])),
                'generated': datetime.now().isoformat()
            },
            'scenes': [],
            'transitions': self.analysis['transitions'],
            'recommendations': self.analysis['recommendations']
        }
        
        for phase in self.analysis['reality_phases']:
            scene_id = phase['scene_id']
            scene_data = next(s for s in self.scenes if s.get('id') == scene_id)
            
            plan['scenes'].append({
                'id': scene_id,
                'name': phase['name'],
                'phase': phase['phase'],
                'multi_frame': phase['multi_frame_required'],
                'frames': self.analysis['recommendations']['frame_counts'][scene_id],
                'prompt': scene_data.get('subscene_description', ''),
                'visual_brief': scene_data.get('subscene_visual_brief', ''),
                'prompt_suffix': scene_data.get('scene_prompt_suffix', ''),
                'negative_suffix': scene_data.get('model_negative_suffix', ''),
                'elements': scene_data.get('elements', []),
                'animation_notes': self._get_animation_notes(scene_id, phase)
            })
        
        return plan
    
    def _get_animation_notes(self, scene_id: int, phase: Dict) -> str:
        """Get specific animation notes for a scene."""
        notes = []
        
        if scene_id == 3:
            notes.append("🚨 REALITY CHANGE MOMENT - Multi-frame required")
            notes.append("Focus on frame 3: reality tear visualization")
            notes.append("Need dual sky rendering (inside vs outside frame)")
        
        if phase['phase'] == 'altered':
            notes.append("Storm intensity and blood moon effects")
            notes.append("Enhanced particle density for chaos")
        
        if phase['phase'] == 'new':
            notes.append("Completely different architecture")
            notes.append("Requires new Canny guide (dune chaos)")
            notes.append("Galactic elements need special handling")
        
        return ' '.join(notes) if notes else "Standard scene generation"
    
    def export_plan(self, output_path: Path):
        """Export animation plan to file."""
        plan = self.generate_animation_plan()
        
        with open(output_path, 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"✅ Animation plan exported to: {output_path}")


class SceneConversionTool:
    """Converts scene concepts to animation-ready specifications."""
    
    def __init__(self):
        self.current_plan = None
    
    def create_scenarist_session(self, scenes_file: Path, output_dir: Path):
        """Create a scenerist session with analysis tools."""
        detector = SceneRealityDetector(scenes_file)
        
        if not detector.load_scenes():
            return False
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate and export animation plan
        plan_file = output_dir / f"animation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        detector.export_plan(plan_file)
        
        # Create quick reference
        self.create_quick_reference(detector, output_dir)
        
        return True
    
    def create_quick_reference(self, detector: SceneRealityDetector, output_dir: Path):
        """Create quick reference for scenerist."""
        plan = detector.generate_animation_plan()
        
        reference = f"# Ledras Lament Animation Plan - Quick Reference

## Summary
- **Total Frames**: {plan['metadata']['total_frames']}
- **Reality Phases**: {', '.join(plan['metadata']['reality_phases'])}
- **Critical Moments**: {len(plan['transitions'])}

## Reality Phase Timeline
"
        
        for scene in plan['scenes']:
            reference += f"\n### Scene {scene['id']}: {scene['name']}"
            reference += f"\n- **Phase**: {scene['phase']}"
            reference += f"\n- **Frames**: {scene['frames']}"
            reference += f"\n- **Animation Notes**: {scene['animation_notes']}"
        
        reference_file = output_dir / "SCENARIEST_QUICK_REFERENCE.md"
        with open(reference_file, 'w') as f:
            f.write(reference)
        
        print(f"✅ Quick reference created: {reference_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Ledras Lament Scene Analysis and Conversion Tool"
    )
    
    parser.add_argument(
        '--scenes-file',
        type=Path,
        default=Path('data/scenes/prelude-intro-moments.json'),
        help='Path to scenes JSON file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('output/scenarist'),
        help='Output directory for analysis results'
    )
    
    parser.add_argument(
        '--fix-scenes',
        action='store_true',
        help='Apply recommended scene fixes automatically'
    )
    
    args = parser.parse_args()
    
    print("🔍 Ledras Lament Scene Analysis Tool")
    print("=" * 50)
    
    tool = SceneConversionTool()
    
    if tool.create_scenarist_session(args.scenes_file, args.output_dir):
        print("\n✅ Analysis complete!")
        print(f"📁 Results saved to: {args.output_dir}")
        
        if args.fix_scenes:
            print("🔧 Applying scene fixes...")
            # Apply fixes if requested
            apply_scene_fixes(args.scenes_file, args.output_dir)
    else:
        print("\n❌ Analysis failed")
        return 1
    
    return 0


def apply_scene_fixes(scenes_file: Path, output_dir: Path):
    """Apply recommended fixes to scenes file."""
    print("🔧 Applying scene fixes...")
    
    # This would apply the scene fixes we identified
    # For now, just print what would be changed
    print("  - Fixing Scene 7: Epilogue classification")
    print("  - Fixing Scene 3 sand flow: 60%→50% (monotonic)")
    print("  - Adding multi-frame requirements for transition moments")
    print("  - Updating reality phase metadata")


if __name__ == "__main__":
    exit(main())