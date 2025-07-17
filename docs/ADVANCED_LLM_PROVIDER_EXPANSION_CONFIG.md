# VPA Advanced LLM Provider Expansion - Configuration Guide

## 📋 Overview

This guide provides step-by-step instructions for configuring and deploying the Advanced LLM Provider Expansion milestone components in the VPA system.

## 🚀 Quick Start Configuration

### 1. Environment Setup

```bash
# Set VPA environment
export VPA_ENVIRONMENT=production

# Enable advanced LLM features
export VPA_ENABLE_ADVANCED_LLM=true
export VPA_ENABLE_MULTI_PROVIDER=true
export VPA_ENABLE_LLM_FALLBACK=true
export VPA_LLM_COST_TRACKING=true
export VPA_LLM_PERFORMANCE_MONITORING=true
```

### 2. Provider Configuration

#### OpenAI Configuration
```bash
# OpenAI API Configuration
export OPENAI_API_KEY=your-openai-api-key
export VPA_OPENAI_MODEL=gpt-4
export VPA_OPENAI_MAX_TOKENS=4000
export VPA_OPENAI_TEMPERATURE=0.7
export VPA_OPENAI_TIMEOUT=30
```

#### Anthropic Configuration
```bash
# Anthropic API Configuration
export ANTHROPIC_API_KEY=your-anthropic-api-key
export VPA_ANTHROPIC_MODEL=claude-3-sonnet-20240229
export VPA_ANTHROPIC_MAX_TOKENS=4000
export VPA_ANTHROPIC_TEMPERATURE=0.7
export VPA_ANTHROPIC_TIMEOUT=30
```

#### Google AI Configuration
```bash
# Google AI Configuration
export GOOGLE_API_KEY=your-google-api-key
export VPA_GOOGLE_MODEL=gemini-pro
export VPA_GOOGLE_MAX_TOKENS=4000
export VPA_GOOGLE_TEMPERATURE=0.7
export VPA_GOOGLE_TIMEOUT=30
```

#### Local Model Configuration
```bash
# Local Model Configuration
export VPA_LOCAL_MODEL_ENDPOINT=http://localhost:11434
export VPA_LOCAL_MODEL_NAME=llama2:7b
export VPA_LOCAL_MODEL_TIMEOUT=60
```

### 3. System Configuration

```bash
# Default Provider Settings
export VPA_DEFAULT_LLM_PROVIDER=openai
export VPA_DEFAULT_LLM_MODEL=gpt-4
export VPA_LLM_PROVIDER_PRIORITY=openai,anthropic,google,local

# Performance Settings
export VPA_LLM_CACHE_ENABLED=true
export VPA_LLM_CACHE_TTL=3600
export VPA_LLM_MAX_CONCURRENT_REQUESTS=10
export VPA_LLM_REQUEST_TIMEOUT=30

# Cost Management
export VPA_LLM_DAILY_COST_LIMIT=100.0
export VPA_LLM_MONTHLY_COST_LIMIT=2000.0
export VPA_LLM_COST_ALERTS=true
```

## 🔧 Advanced Configuration

### Provider Weights and Load Balancing

```python
# config/llm_provider_config.py
LLM_PROVIDER_WEIGHTS = {
    "openai": 0.6,
    "anthropic": 0.3,
    "google": 0.1,
    "local": 0.0  # Fallback only
}

LOAD_BALANCING_STRATEGY = "weighted_round_robin"
```

### Failover Configuration

```python
# config/llm_provider_config.py
FAILOVER_CHAIN = [
    "openai",
    "anthropic", 
    "google",
    "local"
]

CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,
    "recovery_timeout": 300,
    "half_open_max_calls": 3
}
```

### Performance Optimization

