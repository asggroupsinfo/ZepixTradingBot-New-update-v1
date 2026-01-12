"""
ZERO TYPING VERIFICATION - Ensures all 78 commands work with BUTTONS ONLY
Tests that NO command requires manual text input from user
"""
import sys
sys.path.insert(0, 'src')

from menu.command_mapping import COMMAND_PARAM_MAP

def verify_zero_typing():
    """Check all commands - ensure ZERO typing required"""
    
    print("="*70)
    print("ZERO TYPING VERIFICATION - 78 TELEGRAM COMMANDS")
    print("Ensuring ALL commands work with BUTTONS ONLY")
    print("="*70)
    
    typing_required = []
    button_based = []
    
    for cmd_name, cmd_def in COMMAND_PARAM_MAP.items():
        cmd_type = cmd_def.get("type", "unknown")
        params = cmd_def.get("params", [])
        
        # Check if command type allows buttons
        if cmd_type == "direct":
            # No params needed - pure button click
            button_based.append({
                "command": cmd_name,
                "type": cmd_type,
                "params": "none",
                "interface": "BUTTON (no params)"
            })
        
        elif cmd_type == "single":
            # Single parameter - check if presets/options exist
            presets = cmd_def.get("presets", [])
            options = cmd_def.get("options", [])
            
            if presets or options:
                button_based.append({
                    "command": cmd_name,
                    "type": cmd_type,
                    "params": params[0] if params else "unknown",
                    "interface": f"BUTTON ({len(presets or options)} presets)"
                })
            else:
                typing_required.append({
                    "command": cmd_name,
                    "type": cmd_type,
                    "params": params[0] if params else "unknown",
                    "issue": "NO PRESETS - requires typing"
                })
        
        elif cmd_type == "multi":
            # Multiple parameters - check if all have presets
            presets_dict = cmd_def.get("presets", {})
            
            if isinstance(presets_dict, dict):
                # Per-parameter presets
                all_have_presets = all(param in presets_dict for param in params)
                if all_have_presets:
                    button_based.append({
                        "command": cmd_name,
                        "type": cmd_type,
                        "params": ", ".join(params),
                        "interface": f"BUTTONS ({len(params)} params)"
                    })
                else:
                    missing = [p for p in params if p not in presets_dict]
                    typing_required.append({
                        "command": cmd_name,
                        "type": cmd_type,
                        "params": ", ".join(params),
                        "issue": f"Missing presets for: {', '.join(missing)}"
                    })
            else:
                typing_required.append({
                    "command": cmd_name,
                    "type": cmd_type,
                    "params": ", ".join(params),
                    "issue": "NO PRESETS DICT - requires typing"
                })
        
        elif cmd_type == "multi_targets":
            # OLD TYPING-BASED TYPE - should NOT exist
            typing_required.append({
                "command": cmd_name,
                "type": cmd_type,
                "params": ", ".join(params),
                "issue": "OLD TYPE - requires typing input"
            })
        
        elif cmd_type == "dynamic":
            # Dynamic commands load options from runtime data
            button_based.append({
                "command": cmd_name,
                "type": cmd_type,
                "params": params[0] if params else "unknown",
                "interface": "BUTTON (dynamic list)"
            })
        
        else:
            typing_required.append({
                "command": cmd_name,
                "type": cmd_type,
                "params": ", ".join(params) if params else "none",
                "issue": f"UNKNOWN TYPE: {cmd_type}"
            })
    
    # Print results
    print("\n" + "="*70)
    print("[OK] BUTTON-BASED COMMANDS")
    print("="*70)
    for cmd in button_based:
        print(f"[OK] {cmd['command']:30s} | {cmd['interface']}")
    
    if typing_required:
        print("\n" + "="*70)
        print("[ERROR] TYPING-REQUIRED COMMANDS")
        print("="*70)
        for cmd in typing_required:
            print(f"[ERROR] {cmd['command']:30s} | {cmd['issue']}")
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL VERIFICATION SUMMARY")
    print("="*70)
    print(f"Total Commands Tested:     {len(COMMAND_PARAM_MAP)}")
    print(f"Button-Based (OK):         {len(button_based)}")
    print(f"Typing Required (ERROR):   {len(typing_required)}")
    print("="*70)
    
    if typing_required:
        print("[ERROR] VERIFICATION FAILED!")
        print("[ERROR] Some commands still require manual typing")
        print("[ERROR] Fix these commands to use button presets")
        return False
    else:
        print("[OK] VERIFICATION PASSED!")
        print("[OK] ALL 78 COMMANDS ARE 100% BUTTON-BASED")
        print("[OK] ZERO TYPING REQUIRED!")
        return True

if __name__ == "__main__":
    success = verify_zero_typing()
    sys.exit(0 if success else 1)
