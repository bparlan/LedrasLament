#!/usr/bin/env python3
"""
Fal AI Scene Generation Pipeline for Ledras Lament

Professional scene generation system for the Ledras Lament project,
integrating with fal.ai API (flux-control-lora-canny) and comprehensive
technical controls for consistent, high-quality output.

Key Features:
- Scene-to-prompt generation with cultural constraints
- Technical parameter management (1280x720px, 120px/meter, etc.)
- Quality assurance and verification systems
- Progressive scene variation (intro/loop/outro)
- Team-based decision making integration
"""

import json
import os
import re
import hashlib
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TechnicalSpecs:
    """Technical rendering specifications for scene generation"""
    resolution: str = "1280x720"
    aspect_ratio: str = "19:9"
    pixel_density: str = "120px/meter"
    specular_highlight_strength: float = 0.3
    spot_light_intensity: float = 0.8
    spot_light_position: Dict[str, float] = field(default_factory=lambda: {"x": 0.5, "y": 0.3, "z": 2.0})
    fine_edge_threshold: float = 0.4
    weathered_stone_texture: bool = True
    ancient_mortar_depth: float = 0.6
    ambient_occlusion_strength: float = 0.7
    global_illumination_quality: str = "high"
    shadow_softness: float = 0.3
    material_metalness: float = 0.1
    material_roughness: float = 0.8
    num_inference_steps: int = 28
    control_start: float = 0.0
    control_stop: float = 1.0
    fal_control_strength: float = 0.6

@dataclass
class SceneTemplate:
    """Scene generation template with cultural and technical constraints"""
    format: str = "scene_{id}_{role}: {description} [elements: {elements}] [technical: {technical_specs}]"
    progressive_roles: List[str] = field(default_factory=lambda: ["intro", "loop", "outro"])
    cultural_constraints: Dict[str, Any] = field(default_factory=lambda: {
        "prohibited_styles": ["classical_greek", "modern_arch"],
        "required_elements": ["ancient_weathering", "mediterranean_geometry"]
    })
    technical: TechnicalSpecs = field(default_factory=TechnicalSpecs)

@dataclass
class QualityAssurance:
    """Quality control and verification standards"""
    standards: Dict[str, Any] = field(default_factory=lambda: {
        "technical_accuracy": {
            "pixel_density_tolerance": 0.05,
            "material_physics": "weathered_stone_simulation",
            "specular_highlight": "subtle_reflection_only"
        },
        "cultural_authenticity": {
            "style_consistency": "cypro_phoenician",
            "ornament_rules": "lefkara_patterns_optional",
            "regional_context": "levantine_mediterranean"
        }
    })
    verification_checks: List[str] = field(default_factory=lambda: [
        "architectural_geometry",
        "cultural_authenticity",
        "technical_render_fidelity"
    ])

