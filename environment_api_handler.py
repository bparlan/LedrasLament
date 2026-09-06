#!/usr/bin/env python3
"""
Ledras Lament - Environment-based API Key Handler

This script demonstrates proper usage of FAL_API_KEY from the environment
without reading .env files directly. The environment should handle API key
security - this code assumes the environment has already provided FAL_API_KEY.

Best Practice: The environment manages secrets, not the code.
"""

import os
import sys
from typing import Optional
def get_fal_api_key() -> Optional[str]:
    """
    Retrieve FAL_API_KEY from environment variables.
    
    Returns:
        The API key string if available in environment, None otherwise.
        
    Note:
        This reads from os.environ, not from .env files.
        The environment should provide FAL_API_KEY through secure means
        (export, CI/CD, Docker secrets, etc.).
    """
    return os.environ.get("FAL_API_KEY")
def validate_api_key_format(api_key: str) -> bool:
    """
    Basic validation of API key format.
    
    Args:
        api_key: The API key to validate.
        
    Returns:
        True if key appears valid, False otherwise.
    """
    if not api_key:
        return False
    
    # Basic validation - should be a non-empty string
    # FAL keys typically look like UUID:suffix format
    return isinstance(api_key, str) and len(api_key.strip()) > 10
class FALAPIClient:
    """
    Example FAL API client that uses environment-based authentication.
    
    This demonstrates how to properly use FAL_API_KEY from the environment
    without hardcoding secrets in the code.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client with API key from environment or parameter.
        
        Args:
            api_key: Optional API key. If not provided, will try to get
                    from environment variable FAL_API_KEY.
        """
        self.api_key = api_key or get_fal_api_key()
        
        if not self.api_key:
            raise ValueError("FAL_API_KEY not found. Please ensure it's set in the environment.")
            
        if not validate_api_key_format(self.api_key):
            raise ValueError("FAL_API_KEY format appears invalid.")
            
        print(f"✅ FAL API Client initialized successfully")
        print(f"   Key prefix: {self.api_key[:8]}...")
    
    def generate_content(self, prompt: str, **kwargs) -> dict:
        """
        Example method to generate content using FAL API.
        
        Args:
            prompt: The prompt to generate content from.
            **kwargs: Additional parameters for the API call.
            
        Returns:
            Dictionary with generation results.
        """
        print(f"🤖 Generating content with prompt: {prompt[:50]}...")
        
        # In a real implementation, this would make an actual API call
        # For demonstration, we return a mock response
        return {
            "status": "success",
            "prompt": prompt,
            "generated_content": f"Generated response to: {prompt}",
            "usage": {"prompt_tokens": 10, "completion_tokens": 25},
            "model": "fal-ai/flux-control-lora-canny"
        }
def demonstrate_environment_based_usage():
    """
    Demonstrate the complete workflow of using FAL_API_KEY from environment.
    """
    print("🔑 Ledras Lament - Environment-based API Key Usage")
    print("=" * 60)
    
    # Step 1: Check environment
    print("\n📋 Step 1: Check Environment")
    api_key = get_fal_api_key()
    
    if not api_key:
        print("❌ FAL_API_KEY not found in environment")
        print("   This script expects FAL_API_KEY to be set by the environment.")
        print("   Do not read .env files - let the environment handle this.")
        return
    
    print(f"✅ FAL_API_KEY found in environment")
    print(f"   Key length: {len(api_key)} characters")
    print(f"   Key format: {'✅ Valid' if validate_api_key_format(api_key) else '❌ Invalid'}")
    
    # Step 2: Initialize client
    print("\n📋 Step 2: Initialize API Client")
    try:
        client = FALAPIClient()
    except ValueError as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    # Step 3: Use the client
    print("\n📋 Step 3: Use the Client")
    test_prompts = [
        "Generate an ancient Mediterranean scene with Cypriot-Phoenician architecture",
        "Create a scene with traditional Ledras Lament aesthetic",
        "Generate a historical Mediterranean landscape"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n   Example {i}:")
        result = client.generate_content(prompt)
        print(f"     Status: {result['status']}")
        print(f"     Model: {result['model']}")
    
    print("\n✅ Environment-based usage complete")
def show_best_practices():
    """
    Display best practices for API key management.
    """
    print("\n🛡️  Best Practices for API Key Management")
    print("=" * 60)
    
    print("\n✅ DO:")
    print("   • Get API keys from environment variables (os.environ.get())")
    print("   • Use fallback keys when appropriate (FAL_KEY)")
    print("   • Validate key format before use")
    print("   • Never hardcode API keys in source code")
    print("   • Let the environment handle secret management")
    print("   • Use proper error handling when keys are missing")
    
    print("\n❌ DON'T:")
    print("   • Don't read .env files in production code")
    print("   • Don't commit API keys to version control")
    print("   • Don't expose API keys in logs or print statements")
    print("   • Don't use default/hardcoded keys in production")
    print("   • Don't ignore missing API keys (always validate)")
    
    print("\n📋 Environment Setup:")
    print("   # Set in shell environment:")
    print("   export FAL_API_KEY=your-api-key-here")
    print("   ")
    print("   # Or in Docker:")
    print("   docker run -e FAL_API_KEY=your-key image")
    print("   ")
    print("   # Or in CI/CD pipeline")
    print("   # Never in source code!")
def test_environment_integration():
    """
    Test integration with the current environment.
    """
    print("\n🔍 Environment Integration Test")
    print("=" * 60)
    
    # Test 1: Check if FAL_API_KEY is available
    api_key = get_fal_api_key()
    
    if not api_key:
        print("❌ FAILED: FAL_API_KEY not found in environment")
        print("   This environment is not configured for API usage.")
        return False
    
    print("✅ PASSED: FAL_API_KEY found in environment")
    
    # Test 2: Validate format
    if not validate_api_key_format(api_key):
        print("❌ FAILED: FAL_API_KEY format appears invalid")
        return False
    
    print("✅ PASSED: FAL_API_KEY format is valid")
    
    # Test 3: Show key info
    print(f"   Key preview: {api_key[:12]}...")
    print(f"   Key suffix: ...{api_key[-8:]}")
    
    return True
if __name__ == "__main__":
    print("🚀 Ledras Lament - Environment-based API Key Handler")
    print("=" * 70)
    
    # Run tests
    test_passed = test_environment_integration()
    
    if test_passed:
        demonstrate_environment_based_usage()
    else:
        print("\n⚠️  Environment not configured for API usage")
        print("   This is normal - the environment should provide API keys.")
    
    show_best_practices()
    
    print("\n" + "=" * 70)
    print("✨ Environment-based API key handling complete")
    
    # Exit code indicates environment status
    sys.exit(0 if test_passed else 1)
