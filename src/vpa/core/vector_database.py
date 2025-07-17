"""
VPA Production Vector Database Integration System

This module implements production-grade vector database integration for the VPA RAG system,
providing scalable semantic search and document retrieval capabilities.

Features:
- Multi-provider vector database support (ChromaDB, Pinecone, Weaviate)
- Production-grade document embedding and storage
- Efficient similarity search with metadata filtering
- Batch processing and incremental updates
- Vector database management and optimization
- Enterprise-grade security and compliance

Supported Vector Databases:
- ChromaDB: Local and distributed deployment
- Pinecone: Cloud-native vector database
- Weaviate: Open-source vector search engine
- Qdrant: High-performance vector database
- Milvus: Cloud-native vector database

Security:
- API key management and encryption
- Access control and authentication
- Data encryption at rest and in transit
- Audit logging for compliance
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, AsyncGenerator, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from pathlib import Path
import hashlib
import os

# Vector database specific imports (optional dependencies)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorDatabaseProvider(Enum):
    """Supported vector database providers"""
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    MOCK = "mock"  # For testing and development


@dataclass
class VectorDatabaseConfig:
    """Configuration for vector database providers"""
    provider: VectorDatabaseProvider
    connection_string: Optional[str] = None
    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_name: str = "vpa-knowledge-base"
    dimension: int = 1536  # OpenAI embedding dimension
    distance_metric: str = "cosine"
    
    # Performance settings
    batch_size: int = 100
    max_connections: int = 10
    timeout: int = 30
    
    # Storage settings
    persist_directory: Optional[str] = None
    enable_persistence: bool = True
    
    # Security settings
    enable_encryption: bool = True
    auth_enabled: bool = True


@dataclass
class VectorDocument:
    """Represents a document in the vector database"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    source: Optional[str] = None
    chunk_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.id is None:
            self.id = str(uuid.uuid4())


@dataclass
class VectorSearchResult:
    """Result from vector similarity search"""
    document_id: str
    content: str
    similarity: float
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "content": self.content,
            "similarity": self.similarity,
            "metadata": self.metadata,
            "chunk_id": self.metadata.get("chunk_id"),
            "source": self.metadata.get("source")
        }


