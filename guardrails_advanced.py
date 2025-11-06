"""
Advanced guardrails with multiple security layers:
1. OpenAI Moderation (content safety)
2. Jailbreak Detection (prompt injection/SQL injection)
"""
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class JailbreakDetector:
    """
    Detect prompt injection and jailbreak attempts using 
    qualifire/prompt-injection-jailbreak-sentinel-v2
    """
    
    def __init__(self):
        self.model_name = "qualifire/prompt-injection-jailbreak-sentinel-v2"
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
    
     # Get Hugging Face token from environment
        self.hf_token = os.getenv('HF_TOKEN')
        if not self.hf_token:
            print("⚠️ WARNING: HUGGINGFACE_TOKEN not set in .env")
            print("   Get token from: https://huggingface.co/settings/tokens")
            


    def _load_model(self):
        """Lazy load the jailbreak detection model with authentication"""
        if not self.model_loaded:
            print(f"📦 Loading jailbreak detection model from {self.model_name}...")
            
            if not self.hf_token:
                raise ValueError(
                    "HUGGINGFACE_TOKEN not found in environment. "
                    "Get token from https://huggingface.co/settings/tokens "
                    "and add to .env file"
                )
            
            try:
                # Load with authentication token
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    token=self.hf_token  # ✅ Add authentication
                )
                
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    token=self.hf_token  # ✅ Add authentication
                ).to(self.device)
                
                self.model.eval()
                self.model_loaded = True
                print(f"✅ Jailbreak detector loaded on {self.device}")
                
            except Exception as e:
                error_msg = str(e)
                
                if "gated repo" in error_msg or "restricted" in error_msg:
                    print(f"❌ Model access denied!")
                    print(f"   1. Go to: https://huggingface.co/{self.model_name}")
                    print(f"   2. Click 'Request access' and wait for approval")
                    print(f"   3. Add HUGGINGFACE_TOKEN to .env")
                    raise ValueError(
                        f"Access to model {self.model_name} is restricted. "
                        f"Request access at https://huggingface.co/{self.model_name}"
                    )
                else:
                    print(f"❌ Failed to load jailbreak detector: {e}")
                    raise
    
    def detect(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """
        Detect if text contains jailbreak/injection attempts
        
        Args:
            text: Input text to analyze
            threshold: Detection threshold (0.0-1.0, higher = stricter)
            
        Returns:
            dict with 'is_jailbreak' (bool) and 'confidence' (float)
        """
        try:
            # Load model if needed
            if not self.model_loaded:
                self._load_model()
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
            
            # Get jailbreak probability
            # Assuming label 1 = jailbreak/injection detected
            jailbreak_prob = probabilities[0][1].item()
            
            is_jailbreak = jailbreak_prob > threshold
            
            return {
                "is_jailbreak": is_jailbreak,
                "confidence": jailbreak_prob,
                "threshold": threshold,
                "safe_prob": probabilities[0][0].item()
            }
        
        except Exception as e:
            print(f"⚠️ Jailbreak detection failed: {e}")
            # Fail open (allow) rather than blocking legitimate queries
            return {
                "is_jailbreak": False,
                "confidence": 0.0,
                "error": str(e)
            }

class MultiLayerGuardrails:
    """
    Multi-layer security with:
    1. OpenAI Moderation (harmful content)
    2. Jailbreak Detection (prompt injection/SQL injection)
    """
    
    def __init__(self):
        self.jailbreak_detector = JailbreakDetector()
        
        # Import OpenAI here to avoid issues
        from openai import OpenAI
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def run_openai_moderation(self, text: str) -> Dict[str, Any]:
        """Run OpenAI content moderation"""
        try:
            response = self.openai_client.moderations.create(input=text)
            result = response.results[0]
            
            if result.flagged:
                flagged_cats = [
                    cat for cat, val in result.categories.model_dump().items() 
                    if val
                ]
                return {
                    "blocked": True,
                    "reason": "harmful_content",
                    "flagged_categories": flagged_cats,
                    "provider": "OpenAI Moderation"
                }
            
            return {
                "blocked": False,
                "reason": None,
                "provider": "OpenAI Moderation"
            }
        
        except Exception as e:
            print(f"⚠️ OpenAI moderation failed: {e}")
            return {"blocked": False, "error": str(e)}
    
    def run_jailbreak_detection(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Run jailbreak/injection detection"""
        try:
            result = self.jailbreak_detector.detect(text, threshold)
            
            if result.get("is_jailbreak"):
                return {
                    "blocked": True,
                    "reason": "jailbreak_attempt",
                    "confidence": result.get("confidence"),
                    "threshold": result.get("threshold"),
                    "provider": "Jailbreak Sentinel v2"
                }
            
            return {
                "blocked": False,
                "reason": None,
                "confidence": result.get("confidence"),
                "provider": "Jailbreak Sentinel v2"
            }
        
        except Exception as e:
            print(f"⚠️ Jailbreak detection failed: {e}")
            return {"blocked": False, "error": str(e)}
    
    def check_all(self, text: str, jailbreak_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Run all security checks
        
        Returns:
            dict with 'blocked' (bool), 'reason' (str), and 'details' (dict)
        """
        print("🛡️ Running multi-layer security checks...")
        
        results = {
            "blocked": False,
            "reason": None,
            "checks": {}
        }
        
        # Check 1: OpenAI Moderation (harmful content)
        print("   1/2 Checking harmful content...")
        openai_result = self.run_openai_moderation(text)
        results["checks"]["openai_moderation"] = openai_result
        
        if openai_result.get("blocked"):
            results["blocked"] = True
            results["reason"] = "harmful_content"
            results["details"] = openai_result
            print(f"   ❌ Blocked: Harmful content detected")
            return results
        
        print("   ✅ Passed: No harmful content")
        
        # Check 2: Jailbreak Detection (injection attempts)
        print("   2/2 Checking for injection/jailbreak...")
        jailbreak_result = self.run_jailbreak_detection(text, jailbreak_threshold)
        results["checks"]["jailbreak_detection"] = jailbreak_result
        
        if jailbreak_result.get("blocked"):
            results["blocked"] = True
            results["reason"] = "jailbreak_attempt"
            results["details"] = jailbreak_result
            confidence = jailbreak_result.get("confidence", 0)
            print(f"   ❌ Blocked: Jailbreak detected (confidence: {confidence:.2%})")
            return results
        
        confidence = jailbreak_result.get("confidence", 0)
        print(f"   ✅ Passed: No jailbreak detected (confidence: {confidence:.2%})")
        
        # All checks passed
        print("✅ All security checks passed!")
        results["safe_text"] = text
        return results


# Singleton instance
_guardrails = None

def get_guardrails() -> MultiLayerGuardrails:
    """Get or create guardrails instance"""
    global _guardrails
    if _guardrails is None:
        _guardrails = MultiLayerGuardrails()
    return _guardrails


def run_security_checks(text: str, jailbreak_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Convenience function to run all security checks
    
    Args:
        text: Input text to check
        jailbreak_threshold: Sensitivity (0.0-1.0, higher = stricter)
                            0.5 = balanced
                            0.7 = recommended (default)
                            0.9 = very strict
    
    Returns:
        dict with 'blocked' (bool) and details
    """
    guardrails = get_guardrails()
    return guardrails.check_all(text, jailbreak_threshold)
