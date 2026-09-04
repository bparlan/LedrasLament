---
name: video-gen
version: 1.0.0
description: Token-efficient video generation using fal.ai (primary) + Runway (secondary) with editorial assembly orchestration
---

# Video Generation Skill (Agentic Media Pipeline)

**Token-efficient video generation with editorial control**

## Overview

This skill generates short video segments (5-8 seconds) using fal.ai as the primary backend, with Runway as fallback. It orchestrates the editorial assembly pipeline for the final 20-30 second sequences, following the artproject-chatgpt.md guidance for segment-based generation over expensive 30-second direct generation.

## How It Works

1. Parse video generation request into segments (motion/transition/editorial)
2. Use fal.ai API for each 5-8 second segment
3. If fal.ai fails or rate-limited, fall back to Runway
4. Orchestrate segments into final sequence
5. Store segments for later assembly or immediate editing

## Technical Configuration

### Primary Backend: fal.ai

- **Pricing**: $0.05-0.07/sec (Wan 2.5, Kling 2.5 Turbo Pro)
- **API**: Proper programmatic API (not web UI)
- **Models**: Wan 2.5, Kling 2.5 Turbo Pro, Ovi, many image models
- **Endpoint**: fal.ai API (REST)

### Secondary Backend: Runway

- **Pricing**: $0.05/sec (Gen-4 Turbo)
- **API**: Explicitly designed for programmatic generation
- **Models**: Gen-4, Seedream, Gemini, GPT Image, Grok Imagine

## Segment-Based Strategy (FROM artproject-chatgpt.md)

Generate short segments instead of expensive 30-second videos:

```
5–8 sec motion A ↓
5–8 sec motion B ↓  
5–8 sec motion C ↓
motion/transition ↓
20–30 sec final sequence
```

Example segment structure:

```
SCENE 04
├──→ 6 sec motion A
├──→ 6 sec motion B
├──→ 6 sec motion C
           │
           ▼
     editorial assembly
           │
           ▼
        20 sec
```

## Code Implementation

