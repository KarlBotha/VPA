# LLM Interface Specification

## Overview

This document defines the standardized interface for LLM integration within the VPA system. It specifies the requirements for prompt formats, response handling, context management, and error handling to ensure consistent LLM integration across all components.

## Table of Contents

1. [Prompt Structure](#1-prompt-structure)
2. [Response Format](#2-response-format)
3. [Context Management](#3-context-management)
4. [Error Handling](#4-error-handling)
5. [Performance Requirements](#5-performance-requirements)
6. [Integration Patterns](#6-integration-patterns)

## 1. Prompt Structure

### 1.1 Standard Prompt Format

All LLM requests must follow this standard structure:

```json
{
  "request_id": "unique-request-id",
  "system_message": "Role and behavior instructions for the LLM",
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "Message content",
      "timestamp": "ISO-8601 timestamp"
    }
  ],
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 1.0
  },
  "context": {
    "plugin_context": {},
    "user_context": {}
  }
}
```

### 1.2 System Message Guidelines

System messages should follow these guidelines:

1. Begin with a clear role definition: "You are a helpful virtual assistant..."
2. Include specific behavior instructions
3. Define output format expectations
4. Set operational boundaries

Example:
```
You are a helpful virtual assistant named VPA. Provide concise, accurate responses.
When responding to factual questions, indicate your confidence level.
Do not make up information. If you don't know, say so clearly.
Format lists with bullet points and use markdown for emphasis when appropriate.
```

### 1.3 Required Fields

| Field | Requirement | Description |
|-------|-------------|-------------|
| request_id | Required | Unique ID for tracking and correlation |
| system_message | Required | Instructions defining LLM behavior |
| messages | Required | Conversation history in chronological order |
| parameters | Optional | Model-specific parameters |
| context | Optional | Additional context for enhanced responses |

## 2. Response Format

### 2.1 Standard Response Structure

```json
{
  "request_id": "original-request-id",
  "response": "The LLM-generated response text",
  "metadata": {
    "model": "Model name/version used",
    "tokens": {
      "prompt": 123,
      "completion": 456,
      "total": 579
    },
    "processing_time": 1.234
  },
  "actions": [
    {
      "type": "action_type",
      "parameters": {}
    }
  ],
  "error": null
}
```

### 2.2 Action Types

The response may include suggested actions for the system to take:

| Action Type | Purpose | Example Parameters |
|------------|---------|-------------------|
| web_search | Suggest web search | `{"query": "search terms"}` |
| open_app | Suggest opening application | `{"app_name": "Calculator"}` |
| create_reminder | Suggest creating reminder | `{"text": "Buy milk", "time": "2025-09-01T15:00:00"}` |
| plugin_action | Suggest specific plugin action | `{"plugin": "weather", "action": "forecast"}` |

### 2.3 Response Parsing

Responses should be parsed as follows:

1. Extract the main response text
2. Process any actions in the `actions` array
3. Handle any errors in the `error` field
4. Track performance metrics from `metadata`

## 3. Context Management

### 3.1 Conversation History

- Maintain last 10 conversation turns by default
- Include timestamps for each message
- Support for selective history pruning
- Allow plugins to add context-specific history entries

### 3.2 Context Injection

Plugins may inject context through the standard event:

```python
await event_bus.emit_async("llm.context.update", {
    "plugin_id": "weather_plugin",
    "context_type": "user_location",
    "context_data": {"city": "Seattle", "country": "US"},
    "ttl": 3600  # seconds until context expires
})
```

### 3.3 Context Persistence

- User-specific context should persist across sessions
- Temporary context should have explicit TTL
- Context storage should be encrypted for sensitive information

## 4. Error Handling

### 4.1 Error Categories

| Error Category | Description | Recovery Strategy |
|----------------|-------------|------------------|
| ConnectionError | Network/connectivity issue | Retry with backoff |
| Timeout | Response took too long | Retry once with reduced parameters |
| AuthError | Authentication failed | Report to user, use fallback |
| ContentFilter | Content policy violation | Inform user of restrictions |
| QuotaExceeded | Usage limits exceeded | Switch to fallback model |
| InvalidRequest | Malformed request | Log error, fix in code |
| ModelUnavailable | Selected model unavailable | Use fallback model |

### 4.2 Error Response Format

```json
{
  "request_id": "original-request-id",
  "response": null,
  "metadata": {},
  "actions": [],
  "error": {
    "type": "error_category",
    "message": "Human-readable error message",
    "retry_possible": true|false,
    "fallback_used": true|false
  }
}
```

### 4.3 Error Handling Strategy

1. **Retry Logic**:
   - ConnectionError: Retry up to 3 times with exponential backoff
   - Timeout: Retry once with reduced `max_tokens` and `temperature`
   - Other errors: Do not retry automatically

2. **Fallbacks**:
   - First fallback: Try alternate model
   - Second fallback: Use cached responses if available
   - Final fallback: Inform user of service unavailability

3. **Error Reporting**:
   - Emit `llm.error` event with error details
   - Log errors with request context (excluding sensitive data)
   - Track error rates for monitoring

## 5. Performance Requirements

### 5.1 Response Time Targets

| Response Length | Target Time |
|-----------------|------------|
| Short (<50 tokens) | <1.5s |
| Medium (50-200 tokens) | <3s |
| Long (>200 tokens) | <5s |

### 5.2 Resource Utilization

- Memory: <200MB per active LLM adapter
- Disk: Minimize temporary storage
- Network: Compress requests/responses when possible

### 5.3 Monitoring

- Track token usage for cost management
- Monitor response times by request type
- Track error rates and types

## 6. Integration Patterns

### 6.1 Basic Integration Pattern

```python
from vpa.core.events import event_bus
from vpa.core.llm import create_request_id

async def process_user_query(user_input: str):
    # Create unique request ID
    request_id = create_request_id()
    
    # Create standard request
    llm_request = {
        "request_id": request_id,
        "system_message": "You are a helpful assistant.",
        "messages": [
            {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            }
        ],
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 1024
        }
    }
    
    # Submit request via event bus
    await event_bus.emit_async("llm.request", llm_request)
    
    # Response will be handled by subscribed handlers
```

### 6.2 Response Handler Pattern

```python
@event_bus.subscribe("llm.response", async_callback=True)
async def handle_llm_response(event_data):
    # Extract key response data
    request_id = event_data.get("request_id")
    response = event_data.get("response")
    error = event_data.get("error")
    actions = event_data.get("actions", [])
    
    # Handle error case
    if error:
        error_type = error.get("type")
        error_message = error.get("message")
        await handle_llm_error(error_type, error_message, request_id)
        return
    
    # Process response
    await display_response(response)
    
    # Process any actions
    for action in actions:
        await process_suggested_action(action)
```

### 6.3 Context Update Pattern

```python
async def update_user_context(user_id: str, context_data: dict):
    # Update context via event bus
    await event_bus.emit_async("llm.context.update", {
        "user_id": user_id,
        "context_type": "user_preferences",
        "context_data": context_data,
        "persistent": True
    })
```

### 6.4 Model Selection Pattern

```python
async def select_appropriate_model(request_type: str, user_preferences: dict):
    # Determine appropriate model based on request and preferences
    if request_type == "code_generation":
        model = "code-optimized-model"
    elif request_type == "creative":
        model = "creative-optimized-model"
    else:
        model = user_preferences.get("preferred_model", "default-model")
    
    return model
```

## Conclusion

This document establishes the standard interface for LLM integration within the VPA system. By following these specifications, all components will maintain consistent interaction with LLM services, ensuring reliable operation, proper error handling, and efficient resource utilization.

---

*LLM Interface Specification created on August 29, 2025*  
*Version: 1.0*  
*Related Documents: VPA_PLANNING_ENHANCEMENT_ANALYSIS.md (v1.0)*
