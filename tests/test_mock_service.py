import pytest

@pytest.fixture
def mock_input_good():
    return {
      "asset_classification_guid2": "AC0583",
      "asset_classification_name": "Generator (Diesel)",
      "manufacturer_name": "Cummins",
      "model_number": "DQKAB-10679833"
    }

@pytest.fixture
def mock_input_bad():
    """Fixture that will definitely fail validation"""
    return {
      "asset_classification_guid2": "AC0584",
      "asset_classification_name": "",  # Empty classification - will fail
      "manufacturer_name": "To Be Determined",  # Generic manufacturer - will fail
      "model_number": "450"  # Generic model number - will fail
    }


def test_generic_test(mock_input_good):

    fields = ['asset_classification_guid2', 'asset_classification_name', 'manufacturer_name', 'model_number']
    assert fields == [field for field in mock_input_good.keys()]


def test_manufacturer_test(mock_input_good):
    manufacturer_name =  mock_input_good['manufacturer_name']
    model_number = mock_input_good['model_number']
    from src.ai.mockservice import MockService
    service = MockService()
    # Note: _validate_input_schema method doesn't exist in MockAIService
    # This test needs to be updated to use actual methods
    response = service.process_asset_data(mock_input_good)
    assert response is not None



def test_mock_service(mock_input_good):

    from src.ai.mockservice import MockService
    service = MockService()
    service.process_asset_data(mock_input_good)