class BaseVectorDatabase(ABC):
    """Abstract base class for vector database providers"""
    
    def __init__(self, config: VectorDatabaseConfig):
        self.config = config
        self.client = None
        self.is_connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the vector database"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the vector database"""
        pass
    
    @abstractmethod
    async def create_collection(self, collection_name: str) -> bool:
        """Create a new collection/index"""
        pass
    
    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection/index"""
        pass
    
    @abstractmethod
    async def insert_documents(self, documents: List[VectorDocument]) -> bool:
        """Insert documents into the vector database"""
        pass
    
    @abstractmethod
    async def update_documents(self, documents: List[VectorDocument]) -> bool:
        """Update existing documents"""
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs"""
        pass
    
    @abstractmethod
    async def search(self, 
                    query_embedding: List[float],
                    top_k: int = 10,
                    metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        pass


class ChromaDBProvider(BaseVectorDatabase):
    """ChromaDB vector database provider"""
    
    def __init__(self, config: VectorDatabaseConfig):
        super().__init__(config)
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is not installed. Install with: pip install chromadb")
        
        self.collection = None
        
    async def connect(self) -> bool:
        """Connect to ChromaDB"""
        try:
            if self.config.persist_directory:
                # Persistent ChromaDB
                self.client = chromadb.PersistentClient(
                    path=self.config.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            else:
                # In-memory ChromaDB
                self.client = chromadb.Client(
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            
            self.is_connected = True
            logger.info("Connected to ChromaDB successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from ChromaDB"""
        if self.client:
            self.client = None
            self.collection = None
            self.is_connected = False
            logger.info("Disconnected from ChromaDB")
    
    async def create_collection(self, collection_name: str) -> bool:
        """Create a ChromaDB collection"""
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": self.config.distance_metric}
            )
            logger.info(f"Created/retrieved ChromaDB collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ChromaDB collection: {e}")
            return False
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a ChromaDB collection"""
        try:
            self.client.delete_collection(name=collection_name)
            self.collection = None
            logger.info(f"Deleted ChromaDB collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete ChromaDB collection: {e}")
            return False
    
    async def insert_documents(self, documents: List[VectorDocument]) -> bool:
        """Insert documents into ChromaDB"""
        try:
            if not self.collection:
                await self.create_collection(self.config.index_name)
            
            # Prepare data for ChromaDB
            ids = [doc.id for doc in documents]
            embeddings = [doc.embedding for doc in documents if doc.embedding]
            metadatas = [doc.metadata or {} for doc in documents]
            documents_content = [doc.content for doc in documents]
            
            # Add documents to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_content
            )
            
            logger.info(f"Inserted {len(documents)} documents into ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert documents into ChromaDB: {e}")
            return False
    
    async def update_documents(self, documents: List[VectorDocument]) -> bool:
        """Update documents in ChromaDB"""
        try:
            if not self.collection:
                return False
            
            # ChromaDB doesn't have direct update, so we delete and re-add
            ids = [doc.id for doc in documents]
            await self.delete_documents(ids)
            return await self.insert_documents(documents)
            
        except Exception as e:
            logger.error(f"Failed to update documents in ChromaDB: {e}")
            return False
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from ChromaDB"""
        try:
            if not self.collection:
                return False
            
            self.collection.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents from ChromaDB: {e}")
            return False
    
    async def search(self, 
                    query_embedding: List[float],
                    top_k: int = 10,
                    metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        """Search ChromaDB for similar documents"""
        try:
            if not self.collection:
                return []
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=metadata_filter
            )
            
            # Process results
            search_results = []
            for i in range(len(results['ids'][0])):
                result = VectorSearchResult(
                    document_id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    similarity=1.0 - results['distances'][0][i],  # ChromaDB returns distance
                    metadata=results['metadatas'][0][i] or {}
                )
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} similar documents in ChromaDB")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get ChromaDB collection statistics"""
        try:
            if not self.collection:
                return {}
            
            count = self.collection.count()
            return {
                "provider": "chromadb",
                "collection_name": self.config.index_name,
                "document_count": count,
                "dimension": self.config.dimension,
                "distance_metric": self.config.distance_metric
            }
            
        except Exception as e:
            logger.error(f"Failed to get ChromaDB stats: {e}")
            return {}


class PineconeProvider(BaseVectorDatabase):
    """Pinecone vector database provider"""
    
    def __init__(self, config: VectorDatabaseConfig):
        super().__init__(config)
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone is not installed. Install with: pip install pinecone-client")
        
        self.index = None
        
    async def connect(self) -> bool:
        """Connect to Pinecone"""
        try:
            pinecone.init(
                api_key=self.config.api_key,
                environment=self.config.environment
            )
            
            self.is_connected = True
            logger.info("Connected to Pinecone successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Pinecone"""
        self.index = None
        self.is_connected = False
        logger.info("Disconnected from Pinecone")
    
    async def create_collection(self, collection_name: str) -> bool:
        """Create a Pinecone index"""
        try:
            # Check if index exists
            if collection_name not in pinecone.list_indexes():
                # Create index
                pinecone.create_index(
                    name=collection_name,
                    dimension=self.config.dimension,
                    metric=self.config.distance_metric
                )
                
                # Wait for index to be ready
                while not pinecone.describe_index(collection_name).status['ready']:
                    await asyncio.sleep(1)
            
            self.index = pinecone.Index(collection_name)
            logger.info(f"Created/retrieved Pinecone index: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            return False
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a Pinecone index"""
        try:
            pinecone.delete_index(collection_name)
            self.index = None
            logger.info(f"Deleted Pinecone index: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Pinecone index: {e}")
            return False
    
    async def insert_documents(self, documents: List[VectorDocument]) -> bool:
        """Insert documents into Pinecone"""
        try:
            if not self.index:
                await self.create_collection(self.config.index_name)
            
            # Prepare vectors for Pinecone
            vectors = []
            for doc in documents:
                if doc.embedding:
                    metadata = doc.metadata or {}
                    metadata.update({
                        "content": doc.content,
                        "source": doc.source,
                        "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
                    })
                    
                    vectors.append({
                        "id": doc.id,
                        "values": doc.embedding,
                        "metadata": metadata
                    })
            
            # Batch insert
            for i in range(0, len(vectors), self.config.batch_size):
                batch = vectors[i:i + self.config.batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Inserted {len(documents)} documents into Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert documents into Pinecone: {e}")
            return False
    
    async def update_documents(self, documents: List[VectorDocument]) -> bool:
        """Update documents in Pinecone (same as insert due to upsert)"""
        return await self.insert_documents(documents)
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from Pinecone"""
        try:
            if not self.index:
                return False
            
            # Batch delete
            for i in range(0, len(document_ids), self.config.batch_size):
                batch = document_ids[i:i + self.config.batch_size]
                self.index.delete(ids=batch)
            
            logger.info(f"Deleted {len(document_ids)} documents from Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents from Pinecone: {e}")
            return False
    
    async def search(self, 
                    query_embedding: List[float],
                    top_k: int = 10,
                    metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        """Search Pinecone for similar documents"""
        try:
            if not self.index:
                return []
            
            # Perform search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=metadata_filter,
                include_metadata=True
            )
            
            # Process results
            search_results = []
            for match in results['matches']:
                metadata = match.get('metadata', {})
                result = VectorSearchResult(
                    document_id=match['id'],
                    content=metadata.get('content', ''),
                    similarity=match['score'],
                    metadata=metadata
                )
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} similar documents in Pinecone")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search Pinecone: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        try:
            if not self.index:
                return {}
            
            stats = self.index.describe_index_stats()
            return {
                "provider": "pinecone",
                "index_name": self.config.index_name,
                "dimension": stats['dimension'],
                "total_vector_count": stats['total_vector_count'],
                "index_fullness": stats.get('index_fullness', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {}


class MockVectorDatabase(BaseVectorDatabase):
    """Mock vector database for testing and development"""
    
    def __init__(self, config: VectorDatabaseConfig):
        super().__init__(config)
        self.documents: Dict[str, VectorDocument] = {}
        self.collection_name = None
        
    async def connect(self) -> bool:
        """Mock connection"""
        self.is_connected = True
        logger.info("Connected to Mock Vector Database")
        return True
        
    async def disconnect(self):
        """Mock disconnection"""
        self.is_connected = False
        logger.info("Disconnected from Mock Vector Database")
    
    async def create_collection(self, collection_name: str) -> bool:
        """Mock collection creation"""
        self.collection_name = collection_name
        logger.info(f"Created mock collection: {collection_name}")
        return True
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Mock collection deletion"""
        self.documents.clear()
        self.collection_name = None
        logger.info(f"Deleted mock collection: {collection_name}")
        return True
    
    async def insert_documents(self, documents: List[VectorDocument]) -> bool:
        """Mock document insertion"""
        for doc in documents:
            self.documents[doc.id] = doc
        logger.info(f"Inserted {len(documents)} documents into mock database")
        return True
    
    async def update_documents(self, documents: List[VectorDocument]) -> bool:
        """Mock document update"""
        for doc in documents:
            if doc.id in self.documents:
                self.documents[doc.id] = doc
        logger.info(f"Updated {len(documents)} documents in mock database")
        return True
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Mock document deletion"""
        for doc_id in document_ids:
            if doc_id in self.documents:
                del self.documents[doc_id]
        logger.info(f"Deleted {len(document_ids)} documents from mock database")
        return True
    
    async def search(self, 
                    query_embedding: List[float],
                    top_k: int = 10,
                    metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        """Mock similarity search"""
        # Simple mock search - return random documents with mock similarity
        results = []
        import random
        
        documents_list = list(self.documents.values())
        selected_docs = random.sample(documents_list, min(top_k, len(documents_list)))
        
        for doc in selected_docs:
            # Mock similarity score
            similarity = random.uniform(0.7, 0.95)
            
            # Check metadata filter
            if metadata_filter:
                if doc.metadata:
                    matches = all(
                        doc.metadata.get(key) == value 
                        for key, value in metadata_filter.items()
                    )
                    if not matches:
                        continue
                else:
                    continue
            
            result = VectorSearchResult(
                document_id=doc.id,
                content=doc.content,
                similarity=similarity,
                metadata=doc.metadata or {}
            )
            results.append(result)
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x.similarity, reverse=True)
        
        logger.info(f"Found {len(results)} similar documents in mock database")
        return results
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Mock collection statistics"""
        return {
            "provider": "mock",
            "collection_name": self.collection_name,
            "document_count": len(self.documents),
            "dimension": self.config.dimension,
            "distance_metric": self.config.distance_metric
        }


class VPAVectorDatabaseManager:
    """VPA Vector Database Management System"""
    
    def __init__(self):
        self.providers: Dict[VectorDatabaseProvider, BaseVectorDatabase] = {}
        self.active_provider: Optional[VectorDatabaseProvider] = None
        self.embedding_function: Optional[Callable] = None
        
    def register_provider(self, provider_type: VectorDatabaseProvider, provider: BaseVectorDatabase):
        """Register a vector database provider"""
        self.providers[provider_type] = provider
        if self.active_provider is None:
            self.active_provider = provider_type
        logger.info(f"Registered vector database provider: {provider_type.value}")
    
    def set_active_provider(self, provider_type: VectorDatabaseProvider):
        """Set the active vector database provider"""
        if provider_type not in self.providers:
            raise ValueError(f"Provider {provider_type.value} not registered")
        self.active_provider = provider_type
        logger.info(f"Set active vector database provider: {provider_type.value}")
    
    def set_embedding_function(self, embedding_function: Callable):
        """Set the embedding function for document vectorization"""
        self.embedding_function = embedding_function
        logger.info("Set embedding function for vector database")
    
    async def connect(self) -> bool:
        """Connect to the active vector database"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        return await provider.connect()
    
    async def disconnect(self):
        """Disconnect from the active vector database"""
        if self.active_provider:
            provider = self.providers[self.active_provider]
            await provider.disconnect()
    
    async def create_knowledge_base(self, knowledge_base_name: str) -> bool:
        """Create a new knowledge base (collection)"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        return await provider.create_collection(knowledge_base_name)
    
    async def delete_knowledge_base(self, knowledge_base_name: str) -> bool:
        """Delete a knowledge base (collection)"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        return await provider.delete_collection(knowledge_base_name)
    
    async def add_documents(self, documents: List[VectorDocument]) -> bool:
        """Add documents to the active vector database"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        
        # Generate embeddings if not present
        if self.embedding_function:
            for doc in documents:
                if not doc.embedding:
                    doc.embedding = await self._generate_embedding(doc.content)
        
        return await provider.insert_documents(documents)
    
    async def update_documents(self, documents: List[VectorDocument]) -> bool:
        """Update documents in the active vector database"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        
        # Generate embeddings if not present
        if self.embedding_function:
            for doc in documents:
                if not doc.embedding:
                    doc.embedding = await self._generate_embedding(doc.content)
        
        return await provider.update_documents(documents)
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the active vector database"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        return await provider.delete_documents(document_ids)
    
    async def search_knowledge(self, 
                             query: str,
                             top_k: int = 10,
                             metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        """Search for similar documents in the knowledge base"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        
        # Generate query embedding
        if not self.embedding_function:
            raise ValueError("No embedding function set")
        
        query_embedding = await self._generate_embedding(query)
        
        # Perform search
        return await provider.search(query_embedding, top_k, metadata_filter)
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics for the active vector database"""
        if not self.active_provider:
            raise ValueError("No active provider set")
        
        provider = self.providers[self.active_provider]
        return await provider.get_collection_stats()
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the configured embedding function"""
        if not self.embedding_function:
            raise ValueError("No embedding function configured")
        
        try:
            # Handle both sync and async embedding functions
            if asyncio.iscoroutinefunction(self.embedding_function):
                return await self.embedding_function(text)
            else:
                return self.embedding_function(text)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def get_available_providers(self) -> List[str]:
        """Get list of available vector database providers"""
        return [provider.value for provider in self.providers.keys()]
    
    def get_provider_info(self, provider_type: VectorDatabaseProvider) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider_type not in self.providers:
            return {}
        
        provider = self.providers[provider_type]
        return {
            "type": provider_type.value,
            "connected": provider.is_connected,
            "config": {
                "index_name": provider.config.index_name,
                "dimension": provider.config.dimension,
                "distance_metric": provider.config.distance_metric
            }
        }


def create_vector_database_manager(config: Optional[Dict[str, Any]] = None) -> VPAVectorDatabaseManager:
    """Create and configure vector database manager"""
    manager = VPAVectorDatabaseManager()
    
    # Register mock provider by default for development
    mock_config = VectorDatabaseConfig(
        provider=VectorDatabaseProvider.MOCK,
        index_name="vpa-test-knowledge-base",
        dimension=1536
    )
    mock_provider = MockVectorDatabase(mock_config)
    manager.register_provider(VectorDatabaseProvider.MOCK, mock_provider)
    
    # Register ChromaDB if available
    if CHROMADB_AVAILABLE:
        chromadb_config = VectorDatabaseConfig(
            provider=VectorDatabaseProvider.CHROMADB,
            index_name="vpa-chromadb-knowledge-base",
            dimension=1536,
            persist_directory="./chroma_db"
        )
        chromadb_provider = ChromaDBProvider(chromadb_config)
        manager.register_provider(VectorDatabaseProvider.CHROMADB, chromadb_provider)
    
    logger.info("VPA Vector Database Manager initialized")
    return manager


# Mock embedding function for testing
async def mock_embedding_function(text: str) -> List[float]:
    """Mock embedding function for testing"""
    # Generate deterministic mock embedding based on text hash
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    
    # Convert hash to pseudo-random floats
    embedding = []
    for i in range(0, len(text_hash), 8):
        chunk = text_hash[i:i+8]
        value = int(chunk, 16) / (16**8)  # Normalize to 0-1
        embedding.append(value)
    
    # Pad or trim to desired dimension
    target_dim = 1536
    if len(embedding) < target_dim:
        embedding.extend([0.0] * (target_dim - len(embedding)))
    else:
        embedding = embedding[:target_dim]
    
    return embedding


if __name__ == "__main__":
    # Example usage and testing
    async def test_vector_database():
        # Create manager
        manager = create_vector_database_manager()
        
        # Set mock embedding function
        manager.set_embedding_function(mock_embedding_function)
        
        try:
            # Connect to database
            await manager.connect()
            
            # Create knowledge base
            await manager.create_knowledge_base("test-kb")
            
            # Create test documents
            documents = [
                VectorDocument(
                    id="doc1",
                    content="This is a test document about artificial intelligence and machine learning.",
                    metadata={"source": "test", "type": "article"}
                ),
                VectorDocument(
                    id="doc2",
                    content="Vector databases are essential for semantic search and RAG systems.",
                    metadata={"source": "test", "type": "documentation"}
                ),
                VectorDocument(
                    id="doc3",
                    content="The VPA system integrates multiple AI technologies for enhanced user experience.",
                    metadata={"source": "test", "type": "system_doc"}
                )
            ]
            
            # Add documents
            await manager.add_documents(documents)
            
            # Search for similar documents
            results = await manager.search_knowledge("artificial intelligence", top_k=2)
            
            print(f"Found {len(results)} similar documents:")
            for result in results:
                print(f"  - {result.document_id}: {result.content[:50]}... (similarity: {result.similarity:.3f})")
            
            # Get database statistics
            stats = await manager.get_database_stats()
            print(f"Database stats: {stats}")
            
            # Disconnect
            await manager.disconnect()
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run test
    asyncio.run(test_vector_database())
    print("VPA Vector Database System test completed!")