```python
import requests
import base64
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

class VideoGenerator:
    def __init__(self, config: Dict):
        self.fal_api_key = config.get("fal_api_key")
        self.runway_api_key = config.get("runway_api_key")
        self.primary_backend = "fal"
        self.segment_duration = 6  # seconds
        self.max_retries = 3

    def generate_segment(self, prompt: str, style_seed: str, 
                        negative_prompt: str, model: str = None) -> Dict:
        """Generate a single 5-8 second video segment"""
        segment_prompt = f"{prompt} {style_seed}"
        
        for attempt in range(self.max_retries):
            try:
                # Try primary backend (fal.ai)
                result = self._generate_with_fal(segment_prompt, negative_prompt, model)
                if result["success"]:
                    return {
                        "success": True,
                        "segment": result,
                        "backend": "fal",
                        "attempt": attempt + 1
                    }
                
                # If fal fails, try fallback to Runway
                if attempt == self.max_retries - 1:
                    result = self._generate_with_runway(segment_prompt, negative_prompt)
                    if result["success"]:
                        return {
                            "success": True,
                            "segment": result,
                            "backend": "runway",
                            "attempt": attempt + 1
                        }
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {"success": False, "error": str(e)}
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return {"success": False, "error": "Max retries exceeded"}

    def _generate_with_fal(self, prompt: str, negative_prompt: str, model: str = None) -> Dict:
        """Generate video using fal.ai API"""
        headers = {
            "Authorization": f"Bearer {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use appropriate model based on duration
        if model is None:
            model = "wan-2.5"  # Most cost-effective for 6-second segments
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "duration": self.segment_duration,
            "model": model,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "seed": int(time.time()) % 10000  # Ensure variety
        }
        
        response = requests.post(
            "https://api.fal.ai/v1/generate/video",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "video_path": result.get("video_path"),
                "duration": result.get("duration"),
                "model": result.get("model"),
                "seed": result.get("seed"),
                "cost": self._calculate_fal_cost(self.segment_duration, model)
            }
        else:
            return {"success": False, "error": f"fal.ai API error: {response.text}"}

    def _generate_with_runway(self, prompt: str, negative_prompt: str) -> Dict:
        """Generate video using Runway API as fallback"""
        headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "duration": self.segment_duration,
            "model": "gen-4-turbo",
            "num_inference_steps": 15
        }
        
        response = requests.post(
            "https://api.runwayml.com/v1/generate/video",
            headers=headers,
            json=payload,
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "video_path": result.get("video_path"),
                "duration": result.get("duration"),
                "model": result.get("model"),
                "seed": result.get("seed"),
                "cost": self._calculate_runway_cost(self.segment_duration)
            }
        else:
            return {"success": False, "error": f"Runway API error: {response.text}"}

    def _calculate_fal_cost(self, duration: int, model: str) -> float:
        """Calculate cost for fal.ai generation"""
        rates = {
            "wan-2.5": 0.05,
            "kling-2.5-turbo-pro": 0.07
        }
        return duration * rates.get(model, 0.05)

    def _calculate_runway_cost(self, duration: int) -> float:
        """Calculate cost for Runway generation"""
        return duration * 0.05

    def orchestrate_segments(self, segments: List[Dict], editorial_config: Dict) -> Dict:
        """Orchestrate multiple segments into final sequence"""
        # Sort segments by timestamp
        segments.sort(key=lambda x: x.get("timestamp", 0))
        
        # Check for conflicts and overlaps
        conflicts = self._check_segment_conflicts(segments)
        
        # Generate transitions between segments
        transitions = []
        for i in range(len(segments) - 1):
            transition = self._generate_transition(
                segments[i], segments[i + 1], editorial_config
            )
            transitions.append(transition)
        
        final_sequence = {
            "segments": segments,
            "transitions": transitions,
            "total_duration": sum(s.get("duration", self.segment_duration) for s in segments),
            "total_cost": sum(s.get("cost", 0) for s in segments),
            "conflicts": conflicts
        }
        
        return final_sequence

    def _check_segment_conflicts(self, segments: List[Dict]) -> List[Dict]:
        """Check for conflicting segments (same time, incompatible content)"""
        conflicts = []
        timestamps = {}
        
        for segment in segments:
            ts = segment.get("timestamp")
            if ts in timestamps:
                conflict = {
                    "time": ts,
                    "segments": [timestamps[ts], segment],
                    "type": "timestamp_overlap"
                }
                conflicts.append(conflict)
            else:
                timestamps[ts] = segment
        
        return conflicts

    def _generate_transition(self, prev_segment: Dict, next_segment: Dict, 
                           config: Dict) -> Dict:
        """Generate transition between two segments"""
        transition_prompt = f"transition from {prev_segment.get('prompt', '')} " \
                           f"to {next_segment.get('prompt', '')}"
        
        return self.generate_segment(
            transition_prompt,
            config.get("style_seed", ""),
            config.get("negative_prompt", "blurry, deformed"),
            "fal"
        )

# Usage example
if __name__ == "__main__":
    config = {
        "fal_api_key": "your-fal-api-key",
        "runway_api_key": "your-runway-api-key",
        "segment_duration": 6,
        "style_seed": "soft blue rim light, weathered limestone",
        "negative_prompt": "blurry, deformed text, extra objects, watermark"
    }
    
    generator = VideoGenerator(config)
    
    # Generate segments for a scene
    scene_segments = []
    scene_config = {
        "prompt": "glowing central crystal, soft blue rim light, subtle particle drift",
        "timestamp": 0,
        "style_seed": config["style_seed"],
        "negative_prompt": config["negative_prompt"]
    }
    
    for i in range(3):  # 3 segments per scene
        segment = generator.generate_segment(
            scene_config["prompt"],
            scene_config["style_seed"],
            scene_config["negative_prompt"]
        )
        if segment["success"]:
            scene_segments.append({
                "timestamp": i * generator.segment_duration,
                "segment": segment["segment"],
                "backend": segment["backend"]
            })
    
    # Orchestrate all segments
    final_sequence = generator.orchestrate_segments(scene_segments, config)
    print(f"Generated {len(scene_segments)} segments")
    print(f"Total cost: ${final_sequence['total_cost']:.2f}")
```