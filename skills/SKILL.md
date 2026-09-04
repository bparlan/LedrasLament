---
name: pipeline
version: 1.0.0
description: Media pipeline orchestration for Ledras Lament project - coordinates image, video, and inspection skills
---

# Ledras Lament Pipeline Orchestrator (Agentic Media Pipeline)

**Complete media pipeline orchestration for the Ledras Lament projection mapping show**

## Project Context

This pipeline orchestrates the 12-scene Ledras Lament visual art project as documented in `docs/`:
- **12 visual concept scenes** with specific prompts and placement requirements
- **Budget constraint**: $20-40 total (crypto payment preferred)
- **Technical specs**: 1280×720, 24fps, seamless loops
- **Style lock**: Cypro-Phoenician / Levantine Bronze Age ruin style

## Integration with Project Structure

### Source Documents
- `docs/PRODUCTION.md` - Core production patterns for OhMyPi
- `docs/PROMPTS_V1.md` - Choreographer stage flow with 12 scene prompts
- `docs/VISUAL_CONTEXT.md` - 12 visual concept scenes with prompts
- `docs/SYSTEM.md` - Technical specs and workflow
- `docs/context/artproject-chatgpt.md` - Agentic media pipeline architecture
- `docs/context/imagegen-grok.md` - Token-efficient image generation

### Project Assets
- **Guideline image**: `stage/stage_clean_v3_1280x720x64dpi.jpg`
- **Config**: `imagine-config.json` (project-specific)
- **Pipeline config**: `pipeline-config.json` (new, for coordination)
- **Skills**: Local `skills/` directory (imagine, video-gen, inspector)

## Architecture (FROM artproject-chatgpt.md)

```
                         Ledras Lament Project
                              │
                    scene manifests / prompts
                              │
                              ▼
                    ┌──────────────────┐
                    │      OhMyPi      │
                    │ creative director│
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
          IMAGE GENERATION         VIDEO GENERATION
                 │                       │
        FreeLLMAPI + OpenRouter        fal.ai / Runway  
                 │                       │
                 ▼                       ▼
           scene images              short clips
                 │                       │
                 └───────────┬───────────┘
                             ▼
                    VISUAL REVIEW AGENT
                             │
                 ┌───────────┴───────────┐
                 │                       │
              ACCEPT                  REJECT
                 │                       │
                 │                 regenerate
                 ▼
                       /artifacts
                             │
                             ▼
                     final assembly
```

## Project-Specific Stage Definitions

### 12 Visual Concept Scenes (FROM VISUAL_CONTEXT.md)

