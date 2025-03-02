import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHROMA_PERSIST_DIRECTORY

class VectorStore:
    def __init__(self):
        # Create the persistence directory if it doesn't exist
        os.makedirs(CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
        
        # Use sentence-transformers model for embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name="documents",
                embedding_function=self.embedding_function
            )
        except:
            self.collection = self.client.create_collection(
                name="documents",
                embedding_function=self.embedding_function
            )

    def add_document(self, doc_id, text, metadata):
        """
        Add a document to the vector store
        Returns the unique vector ID
        """
        # Generate a unique ID for the vector
        vector_id = str(uuid.uuid4())
        
        # Extract text snippet for embedding (limit length)
        text_for_embedding = text[:8000]  # Limit for performance
        
        # Add document metadata
        doc_metadata = {
            "doc_id": str(doc_id),
            "filename": metadata.get("filename", ""),
            "doc_type": metadata.get("type", ""),
            "summary": metadata.get("summary", "")
        }
        
        # Add document to collection
        self.collection.add(
            ids=[vector_id],
            documents=[text_for_embedding],
            metadatas=[doc_metadata]
        )
        
        return vector_id

    def search_similar(self, query_text, limit=5):
        """
        Search for documents similar to the query text
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=limit
        )
        
        search_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                score = results['distances'][0][i] if 'distances' in results else 0.0
                # Convert distance to similarity score (ChromaDB returns distances)
                similarity = 1.0 - min(score, 1.0)
                
                search_results.append({
                    "vector_id": id,
                    "doc_id": int(metadata["doc_id"]),
                    "filename": metadata["filename"],
                    "score": similarity,
                    "doc_type": metadata["doc_type"],
                    "summary": metadata["summary"]
                })
        
        return search_results
    
    def find_related(self, doc_id, doc_text, limit=5):
        """Find documents related to the given document"""
        # Use the document text to find similar documents
        results = self.collection.query(
            query_texts=[doc_text[:8000]],  # Limit text for performance
            n_results=limit + 1,  # Get extra to filter out the document itself
            where={"doc_id": {"$ne": str(doc_id)}}  # Exclude the current document
        )
        
        search_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                score = results['distances'][0][i] if 'distances' in results else 0.0
                # Convert distance to similarity score
                similarity = 1.0 - min(score, 1.0)
                
                search_results.append({
                    "vector_id": id,
                    "doc_id": int(metadata["doc_id"]),
                    "filename": metadata["filename"],
                    "score": similarity,
                    "doc_type": metadata["doc_type"],
                    "summary": metadata["summary"]
                })
        
        return search_results[:limit]
    
    def delete_document(self, vector_id):
        """Delete a document from the vector store"""
        try:
            self.collection.delete(ids=[vector_id])
            return True
        except Exception as e:
            print(f"Error deleting document from vector store: {e}")
            return False