def test_manufacturer_validation():
    """Test manufacturer validation with comprehensive edge cases"""
    from src.ai.mockservice import check_manufacturer, AssetProcessingResult
    
    # Valid manufacturers
    test_data = {"asset_classification_guid2": "AC123", "asset_classification_name": "Test", "manufacturer_name": "Test", "model_number": "Test"}
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Cummins", state)
    assert state.ai_state["manufacturer"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Caterpillar", state)
    assert state.ai_state["manufacturer"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Kohler", state)
    assert state.ai_state["manufacturer"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Generac", state)
    assert state.ai_state["manufacturer"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Custom Manufacturer Inc.", state)
    assert state.ai_state["manufacturer"]["status"] == "ok"
    
    # Invalid manufacturers - generic/placeholder values
    state = AssetProcessingResult(**test_data)
    check_manufacturer("To Be Determined", state)
    assert state.ai_state["manufacturer"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("to be determined", state)
    assert state.ai_state["manufacturer"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("TO BE DETERMINED", state)
    assert state.ai_state["manufacturer"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("unknown", state)
    assert state.ai_state["manufacturer"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Unknown", state)
    assert state.ai_state["manufacturer"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("UNKNOWN", state)
    assert state.ai_state["manufacturer"]["status"] == "generic"
    
    # Invalid manufacturers - empty/None
    state = AssetProcessingResult(**test_data)
    check_manufacturer("", state)
    assert state.ai_state["manufacturer"]["status"] == "missing"
    
    state = AssetProcessingResult(**test_data)
    check_manufacturer("   ", state)
    assert state.ai_state["manufacturer"]["status"] == "missing"


def test_asset_classification_validation():
    """Test asset classification validation with edge cases"""
    from src.ai.mockservice import check_asset_classification, AssetProcessingResult
    
    test_data = {"asset_classification_guid2": "AC123", "asset_classification_name": "Test", "manufacturer_name": "Test", "model_number": "Test"}
    
    # Valid asset classifications
    state = AssetProcessingResult(**test_data)
    check_asset_classification("Generator (Diesel)", state)
    assert state.ai_state["asset_classification"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_asset_classification("Generator Emissions/UREA/DPF Systems", state)
    assert state.ai_state["asset_classification"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_asset_classification("Pump System", state)
    assert state.ai_state["asset_classification"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_asset_classification("ABC", state)
    assert state.ai_state["asset_classification"]["status"] == "ok"
    
    # Invalid asset classifications - too short
    state = AssetProcessingResult(**test_data)
    check_asset_classification("AB", state)
    assert state.ai_state["asset_classification"]["status"] == "invalid"
    
    state = AssetProcessingResult(**test_data)
    check_asset_classification("A", state)
    assert state.ai_state["asset_classification"]["status"] == "invalid"
    
    state = AssetProcessingResult(**test_data)
    check_asset_classification("", state)
    assert state.ai_state["asset_classification"]["status"] == "missing"
    
    state = AssetProcessingResult(**test_data)
    check_asset_classification("  ", state)
    assert state.ai_state["asset_classification"]["status"] == "missing"
    
    # Edge cases
    state = AssetProcessingResult(**test_data)
    check_asset_classification("   Generator   ", state)
    assert state.ai_state["asset_classification"]["status"] == "ok"

def test_model_number_validation():
    """Test model number validation function"""
    from src.ai.mockservice import check_model_number, AssetProcessingResult
    
    test_data = {"asset_classification_guid2": "AC123", "asset_classification_name": "Test", "manufacturer_name": "Test", "model_number": "Test"}
    
    # Valid model numbers
    state = AssetProcessingResult(**test_data)
    check_model_number("DQKAB-10679833", state)
    assert state.ai_state["model_number"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("QSK19-G4", state)
    assert state.ai_state["model_number"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("3516B", state)
    assert state.ai_state["model_number"]["status"] == "ok"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("ABC123", state)
    assert state.ai_state["model_number"]["status"] == "ok"
    
    # Invalid model numbers - too short
    state = AssetProcessingResult(**test_data)
    check_model_number("AB", state)
    assert state.ai_state["model_number"]["status"] == "invalid"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("12", state)
    assert state.ai_state["model_number"]["status"] == "invalid"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("", state)
    assert state.ai_state["model_number"]["status"] == "missing"
    
    # Invalid model numbers - generic patterns
    state = AssetProcessingResult(**test_data)
    check_model_number("450", state)
    assert state.ai_state["model_number"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("500", state)
    assert state.ai_state["model_number"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("600", state)
    assert state.ai_state["model_number"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("1000", state)
    assert state.ai_state["model_number"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("2000", state)
    assert state.ai_state["model_number"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("generator", state)
    assert state.ai_state["model_number"]["status"] == "generic"
    
    state = AssetProcessingResult(**test_data)
    check_model_number("GENERATOR", state)
    assert state.ai_state["model_number"]["status"] == "generic"


def test_validation_functions_integration():
    """Test how validation functions work together"""
    from src.ai.mockservice import check_manufacturer, check_asset_classification, check_model_number, AssetProcessingResult
    
    test_data = {"asset_classification_guid2": "AC123", "asset_classification_name": "Test", "manufacturer_name": "Test", "model_number": "Test"}
    
    # All valid data scenario
    state = AssetProcessingResult(**test_data)
    check_manufacturer("Cummins", state)
    check_asset_classification("Generator (Diesel)", state)
    check_model_number("DQKAB-10679833", state)
    
    assert state.ai_state["manufacturer"]["status"] == "ok"
    assert state.ai_state["asset_classification"]["status"] == "ok"
    assert state.ai_state["model_number"]["status"] == "ok"
    assert state.is_valid() == True
    
    # Mixed valid/invalid data scenarios
    state = AssetProcessingResult(**test_data)
    check_manufacturer("To Be Determined", state)
    check_asset_classification("Generator (Diesel)", state)
    check_model_number("DQKAB-10679833", state)
    
    assert state.ai_state["manufacturer"]["status"] == "generic"
    assert state.ai_state["asset_classification"]["status"] == "ok"
    assert state.ai_state["model_number"]["status"] == "ok"
    assert state.is_valid() == False  # Should be invalid due to manufacturer
    
    # All invalid data
    state = AssetProcessingResult(**test_data)
    check_manufacturer("", state)
    check_asset_classification("", state)
    check_model_number("450", state)
    
    assert state.ai_state["manufacturer"]["status"] == "missing"
    assert state.ai_state["asset_classification"]["status"] == "missing"
    assert state.ai_state["model_number"]["status"] == "generic"
    assert state.is_valid() == False



def test_asset_processing_result_initialization():
    """Test AssetProcessingResult initialization and basic functionality"""
    from src.ai.mockservice import AssetProcessingResult
    
    # Test initialization with data
    data = {
        "asset_classification_guid2": "AC0583",
        "asset_classification_name": "Generator (Diesel)", 
        "manufacturer_name": "Cummins",
        "model_number": "DQKAB-10679833"
    }
    state = AssetProcessingResult(**data)
    
    # Check that ai_state is initialized as empty dict
    assert state.ai_state == {}
    assert state.is_valid() == True  # No failed validations yet

def test_asset_processing_result_insert_and_retrieval():
    """Test inserting and retrieving state information"""
    from src.ai.mockservice import AssetProcessingResult
    
    data = {
        "asset_classification_guid2": "AC0583",
        "asset_classification_name": "Generator (Diesel)",
        "manufacturer_name": "Cummins", 
        "model_number": "DQKAB-10679833"
    }
    state = AssetProcessingResult(**data)
    
    # Insert valid state
    state.insert_state("manufacturer", "ok", "Valid manufacturer provided", value="Cummins")
    assert state.ai_state["manufacturer"]["status"] == "ok"
    assert state.ai_state["manufacturer"]["reason"] == "Valid manufacturer provided"
    assert state.ai_state["manufacturer"]["value"] == "Cummins"
    
    # Insert invalid state
    state.insert_state("model_number", "generic", "Model number too generic", value="450")
    assert state.ai_state["model_number"]["status"] == "generic"
    assert state.ai_state["model_number"]["reason"] == "Model number too generic"
    assert state.ai_state["model_number"]["value"] == "450"

def test_asset_processing_result_failed_validations():
    """Test get_failed_validations functionality"""
    from src.ai.mockservice import AssetProcessingResult
    
    data = {
        "asset_classification_guid2": "AC0583",
        "asset_classification_name": "Generator (Diesel)",
        "manufacturer_name": "Cummins",
        "model_number": "DQKAB-10679833"
    }
    state = AssetProcessingResult(**data)
    
    # Add mix of valid and invalid states
    state.insert_state("manufacturer", "ok", "Valid manufacturer", value="Cummins")
    state.insert_state("model_number", "generic", "Too generic", value="450")
    state.insert_state("asset_classification", "missing", "Classification missing", value="")
    
    failed = state.get_failed_validations()
    
    # Should return only failed validations (not "ok")
    assert len(failed) == 2
    assert "manufacturer" not in failed
    assert "model_number" in failed
    assert "asset_classification" in failed
    assert failed["model_number"]["status"] == "generic"
    assert failed["asset_classification"]["status"] == "missing"

def test_asset_processing_result_is_valid():
    """Test is_valid method"""
    from src.ai.mockservice import AssetProcessingResult
    
    data = {
        "asset_classification_guid2": "AC0583",
        "asset_classification_name": "Generator (Diesel)",
        "manufacturer_name": "Cummins",
        "model_number": "DQKAB-10679833"
    }
    state = AssetProcessingResult(**data)
    
    # Empty state should be valid
    assert state.is_valid() == True
    
    # All "ok" should be valid
    state.insert_state("manufacturer", "ok", "Valid", value="Cummins")
    state.insert_state("model_number", "ok", "Valid", value="DQKAB-123")
    assert state.is_valid() == True
    
    # Any non-"ok" should make it invalid
    state.insert_state("asset_classification", "missing", "Missing", value="")
    assert state.is_valid() == False

def test_asset_processing_result_clear():
    """Test clearing state"""
    from src.ai.mockservice import AssetProcessingResult
    
    data = {
        "asset_classification_guid2": "AC0583",
        "asset_classification_name": "Generator (Diesel)",
        "manufacturer_name": "Cummins",
        "model_number": "DQKAB-10679833"
    }
    state = AssetProcessingResult(**data)
    
    # Add some state
    state.insert_state("manufacturer", "ok", "Valid", value="Cummins")
    state.insert_state("model_number", "generic", "Too generic", value="450")
    assert len(state.ai_state) == 2
    
    # Clear and verify
    state.clear_ai_state()
    assert state.ai_state == {}
    assert state.is_valid() == True




def test_bad_mock_service(mock_input_bad):
    from src.ai.mockservice import MockService
    service = MockService()
    service.process_asset_data(mock_input_bad)

def test_integration_process_asset_data_valid():
    """Test process_asset_data with valid data"""
    from src.ai.mockservice import MockService
    
    valid_data = {
        "asset_classification_guid2": "AC0583",
        "asset_classification_name": "Generator (Diesel)",
        "manufacturer_name": "Cummins",
        "model_number": "DQKAB-10679833"
    }
    
    service = MockService()
    result = service.process_asset_data(valid_data)
    
    # Check that AssetProcessingResult is returned
    assert result is not None
    assert hasattr(result, 'ai_state')
    
    # Check that all validations passed
    assert result.is_valid() == True
    
    # Check specific validation states
    ai_state = result.get_ai_state()
    assert ai_state["manufacturer"]["status"] == "ok"
    assert ai_state["asset_classification"]["status"] == "ok"
    assert ai_state["model_number"]["status"] == "ok"

def test_integration_process_asset_data_invalid():
    """Test process_asset_data with invalid data"""
    from src.ai.mockservice import MockService
    
    invalid_data = {
        "asset_classification_guid2": "AC0584",
        "asset_classification_name": "",  # Empty - should fail
        "manufacturer_name": "To Be Determined",  # Generic - should fail
        "model_number": "450"  # Generic - should fail
    }
    
    service = MockService()
    result = service.process_asset_data(invalid_data)
    
    # Check that AssetProcessingResult is returned
    assert result is not None
    assert hasattr(result, 'ai_state')
    
    # Check that validation failed overall
    assert result.is_valid() == False
    
    # Check that all failed validations are captured
    failed = result.get_failed_validations()
    assert len(failed) == 3  # All three should fail
    
    assert "manufacturer" in failed
    assert failed["manufacturer"]["status"] == "generic"
    
    assert "asset_classification" in failed
    assert failed["asset_classification"]["status"] == "missing"
    
    assert "model_number" in failed
    assert failed["model_number"]["status"] == "generic"