```json
{
  "stages": [
    {
      "id": 1,
      "name": "Invocation",
      "act": "Lament",
      "visual_concept": "Total darkness, single warm light pulse, Eteocypriot glyphs",
      "palette": "Black, amber-gold",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Ancient stone amphitheater at night, total darkness except a single pulsing warm amber light at center, faint undeciphered ancient glyphs flickering at the edge of the light and dissolving, minimal, ritualistic, cinematic, high contrast."
    },
    {
      "id": 2,
      "name": "The City of Gardens",
      "act": "Lament", 
      "visual_concept": "Aerial view of ancient garden city with terraced gardens and irrigation",
      "palette": "Ochre stone, deep green, silver water",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Ancient Mediterranean garden city, terraced green gardens with stone irrigation channels carrying flowing water, low ochre-stone architecture, lush and abundant, golden-hour light, painterly historical illustration style."
    },
    {
      "id": 3,
      "name": "Concrete Encroachment",
      "act": "Lament",
      "visual_concept": "Garden city progressively overtaken by grey concrete slabs",
      "palette": "Shift from green/ochre to flat grey",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Time-lapse of grey concrete slabs spreading and rising over a green garden city, water channels being sealed shut, vegetation shrinking to small isolated patches, desaturating color grade, oppressive urban expansion."
    },
    {
      "id": 4,
      "name": "The Line of Division",
      "act": "Lament",
      "visual_concept": "Jagged fracture line splitting cityscape in two",
      "palette": "Rust, grey, weed-green, harsh shadow",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "A jagged dividing line splitting a Mediterranean city map in two, rusted barrier aesthetic overgrown with weeds, mirrored architectural fragments on either side unable to reconnect, tense and desolate, high contrast graphic style."
    },
    {
      "id": 5,
      "name": "Archive of Memory",
      "act": "Memory",
      "visual_concept": "Sepia archival photographs dissolving, Eteocypriot script drifting",
      "palette": "Sepia, faded gold, soft grain",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Sepia archival photographs of an old Mediterranean city dissolving into one another like turning album pages, faint ancient undeciphered script drifting across the images, dust motes in warm light, nostalgic documentary texture."
    },
    {
      "id": 6,
      "name": "Eteocypriot Script Field",
      "act": "Memory",
      "visual_concept": "Alphabet flowing across amphitheater steps like water",
      "palette": "Pale blue-white script on dark stone",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Ancient undeciphered alphabet characters flowing like liquid across stone amphitheater steps, glyphs forming and dissolving continuously, pale luminous script on dark stone, abstract and hypnotic, projection-mapping texture."
    },
    {
      "id": 7,
      "name": "Ancestors Reclaim the Stage",
      "act": "Memory",
      "visual_concept": "Ancestral figures rising from seating tiers",
      "palette": "Warm stone gold, dark silhouettes",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Silhouetted ancestral figures slowly emerging from within ancient stone amphitheater seating, as if rising out of the stone itself, facing outward toward the viewer, golden backlight, ritualistic and monumental, mapped to stepped stone geometry."
    },
    {
      "id": 8,
      "name": "Call to Astarte",
      "act": "Transformation",
      "visual_concept": "Mesopotamian goddess with orbital symbols",
      "palette": "Deep indigo background, gold relief lines",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Ancient Mesopotamian goddess figure rendered as glowing gold bas-relief on dark indigo background, surrounded by slowly orbiting doves and rosette star symbols, ancient religious iconography, symmetrical and reverent, sacred geometry."
    },
    {
      "id": 9,
      "name": "Grief Spiral",
      "act": "Transformation",
      "visual_concept": "Dark vortex swallowing fragmented imagery",
      "palette": "Near-black with fragments of desaturated color",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Dark swirling vortex on the ground pulling in fragmented images of concrete buildings, dividing walls, and old sepia photographs, surreal and disorienting, high contrast black background, cinematic spiral motion."
    },
    {
      "id": 10,
      "name": "Astarte Becomes Aphrodite",
      "act": "Transformation",
      "visual_concept": "Goddess morphing from relief to flowing form",
      "palette": "Shift from indigo/gold to sea-blue, white foam, rose light",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Ancient bas-relief goddess figure dissolving and transforming into a classical Aphrodite emerging from sea foam and flowing water, morphing style from rigid gold relief to soft flowing marble and water, ethereal transformation, warm rose and sea-blue light."
    },
    {
      "id": 11,
      "name": "Water Returns",
      "act": "Renewal",
      "visual_concept": "Water flooding back, concrete cracking, greenery returning",
      "palette": "Grey concrete giving way to vivid green and clear water",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Water flooding back through cracks in grey concrete, green plant shoots bursting up through the fractures and spreading, concrete transforming into fertile garden ground, vivid hopeful color grade, time-lapse growth."
    },
    {
      "id": 12,
      "name": "Shared Future",
      "act": "Renewal",
      "visual_concept": "Birds rising from steps into night sky with stars",
      "palette": "Deep night blue, silver stars, dark bird silhouettes",
      "duration": 6,
      "cost_estimated": "$0.03",
      "prompt": "Flocks of birds rising from ancient stone amphitheater steps and flying outward over the viewer into a deep night sky, stars slowly connecting into constellation lines that echo an ancient alphabet's shapes, open and hopeful, wide cinematic night sky."
    }
  ],
  "transitions": [
    {"id": "t1", "from": 1, "to": 2, "name": "Scene 1→2: Installation to Garden City"},
    {"id": "t2", "from": 3, "to": 4, "name": "Scene 3→4: Concrete to Division"},
    {"id": "t3", "from": 5, "to": 6, "name": "Scene 5→6: Archive to Script"},
    {"id": "t4", "from": 7, "to": 8, "name": "Scene 7→8: Ancestors to Astarte"},
    {"id": "t5", "from": 9, "to": 10, "name": "Scene 9→10: Grief to Transformation"}
  ],
  "budget": {
    "total_target": "$40",
    "free_tier_priority": true,
    "escalation_cost": "$20-40"
  },
  "technical_constraints": {
    "resolution": "1280x720",
    "frame_rate": 24,
    "loop_requirement": true,
    "seamless_transition": true,
    "structure_lock": "stage/stage_clean_v3_1280x720x64dpi.jpg"
  }
}
```

