
from typing import Dict, Any
from dataclasses import dataclass
import logging
from src.models.schemas import MatchResponse
from src.salesforce.salesforce import SalesForceService
from src.ai.io import LRUCache
from src.exceptions import ValidationError, ProcessingError, AIServiceError, CacheError
logger = logging.getLogger(__name__)

@dataclass
class MockResponse:
    # Response fields (matching MatchResponse schema)
    asset_classification: str = ""
    manufacturer: str = ""
    product_line: str = ""
    explanation: str = ""
    model_number: str = ""


@dataclass
class AssetProcessingResult(MockResponse):
    ai_state: dict = None

    def __post_init__(self):
        if self.ai_state is None:
            self.ai_state = {}

    def update_ai_state(self, ai_state: Dict[str, Any]) -> None:
        self.ai_state = ai_state

    def get_ai_state(self) -> Dict[str, Any]:
        return self.ai_state

    def clear_ai_state(self) -> None:
        self.ai_state = {}

    def insert_state(self, field_name: str, status: str, reason: str = "", value: str = '') -> None:
        """Insert validation state for a field.
        
        Args:
            field_name: Name of the field being validated
            status: Validation status ("ok", "invalid", "generic", "missing")
            reason: Description of the validation result
            value: The actual value being tracked/extracted
        """
        self.ai_state[field_name] = {
            "status": status,
            "reason": reason,
            "value": value
        }

    def get_failed_validations(self) -> Dict[str, Dict[str, str]]:
        """Return all fields that failed validation (status != 'ok')"""
        return {
            field: state for field, state in self.ai_state.items() 
            if state.get("status") != "ok"
        }

    def is_valid(self) -> bool:
        """Check if all tracked fields passed validation"""
        return len(self.get_failed_validations()) == 0

    def generate_explanation(self) -> str:
        """Generate explanation based on validation results and product line detection.
        
        Returns:
            String explanation of the processing results
        """
        # Get values from ai_state where they're stored by validation functions
        manufacturer = self.ai_state.get("manufacturer", {}).get("value", "")
        model_number = self.ai_state.get("model_number", {}).get("value", "")
        product_line = self.ai_state.get("product_line", {}).get("value", "")
        
        # Check if validation passed and product line found
        if self.is_valid() and product_line:
            # Generate manufacturer-specific "match found" explanation
            explanations = {
                "cummins": f"The model number '{model_number}' corresponds to the '{product_line}' product line, a diesel generator set manufactured by Cummins. The '{product_line}' model is part of Cummins' 60Hz diesel generator offerings with robust performance specifications. This information is sourced from Cummins' official product documentation.",
                "caterpillar": f"The model number '{model_number}' identifies a Caterpillar '{product_line}' series generator. This model is part of Caterpillar's industrial generator lineup known for reliability and performance in demanding applications.",
                "kohler": f"The model number '{model_number}' represents a Kohler '{product_line}' series generator, part of their commercial and industrial power generation portfolio."
            }
            
            manufacturer_lower = manufacturer.lower()
            explanation = explanations.get(
                manufacturer_lower,
                f"The model number '{model_number}' has been matched to the '{product_line}' product line based on manufacturer specifications and industry standard naming conventions."
            )
        else:
            # Generate "needs more specific data" explanation
            failed_validations = self.get_failed_validations()
            if failed_validations:
                failed_fields = list(failed_validations.keys())
                explanation = f"The data needs to be more specific for accurate matching. Issues found with: {', '.join(failed_fields)}. Please provide more detailed information."
            else:
                explanation = f"Valid data provided but no specific product line match could be determined for model '{model_number}'."
        
        # Store explanation in ai_state
        self.ai_state["explanation"] = {
            "status": "generated",
            "reason": "Explanation generated based on processing results",
            "value": explanation
        }
        
        return explanation

    def update_with_enriched_data(self, enriched_data: Dict) -> None:
        """Update ai_state with enriched data from Salesforce.
        
        Args:
            enriched_data: Dictionary of enriched data from SalesForceService
        """
        for field_name, enrichment in enriched_data.items():
            if field_name in self.ai_state:
                # Update the field with enriched value
                self.ai_state[field_name] = {
                    "status": "ok",
                    "reason": f"Enriched via Salesforce: {enrichment.get('source', 'Unknown')}",
                    "value": enrichment.get("enhanced_value", "")
                }

    def create_match_response(self, original_input: Dict[str, Any]) -> MatchResponse:
        """Create match response based on validation results and product line detection.

        Args:
            original_input: The original input data for fallback values
            
        Returns:
            MatchResponse object with validation results and product line detection
        """
        # Extract values from ai_state, using original input as fallback
        asset_classification = self.ai_state.get("asset_classification", {}).get("value", original_input.get("asset_classification_name", ""))
        manufacturer = self.ai_state.get("manufacturer", {}).get("value", original_input.get("manufacturer_name", ""))
        model_number = self.ai_state.get("model_number", {}).get("value", original_input.get("model_number", ""))
        product_line = self.ai_state.get("product_line", {}).get("value", "")
        explanation = self.ai_state.get("explanation", {}).get("value", "")

        return MatchResponse(
            asset_classification=asset_classification,
            manufacturer=manufacturer,
            model_number=model_number,
            product_line=product_line,
            explanation=explanation
        )