```python
# config/llm_provider_config.py
PERFORMANCE_CONFIG = {
    "caching": {
        "enabled": True,
        "ttl": 3600,
        "max_size": 1000
    },
    "connection_pooling": {
        "enabled": True,
        "max_connections": 100,
        "max_keepalive_connections": 20
    },
    "request_batching": {
        "enabled": True,
        "batch_size": 10,
        "batch_timeout": 1.0
    }
}
```

## 📊 Monitoring Configuration

### Performance Metrics

```python
# config/monitoring_config.py
METRICS_CONFIG = {
    "response_time_tracking": True,
    "token_usage_tracking": True,
    "cost_tracking": True,
    "error_rate_monitoring": True,
    "provider_health_checks": True
}

ALERTING_CONFIG = {
    "response_time_threshold": 5.0,
    "error_rate_threshold": 0.1,
    "cost_threshold_daily": 100.0,
    "cost_threshold_monthly": 2000.0
}
```

### Logging Configuration

```python
# config/logging_config.py
LLM_LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": [
        {
            "type": "file",
            "filename": "logs/vpa_llm_providers.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        {
            "type": "console",
            "level": "INFO"
        }
    ]
}
```

## 🔐 Security Configuration

### API Key Management

```python
# config/security_config.py
API_KEY_CONFIG = {
    "encryption_enabled": True,
    "key_rotation_enabled": True,
    "key_rotation_interval": 2592000,  # 30 days
    "secure_storage": True
}
```

### Data Protection

```python
# config/security_config.py
DATA_PROTECTION_CONFIG = {
    "request_encryption": True,
    "response_encryption": True,
    "pii_detection": True,
    "content_filtering": True,
    "audit_logging": True
}
```

## 🧪 Testing Configuration

### Unit Testing

```bash
# Run unit tests
python -m pytest tests/core/test_advanced_llm_provider_expansion.py -v

# Run with coverage
python -m pytest tests/core/test_advanced_llm_provider_expansion.py --cov=src.vpa.core --cov-report=html
```

### Integration Testing

```bash
# Run integration tests
python scripts/test_llm_provider_integration.py --verbose

# Test specific provider
python scripts/test_llm_provider_integration.py --provider openai

# Run security tests
python scripts/test_llm_provider_integration.py --security
```

### Performance Testing

```bash
# Run performance benchmarks
python scripts/benchmark_llm_providers.py --iterations 50 --concurrent 5

# Test specific providers
python scripts/benchmark_llm_providers.py --providers openai,anthropic --iterations 100

# Generate performance report
python scripts/benchmark_llm_providers.py --verbose > performance_report.txt
```

## 📈 Deployment Configuration

### Production Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  vpa-llm-service:
    image: vpa:latest
    environment:
      - VPA_ENVIRONMENT=production
      - VPA_ENABLE_ADVANCED_LLM=true
      - VPA_ENABLE_MULTI_PROVIDER=true
      - VPA_LLM_COST_TRACKING=true
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    ports:
      - "8080:8080"
    restart: unless-stopped
```

### Kubernetes Deployment

```yaml
# k8s/vpa-llm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vpa-llm-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vpa-llm-service
  template:
    metadata:
      labels:
        app: vpa-llm-service
    spec:
      containers:
      - name: vpa-llm-service
        image: vpa:latest
        env:
        - name: VPA_ENVIRONMENT
          value: "production"
        - name: VPA_ENABLE_ADVANCED_LLM
          value: "true"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-api-keys
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-api-keys
              key: anthropic-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        ports:
        - containerPort: 8080