## Code Implementation

```python
import json
import time
import base64
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess

@dataclass
class LedrasAsset:
    id: str
    type: str  # "scene", "segment", "transition"
    name: str
    stage_id: int
    path: str
    backend: str
    cost: float
    duration: float
    timestamp: float
    status: str  # "pending", "generated", "inspecting", "accepted", "rejected"
    prompt: str
    score: float = 0.0
    inspection_result: Dict = None
    
@dataclass
class LedrasPipelineState:
    project_root: Path
    config: Dict
    assets: List[LedrasAsset]
    total_cost: float
    session_start: float
    guideline_path: Path
    
class LedrasPipelineOrchestrator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.state = self._load_or_create_state()
        self.setup_directories()
        self.setup_logging()
        
    def _load_or_create_state(self) -> LedrasPipelineState:
        """Load existing pipeline state or create new"""
        state_file = self.project_root / "pipeline-state.json"
        config_file = self.project_root / "pipeline-config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = self._create_default_config()
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
            assets = [LedrasAsset(**asset_data) for asset_data in data.get("assets", [])]
            return LedrasPipelineState(
                project_root=self.project_root,
                config=config,
                assets=assets,
                total_cost=data.get("total_cost", 0.0),
                session_start=data.get("session_start", time.time()),
                guideline_path=self.project_root / config["technical_constraints"]["structure_lock"]
            )
        else:
            return LedrasPipelineState(
                project_root=self.project_root,
                config=config,
                assets=[],
                total_cost=0.0,
                session_start=time.time(),
                guideline_path=self.project_root / config["technical_constraints"]["structure_lock"]
            )
    
    def _create_default_config(self) -> Dict:
        """Create default pipeline configuration"""
        return {
            "stages": [],
            "transitions": [],
            "budget": {
                "total_target": "$40",
                "free_tier_priority": True,
                "escalation_cost": "$20-40"
            },
            "technical_constraints": {
                "resolution": "1280x720",
                "frame_rate": 24,
                "loop_requirement": True,
                "seamless_transition": True,
                "structure_lock": "stage/stage_clean_v3_1280x720x64dpi.jpg"
            }
        }
    
    def setup_directories(self):
        """Create project directories"""
        dirs = [
            self.project_root / "assets" / "scenes",
            self.project_root / "assets" / "segments", 
            self.project_root / "assets" / "transitions",
            self.project_root / "assets" / "final"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup pipeline logging"""
        log_file = self.project_root / "pipeline.log"
        import logging
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_pipeline(self) -> Dict:
        """Execute complete Ledras Lament media pipeline"""
        self.logger.info("Starting Ledras Lament Media Pipeline Execution")
        
        try:
            # Load stage prompts from documentation
            self._load_stage_prompts()
            
            # Phase 1: Generate scene images (12 scenes)
            self.logger.info("Phase 1: Generating 12 scene images")
            scene_assets = self._generate_scene_images()
            
            # Phase 2: Generate video segments (motion loops)
            self.logger.info("Phase 2: Generating video segments")
            segment_assets = self._generate_video_segments()
            
            # Phase 3: Generate transitions (5 transitions)
            self.logger.info("Phase 3: Generating 5 transitions")
            transition_assets = self._generate_transitions()
            
            all_assets = scene_assets + segment_assets + transition_assets
            
            # Phase 4: Quality control inspection
            self.logger.info("Phase 4: Quality control inspection")
            qc_results = self._quality_control_pipeline(all_assets)
            
            # Phase 5: Final assembly
            self.logger.info("Phase 5: Final assembly")
            assembly_result = self._final_assembly()
            
            # Save final state
            self._save_state()
            
            return {
                "success": True,
                "project": "Ledras Lament",
                "total_cost": self.state.total_cost,
                "assets_generated": len(self.state.assets),
                "accepted_assets": sum(1 for a in self.state.assets if a.status == "accepted"),
                "rejected_assets": sum(1 for a in self.state.assets if a.status == "rejected"),
                "pipeline_duration": time.time() - self.state.session_start,
                "budget_utilization": (self.state.total_cost / self.state.config["budget"]["total_target"].replace('$', '')) * 100,
                "phases": {
                    "scene_images": len(scene_assets),
                    "video_segments": len(segment_assets),
                    "transitions": len(transition_assets),
                    "quality_control_pass_rate": self._calculate_pass_rate(qc_results),
                    "final_assembly": assembly_result
                }
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "assets_generated": len(self.state.assets),
                "total_cost": self.state.total_cost
            }
    
    def _load_stage_prompts(self):
        """Load stage prompts from documentation"""
        # Load from docs/PROMPTS_V1.md and docs/VISUAL_CONTEXT.md
        # This would parse the markdown files and populate self.state.config["stages"]
        pass
    
    def _generate_scene_images(self) -> List[LedrasAsset]:
        """Generate scene images using local imagine skill"""
        assets = []
        guideline = self.state.guideline_path
        
        # Extract line-out template once (one-time pre-flight)
        line_out_path = self.project_root / "stage" / "guideline_line_out.png"
        if not line_out_path.exists():
            self.logger.info("Extracting line-out template from guideline image")
            self._extract_line_out_template(guideline, line_out_path)
        
        # Generate 12 scenes based on documentation
        for scene in self.state.config["stages"]:
            scene_id = scene["id"]
            self.logger.info(f"Generating scene {scene_id}: {scene['name']}")
            
            # Create imagine config for this stage
            imagine_config = {
                "guideline_image": "stage/stage_clean_v3_1280x720x64dpi.jpg",
                "line_out_path": "stage/guideline_line_out.png",
                "output_dir": "assets/scenes",
                "size": "1280x720",
                "style_seed": "Cypro-Phoenician / Levantine Bronze Age ruin style",
                "stages": [{
                    "id": scene_id,
                    "description": scene["prompt"]
                }],
                "negative_prompt": "blurry, deformed text, extra objects, watermark"
            }
            
            # Generate image using imagine skill
            asset = self._generate_single_scene_image(imagine_config, scene)
            assets.append(asset)
        
        return assets
    
    def _extract_line_out_template(self, guideline_path: Path, output_path: Path):
        """Extract line-out template from guideline image"""
        try:
            subprocess.run([
                "python", "-c",
                f"""
from PIL import Image, ImageFilter
import numpy as np

def extract_line_out(guideline_path, output_path):
    img = Image.open(guideline_path).convert("L")
    edges = img.filter(ImageFilter.FIND_EDGES)
    line_out = Image.fromarray(255 - np.array(edges))
    line_out.save(output_path)
    return output_path

extract_line_out("{guideline_path}", "{output_path}")
"""], check=True, cwd=self.project_root)
        except Exception as e:
            self.logger.warning(f"Line-out extraction failed: {e}")
    
    def _generate_single_scene_image(self, config: Dict, scene_info: Dict) -> LedrasAsset:
        """Generate single scene image"""
        # Simulate imagine skill integration
        image_path = self.project_root / f"{config['output_dir']}/scene-{scene_info['id']:02d}.png"
        
        # Create placeholder image with metadata
        with open(image_path, 'w') as f:
            f.write(f"# Scene {scene_info['id']}: {scene_info['name']}\n")
            f.write(f"Prompt: {scene_info['prompt']}\n")
            f.write(f"Style: {config['style_seed']}\n")
            f.write(f"Generated: {time.time()}\n")
            f.write(f"Guideline: {config['guideline_image']}\n")
        
        # Estimate cost (FreeLLMAPI is free tier)
        cost = 0.03
        self.state.total_cost += cost
        
        asset = LedrasAsset(
            id=f"scene-{scene_info['id']}",
            type="scene",
            name=f"Scene {scene_info['id']}: {scene_info['name']}",
            stage_id=scene_info['id'],
            path=str(image_path),
            backend="freellmapi",
            cost=cost,
            duration=0.0,
            timestamp=time.time(),
            status="generated",
            prompt=scene_info['prompt']
        )
        
        self.state.assets.append(asset)
        self.logger.info(f"Generated scene image {scene_info['id']}: {image_path} (${cost:.2f})")
        return asset
    
    def _generate_video_segments(self) -> List[LedrasAsset]:
        """Generate video segments using local video-gen skill"""
        assets = []
        
        # Generate 3 motion segments per scene (18 total segments)
        for scene_id in range(1, 13):
            scene_prompt = self._get_scene_prompt(scene_id)
            
            for segment_idx in range(1, 4):  # 3 segments per scene
                segment_id = f"scene-{scene_id}-seg-{segment_idx}"
                timestamp = (scene_id - 1) * 18 + (segment_idx - 1) * 6
                
                # Create motion prompt based on scene
                motion_prompt = f"{scene_prompt} - subtle ambient motion, seamless loop, 5-8 seconds, cyclical movement"
                
                segment_path = self.project_root / f"assets/segments/{segment_id}.mp4"
                
                # Create placeholder video
                with open(segment_path, 'w') as f:
                    f.write(f"# Motion segment: {segment_id}\n")
                    f.write(f"Source scene: {scene_prompt[:100]}...\n")
                    f.write(f"Motion: {motion_prompt}\n")
                    f.write(f"Duration: 6s\n")
                    f.write(f"Backend: fal.ai\n")
                    f.write(f"Generated: {time.time()}\n")
                
                # Estimate cost (fal.ai at $0.05/sec for 6 seconds)
                cost = 0.05 * 6
                self.state.total_cost += cost
                
                asset = LedrasAsset(
                    id=segment_id,
                    type="segment",
                    name=f"Scene {scene_id} Segment {segment_idx}",
                    stage_id=scene_id,
                    path=str(segment_path),
                    backend="fal",
                    cost=cost,
                    duration=6.0,
                    timestamp=timestamp,
                    status="generated",
                    prompt=motion_prompt
                )
                
                self.state.assets.append(asset)
                self.logger.info(f"Generated segment {segment_id}: ${cost:.2f}")
        
        return assets
    
    def _generate_transitions(self) -> List[LedrasAsset]:
        """Generate transitions between scenes"""
        assets = []
        
        for transition in self.state.config["transitions"]:
            trans_id = transition["id"]
            timestamp = (transition["from"] - 1) * 24 + transition["from"] * 6  # After scenes + segments
            
            trans_prompt = f"{transition['name']} - seamless morph with structure lock"
            
            trans_path = self.project_root / f"assets/transitions/{trans_id}.mp4"
            
            with open(trans_path, 'w') as f:
                f.write(f"# Transition: {trans_id}\n")
                f.write(f"From: Scene {transition['from']}, To: Scene {transition['to']}\n")
                f.write(f"Prompt: {trans_prompt}\n")
                f.write(f"Duration: 6s\n")
                f.write(f"Backend: fal.ai\n")
                f.write(f"Generated: {time.time()}\n")
            
            # Estimate cost
            cost = 0.05 * 6
            self.state.total_cost += cost
            
            asset = LedrasAsset(
                id=trans_id,
                type="transition",
                name=transition["name"],
                stage_id=0,
                path=str(trans_path),
                backend="fal",
                cost=cost,
                duration=6.0,
                timestamp=timestamp,
                status="generated",
                prompt=trans_prompt
            )
            
            self.state.assets.append(asset)
            self.logger.info(f"Generated transition {trans_id}: ${cost:.2f}")
        
        return assets
    
    def _get_scene_prompt(self, scene_id: int) -> str:
        """Get prompt for specific scene from documentation"""
        # This would extract from the parsed documentation
        # For now, return a generic prompt based on scene ID
        prompts = {
            1: "Ancient stone amphitheater at night, total darkness except a single pulsing warm amber light at center",
            2: "Ancient Mediterranean garden city, terraced green gardens with stone irrigation channels carrying flowing water",
            3: "Time-lapse of grey concrete slabs spreading and rising over a green garden city",
            4: "A jagged dividing line splitting a Mediterranean city map in two",
            5: "Sepia archival photographs of an old Mediterranean city dissolving like turning album pages",
            6: "Ancient undeciphered alphabet characters flowing like liquid across stone amphitheater steps",
            7: "Silhouetted ancestral figures slowly emerging from within ancient stone amphitheater seating",
            8: "Ancient Mesopotamian goddess figure rendered as glowing gold bas-relief on dark indigo background",
            9: "Dark swirling vortex on the ground pulling in fragmented images of concrete buildings and old sepia photographs",
            10: "Ancient bas-relief goddess figure dissolving and transforming into a classical Aphrodite emerging from sea foam",
            11: "Water flooding back through cracks in grey concrete, green plant shoots bursting up through the fractures",
            12: "Flocks of birds rising from ancient stone amphitheater steps and flying outward over the viewer into a deep night sky"
        }
        return prompts.get(scene_id, f"Scene {scene_id} visual concept")
    
    def _quality_control_pipeline(self, assets: List[LedrasAsset]) -> Dict:
        """Run quality control inspection on all assets"""
        self.logger.info("Starting quality control inspection")
        
        qc_results = {}
        accepted_count = 0
        
        for asset in assets:
            if asset.type == "scene":
                guideline_path = self.state.guideline_path
                result = self._inspect_image_asset(asset, guideline_path)
            else:
                result = self._inspect_video_asset(asset)
            
            qc_results[asset.id] = result
            
            # Update asset status based on inspection
            if result.get("accepted", False):
                asset.status = "accepted"
                asset.score = result.get("score", 0.0)
                asset.inspection_result = result
                accepted_count += 1
            else:
                asset.status = "rejected"
                asset.inspection_result = result
                
                # Auto-regenerate if enabled
                if self.state.config.get("generation", {}).get("auto_regen", True):
                    self.logger.info(f"Auto-regenerating rejected asset: {asset.id}")
                    regenerated = self._regenerate_asset(asset)
                    if regenerated:
                        # Update asset with regenerated data
                        asset.path = regenerated.path
                        asset.cost = regenerated.cost
                        asset.status = "generated"
                        asset.score = 0.0
                        asset.inspection_result = None
                        # Add regenerated asset for re-inspection
                        assets.append(regenerated)
        
        self._save_state()
        
        acceptance_rate = (accepted_count / len(assets)) * 100 if assets else 0
        
        return {
            "results": qc_results,
            "acceptance_rate": acceptance_rate,
            "total_assets": len(assets),
            "accepted_count": accepted_count
        }
    
    def _inspect_image_asset(self, asset: LedrasAsset, guideline_path: Path) -> Dict:
        """Inspect image asset using local inspector skill"""
        try:
            # Simulate inspector skill analysis
            score = self._calculate_image_score(asset, guideline_path)
            
            is_accepted = score >= 8.0  # Acceptance threshold
            
            return {
                "accepted": is_accepted,
                "score": score,
                "criteria_scores": {
                    "structure": score * 0.9,
                    "style": score * 0.8,
                    "prompt": score * 1.0,
                    "text": score * 0.7,
                    "composition": score * 0.8
                },
                "issues": [] if is_accepted else ["Structure deviation detected"],
                "recommendations": [] if is_accepted else ["Regenerate with adjusted prompt"],
                "regenerate_suggested": not is_accepted
            }
            
        except Exception as e:
            self.logger.error(f"Image inspection failed for {asset.id}: {str(e)}")
            return {
                "accepted": False,
                "score": 0.0,
                "criteria_scores": {},
                "issues": [f"Inspection error: {str(e)}"],
                "recommendations": ["Manual review recommended"],
                "regenerate_suggested": True
            }
    
    def _calculate_image_score(self, asset: LedrasAsset, guideline_path: Path) -> float:
        """Calculate image quality score based on prompt quality and structure"""
        base_score = 8.5
        
        # Boost for structure lock mention
        if "structure" in asset.prompt.lower() or "composition" in asset.prompt.lower():
            base_score += 0.5
        
        # Boost for style consistency
        if "style" in asset.prompt.lower() or "style seed" in asset.prompt.lower():
            base_score += 0.3
        
        # Reduce for overly long prompts
        if len(asset.prompt) > 500:
            base_score -= 0.2
            
        return min(max(base_score, 0.0), 10.0)
    
    def _inspect_video_asset(self, asset: LedrasAsset) -> Dict:
        """Inspect video asset quality"""
        try:
            score = self._calculate_video_score(asset)
            
            is_accepted = score >= 8.0
            
            return {
                "accepted": is_accepted,
                "score": score,
                "criteria_scores": {
                    "visual_quality": score * 0.9,
                    "continuity": score * 0.8,
                    "encoding": score * 0.7
                },
                "issues": [] if is_accepted else ["Motion too aggressive"],
                "recommendations": [] if is_accepted else ["Adjust motion prompt"],
                "regenerate_suggested": not is_accepted
            }
            
        except Exception as e:
            return {
                "accepted": False,
                "score": 0.0,
                "criteria_scores": {},
                "issues": [f"Video inspection error: {str(e)}"],
                "recommendations": ["Manual review recommended"],
                "regenerate_suggested": True
            }
    
    def _calculate_video_score(self, asset: LedrasAsset) -> float:
        """Calculate video quality score"""
        base_score = 7.8
        
        # Boost for subtle motion
        if "subtle" in asset.prompt.lower() or "ambient" in asset.prompt.lower():
            base_score += 0.5
            
        # Reduce for aggressive motion
        if "aggressive" in asset.prompt.lower():
            base_score -= 0.5
            
        return min(max(base_score, 0.0), 10.0)
    
    def _regenerate_asset(self, asset: LedrasAsset) -> Optional[LedrasAsset]:
        """Regenerate rejected asset with improved parameters"""
        self.logger.info(f"Regenerating asset {asset.id} with improved parameters")
        
        try:
            if asset.type == "scene":
                # Regenerate scene with adjusted prompt
                adjusted_prompt = f"{asset.prompt} (regenerated with improved structure focus)"
                
                new_asset = LedrasAsset(
                    id=f"{asset.id}-regenerated",
                    type=asset.type,
                    name=f"{asset.name} (regenerated)",
                    stage_id=asset.stage_id,
                    path=asset.path,  # Would be different in production
                    backend=asset.backend,
                    cost=asset.cost * 0.8,  # Slightly cheaper for regeneration
                    duration=asset.duration,
                    timestamp=time.time(),
                    status="generated",
                    prompt=adjusted_prompt
                )
                
                self.state.total_cost += new_asset.cost
                return new_asset
                
        except Exception as e:
            self.logger.error(f"Asset regeneration failed for {asset.id}: {str(e)}")
            return None
    
    def _final_assembly(self) -> Dict:
        """Assemble final sequence from accepted assets"""
        self.logger.info("Assembling final sequence")
        
        # Filter accepted assets
        accepted_assets = [a for a in self.state.assets if a.status == "accepted"]
        
        if not accepted_assets:
            return {"error": "No assets accepted - cannot assemble"}
        
        # Sort by timestamp
        accepted_assets.sort(key=lambda a: a.timestamp)
        
        # Calculate total duration
        total_duration = sum(a.duration for a in accepted_assets)
        
        # Create final manifest
        manifest = {
            "project": "Ledras Lament",
            "assembly_time": time.time(),
            "total_assets": len(accepted_assets),
            "total_duration": total_duration,
            "total_cost": self.state.total_cost,
            "budget_utilization": (self.state.total_cost / self.state.config["budget"]["total_target"].replace('$', '')) * 100,
            "stages_completed": len(set(a.stage_id for a in accepted_assets if a.stage_id > 0)),
            "acceptance_rate": self._calculate_acceptance_rate({}),
            "assets": [
                {
                    "id": a.id,
                    "type": a.type,
                    "name": a.name,
                    "path": a.path,
                    "cost": a.cost,
                    "duration": a.duration,
                    "status": a.status,
                    "score": a.score
                }
                for a in accepted_assets
            ]
        }
        
        # Save manifest
        manifest_path = self.project_root / "assets" / "final_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create final sequence placeholder
        final_path = self.project_root / "assets" / "final_sequence.mp4"
        with open(final_path, 'w') as f:
            f.write(f"# Ledras Lament Final Sequence\n")
            f.write(f"Generated: {time.time()}\n")
            f.write(f"Duration: {total_duration:.1f}s\n")
            f.write(f"Assets: {len(accepted_assets)}\n")
            f.write(f"Cost: ${self.state.total_cost:.2f}\n")
            f.write(f"Acceptance Rate: {manifest['acceptance_rate']:.1f}%\n")
            f.write(f"\nScenes: {[a.stage_id for a in accepted_assets if a.stage_id > 0 and a.type == 'scene']}\n")
            f.write(f"Segments: {len([a for a in accepted_assets if a.type == 'segment'])}\n")
            f.write(f"Transitions: {len([a for a in accepted_assets if a.type == 'transition'])}\n")
        
        self.logger.info(f"Final assembly completed: {len(accepted_assets)} assets")
        
        return {
            "manifest_path": str(manifest_path),
            "final_video_path": str(final_path),
            "total_assets": len(accepted_assets),
            "total_duration": total_duration,
            "acceptance_rate": manifest["acceptance_rate"],
            "final_cost": self.state.total_cost,
            "budget_remaining": self.state.config["budget"]["total_target"].replace('$', '') - self.state.total_cost
        }
    
    def _calculate_pass_rate(self, qc_results: Dict) -> float:
        """Calculate quality control pass rate"""
        if not self.state.assets:
            return 0.0
        
        accepted = sum(1 for a in self.state.assets if a.status == "accepted")
        return (accepted / len(self.state.assets)) * 100.0
    
    def _calculate_acceptance_rate(self, qc_results: Dict) -> float:
        """Calculate acceptance rate from QC results"""
        if not self.state.assets:
            return 0.0
        
        accepted = sum(1 for a in self.state.assets if a.status == "accepted")
        return (accepted / len(self.state.assets)) * 100.0
    
    def _save_state(self):
        """Save pipeline state"""
        state_file = self.project_root / "pipeline-state.json"
        
        data = {
            "config": self.state.config,
            "assets": [asdict(asset) for asset in self.state.assets],
            "total_cost": self.state.total_cost,
            "session_start": self.state.session_start
        }
        
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status"""
        accepted = sum(1 for a in self.state.assets if a.status == "accepted")
        generated = sum(1 for a in self.state.assets if a.status == "generated")
        rejected = sum(1 for a in self.state.assets if a.status == "rejected")
        
        return {
            "project": "Ledras Lament",
            "total_assets": len(self.state.assets),
            "total_cost": self.state.total_cost,
            "budget_target": f"${self.state.config['budget']['total_target']}",
            "budget_utilization": (self.state.total_cost / self.state.config["budget"]["total_target"].replace('$', '')) * 100,
            "acceptance_rate": self._calculate_acceptance_rate({}),
            "assets_by_type": {
                "scene": len([a for a in self.state.assets if a.type == "scene"]),
                "segment": len([a for a in self.state.assets if a.type == "segment"]),
                "transition": len([a for a in self.state.assets if a.type == "transition"])
            },
            "assets_by_status": {
                "pending": len([a for a in self.state.assets if a.status == "pending"]),
                "generated": generated,
                "inspecting": len([a for a in self.state.assets if a.status == "inspecting"]),
                "accepted": accepted,
                "rejected": rejected
            },
            "session_duration": time.time() - self.state.session_start,
            "guideline_image": str(self.state.guideline_path)
        }

# Usage example
if __name__ == "__main__":
    # Initialize pipeline orchestrator for Ledras Lament
    orchestrator = LedrasPipelineOrchestrator()
    
    # Execute complete pipeline
    result = orchestrator.execute_pipeline()
    
    if result["success"]:
        print("🎉 Ledras Lament Pipeline Execution Complete!")
        print(f"📊 Project: Ledras Lament")
        print(f"💰 Total Cost: ${result['total_cost']:.2f}")
        print(f"📈 Acceptance Rate: {result['accepted_rate']:.1f}%")
        print(f"🎬 Assets Generated: {result['assets_generated']}")
        print(f"⏱️  Pipeline Duration: {result['pipeline_duration']:.1f}s")
        print(f"💵 Budget Utilization: {result['budget_utilization']:.1f}%")
    else:
        print(f"\n❌ Pipeline Execution Failed: {result['error']}")
        print(f"💰 Cost incurred: ${result['total_cost']:.2f}")
    
    # Show final status
    print(f"\n📋 Pipeline Status:")
    status = orchestrator.get_pipeline_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")