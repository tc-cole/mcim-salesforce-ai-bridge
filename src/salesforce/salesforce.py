from typing import Dict, List, Optional
import random
from src.models.schemas import MatchResponse


def _get_product_line() -> Dict:
    """Simulate Salesforce product line enrichment"""
    product_lines = ["QSK Series", "C-Series", "DQKAB Series", "PowerTech Series"]
    selected_line = random.choice(product_lines)

    return {
        "enhanced_value": selected_line,
        "confidence": 0.92,
        "source": "Salesforce Product Catalog",
        "additional_data": {
            "product_family": "Industrial Generators",
            "tier_level": "Tier 4 Final",
            "warranty_years": random.randint(2, 5),
            "service_interval": f"{random.randint(250, 500)} hours"
        }
    }


def _generate_explanation(enriched_data: Dict) -> str:
    """Generate explanation of enrichment process"""
    sources = [data.get("source", "Unknown") for data in enriched_data.values()]
    confidence_scores = [data.get("confidence", 0) for data in enriched_data.values()]
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

    return f"Enriched {len(enriched_data)} fields using {', '.join(set(sources))} with average confidence of {avg_confidence:.2f}. Enhanced data includes detailed specifications, vendor information, and technical parameters."


class SalesForceService:
    def __init__(self, failed_validations: dict) -> None:
        self.failed_validations = failed_validations
        
        # Mock Salesforce enrichment database
        self.manufacturer_db = {
            "generic": ["Cummins Power Generation", "Caterpillar Inc.", "Kohler Co.", "Generac Power Systems"],
            "aliases": {
                "cummins": "Cummins Power Generation",
                "cat": "Caterpillar Inc.", 
                "caterpillar": "Caterpillar Inc.",
                "kohler": "Kohler Co.",
                "generac": "Generac Power Systems"
            }
        }
        
        self.model_db = {
            "enhanced_models": {
                "450": "C450D6-450kW-Diesel-Generator",
                "500": "QSK19-G4-500kW-Natural-Gas", 
                "600": "3516B-600kW-Diesel-Marine",
                "1000": "QST30-G5-1000kW-Standby",
                "2000": "3520C-2000kW-Prime-Power"
            }
        }
        
        self.classification_db = {
            "generator": {
                "specific": "Emergency Backup Generator (Diesel)",
                "power_range": "450-2000kW",
                "fuel_type": "Diesel/Natural Gas"
            },
            "emissions": {
                "specific": "Tier 4 Final Emissions Control System",
                "components": "DPF, SCR, DEF Tank"
            }
        }

    def enrich_failed_validations(self) -> dict:
        """Enrich failed validations using Salesforce data.
        
        Returns:
            Dictionary with enriched data and summary
        """
        enriched_data = {}
        for field_name, validation_info in self.failed_validations.items():
            # Map field names directly to enrichment methods
            enriched_data[field_name] = self.lookup_enrichment(field_name)

        return {
            "enriched_data": enriched_data,
            "summary": {
                "fields_enriched": len(enriched_data),
                "avg_confidence": sum(data.get("confidence", 0) for data in enriched_data.values()) / len(enriched_data) if enriched_data else 0,
                "explanation": _generate_explanation(enriched_data)
            }
        }
    
    def create_enriched_match_request(self) -> Dict:
        """Convert enriched data back to MatchRequest format for reprocessing using ai_state"""
        enrichment_result = self.enrich_failed_validations()
        enriched_data = enrichment_result["enriched_data"]
        
        # Build enhanced request from ai_state and enrichments
        enhanced_request = {}
        
        # Apply enrichments or use original values from validation context
        if "manufacturer" in enriched_data:
            enhanced_request["manufacturer_name"] = enriched_data["manufacturer"]["enhanced_value"]
        else:
            enhanced_request["manufacturer_name"] = "Unknown"  # fallback
        
        if "model_number" in enriched_data:
            enhanced_request["model_number"] = enriched_data["model_number"]["enhanced_value"]
        else:
            enhanced_request["model_number"] = "Unknown"  # fallback
            
        if "asset_classification" in enriched_data:
            enhanced_request["asset_classification_name"] = enriched_data["asset_classification"]["enhanced_value"]
        else:
            enhanced_request["asset_classification_name"] = "Unknown"  # fallback
            
        # Always include required GUID field
        enhanced_request["asset_classification_guid2"] = "AC_ENRICHED"
        
        return enhanced_request

    def lookup_enrichment(self, field_name: str) -> dict:
        """Lookup enrichment data based on field name.
        
        Args:
            field_name: The field that needs enrichment
            
        Returns:
            Dictionary with enriched data
        """
        if field_name == 'manufacturer':
            return self._get_manufacturer()
        elif field_name == 'asset_classification':
            return self._get_asset_classification()
        elif field_name == 'model_number':
            return self._get_model_number()
        elif field_name == 'product_line':
            return _get_product_line()
        else:
            return {
                "enhanced_value": "",
                "confidence": 0.0,
                "source": "Unknown",
                "additional_data": {}
            }

    def _get_manufacturer(self) -> Dict:
        """Simulate Salesforce manufacturer enrichment lookup"""
        # Simulate querying Salesforce Asset and Vendor records
        enhanced_manufacturer = random.choice(self.manufacturer_db["generic"])
        
        return {
            "enhanced_value": enhanced_manufacturer,
            "confidence": 0.95,
            "source": "Salesforce Vendor Master",
            "additional_data": {
                "vendor_id": f"VND_{random.randint(1000, 9999)}",
                "primary_contact": "service@manufacturer.com",
                "support_level": "Premium"
            }
        }


    def _get_asset_classification(self) -> Dict:
        """Simulate Salesforce asset classification enrichment"""
        classification_type = random.choice(["generator", "emissions"])
        classification_data = self.classification_db[classification_type]
        
        return {
            "enhanced_value": classification_data["specific"],
            "confidence": 0.90,
            "source": "Salesforce Asset Hierarchy",
            "additional_data": {
                "category_id": f"CAT_{random.randint(100, 999)}",
                "parent_category": "Power Generation Equipment",
                "specifications": classification_data
            }
        }

    def _get_model_number(self) -> Dict:
        """Simulate Salesforce model number enrichment"""
        # Simulate looking up detailed specifications
        generic_models = list(self.model_db["enhanced_models"].keys())
        base_model = random.choice(generic_models)
        enhanced_model = self.model_db["enhanced_models"][base_model]
        
        return {
            "enhanced_value": enhanced_model,
            "confidence": 0.88,
            "source": "Salesforce Technical Specifications",
            "additional_data": {
                "serial_number_prefix": f"SN{random.randint(10000, 99999)}",
                "manufacture_year": random.randint(2018, 2024),
                "power_rating": f"{base_model}kW",
                "fuel_consumption": f"{random.randint(15, 35)} gal/hr"
            }
        }



