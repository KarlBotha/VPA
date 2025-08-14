import importlib.util, sys, glob, os

def load_symbol_from_paths(symbol, candidate_files):
    """Dynamically load a symbol from candidate file paths"""
    for f in candidate_files:
        if not os.path.exists(f):
            continue
            
        try:
            # Create a unique module name based on file path hash
            modname = f"dyn_{abs(hash(f))}"
            
            # Load the module
            spec = importlib.util.spec_from_file_location(modname, f)
            if spec is None or spec.loader is None:
                continue
                
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules to prevent reload issues
            sys.modules[modname] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Try to get the symbol
            if hasattr(module, symbol):
                return getattr(module, symbol)
                
            # Also check for symbol in module's __dict__ with case variations
            for attr_name in dir(module):
                if attr_name.lower() == symbol.lower():
                    return getattr(module, attr_name)
                    
        except Exception as e:
            # Log error but continue trying other files
            print(f"Failed to load {symbol} from {f}: {e}")
            continue
    
    return None

def load_module_from_paths(candidate_files, preferred_name=None):
    """Load entire module from candidate paths"""
    for f in candidate_files:
        if not os.path.exists(f):
            continue
            
        try:
            modname = preferred_name or f"dyn_mod_{abs(hash(f))}"
            spec = importlib.util.spec_from_file_location(modname, f)
            
            if spec is None or spec.loader is None:
                continue
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[modname] = module
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            print(f"Failed to load module from {f}: {e}")
            continue
    
    return None

def get_recovery_map(recover_map_path="tools/recover/recover_map.json"):
    """Load the recovery map JSON"""
    try:
        import json
        with open(recover_map_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load recovery map: {e}")
        return {}

def resolve_relative_path(path, base_dir=None):
    """Resolve relative path to absolute path"""
    if base_dir is None:
        # Try to find project root
        current = os.path.dirname(os.path.abspath(__file__))
        while current and current != os.path.dirname(current):
            if os.path.exists(os.path.join(current, 'src', 'vpa')):
                base_dir = current
                break
            current = os.path.dirname(current)
        
        if base_dir is None:
            base_dir = os.getcwd()
    
    return os.path.join(base_dir, path) if not os.path.isabs(path) else path