```

## 🔄 Migration Guide

### From Legacy LLM System

1. **Backup Current Configuration**
   ```bash
   cp config/llm_config.py config/llm_config.py.backup
   ```

2. **Update Configuration**
   ```python
   # Update imports
   from src.vpa.core.enhanced_llm_integration import VPAEnhancedLLMIntegration
   from src.vpa.core.llm_provider_manager import create_llm_provider_manager
   
   # Create new system
   manager = create_llm_provider_manager()
   llm_integration = VPAEnhancedLLMIntegration(manager)
   ```

3. **Update API Calls**
   ```python
   # Old API
   response = llm_system.generate_response(query)
   
   # New API
   request = EnhancedLLMRequest(user_query=query, user_id=user_id)
   response = await llm_integration.generate_enhanced_response(request)
   ```

4. **Test Migration**
   ```bash
   python scripts/test_llm_provider_integration.py
   ```

### Configuration Validation

```python
# scripts/validate_config.py
def validate_llm_config():
    """Validate LLM provider configuration."""
    
    # Check required environment variables
    required_vars = [
        "VPA_ENVIRONMENT",
        "VPA_DEFAULT_LLM_PROVIDER"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Missing required environment variable: {var}")
            return False
    
    # Check API keys
    if os.getenv("VPA_DEFAULT_LLM_PROVIDER") == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Missing OpenAI API key")
            return False
    
    print("✅ Configuration validation passed")
    return True
```

## 🚨 Troubleshooting

### Common Issues

1. **Provider Connection Issues**
   ```bash
   # Check API key
   echo $OPENAI_API_KEY
   
   # Test connection
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

2. **Performance Issues**
   ```bash
   # Check system resources
   python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
   
   # Monitor LLM performance
   python scripts/benchmark_llm_providers.py --providers openai --iterations 10
   ```

3. **Cost Tracking Issues**
   ```bash
   # Check cost tracking configuration
   python -c "import os; print(f'Cost tracking: {os.getenv(\"VPA_LLM_COST_TRACKING\")}')"
   ```

### Debug Mode

```bash
# Enable debug logging
export VPA_LOG_LEVEL=DEBUG
export VPA_DEBUG_MODE=true

# Run with debug
python scripts/test_llm_provider_integration.py --verbose
```

## 📚 Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VPA_ENVIRONMENT` | `development` | VPA environment |
| `VPA_ENABLE_ADVANCED_LLM` | `false` | Enable advanced LLM features |
| `VPA_ENABLE_MULTI_PROVIDER` | `false` | Enable multi-provider support |
| `VPA_DEFAULT_LLM_PROVIDER` | `openai` | Default LLM provider |
| `VPA_DEFAULT_LLM_MODEL` | `gpt-4` | Default LLM model |
| `VPA_LLM_CACHE_ENABLED` | `true` | Enable response caching |
| `VPA_LLM_CACHE_TTL` | `3600` | Cache TTL in seconds |
| `VPA_LLM_COST_TRACKING` | `false` | Enable cost tracking |
| `VPA_LLM_PERFORMANCE_MONITORING` | `false` | Enable performance monitoring |

### Provider Models

| Provider | Models | Default |
|----------|--------|---------|
| OpenAI | `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo` | `gpt-4` |
| Anthropic | `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku` | `claude-3-sonnet` |
| Google | `gemini-pro`, `gemini-pro-vision`, `palm-2` | `gemini-pro` |
| Local | `llama2:7b`, `llama2:13b`, `codellama:7b` | `llama2:7b` |

## ✅ Configuration Checklist

- [ ] Environment variables configured
- [ ] API keys set for required providers
- [ ] Provider priority order defined
- [ ] Performance settings optimized
- [ ] Cost limits configured
- [ ] Security settings enabled
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Testing completed
- [ ] Documentation updated

## 🎯 Next Steps

1. **Complete Provider Integration**: Finish implementing all LLM provider integrations
2. **Optimize Performance**: Fine-tune caching and load balancing
3. **Enhance Security**: Implement additional security measures
4. **Scale Deployment**: Prepare for production scaling
5. **Monitor and Optimize**: Continuous performance monitoring and optimization

---

## 📞 Support

For configuration issues or questions:
- Check the troubleshooting section
- Review the test scripts and their outputs
- Consult the main documentation
- Enable debug logging for detailed information

---

**VPA Advanced LLM Provider Expansion - Configuration Complete** ✅
