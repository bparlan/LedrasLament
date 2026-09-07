def get_resolution(config):
    """Convert image_size config to (width, height) tuple.
    
    Supports:
    - landscape_16_9: (1280, 720)
    - landscape_4_3: (1280, 960)  
    - portrait_9_16: (REMOVED) - landscape-only project
    Unknown values default to landscape_16_9 and emit a warning.
    """
    size_map = {
        "landscape_16_9": (1280, 720),
        "landscape_4_3": (1280, 960),
        # portrait_9_16 removed - project uses landscape-only
    }
    size_str = config.get("image_size", "landscape_16_9")
    if size_str not in size_map:
        print(f"⚠️  Unknown image_size '{size_str}', using default landscape_16_9")
        size_str = "landscape_16_9"
    return size_map[size_str]


def estimate_cost(width, height, model):
    """Estimate Fal.ai cost based on resolution and model.
    
    For flux-control-lora-canny model uses 0.005 per megapixel,
    otherwise 0.01 per megapixel.
    """
    rate = 0.005 if model == "fal-ai/flux-control-lora-canny" else 0.01
    return (width * height) / 1_000_000 * rate