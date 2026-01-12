"""
Parameter Validator - Validates all parameter types for commands
"""
from typing import Any, Tuple, Optional, List
from .command_mapping import PARAM_TYPE_DEFINITIONS, COMMAND_PARAM_MAP
from .menu_constants import SYMBOLS, TIMEFRAMES, TRENDS, LOGICS, SL_SYSTEMS, PROFIT_SL_MODES, RISK_TIERS

class ParameterValidator:
    """Validates parameters based on their type definitions"""
    
    @staticmethod
    def validate(param_name: str, param_value: Any, command_name: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate a parameter value
        Returns: (is_valid, error_message)
        """
        try:
            print(f"[VALIDATE PARAM] Validating '{param_name}' = '{param_value}'", flush=True)
            
            # Get parameter type definition
            if param_name not in PARAM_TYPE_DEFINITIONS:
                print(f"[VALIDATE PARAM ERROR] Unknown parameter type: {param_name}", flush=True)
                return False, f"Unknown parameter type: {param_name}"
            
            param_def = PARAM_TYPE_DEFINITIONS[param_name]
            print(f"[VALIDATE PARAM] Param definition: {param_def}", flush=True)
            
            # Apply format conversion if needed
            original_value = param_value
            if param_def.get("format") == "uppercase":
                param_value = str(param_value).upper()
                print(f"[VALIDATE PARAM] Converted to uppercase: {original_value} -> {param_value}", flush=True)
            elif param_def.get("format") == "lowercase":
                param_value = str(param_value).lower()
                print(f"[VALIDATE PARAM] Converted to lowercase: {original_value} -> {param_value}", flush=True)
            
            # Check valid values if specified (do this BEFORE validation function)
            if "valid_values" in param_def:
                valid_values = param_def["valid_values"]
                print(f"[VALIDATE PARAM] Checking valid_values: {valid_values}", flush=True)
                
                # Handle both list of strings and list of dicts (for date presets)
                if valid_values and isinstance(valid_values[0], dict):
                    # Extract 'value' field from dict format
                    valid_value_list = [item['value'] for item in valid_values]
                    print(f"[VALIDATE PARAM] Extracted values from dicts: {valid_value_list}", flush=True)
                else:
                    valid_value_list = valid_values
                
                if param_value not in valid_value_list:
                    print(f"[VALIDATE PARAM ERROR] Value '{param_value}' not in valid_values: {valid_value_list}", flush=True)
                    return False, f"{param_name} must be one of: {', '.join(map(str, valid_value_list))}"
                print(f"[VALIDATE PARAM] Value '{param_value}' is in valid_values", flush=True)
            
            # Run validation function if specified
            if "validation" in param_def:
                try:
                    is_valid = param_def["validation"](param_value)
                    if not is_valid:
                        print(f"[VALIDATE PARAM ERROR] Validation function returned False for '{param_value}'", flush=True)
                        return False, f"Invalid {param_name}: {param_value}"
                    print(f"[VALIDATE PARAM] Validation function passed", flush=True)
                except (ValueError, TypeError) as e:
                    print(f"[VALIDATE PARAM ERROR] Validation function exception: {e}", flush=True)
                    return False, f"Invalid {param_name} format: {str(e)}"
            
            # Check numeric ranges
            if param_def.get("type") in ["float", "int"]:
                try:
                    num_value = float(param_value) if param_def.get("type") == "float" else int(param_value)
                    
                    if "min" in param_def and num_value < param_def["min"]:
                        return False, f"{param_name} must be at least {param_def['min']}"
                    
                    if "max" in param_def and num_value > param_def["max"]:
                        return False, f"{param_name} must be at most {param_def['max']}"
                except (ValueError, TypeError):
                    return False, f"{param_name} must be a number"
            
            print(f"[VALIDATE PARAM] Parameter '{param_name}' validation PASSED", flush=True)
            return True, None
            
        except Exception as e:
            print(f"[VALIDATE PARAM ERROR] Exception: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def _get_required_params(command_name: str) -> List[str]:
        """Get required parameters from COMMAND_PARAM_MAP"""
        if command_name in COMMAND_PARAM_MAP:
            return COMMAND_PARAM_MAP[command_name].get("params", [])
        return []
    
    @staticmethod
    def validate_command_params(command_name: str, params: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate all parameters for a command
        Returns: (is_valid, error_message)
        """
        print(f"[VALIDATE] Validating command '{command_name}' with params: {params}", flush=True)
        
        if command_name not in COMMAND_PARAM_MAP:
            print(f"[VALIDATE ERROR] Unknown command: {command_name}", flush=True)
            return False, f"Unknown command: {command_name}"
        
        # Check required params first (before other validation)
        required_params = ParameterValidator._get_required_params(command_name)
        missing = [p for p in required_params if p not in params or params[p] is None]
        if missing:
            print(f"[VALIDATE ERROR] Missing required parameters: {missing}", flush=True)
            return False, f"Missing required parameters: {', '.join(missing)}"
        
        command_def = COMMAND_PARAM_MAP[command_name]
        
        print(f"[VALIDATE] Required params for {command_name}: {required_params}", flush=True)
        
        # Check all required parameters are present (redundant check for logging)
        for param_name in required_params:
            if param_name not in params:
                print(f"[VALIDATE ERROR] Missing required parameter: {param_name}", flush=True)
                return False, f"Missing required parameter: {param_name}"
            
            # Validate each parameter
            print(f"[VALIDATE] Validating param '{param_name}' with value: {params[param_name]}", flush=True)
            is_valid, error = ParameterValidator.validate(param_name, params[param_name], command_name)
            if not is_valid:
                print(f"[VALIDATE ERROR] Parameter '{param_name}' validation failed: {error}", flush=True)
                return False, error
            print(f"[VALIDATE] Parameter '{param_name}' validation passed", flush=True)
        
        # Check for extra parameters - but be lenient for profit_sl_mode
        if command_name != "profit_sl_mode":  # Allow extra params for profit_sl_mode
            for param_name in params:
                if param_name not in required_params:
                    print(f"[VALIDATE ERROR] Unknown parameter: {param_name}", flush=True)
                    return False, f"Unknown parameter: {param_name}"
        
        print(f"[VALIDATE] All parameters validated successfully for {command_name}", flush=True)
        return True, None
    
    @staticmethod
    def format_parameter(param_name: str, param_value: Any) -> Any:
        """Format parameter value according to its type definition"""
        if param_name not in PARAM_TYPE_DEFINITIONS:
            return param_value
        
        param_def = PARAM_TYPE_DEFINITIONS[param_name]
        
        # Apply format conversion
        if param_def.get("format") == "uppercase":
            return str(param_value).upper()
        elif param_def.get("format") == "lowercase":
            return str(param_value).lower()
        
        # Convert to appropriate type
        if param_def.get("type") == "float":
            try:
                return float(param_value)
            except (ValueError, TypeError):
                return param_value
        elif param_def.get("type") == "int":
            try:
                return int(param_value)
            except (ValueError, TypeError):
                return param_value
        
        return param_value
    
    @staticmethod
    def get_parameter_options(param_name: str) -> Optional[list]:
        """Get available options for a parameter"""
        if param_name not in PARAM_TYPE_DEFINITIONS:
            return None
        
        param_def = PARAM_TYPE_DEFINITIONS[param_name]
        
        if "valid_values" in param_def:
            return param_def["valid_values"]
        
        return None
    
    @staticmethod
    def get_parameter_range(param_name: str) -> Optional[dict]:
        """Get min/max range for a parameter"""
        if param_name not in PARAM_TYPE_DEFINITIONS:
            return None
        
        param_def = PARAM_TYPE_DEFINITIONS[param_name]
        range_info = {}
        
        if "min" in param_def:
            range_info["min"] = param_def["min"]
        if "max" in param_def:
            range_info["max"] = param_def["max"]
        
        return range_info if range_info else None

