"""
VPA Vector Database Production Deployment Configuration

This configuration file provides production-ready settings for the VPA
vector database integration system, including security, performance,
and monitoring configurations.

Configuration Categories:
- Vector database provider settings
- Performance optimization parameters
- Security and authentication settings
- Monitoring and logging configuration
- Backup and recovery settings
- Environment-specific configurations
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class VectorDatabaseProvider(Enum):
    """Supported vector database providers"""
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    MOCK = "mock"


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    enable_authentication: bool = True
    api_key_required: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_requests_per_minute: int = 100
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    session_timeout_minutes: int = 30


@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    max_concurrent_requests: int = 50
    connection_pool_size: int = 10
    query_timeout_seconds: int = 30
    cache_size_mb: int = 512
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 3600
    batch_size: int = 100
    max_document_size_mb: int = 5
    embedding_batch_size: int = 32
    search_result_limit: int = 1000


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    enable_metrics: bool = True
    metrics_port: int = 8001
    log_level: str = "INFO"
    log_format: str = "json"
    enable_tracing: bool = True
    health_check_interval_seconds: int = 30
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "error_rate_percent": 5.0,
        "response_time_ms": 1000,
        "memory_usage_percent": 80.0,
        "cpu_usage_percent": 80.0
    })


@dataclass
class BackupConfig:
    """Backup and recovery configuration"""
    enable_backup: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    backup_storage_path: str = "/backups/vpa_vector_db"
    enable_point_in_time_recovery: bool = True
    backup_encryption: bool = True


@dataclass
class VectorDatabaseConfig:
    """Vector database specific configuration"""
    provider: VectorDatabaseProvider = VectorDatabaseProvider.CHROMADB
    
    # Connection settings
    host: str = "localhost"
    port: int = 8000
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    
    # Database settings
    database_name: str = "vpa_vector_db"
    collection_name: str = "documents"
    index_name: str = "vpa_index"
    
    # Vector settings
    dimension: int = 1536
    metric: str = "cosine"
    
    # Performance settings
    ef_construction: int = 200
    max_connections: int = 16
    batch_size: int = 100
    
    # Replication settings
    replication_factor: int = 1
    enable_sharding: bool = False
    shard_count: int = 1


@dataclass
class DocumentProcessingConfig:
    """Document processing configuration"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    max_chunk_size: int = 2000
    
    # Text processing
    enable_text_cleaning: bool = True
    remove_special_characters: bool = True
    normalize_whitespace: bool = True
    
    # Language processing
    default_language: str = "en"
    enable_language_detection: bool = True
    
    # Metadata extraction
    extract_metadata: bool = True
    metadata_fields: List[str] = field(default_factory=lambda: [
        "title", "author", "creation_date", "file_type", "source"
    ])


