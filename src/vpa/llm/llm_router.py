import os
from typing import Dict, Any

def chat(prompt: str, system: str = "", **kw) -> Dict[str, Any]:
    """Route chat request to available LLM provider"""
    
    # Check feature flag
    if not os.getenv("VPA_ENABLE_LLM", "0").lower() in ["1", "true", "yes"]:
        return {
            "response": "LLM features disabled. Set VPA_ENABLE_LLM=1 to enable.",
            "provider": "disabled",
            "success": False
        }
    
    # Try OpenAI first
    result = try_openai(prompt, system, **kw)
    if result["success"]:
        return result
    
    # Try Anthropic
    result = try_anthropic(prompt, system, **kw)
    if result["success"]:
        return result
    
    # Try Google AI
    result = try_google_ai(prompt, system, **kw)
    if result["success"]:
        return result
    
    # Try recovered LLM components
    result = try_recovered_llm(prompt, system, **kw)
    if result["success"]:
        return result
    
    # Fallback response
    return {
        "response": f"Echo response: {prompt}",
        "provider": "fallback",
        "success": True,
        "note": "No LLM providers available. Install openai, anthropic, or google-generativeai packages."
    }

def try_openai(prompt: str, system: str = "", **kw) -> Dict[str, Any]:
    """Try OpenAI API"""
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"success": False, "error": "OPENAI_API_KEY not set"}
        
        client = openai.OpenAI(api_key=api_key)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=kw.get("model", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=kw.get("max_tokens", 150),
            temperature=kw.get("temperature", 0.7)
        )
        
        return {
            "response": response.choices[0].message.content,
            "provider": "openai",
            "model": response.model,
            "usage": response.usage.dict() if response.usage else None,
            "success": True
        }
        
    except ImportError:
        return {"success": False, "error": "openai package not installed"}
    except Exception as e:
        return {"success": False, "error": f"OpenAI error: {str(e)}"}

def try_anthropic(prompt: str, system: str = "", **kw) -> Dict[str, Any]:
    """Try Anthropic Claude API"""
    try:
        import anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {"success": False, "error": "ANTHROPIC_API_KEY not set"}
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Combine system and user prompts for Claude
        full_prompt = f"{system}\n\nHuman: {prompt}\n\nAssistant:" if system else f"Human: {prompt}\n\nAssistant:"
        
        response = client.completions.create(
            model=kw.get("model", "claude-3-haiku-20240307"),
            prompt=full_prompt,
            max_tokens_to_sample=kw.get("max_tokens", 150),
            temperature=kw.get("temperature", 0.7)
        )
        
        return {
            "response": response.completion.strip(),
            "provider": "anthropic",
            "model": response.model,
            "success": True
        }
        
    except ImportError:
        return {"success": False, "error": "anthropic package not installed"}
    except Exception as e:
        return {"success": False, "error": f"Anthropic error: {str(e)}"}

def try_google_ai(prompt: str, system: str = "", **kw) -> Dict[str, Any]:
    """Try Google Generative AI"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "error": "GOOGLE_AI_API_KEY or GEMINI_API_KEY not set"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(kw.get("model", "gemini-pro"))
        
        # Combine system and user prompts
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=kw.get("max_tokens", 150),
                temperature=kw.get("temperature", 0.7)
            )
        )
        
        return {
            "response": response.text,
            "provider": "google-ai",
            "model": kw.get("model", "gemini-pro"),
            "success": True
        }
        
    except ImportError:
        return {"success": False, "error": "google-generativeai package not installed"}
    except Exception as e:
        return {"success": False, "error": f"Google AI error: {str(e)}"}

def try_recovered_llm(prompt: str, system: str = "", **kw) -> Dict[str, Any]:
    """Try recovered LLM components from archives"""
    try:
        from ..util.dynload import get_recovery_map, load_symbol_from_paths, resolve_relative_path
        
        recovery_map = get_recovery_map()
        
        # Try LLM provider manager
        llm_candidates = (
            recovery_map.get("openai_client", []) +
            recovery_map.get("anthropic_client", []) +
            recovery_map.get("google_ai", [])
        )
        
        if llm_candidates:
            llm_candidates = [resolve_relative_path(p) for p in llm_candidates]
            
            # Try to load LLM provider manager
            for class_name in ["LLMProviderManager", "LLMManager", "AIProvider"]:
                llm_manager_class = load_symbol_from_paths(class_name, llm_candidates)
                if llm_manager_class:
                    try:
                        llm_manager = llm_manager_class()
                        
                        # Try different method names
                        for method_name in ["chat", "generate", "complete", "ask"]:
                            if hasattr(llm_manager, method_name):
                                method = getattr(llm_manager, method_name)
                                response = method(prompt, system_prompt=system, **kw)
                                
                                if isinstance(response, str):
                                    return {
                                        "response": response,
                                        "provider": "recovered",
                                        "success": True
                                    }
                                elif isinstance(response, dict) and "response" in response:
                                    response["provider"] = "recovered"
                                    response["success"] = True
                                    return response
                        
                    except Exception as e:
                        continue
        
        return {"success": False, "error": "No recovered LLM components work"}
        
    except Exception as e:
        return {"success": False, "error": f"Recovery error: {str(e)}"}

def list_available_providers():
    """List available LLM providers"""
    providers = []
    
    # Check OpenAI
    result = try_openai("test", max_tokens=1)
    if result["success"] or result.get("error") != "openai package not installed":
        providers.append({
            "name": "OpenAI",
            "available": result["success"],
            "status": "Ready" if result["success"] else result.get("error", "Unknown error")
        })
    
    # Check Anthropic
    result = try_anthropic("test", max_tokens=1)
    if result["success"] or result.get("error") != "anthropic package not installed":
        providers.append({
            "name": "Anthropic",
            "available": result["success"],
            "status": "Ready" if result["success"] else result.get("error", "Unknown error")
        })
    
    # Check Google AI
    result = try_google_ai("test", max_tokens=1)
    if result["success"] or result.get("error") not in ["google-generativeai package not installed"]:
        providers.append({
            "name": "Google AI",
            "available": result["success"],
            "status": "Ready" if result["success"] else result.get("error", "Unknown error")
        })
    
    return providers

if __name__ == "__main__":
    # Test the router
    import sys
    if len(sys.argv) > 1:
        test_prompt = " ".join(sys.argv[1:])
        result = chat(test_prompt)
        print(f"Response: {result['response']}")
        print(f"Provider: {result['provider']}")
    else:
        print("Available providers:")
        for provider in list_available_providers():
            status = "✅" if provider["available"] else "❌"
            print(f"{status} {provider['name']}: {provider['status']}")
