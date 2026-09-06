#!/usr/bin/env python3
"""
FAL API Key Usage Script

This script demonstrates proper usage of FAL_API_KEY from environment variables
without reading .env files directly. The environment should have FAL_API_KEY set
by the system (e.g., through shell export, CI/CD pipeline, or other means).

The environment is expected to handle API key security - never hardcode keys in code.
"""

import os
import sys
from typing import Optional
class FALAPIKeyManager:
    """
    Manages FAL API key usage with proper error handling and validation.
    
    This class provides a clean interface for accessing the FAL_API_KEY
    from environment variables without directly reading .env files.
    """
    
    def __init__(self, key_name: str = "FAL_API_KEY"):
        self.key_name = key_name
        self._api_key: Optional[str] = None
        
    def get_api_key(self) -> Optional[str]:
        """
        Retrieve the FAL API key from environment variables.
        
        Returns:
            The API key string if available, None otherwise.
            
        Note:
            This method reads from os.environ, not from .env files.
            The environment should already have the key available.
        """
        if self._api_key is None:
            self._api_key = os.environ.get(self.key_name)
        return self._api_key
    
    def validate_key(self) -> bool:
        """
        Validate that the API key is present and has minimum required format.
        
        Returns:
            True if key is present and looks valid, False otherwise.
        """
        key = self.get_api_key()
        if not key:
            return False
            
        # Basic validation - key should be a non-empty string
        return isinstance(key, str) and len(key.strip()) > 0
    
    def get_fallback_key(self, fallback_key_name: str = "FAL_KEY") -> Optional[str]:
        """
        Get API key from fallback environment variable if primary key is not set.
        
        Args:
            fallback_key_name: Name of the fallback environment variable.
            
        Returns:
            API key from fallback if available, None otherwise.
        """
        if self.validate_key():
            return self.get_api_key()
            
        return os.environ.get(fallback_key_name)
def demonstrate_api_key_usage():
    """
    Demonstrate proper usage of FAL_API_KEY in a realistic scenario.
    
    This example shows how to use the FAL API key for operations that
    require authentication, following security best practices.
    """
    print("🔑 FAL API Key Usage Demo")
    print("=" * 50)
    
    # Initialize the key manager
    key_manager = FALAPIKeyManager()
    
    # Check if key is available
    if not key_manager.validate_key():
        print("❌ FAL_API_KEY is not set in environment variables.")
        print("   The environment should provide this key.")
        print("   This is not an error - it means the environment needs to be configured.")
        print("   Do not hardcode API keys in your code.")
        
        # Try fallback key
        fallback_key = key_manager.get_fallback_key()
        if fallback_key:
            print(f"✅ Found fallback key: {fallback_key[:8]}...")
        else:
            print("⚠️  No fallback key found either.")
            
        return
    
    # Key is available
    api_key = key_manager.get_api_key()
    print(f"✅ FAL_API_KEY found: {api_key[:8]}...")
    
    # Demonstrate secure usage
    print("\n🔧 Using API key for authentication:")
    print(f"   Key length: {len(api_key)} characters")
    print(f"   Key starts with: {api_key[:8]}")
    print(f"   Key ends with: ...{api_key[-4:]}")
    
    # Example of how you might use this with a FAL API client
    print("\n📡 Example usage with FAL client:")
    print("""
# Example of how to use the API key with FAL client:

import os
from fal_client import Client

# Get the API key from environment (not from .env file)
fal_api_key = os.environ.get('FAL_API_KEY')
if not fal_api_key:
    raise ValueError("FAL_API_KEY must be set in environment")

# Use the key to create a client
client = Client(fal_api_key)

# Make API calls...
""")
    
    print("✅ API key usage demonstration complete")
def test_environment_key_availability():
    """
    Test and report on the availability of FAL_API_KEY in the current environment.
    
    This function provides a comprehensive report of API key status without
    attempting to read from .env files.
    """
    print("🔍 Testing FAL API Key Environment Availability")
    print("=" * 60)
    
    # Check primary key
    primary_key = os.environ.get("FAL_API_KEY")
    
    # Check fallback key  
    fallback_key = os.environ.get("FAL_KEY")
    
    print(f"📊 Environment Analysis:")
    print(f"   FAL_API_KEY: {'✅ SET' if primary_key else '❌ NOT SET'}")
    print(f"   FAL_KEY: {'✅ SET' if fallback_key else '❌ NOT SET'}")
    
    if primary_key:
        print(f"   Primary key length: {len(primary_key)} characters")
        print(f"   Primary key preview: {primary_key[:12]}...")
    
    if fallback_key:
        print(f"   Fallback key length: {len(fallback_key)} characters")
        print(f"   Fallback key preview: {fallback_key[:12]}...")
    
    if not primary_key and not fallback_key:
        print("\n⚠️  WARNING: No FAL API keys found in environment")
        print("   This is expected if the environment is not configured for API usage.")
        print("   The environment should provide API keys through secure means.")
        return False
    
    print("\n✅ Environment has API key(s) available")
    return True
def secure_api_key_workflow():
    """
    Example of a complete workflow for using API keys securely.
    
    This shows the proper pattern for handling API keys in production code.
    """
    print("🔐 Secure API Key Workflow Example")
    print("=" * 40)
    
    # Step 1: Import environment handling
    print("Step 1: Import environment handling modules")
    print("   import os")
    print("   # Never read from .env files in production code")
    
    # Step 2: Check for required keys
    print("\nStep 2: Check for required environment variables")
    if not os.environ.get("FAL_API_KEY"):
        print("   ❌ FAL_API_KEY not found in environment")
        print("   ⏳ Environment should provide this key before runtime")
        print("   💡 This is normal - the environment manages secret management")
        return
    
    print("   ✅ FAL_API_KEY found in environment")
    
    # Step 3: Use the key
    print("\nStep 3: Use the key securely")
    api_key = os.environ["FAL_API_KEY"]
    print(f"   ✅ API key available (length: {len(api_key)})")
    
    # Step 4: Create client or make API calls
    print("\nStep 4: Initialize client and make API calls")
    print("   # Use the key to initialize your API client")
    print("   # Make secure API calls without storing the key in variables")
    
    print("\n✅ Secure workflow complete")
if __name__ == "__main__":
    print("🚀 FAL API Key Usage Manager")
    print("=" * 30)
    
    # Run all demonstrations
    demonstrate_api_key_usage()
    
    print("\n" + "=" * 70)
    
    test_environment_key_availability()
    
    print("\n" + "=" * 70)
    
    secure_api_key_workflow()
    
    print("\n" + "=" * 70)
    print("✨ FAL API Key Usage Complete")
    print("\n📝 Key Takeaways:")
    print("   • Never read API keys from .env files in production code")
    print("   • Environment should provide API keys through secure means")
    print("   • Always validate key presence before use")
    print("   • Use fallback keys only when necessary")
    print("   • Treat API keys as secrets - don't expose them in logs")
    
    # Exit with code 0 since this is just a demonstration
    # and not actually making API calls
    sys.exit(0)
