"""
Quality validation utilities for Ledras Lament scene generation.

Provides validation, token management, and quality assurance for the scene generation pipeline.
"""

import json
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
class ValidationRegistry:
    """Manages validation tokens and quality metrics for scene generation"""
    
    def __init__(self):
        self.validation_tokens = {}
        self.quality_metrics = {}
        self.validation_history = []
    
    def generate_validation_token(self, scene_id: int, role: str, scene_content: str) -> str:
        """Generate deterministic validation token for scene generation"""
        token_data = f"{scene_id}-{role}-{scene_content}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        token = base64.urlsafe_b64encode(token_hash[:24].encode()).decode()
        
        self.validation_tokens[token] = {
            'scene_id': scene_id,
            'role': role,
            'content_hash': token_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        return token
    
    def record_validation_result(self, token: str, validation_result: Dict[str, Any]):
        """Record validation results against a token"""
        if token in self.validation_tokens:
            self.validation_history.append({
                'token': token,
                'validation_result': validation_result,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        return {
            'total_validations': len(self.validation_history),
            'validation_tokens': len(self.validation_tokens),
            'quality_metrics': self.quality_metrics,
            'validation_history': self.validation_history[-10:]  # Last 10 entries
        }
class LedrasQualityValidator:
    """Quality validation utility class for Ledras scene generation"""
    
    @staticmethod
    def validate_prompt_against_standards(prompt: str, standards_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate prompt against configurable standards"""
        validation_results = {
            'passed': True,
            'violations': [],
            'compliance_score': 100.0,
            'technical_compliance': {},
            'narrative_compliance': {}
        }
        
        # Technical standards validation
        technical_standards = standards_config.get('technical', {})
        for standard, expected_pattern in technical_standards.items():
            if expected_pattern and expected_pattern not in prompt:
                validation_results['violations'].append(f'Missing {standard} specification')
                validation_results['compliance_score'] -= 25
        
        # Cultural authenticity validation
        cultural_standards = standards_config.get('cultural', {})
        for standard, expected_pattern in cultural_standards.items():
            if expected_pattern and expected_pattern not in prompt:
                validation_results['violations'].append(f'Missing {standard} reference')
                validation_results['compliance_score'] -= 25
        
        validation_results['passed'] = len(validation_results['violations']) == 0
        
        return validation_results

# Export the validator for use in other scripts
__all__ = ['ValidationRegistry', 'LedrasQualityValidator']