class MockService:
    def __init__(self, cache_size: int = 100):
        # Initialize LRU cache for response caching (cost optimization)
        self.response_cache = LRUCache(cache_size)
        
        self.known_patterns = {
            "cummins": {
                "dqkab": "DQKAB",
                "qsk": "QSK",
                "kta": "KTA",
                "nt": "NT",
                "l10": "L10"
            },
            "caterpillar": {
                "3516": "3516",
                "c32": "C32",
                "c15": "C15",
                "3412": "3412"
            },
            "kohler": {
                "20rz": "20RZ",
                "30rz": "30RZ",
                "40rz": "40RZ"
            }
        }



    def process_asset_data(self, asset_data: Dict[str, Any]) -> AssetProcessingResult:
        """Process asset data through validation and return AssetProcessingResult with results.
        Cost optimization: Uses LRU cache to avoid reprocessing identical inputs.
        
        Args:
            asset_data: Dictionary containing asset information
            
        Returns:
            AssetProcessingResult instance with validation results tracked
        """
        # Cost Optimization: Check cache first
        try:
            cache_key = _create_cache_key(asset_data)
            cached_response = self.response_cache.get(cache_key)
            
            if cached_response:
                logging.info(f"Cache hit for {cache_key} - returning cached response (cost savings!)")
                return cached_response
            
            logging.info(f"Cache miss for {cache_key} - processing new request")
        except Exception as e:
            # Log cache error but continue processing
            logging.warning(f"Cache operation failed: {e}. Continuing without cache.")
            cache_key = None
        
        state = AssetProcessingResult()

        asset_classification = asset_data.get("asset_classification_name", "")
        manufacturer = asset_data.get("manufacturer_name", "")
        model_number = asset_data.get("model_number", "")

        # Run validations and track results in aistate
        check_manufacturer(manufacturer, state)
        check_model_number(model_number, state)
        check_asset_classification(asset_classification, state)
        self._get_product_line(manufacturer, model_number, state)

        if state.is_valid():
            logging.info(f"Processing asset {state.model_number} is valid")
            # Generate explanation for successful processing
            explanation = state.generate_explanation()
            logging.info(f"Processing successful: {explanation}")
        else:
            logging.info(f"Processing asset {state.model_number} is invalid")
            failed_validations = state.get_failed_validations()
            salesforce = SalesForceService(failed_validations)
            enrichment_result = salesforce.enrich_failed_validations()
            
            # Let AssetProcessingResult update itself with enriched data
            state.update_with_enriched_data(enrichment_result["enriched_data"])
            
            # Re-run product line detection with enriched data
            enriched_manufacturer = state.ai_state.get("manufacturer", {}).get("value", manufacturer)
            enriched_model_number = state.ai_state.get("model_number", {}).get("value", model_number)
            self._get_product_line(enriched_manufacturer, enriched_model_number, state)
            
            # Generate final explanation with enriched data
            explanation = state.generate_explanation()
            logging.info(f"After enrichment: {explanation}")

        # Cost Optimization: Cache the processed result
        if cache_key:
            try:
                self.response_cache.set(cache_key, state)
                logging.info(f"Cached response for {cache_key}")
            except Exception as e:
                logging.warning(f"Failed to cache response: {e}")

        return state



    def _get_product_line(self, manufacturer_name: str, model_number: str, ai_state: AssetProcessingResult) -> None:
        """Detect product line from manufacturer and model number, update processing result.
        
        Args:
            manufacturer_name: The manufacturer name
            model_number: The model number to analyze
            ai_state: AssetProcessingResult instance to track product line results
        """
        manufacturer_lower = manufacturer_name.lower()
        model_lower = model_number.lower()

        # Check known manufacturer patterns
        if manufacturer_lower in self.known_patterns:
            patterns = self.known_patterns[manufacturer_lower]
            for pattern, product_line in patterns.items():
                if pattern in model_lower:
                    ai_state.insert_state("product_line", "ok", f"Found product line '{product_line}' from pattern '{pattern}'", value=product_line)
                    return

        # Fallback: extract potential product line from model number prefix
        if len(model_number) > 3:
            potential_line = model_number[:4].upper()
            if any(char.isalpha() for char in potential_line):
                ai_state.insert_state("product_line", "ok", f"Extracted potential product line '{potential_line}' from model prefix", value=potential_line)
                return

        # No product line found
        ai_state.insert_state("product_line", "not_found", "No specific product line match found", value="")


