from pydantic import BaseModel, Field

class MatchRequest(BaseModel):
    asset_classification_guid2: str = Field(..., description="Asset Class GUID2")
    asset_classification_name: str = Field(..., description="Asset Class Name")
    manufacturer_name: str = Field(..., description="Manufacturer Name")
    model_number: str = Field(..., description="Model Number")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_classification_guid2": "AC0583",
                "asset_classification_name": "Generator (Diesel)",
                "manufacturer_name": "Cummins",
                "model_number": "DQKAB-10679833"
            }
        }


class MatchResponse(BaseModel):
    asset_classification: str = Field(..., description="Asset classification")
    manufacturer: str = Field(..., description="Manufacturer name")
    model_number: str = Field(..., description="Model number")
    product_line: str = Field(..., description="Product line (empty if no match)")
    explanation: str = Field(..., description="Detailed explanation of the match or why no match was found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_classification": "Generator (Diesel)",
                "manufacturer": "Cummins",
                "model_number": "DQKAB-10679833",
                "product_line": "DQKAB",
                "explanation": "The model number 'DQKAB-10679833' corresponds to the 'DQKAB' product line, a diesel generator set manufactured by Cummins..."
            }
        }


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy"
            }
        }


class WelcomeResponse(BaseModel):
    message: str = Field(..., description="Welcome message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Salesforce AI Bridge is running"
            }
        }


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: str = Field(None, description="Additional error details")
    field: str = Field(None, description="Field that caused the error (for validation errors)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data provided",
                "details": "Manufacturer name cannot be empty",
                "field": "manufacturer_name"
            }
        }