@dataclass
class EmbeddingConfig:
    """Embedding model configuration"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    model_path: Optional[str] = None
    device: str = "cpu"  # or "cuda" for GPU
    batch_size: int = 32
    max_sequence_length: int = 512
    normalize_embeddings: bool = True
    
    # Caching
    enable_embedding_cache: bool = True
    cache_size: int = 10000
    
    # Model optimization
    use_half_precision: bool = False
    compile_model: bool = False


@dataclass
class VPAVectorDatabaseDeploymentConfig:
    """Main deployment configuration"""
    environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT
    
    # Core configuration
    vector_database: VectorDatabaseConfig = field(default_factory=VectorDatabaseConfig)
    document_processing: DocumentProcessingConfig = field(default_factory=DocumentProcessingConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    
    # System configuration
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    
    # Application settings
    debug: bool = False
    testing: bool = False
    
    def __post_init__(self):
        """Post-initialization configuration adjustments"""
        # Adjust settings based on environment
        if self.environment == DeploymentEnvironment.PRODUCTION:
            self._configure_production()
        elif self.environment == DeploymentEnvironment.STAGING:
            self._configure_staging()
        else:
            self._configure_development()
    
    def _configure_production(self):
        """Configure for production environment"""
        self.debug = False
        self.testing = False
        
        # Security settings
        self.security.enable_authentication = True
        self.security.api_key_required = True
        self.security.encrypt_at_rest = True
        self.security.encrypt_in_transit = True
        self.security.allowed_origins = []  # Configure specific origins
        
        # Performance settings
        self.performance.max_concurrent_requests = 100
        self.performance.connection_pool_size = 20
        self.performance.cache_size_mb = 1024
        
        # Monitoring settings
        self.monitoring.enable_metrics = True
        self.monitoring.enable_tracing = True
        self.monitoring.log_level = "INFO"
        
        # Backup settings
        self.backup.enable_backup = True
        self.backup.backup_encryption = True
        
        # Vector database settings
        self.vector_database.replication_factor = 3
        self.vector_database.enable_sharding = True
    
    def _configure_staging(self):
        """Configure for staging environment"""
        self.debug = False
        self.testing = True
        
        # Security settings
        self.security.enable_authentication = True
        self.security.api_key_required = True
        
        # Performance settings
        self.performance.max_concurrent_requests = 50
        self.performance.connection_pool_size = 10
        
        # Monitoring settings
        self.monitoring.enable_metrics = True
        self.monitoring.log_level = "DEBUG"
        
        # Backup settings
        self.backup.enable_backup = True
        self.backup.backup_retention_days = 7
    
    def _configure_development(self):
        """Configure for development environment"""
        self.debug = True
        self.testing = True
        
        # Security settings (relaxed for development)
        self.security.enable_authentication = False
        self.security.api_key_required = False
        self.security.rate_limit_requests_per_minute = 1000
        
        # Performance settings
        self.performance.max_concurrent_requests = 10
        self.performance.connection_pool_size = 5
        self.performance.cache_size_mb = 256
        
        # Monitoring settings
        self.monitoring.enable_metrics = True
        self.monitoring.log_level = "DEBUG"
        
        # Backup settings
        self.backup.enable_backup = False
        
        # Use mock provider for development
        self.vector_database.provider = VectorDatabaseProvider.MOCK
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "testing": self.testing,
            "vector_database": {
                "provider": self.vector_database.provider.value,
                "host": self.vector_database.host,
                "port": self.vector_database.port,
                "database_name": self.vector_database.database_name,
                "collection_name": self.vector_database.collection_name,
                "index_name": self.vector_database.index_name,
                "dimension": self.vector_database.dimension,
                "metric": self.vector_database.metric,
                "ef_construction": self.vector_database.ef_construction,
                "max_connections": self.vector_database.max_connections,
                "batch_size": self.vector_database.batch_size,
                "replication_factor": self.vector_database.replication_factor,
                "enable_sharding": self.vector_database.enable_sharding,
                "shard_count": self.vector_database.shard_count
            },
            "document_processing": {
                "chunk_size": self.document_processing.chunk_size,
                "chunk_overlap": self.document_processing.chunk_overlap,
                "min_chunk_size": self.document_processing.min_chunk_size,
                "max_chunk_size": self.document_processing.max_chunk_size,
                "enable_text_cleaning": self.document_processing.enable_text_cleaning,
                "remove_special_characters": self.document_processing.remove_special_characters,
                "normalize_whitespace": self.document_processing.normalize_whitespace,
                "default_language": self.document_processing.default_language,
                "enable_language_detection": self.document_processing.enable_language_detection,
                "extract_metadata": self.document_processing.extract_metadata,
                "metadata_fields": self.document_processing.metadata_fields
            },
            "embedding": {
                "model_name": self.embedding.model_name,
                "model_path": self.embedding.model_path,
                "device": self.embedding.device,
                "batch_size": self.embedding.batch_size,
                "max_sequence_length": self.embedding.max_sequence_length,
                "normalize_embeddings": self.embedding.normalize_embeddings,
                "enable_embedding_cache": self.embedding.enable_embedding_cache,
                "cache_size": self.embedding.cache_size,
                "use_half_precision": self.embedding.use_half_precision,
                "compile_model": self.embedding.compile_model
            },
            "security": {
                "enable_authentication": self.security.enable_authentication,
                "api_key_required": self.security.api_key_required,
                "max_request_size": self.security.max_request_size,
                "rate_limit_requests_per_minute": self.security.rate_limit_requests_per_minute,
                "allowed_origins": self.security.allowed_origins,
                "encrypt_at_rest": self.security.encrypt_at_rest,
                "encrypt_in_transit": self.security.encrypt_in_transit,
                "session_timeout_minutes": self.security.session_timeout_minutes
            },
            "performance": {
                "max_concurrent_requests": self.performance.max_concurrent_requests,
                "connection_pool_size": self.performance.connection_pool_size,
                "query_timeout_seconds": self.performance.query_timeout_seconds,
                "cache_size_mb": self.performance.cache_size_mb,
                "enable_query_cache": self.performance.enable_query_cache,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "batch_size": self.performance.batch_size,
                "max_document_size_mb": self.performance.max_document_size_mb,
                "embedding_batch_size": self.performance.embedding_batch_size,
                "search_result_limit": self.performance.search_result_limit
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "metrics_port": self.monitoring.metrics_port,
                "log_level": self.monitoring.log_level,
                "log_format": self.monitoring.log_format,
                "enable_tracing": self.monitoring.enable_tracing,
                "health_check_interval_seconds": self.monitoring.health_check_interval_seconds,
                "alert_thresholds": self.monitoring.alert_thresholds
            },
            "backup": {
                "enable_backup": self.backup.enable_backup,
                "backup_interval_hours": self.backup.backup_interval_hours,
                "backup_retention_days": self.backup.backup_retention_days,
                "backup_storage_path": self.backup.backup_storage_path,
                "enable_point_in_time_recovery": self.backup.enable_point_in_time_recovery,
                "backup_encryption": self.backup.backup_encryption
            }
        }
    
    @classmethod
    def from_environment(cls, env: str = None) -> "VPAVectorDatabaseDeploymentConfig":
        """Create configuration from environment"""
        if env is None:
            env = os.getenv("VPA_ENVIRONMENT", "development")
        
        try:
            environment = DeploymentEnvironment(env.lower())
        except ValueError:
            environment = DeploymentEnvironment.DEVELOPMENT
        
        config = cls(environment=environment)
        
        # Override with environment variables
        config._load_from_environment()
        
        return config
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Vector database settings
        if os.getenv("VPA_VECTOR_DB_PROVIDER"):
            try:
                self.vector_database.provider = VectorDatabaseProvider(
                    os.getenv("VPA_VECTOR_DB_PROVIDER")
                )
            except ValueError:
                pass
        
        self.vector_database.host = os.getenv("VPA_VECTOR_DB_HOST", self.vector_database.host)
        self.vector_database.port = int(os.getenv("VPA_VECTOR_DB_PORT", self.vector_database.port))
        self.vector_database.username = os.getenv("VPA_VECTOR_DB_USERNAME")
        self.vector_database.password = os.getenv("VPA_VECTOR_DB_PASSWORD")
        self.vector_database.api_key = os.getenv("VPA_VECTOR_DB_API_KEY")
        
        # Embedding settings
        self.embedding.model_name = os.getenv("VPA_EMBEDDING_MODEL", self.embedding.model_name)
        self.embedding.device = os.getenv("VPA_EMBEDDING_DEVICE", self.embedding.device)
        
        # Security settings
        self.security.enable_authentication = os.getenv("VPA_ENABLE_AUTH", "true").lower() == "true"
        self.security.api_key_required = os.getenv("VPA_REQUIRE_API_KEY", "true").lower() == "true"
        
        # Performance settings
        self.performance.max_concurrent_requests = int(
            os.getenv("VPA_MAX_CONCURRENT_REQUESTS", self.performance.max_concurrent_requests)
        )
        self.performance.cache_size_mb = int(
            os.getenv("VPA_CACHE_SIZE_MB", self.performance.cache_size_mb)
        )
        
        # Monitoring settings
        self.monitoring.log_level = os.getenv("VPA_LOG_LEVEL", self.monitoring.log_level)
        self.monitoring.enable_metrics = os.getenv("VPA_ENABLE_METRICS", "true").lower() == "true"


# Pre-configured environments
DEVELOPMENT_CONFIG = VPAVectorDatabaseDeploymentConfig(
    environment=DeploymentEnvironment.DEVELOPMENT
)

STAGING_CONFIG = VPAVectorDatabaseDeploymentConfig(
    environment=DeploymentEnvironment.STAGING
)

PRODUCTION_CONFIG = VPAVectorDatabaseDeploymentConfig(
    environment=DeploymentEnvironment.PRODUCTION
)


def get_config(environment: str = None) -> VPAVectorDatabaseDeploymentConfig:
    """
    Get configuration for specified environment
    
    Args:
        environment: Environment name (development, staging, production)
    
    Returns:
        Configuration object
    """
    return VPAVectorDatabaseDeploymentConfig.from_environment(environment)


def validate_config(config: VPAVectorDatabaseDeploymentConfig) -> List[str]:
    """
    Validate configuration settings
    
    Args:
        config: Configuration to validate
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Validate vector database settings
    if not config.vector_database.host:
        errors.append("Vector database host is required")
    
    if config.vector_database.port <= 0:
        errors.append("Vector database port must be positive")
    
    if config.vector_database.dimension <= 0:
        errors.append("Vector dimension must be positive")
    
    # Validate document processing settings
    if config.document_processing.chunk_size <= 0:
        errors.append("Chunk size must be positive")
    
    if config.document_processing.chunk_overlap >= config.document_processing.chunk_size:
        errors.append("Chunk overlap must be less than chunk size")
    
    # Validate performance settings
    if config.performance.max_concurrent_requests <= 0:
        errors.append("Max concurrent requests must be positive")
    
    if config.performance.connection_pool_size <= 0:
        errors.append("Connection pool size must be positive")
    
    # Validate security settings for production
    if config.environment == DeploymentEnvironment.PRODUCTION:
        if not config.security.enable_authentication:
            errors.append("Authentication must be enabled in production")
        
        if not config.security.encrypt_at_rest:
            errors.append("Encryption at rest must be enabled in production")
        
        if not config.security.encrypt_in_transit:
            errors.append("Encryption in transit must be enabled in production")
    
    return errors


if __name__ == "__main__":
    # Example usage
    config = get_config("production")
    errors = validate_config(config)
    
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration validation passed")
        print(f"Environment: {config.environment.value}")
        print(f"Vector DB Provider: {config.vector_database.provider.value}")
        print(f"Authentication: {config.security.enable_authentication}")
        print(f"Backup: {config.backup.enable_backup}")