def check_manufacturer(manufacturer: str, ai_state: AssetProcessingResult) -> None:
    """Check if manufacturer is valid and track validation state.
    
    Args:
        manufacturer: The manufacturer name to validate
        ai_state: AssetProcessingResult instance to track validation results
    """
    if not manufacturer or not manufacturer.strip():
        ai_state.insert_state("manufacturer", "missing", "Manufacturer is empty or missing", value="")
        return
    
    if manufacturer.lower().strip() in ['to be determined', 'unknown']:
        ai_state.insert_state("manufacturer", "generic", "Manufacturer is generic placeholder", value=manufacturer)
        return
    
    ai_state.insert_state("manufacturer", "ok", "Valid manufacturer provided", value=manufacturer)

def check_asset_classification(asset_classification: str, ai_state: AssetProcessingResult) -> None:
    """Check if asset classification is valid and track validation state.
    
    Args:
        asset_classification: The asset classification to validate
        ai_state: AssetProcessingResult instance to track validation results
    """
    if not asset_classification or not asset_classification.strip():
        ai_state.insert_state("asset_classification", "missing", "Asset classification is empty or missing", value="")
        return
    
    if len(asset_classification.strip()) < 3:
        ai_state.insert_state("asset_classification", "invalid", "Asset classification too short (minimum 3 characters)", value=asset_classification)
        return
    
    ai_state.insert_state("asset_classification", "ok", "Valid asset classification provided", value=asset_classification)


def check_model_number(model_number: str, ai_state: AssetProcessingResult) -> None:
    """Check if model number is too generic or insufficient and track validation state.
    
    Args:
        model_number: The model number to validate
        ai_state: AssetProcessingResult instance to track validation results
    """
    if not model_number or not model_number.strip():
        ai_state.insert_state("model_number", "missing", "Model number is empty or missing", value="")
        return
    
    if len(model_number.strip()) < 3:
        ai_state.insert_state("model_number", "invalid", "Model number too short (minimum 3 characters)", value=model_number)
        return

    # Check for overly generic model numbers
    generic_patterns = ["450", "500", "600", "1000", "2000", "generator"]
    if model_number.lower().strip() in generic_patterns:
        ai_state.insert_state("model_number", "generic", f"Model number '{model_number}' is too generic", value=model_number)
        return

    ai_state.insert_state("model_number", "ok", "Valid model number provided", value=model_number)

def _create_cache_key(asset_data: Dict[str, Any]) -> str:
    """Create a cache key from asset data for response caching.

    Args:
        asset_data: Dictionary containing asset information

    Returns:
        String cache key
    """
    # Create deterministic cache key from input data
    asset_classification = asset_data.get("asset_classification_name", "").strip().lower()
    manufacturer = asset_data.get("manufacturer_name", "").strip().lower()
    model_number = asset_data.get("model_number", "").strip().lower()

    return f"{asset_classification}|{manufacturer}|{model_number}"