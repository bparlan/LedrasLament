#!/usr/bin/env python3
"""
Test script to verify quality validation setup for Ledras Lament.
"""

from quality_validator import ValidationRegistry, LedrasQualityValidator

def test_validation_registry():
    """Test the validation registry functionality"""
    print("🧪 Testing Validation Registry...")
    
    registry = ValidationRegistry()
    
    # Test token generation
    token = registry.generate_validation_token(4, "loop", "amphitheater with water channels")
    assert token is not None
    assert len(token) > 0
    
    # Test token storage
    assert token in registry.validation_tokens
    assert registry.validation_tokens[token]['scene_id'] == 4
    assert registry.validation_tokens[token]['role'] == "loop"
    
    # Test validation recording
    test_result = {'quality_score': 85, 'passed': True}
    registry.record_validation_result(token, test_result)
    
    # Test report generation
    report = registry.get_validation_report()
    assert report['total_validations'] == 1
    assert report['validation_tokens'] == 1
    
    print("✅ Validation Registry tests passed")

def test_quality_validator():
    """Test the quality validator functionality"""
    print("🧪 Testing LedrasQualityValidator...")
    
    standards_config = {
        'technical': {
            'specular_highlight_strength': 'specular:0.3',
            'pixel_density': 'density:120px/meter',
            'resolution': 'res:1280x720'
        },
        'cultural': {
            'cultural_authenticity': 'team:cypro_phoenician'
        }
    }
    
    # Test valid prompt
    valid_prompt = 'scene_4_loop: Amphitheater... [technical: res:1280x720, density:120px/meter, specular:0.3] [team:cypro_phoenician]'
    result = LedrasQualityValidator.validate_prompt_against_standards(valid_prompt, standards_config)
    
    assert result['passed'] == True
    assert len(result['violations']) == 0
    assert result['compliance_score'] == 100.0
    
    # Test invalid prompt
    invalid_prompt = 'scene_4_loop: Amphitheater... [technical: wrong]'
    result = LedrasQualityValidator.validate_prompt_against_standards(invalid_prompt, standards_config)
    
    assert result['passed'] == False
    assert len(result['violations']) > 0
    assert result['compliance_score'] < 100.0
    
    print("✅ LedrasQualityValidator tests passed")

if __name__ == "__main__":
    print("=" * 60)
    print("QUALITY VALIDATION TESTS")
    print("=" * 60)
    
    test_validation_registry()
    test_quality_validator()
    
    print("\n🎉 All quality validation tests passed!")
    print("Quality validation system is ready for use in the Ledras pipeline.")
