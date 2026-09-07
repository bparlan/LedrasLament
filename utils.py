def get_resolution(config):
    """Convert image_size config to (width, height) tuple.
    
    NOTE: The fal API's `landscape_16_9` enum produces 1024×576, not 1280×720.
    The project uses explicit {"width": 1280, "height": 704} — this function
    is only used for cost estimation, not actual API calls.
    
    Supports:
    - landscape_16_9: (1024, 576)  — actual fal API output
    - landscape_4_3:  (1024, 768)  — actual fal API output
    - explicit: passes through width/height from {"width": N, "height": M}
    Unknown values default to landscape_16_9 and emit a warning.
    """
    size_str = config.get("image_size", "landscape_16_9")
    
    # Handle explicit {width, height} dicts
    if isinstance(size_str, dict):
        return (size_str["width"], size_str["height"])
    
    size_map = {
        "landscape_16_9": (1024, 576),
        "landscape_4_3": (1024, 768),
    }
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