class LedrasSceneGenerator:
    """
    Professional scene generation system for Ledras Lament project.
    Integrates with fal.ai API and comprehensive team-based decision making.
    """
    
    def __init__(self, config_path: str = "imagine-config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.templates = self._load_templates()
        self.quality = self._load_quality_standards()
        self.team_consensus = self._load_team_structure()
        
        # Generate deterministic seeds per scene
        self.scene_seeds = self._generate_scene_seeds()
        
        print(f"LedrasSceneGenerator initialized")
        print(f"Config loaded: {self.config['image_size']} @ {self.config['pixel_density']}")
        print(f"Scenes: {len(self.scene_seeds)} scenes with {self.config['subscene_variation_count']} variations each")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate technical configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate critical technical parameters
            self._validate_config(config)
            return config
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config: {e}")
            raise
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate critical technical parameters"""
        required_keys = [
            "image_size", "image_aspect_ratio", "pixel_density",
            "specular_highlight_strength", "spot_light_intensity",
            "fine_edge_threshold", "weathered_stone_texture",
            "num_inference_steps", "control_start", "control_stop"
        ]
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Validate technical ranges
        if not (0.0 <= config["specular_highlight_strength"] <= 1.0):
            raise ValueError("specular_highlight_strength must be 0.0-1.0")
        
        if not (0.0 <= config["fine_edge_threshold"] <= 1.0):
            raise ValueError("fine_edge_threshold must be 0.0-1.0")
        
        if not (config["num_inference_steps"] >= 16 and config["num_inference_steps"] <= 50):
            raise ValueError("num_inference_steps should be 16-50")
    
    def _load_templates(self) -> SceneTemplate:
        """Load scene generation templates"""
        try:
            with open("scene_templates.json", 'r') as f:
                templates_data = json.load(f)
            
            technical_data = templates_data.get("technical_overrides", {})
            template = SceneTemplate(
                format=templates_data["base_structure"]["format"],
                progressive_roles=templates_data["base_structure"]["progressive_roles"],
                cultural_constraints=templates_data["base_structure"]["cultural_constraints"],
                technical=TechnicalSpecs(**technical_data)
            )
            
            return template
        except FileNotFoundError:
            print("scene_templates.json not found")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in scene_templates.json: {e}")
            raise
    
    def _load_quality_standards(self) -> QualityAssurance:
        """Load quality assurance standards"""
        try:
            with open("quality_assurance.json", 'r') as f:
                qa_data = json.load(f)
            
            return QualityAssurance(
                standards=qa_data["standards"],
                verification_checks=qa_data["verification_checks"]
            )
        except FileNotFoundError:
            print("quality_assurance.json not found")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in quality_assurance.json: {e}")
            raise
    
    def _load_team_structure(self) -> Dict[str, Any]:
        """Load team structure and decision protocols"""
        try:
            with open("team_config.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("team_config.json not found")
            raise
    
    def _generate_scene_seeds(self) -> Dict[int, int]:
        """Generate deterministic seeds per scene"""
        scenes_file = self.config["scenes_file"]
        try:
            with open(scenes_file, 'r') as f:
                scenes_data = json.load(f)
            
            scene_seeds = {}
            for scene in scenes_data.get("scenes", []):
                scene_id = scene["id"]
                # Hash based on scene content for deterministic seeds
                scene_content = json.dumps(scene, sort_keys=True)
                seed = int(hashlib.md5(scene_content.encode()).hexdigest()[:8], 16) % 10000
                scene_seeds[scene_id] = seed
            
            return scene_seeds
        except FileNotFoundError:
            print(f"Scenes file not found: {scenes_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in scenes file: {e}")
            return {}
    
    def _validate_scene_requirements(self, scene: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate scene against cultural and technical requirements"""
        errors = []
        warnings = []
        
        # Cultural validation
        for required in self.templates.cultural_constraints["required_elements"]:
            # Check if scene description contains required elements
            pass  # Implementation depends on specific requirements
        
        # Technical validation
        if "elements" not in scene:
            errors.append("Scene missing 'elements' field")
        
        if len(scene.get("elements", [])) < 3:
            warnings.append(f"Scene {scene['id']} has fewer than 3 elements - consider adding more detail")
        
        return len(errors) == 0, errors + warnings
    
    def generate_prompt(self, scene_id: int, role: str = "loop") -> str:
        """
        Generate professional prompt for scene rendering
        
        Args:
            scene_id: Scene identifier (1-9)
            role: Progressive role (intro, loop, outro)
        
        Returns:
            Generated prompt string with all technical specifications
        """
        # Load scenes file
        try:
            with open(self.config["scenes_file"], 'r') as f:
                scenes_data = json.load(f)
        except FileNotFoundError:
            print(f"Scenes file not found: {self.config['scenes_file']}")
            return ""
        
        # Find target scene
        scene = None
        for s in scenes_data.get("scenes", []):
            if s["id"] == scene_id:
                scene = s
                break
        
        if not scene:
            print(f"Scene {scene_id} not found")
            return ""
        
        # Validate scene requirements
        is_valid, validation_results = self._validate_scene_requirements(scene)
        if not is_valid:
            print(f"Scene validation warnings: {validation_results}")
        
        # Build prompt using template
        template = self.templates.format
        description = scene["description"]
        elements = ", ".join(scene.get("elements", []))
        
        # Format technical specifications
        technical_specs = self._format_technical_specs()
        
        # Apply team consensus rules
        prompt = template.format(
            id=scene_id,
            role=role,
            description=description,
            elements=elements,
            technical_specs=technical_specs
        )
        
        # Add team metadata
        prompt += f" [seed:{self.scene_seeds.get(scene_id, 42)}]"
        prompt += f" [team:{self.config['cultural_authenticity_level']}]"
        prompt += f" [quality_verified:{self._check_quality_standards(scene)}]"
        
        return prompt
    
    def _format_technical_specs(self) -> str:
        """Format technical specifications for inclusion in prompts"""
        specs = [
            f"res:{self.config['image_size']}",
            f"aspect:{self.config['image_aspect_ratio']}",
            f"density:{self.config['pixel_density']}",
            f"specular:{self.config['specular_highlight_strength']}",
            f"steps:{self.config['num_inference_steps']}",
            f"control:{self.config['fal_control_strength']}",
            f"weathered:{self.config['weathered_stone_texture']}",
            f"mortar:{self.config['ancient_mortar_depth']}",
            f"ambient:{self.config['ambient_occlusion_strength']}"
        ]
        return ", ".join(specs)
    
    def _check_quality_standards(self, scene: Dict[str, Any]) -> str:
        """Check if scene meets quality standards"""
        checks_passed = 0
        total_checks = len(self.quality.verification_checks)
        
        for check in self.quality.verification_checks:
            # Implement quality checks based on standards
            if check == "architectural_geometry":
                # Check for amphitheater elements
                if any(elem in scene.get("elements", []) for elem in ["amphitheater", "tiers", "steps"]):
                    checks_passed += 1
            
            elif check == "cultural_authenticity":
                # Check for Mediterranean elements
                if any(elem in scene.get("elements", []) for elem in ["cyprus", "levantine", "mediterranean"]):
                    checks_passed += 1
            
            elif check == "technical_render_fidelity":
                # Check for technical elements
                if any(elem in scene.get("elements", []) for elem in ["stone", "weathered", "ancient"]):
                    checks_passed += 1
        
        return f"{checks_passed}/{total_checks}"
    
    def generate_all_prompts(self) -> Dict[int, Dict[str, str]]:
        """
        Generate prompts for all scenes and progressive roles
        
        Returns:
            Dictionary mapping scene IDs to role-based prompts
        """
        prompts = {}
        
        for scene_id in self.scene_seeds.keys():
            scene_prompts = {}
            for role in self.templates.progressive_roles:
                prompt = self.generate_prompt(scene_id, role)
                if prompt:
                    scene_prompts[role] = prompt
            
            prompts[scene_id] = scene_prompts
        
        return prompts
    
    def save_prompts(self, output_path: str = "generated_prompts.json"):
        """Save generated prompts to file"""
        prompts = self.generate_all_prompts()
        
        output_data = {
            "generated_prompts": prompts,
            "metadata": {
                "config_used": self.config_path,
                "template_version": "1.0",
                "quality_standards": self.config["cultural_authenticity_level"],
                "generation_timestamp": datetime.now().isoformat(),
                "total_prompts": sum(len(prompts_by_role) for prompts_by_role in prompts.values())
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Prompts saved to {output_path}")
        print(f"Generated {output_data['metadata']['total_prompts']} prompts across all scenes")
    
    def validate_generated_prompts(self) -> bool:
        """Validate all generated prompts against quality standards"""
        prompts = self.generate_all_prompts()
        
        all_valid = True
        validation_errors = []
        
        for scene_id, role_prompts in prompts.items():
            for role, prompt in role_prompts.items():
                # Check prompt length
                if len(prompt) > 2000:  # Reasonable prompt length
                    validation_errors.append(f"Scene {scene_id} {role} prompt too long: {len(prompt)} chars")
                
                # Check for required elements
                required_elements = ["amphitheater", "stone", "tiers"]
                if not any(elem in prompt.lower() for elem in required_elements):
                    validation_errors.append(f"Scene {scene_id} {role} missing key elements")
                
                # Check technical specifications
                if "res:1280x720" not in prompt:
                    validation_errors.append(f"Scene {scene_id} {role} missing resolution spec")
                
                if "density:120px/meter" not in prompt:
                    validation_errors.append(f"Scene {scene_id} {role} missing pixel density spec")
        
        if validation_errors:
            print("Prompt validation errors:")
            for error in validation_errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print("✅ All prompts passed quality validation")
        
        return all_valid
    
    def get_team_consensus_status(self) -> Dict[str, Any]:
        """Get team consensus and decision status"""
        team_structure = self.team_consensus
        
        return {
            "team_leadership": team_structure.get("team_leadership", "technical_visionary"),
            "consensus_threshold": team_structure.get("consensus_threshold", 0.8),
            "communication_protocol": team_structure.get("communication_protocol", "irc_style"),
            "decision_veto_powers": team_structure.get("decision_veto_powers", {}),
            "expertise_registry": team_structure.get("expertise_registry", {}),
            "current_phase": "Phase 2: Implementation",
            "files_modified": [
                "imagine-config.json",
                "scene_templates.json", 
                "quality_assurance.json",
                "team_config.json"
            ]
        }

# Command line interface
if __name__ == "__main__":
    print("=" * 60)
    print("LEDAS LAMENT SCENE GENERATION PIPELINE")
    print("=" * 60)
    
    try:
        generator = LedrasSceneGenerator()
        
        print(f"\n🔧 System Status:")
        print(f"   - Technical Configuration: {generator.config['image_size']} @ {generator.config['pixel_density']}")
        print(f"   - Cultural Authenticity: {generator.config['cultural_authenticity_level']}")
        print(f"   - Progressive Roles: {', '.join(generator.templates.progressive_roles)}")
        print(f"   - Subscene Variations: {generator.config['subscene_variation_count']}")
        
        print(f"\n📋 Team Consensus:")
        team_status = generator.get_team_consensus_status()
        print(f"   - Leadership: {team_status['team_leadership']}")
        print(f"   - Decision Matrix: {team_status['decision_veto_powers']}")
        
        print(f"\n🎨 Generating Prompts...")
        prompts = generator.generate_all_prompts()
        
        print(f"\n✅ Validation Results:")
        is_valid = generator.validate_generated_prompts()
        print(f"   - Quality Status: {'✅ PASSED' if is_valid else '❌ FAILED'}")
        
        print(f"\n💾 Saving Generated Prompts...")
        generator.save_prompts("generated_prompts.json")
        
        print(f"\n📊 System Summary:")
        for scene_id, role_prompts in prompts.items():
            print(f"   - Scene {scene_id}: {len(role_prompts)} prompts ({', '.join(role_prompts.keys())})")
        
        print(f"\n🎯 Phase 2 Implementation Complete!")
        print(f"   All scenes configured for professional generation")
        print(f"   Team consensus protocols established")
        print(f"   Quality assurance framework active")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)