"""
VPA RAG (Retrieval-Augmented Generation) System

This module implements the RAG system for the VPA, enabling context-aware
conversations by retrieving relevant information from stored knowledge.

Features:
- Document ingestion and vectorization
- Semantic search and retrieval
- Context integration with conversation flow
- User-specific knowledge management
- Integration with authentication system

Security:
- User-scoped knowledge isolation
- Encrypted storage of sensitive documents
- Access control integration
"""

import json
import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import tempfile
import os

# Vector storage and embeddings
try:
    import numpy as np
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    np = None
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from .database import ConversationDatabaseManager
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeChunk:
    """Represents a chunk of knowledge in the RAG system"""
    chunk_id: str
    user_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeChunk':
        """Create from dictionary"""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class DocumentMetadata:
    """Metadata for ingested documents"""
    document_id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    ingested_at: datetime
    last_accessed: Optional[datetime] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['ingested_at'] = self.ingested_at.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        """Create from dictionary"""
        data['ingested_at'] = datetime.fromisoformat(data['ingested_at'])
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


class VPARAGSystem:
    """
    VPA RAG (Retrieval-Augmented Generation) System
    
    Provides semantic search and context retrieval for enhanced conversations.
    Integrates with the VPA authentication and database systems.
    """
    
    def __init__(self, db_manager: ConversationDatabaseManager, 
                 model_name: str = "all-MiniLM-L6-v2",
                 vector_dim: int = 384,
                 max_chunk_size: int = 512):
        """
        Initialize the RAG system
        
        Args:
            db_manager: Database manager for storage
            model_name: Sentence transformer model name
            vector_dim: Vector dimension for embeddings
            max_chunk_size: Maximum size for text chunks
        """
        self.db_manager = db_manager
        self.model_name = model_name
        self.vector_dim = vector_dim
        self.max_chunk_size = max_chunk_size
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Initialize vector storage
        self._init_vector_storage()
        
        # Initialize database tables
        self._init_rag_tables()
        
        logger.info(f"VPA RAG System initialized with model: {model_name}")

    def _init_embedding_model(self):
        """Initialize the sentence transformer model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("Sentence Transformers not available. RAG functionality will be limited.")
            self.embedding_model = None
            return
            
        try:
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None

    def _init_vector_storage(self):
        """Initialize FAISS vector index"""
        if not FAISS_AVAILABLE or self.embedding_model is None:
            logger.warning("FAISS not available or no embedding model. Using fallback search.")
            self.vector_index = None
            return
            
        try:
            # Create FAISS index for similarity search
            self.vector_index = faiss.IndexFlatIP(self.vector_dim)  # Inner product for cosine similarity
            logger.info(f"Initialized FAISS index with dimension: {self.vector_dim}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            self.vector_index = None

    def _init_rag_tables(self):
        """Initialize RAG-specific database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Knowledge chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_knowledge_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (username)
                )
            """)
            
            # Document metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_documents (
                    document_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    tags TEXT,
                    description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (username)
                )
            """)
            
            # Vector index mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_vector_index (
                    chunk_id TEXT PRIMARY KEY,
                    vector_position INTEGER NOT NULL,
                    FOREIGN KEY (chunk_id) REFERENCES rag_knowledge_chunks (chunk_id)
                )
            """)
            
            conn.commit()
            
        logger.info("RAG database tables initialized")

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = None
        try:
            conn = self.db_manager._get_connection()
            yield conn
        finally:
            if conn:
                conn.close()

    def ingest_document(self, user_id: str, content: str, filename: str,
                       file_type: str = "text", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Ingest a document into the RAG system
        
        Args:
            user_id: User ID who owns this document
            content: Document content
            filename: Original filename
            file_type: Type of file (text, pdf, etc.)
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        if not user_id or not content:
            raise ValueError("User ID and content are required")
            
        # Generate document ID
        document_id = self._generate_document_id(user_id, filename, content)
        
        # Chunk the document
        chunks = self._chunk_text(content)
        
        # Process chunks and create embeddings
        knowledge_chunks = []
        for i, chunk_content in enumerate(chunks):
            chunk_id = f"{document_id}_{i}"
            
            # Create embedding if model is available
            embedding = None
            if self.embedding_model:
                try:
                    embedding = self.embedding_model.encode(chunk_content).tolist()
                except Exception as e:
                    logger.warning(f"Failed to create embedding for chunk {chunk_id}: {e}")
            
            # Create knowledge chunk
            chunk_metadata = {
                "chunk_index": i,
                "filename": filename,
                "file_type": file_type,
                **(metadata or {})
            }
            
            chunk = KnowledgeChunk(
                chunk_id=chunk_id,
                user_id=user_id,
                document_id=document_id,
                content=chunk_content,
                metadata=chunk_metadata,
                embedding=embedding,
                created_at=datetime.now()
            )
            
            knowledge_chunks.append(chunk)
        
        # Store in database
        self._store_document_and_chunks(document_id, user_id, filename, file_type,
                                      len(content), knowledge_chunks, metadata)
        
        # Update vector index
        if self.vector_index and knowledge_chunks:
            self._update_vector_index(knowledge_chunks)
        
        logger.info(f"Ingested document {filename} for user {user_id}: {len(chunks)} chunks")
        return document_id

    def _generate_document_id(self, user_id: str, filename: str, content: str) -> str:
        """Generate unique document ID"""
        unique_string = f"{user_id}_{filename}_{len(content)}_{datetime.now().isoformat()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing
        
        Simple implementation - can be enhanced with more sophisticated chunking
        """
        chunks = []
        words = text.split()
        
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > self.max_chunk_size and current_chunk:
                # Save current chunk and start new one
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _store_document_and_chunks(self, document_id: str, user_id: str, filename: str,
                                 file_type: str, file_size: int, chunks: List[KnowledgeChunk],
                                 metadata: Optional[Dict[str, Any]] = None):
        """Store document metadata and chunks in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Store document metadata
            doc_metadata = DocumentMetadata(
                document_id=document_id,
                user_id=user_id,
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                chunk_count=len(chunks),
                ingested_at=datetime.now(),
                tags=metadata.get("tags") if metadata else None,
                description=metadata.get("description") if metadata else None
            )
            
            cursor.execute("""
                INSERT INTO rag_documents 
                (document_id, user_id, filename, file_type, file_size, chunk_count,
                 ingested_at, tags, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_metadata.document_id,
                doc_metadata.user_id,
                doc_metadata.filename,
                doc_metadata.file_type,
                doc_metadata.file_size,
                doc_metadata.chunk_count,
                doc_metadata.ingested_at,
                json.dumps(doc_metadata.tags) if doc_metadata.tags else None,
                doc_metadata.description
            ))
            
            # Store chunks
            for chunk in chunks:
                embedding_blob = None
                if chunk.embedding:
                    embedding_blob = json.dumps(chunk.embedding).encode()
                
                cursor.execute("""
                    INSERT INTO rag_knowledge_chunks
                    (chunk_id, user_id, document_id, content, metadata, embedding, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id,
                    chunk.user_id,
                    chunk.document_id,
                    chunk.content,
                    json.dumps(chunk.metadata),
                    embedding_blob,
                    chunk.created_at
                ))
            
            conn.commit()

    def _update_vector_index(self, chunks: List[KnowledgeChunk]):
        """Update FAISS vector index with new chunks"""
        if not self.vector_index or not chunks:
            return
            
        # Get embeddings for chunks that have them
        embeddings = []
        chunk_ids = []
        
        for chunk in chunks:
            if chunk.embedding:
                embeddings.append(chunk.embedding)
                chunk_ids.append(chunk.chunk_id)
        
        if not embeddings:
            return
            
        # Convert to numpy array and add to index
        embedding_matrix = np.array(embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embedding_matrix)
        
        # Get current index size for position tracking
        start_position = self.vector_index.ntotal
        
        # Add to FAISS index
        self.vector_index.add(embedding_matrix)
        
        # Store position mapping in database
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for i, chunk_id in enumerate(chunk_ids):
                cursor.execute("""
                    INSERT INTO rag_vector_index (chunk_id, vector_position)
                    VALUES (?, ?)
                """, (chunk_id, start_position + i))
            conn.commit()

    def search_knowledge(self, user_id: str, query: str, top_k: int = 5,
                        min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """
        Search for relevant knowledge chunks
        
        Args:
            user_id: User ID to scope search
            query: Search query
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of relevant chunks with similarity scores
        """
        if not query:
            return []
        
        # Try vector search first if available
        if self.embedding_model and self.vector_index and self.vector_index.ntotal > 0:
            return self._vector_search(user_id, query, top_k, min_similarity)
        else:
            # Fallback to text search
            return self._text_search(user_id, query, top_k)

    def _vector_search(self, user_id: str, query: str, top_k: int,
                      min_similarity: float) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search in FAISS index
            similarities, indices = self.vector_index.search(query_vector, min(top_k * 2, self.vector_index.ntotal))
            
            # Get chunk IDs and filter by user
            results = []
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                for similarity, idx in zip(similarities[0], indices[0]):
                    if similarity < min_similarity:
                        continue
                    
                    # Get chunk ID from position
                    cursor.execute("""
                        SELECT chunk_id FROM rag_vector_index WHERE vector_position = ?
                    """, (int(idx),))
                    
                    row = cursor.fetchone()
                    if not row:
                        continue
                        
                    chunk_id = row[0]
                    
                    # Get chunk data and check user access
                    cursor.execute("""
                        SELECT chunk_id, user_id, document_id, content, metadata, created_at
                        FROM rag_knowledge_chunks
                        WHERE chunk_id = ? AND user_id = ?
                    """, (chunk_id, user_id))
                    
                    chunk_row = cursor.fetchone()
                    if chunk_row:
                        results.append({
                            "chunk_id": chunk_row[0],
                            "user_id": chunk_row[1],
                            "document_id": chunk_row[2],
                            "content": chunk_row[3],
                            "metadata": json.loads(chunk_row[4]),
                            "created_at": chunk_row[5],
                            "similarity": float(similarity)
                        })
                    
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return self._text_search(user_id, query, top_k)

    def _text_search(self, user_id: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback text-based search using SQLite FTS"""
        results = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Simple text search - can be enhanced with FTS
            cursor.execute("""
                SELECT chunk_id, user_id, document_id, content, metadata, created_at
                FROM rag_knowledge_chunks
                WHERE user_id = ? AND content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, f"%{query}%", top_k))
            
            for row in cursor.fetchall():
                results.append({
                    "chunk_id": row[0],
                    "user_id": row[1],
                    "document_id": row[2],
                    "content": row[3],
                    "metadata": json.loads(row[4]),
                    "created_at": row[5],
                    "similarity": 0.5  # Default similarity for text search
                })
        
        return results

    def get_user_documents(self, user_id: str) -> List[DocumentMetadata]:
        """Get all documents for a user"""
        documents = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT document_id, user_id, filename, file_type, file_size,
                       chunk_count, ingested_at, last_accessed, tags, description
                FROM rag_documents
                WHERE user_id = ?
                ORDER BY ingested_at DESC
            """, (user_id,))
            
            for row in cursor.fetchall():
                doc_data = {
                    "document_id": row[0],
                    "user_id": row[1],
                    "filename": row[2],
                    "file_type": row[3],
                    "file_size": row[4],
                    "chunk_count": row[5],
                    "ingested_at": row[6],
                    "last_accessed": row[7],
                    "tags": json.loads(row[8]) if row[8] else None,
                    "description": row[9]
                }
                documents.append(DocumentMetadata.from_dict(doc_data))
        
        return documents

    def delete_document(self, user_id: str, document_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Verify user owns the document
                cursor.execute("""
                    SELECT document_id FROM rag_documents
                    WHERE document_id = ? AND user_id = ?
                """, (document_id, user_id))
                
                if not cursor.fetchone():
                    return False
                
                # Delete chunks first
                cursor.execute("""
                    DELETE FROM rag_knowledge_chunks
                    WHERE document_id = ? AND user_id = ?
                """, (document_id, user_id))
                
                # Delete vector index entries
                cursor.execute("""
                    DELETE FROM rag_vector_index
                    WHERE chunk_id LIKE ?
                """, (f"{document_id}_%",))
                
                # Delete document metadata
                cursor.execute("""
                    DELETE FROM rag_documents
                    WHERE document_id = ? AND user_id = ?
                """, (document_id, user_id))
                
                conn.commit()
                
                logger.info(f"Deleted document {document_id} for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    def get_rag_stats(self, user_id: str) -> Dict[str, Any]:
        """Get RAG system statistics for a user"""
        stats = {
            "documents": 0,
            "chunks": 0,
            "total_content_size": 0,
            "vector_index_size": 0,
            "last_ingestion": None
        }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Document count and total size
            cursor.execute("""
                SELECT COUNT(*), SUM(file_size), MAX(ingested_at)
                FROM rag_documents
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                stats["documents"] = row[0] or 0
                stats["total_content_size"] = row[1] or 0
                stats["last_ingestion"] = row[2]
            
            # Chunk count
            cursor.execute("""
                SELECT COUNT(*)
                FROM rag_knowledge_chunks
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                stats["chunks"] = row[0] or 0
        
        # Vector index size
        if self.vector_index:
            stats["vector_index_size"] = self.vector_index.ntotal
        
        return stats


def create_rag_system(db_manager: ConversationDatabaseManager,
                     model_name: str = "all-MiniLM-L6-v2") -> VPARAGSystem:
    """
    Factory function to create a VPA RAG system
    
    Args:
        db_manager: Database manager instance
        model_name: Sentence transformer model name
        
    Returns:
        Configured VPA RAG system
    """
    return VPARAGSystem(db_manager, model_name)


# RAG integration with conversation flow
def enhance_conversation_with_rag(rag_system: VPARAGSystem, user_id: str,
                                 user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance conversation context with relevant knowledge from RAG system
    
    Args:
        rag_system: VPA RAG system instance
        user_id: User ID
        user_message: User's message
        context: Current conversation context
        
    Returns:
        Enhanced context with relevant knowledge
    """
    try:
        # Search for relevant knowledge
        relevant_chunks = rag_system.search_knowledge(user_id, user_message, top_k=3)
        
        if relevant_chunks:
            # Add relevant knowledge to context
            context["rag_context"] = {
                "relevant_chunks": relevant_chunks,
                "source_documents": list(set(chunk["document_id"] for chunk in relevant_chunks)),
                "search_query": user_message
            }
            
            # Create summary of relevant content
            relevant_content = []
            for chunk in relevant_chunks:
                relevant_content.append({
                    "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                    "source": chunk["metadata"].get("filename", "Unknown"),
                    "similarity": chunk["similarity"]
                })
            
            context["rag_summary"] = relevant_content
            
            logger.info(f"Enhanced conversation with {len(relevant_chunks)} relevant chunks for user {user_id}")
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to enhance conversation with RAG: {e}")
        return context


if __name__ == "__main__":
    # Example usage and testing
    import tempfile
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
    
    # Initialize system
    db_manager = ConversationDatabaseManager(Path(db_path))
    rag_system = create_rag_system(db_manager)
    
    print("VPA RAG System initialized successfully!")
    print(f"Vector index available: {rag_system.vector_index is not None}")
    print(f"Embedding model available: {rag_system.embedding_model is not None}")
    
    # Clean up
    os.unlink(db_path)
