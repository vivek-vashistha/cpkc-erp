# Vector-based RAG implementation using OpenAI embeddings and ChromaDB
import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np

class VectorRAG:
    """
    Production-grade RAG system using OpenAI embeddings and ChromaDB
    """
    
    def __init__(self, 
                 collection_name: str = "anomaly_patterns",
                 persist_directory: str = "./chroma_db",
                 openai_model: str = "text-embedding-3-small"):
        
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = openai_model
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=None  # We'll handle embeddings manually
            )
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Anomaly detection patterns and rules"}
            )
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def add_knowledge(self, 
                     category: str, 
                     title: str, 
                     content: str, 
                     metadata: Optional[Dict] = None) -> str:
        """Add knowledge item to vector database"""
        
        # Create unique ID
        item_id = str(uuid.uuid4())
        
        # Prepare text for embedding
        text_for_embedding = f"{title}. {content}"
        
        # Get embedding
        embedding = self._get_embedding(text_for_embedding)
        
        if not embedding:
            print(f"Failed to get embedding for: {title}")
            return None
        
        # Prepare metadata
        full_metadata = {
            "category": category,
            "title": title,
            "content": content,
            "created_at": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # Add to ChromaDB
        try:
            self.collection.add(
                ids=[item_id],
                embeddings=[embedding],
                documents=[text_for_embedding],
                metadatas=[full_metadata]
            )
            print(f"Added knowledge item: {title}")
            return item_id
        except Exception as e:
            print(f"Error adding to ChromaDB: {e}")
            return None
    
    def search_knowledge(self, 
                        query: str, 
                        category: Optional[str] = None, 
                        top_k: int = 5,
                        similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search knowledge base using semantic similarity"""
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        if not query_embedding:
            print(f"Failed to get embedding for query: {query}")
            return []
        
        # Prepare where clause for category filtering
        where_clause = {}
        if category:
            where_clause["category"] = category
        
        try:
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            processed_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0], 
                results["distances"][0]
            )):
                # Convert distance to similarity score (ChromaDB uses cosine distance)
                similarity_score = 1 - distance
                
                if similarity_score >= similarity_threshold:
                    processed_results.append({
                        "id": results["ids"][0][i],
                        "title": metadata.get("title", ""),
                        "content": metadata.get("content", ""),
                        "category": metadata.get("category", ""),
                        "similarity_score": similarity_score,
                        "metadata": metadata
                    })
            
            # Sort by similarity score
            processed_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return processed_results
            
        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return []
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            count = self.collection.count()
            return {
                "total_items": count,
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_items": 0, "error": str(e)}
    
    def delete_knowledge(self, item_id: str) -> bool:
        """Delete knowledge item by ID"""
        try:
            self.collection.delete(ids=[item_id])
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False
    
    def update_knowledge(self, 
                        item_id: str, 
                        title: Optional[str] = None, 
                        content: Optional[str] = None, 
                        metadata: Optional[Dict] = None) -> bool:
        """Update existing knowledge item"""
        try:
            # Get current item
            current = self.collection.get(ids=[item_id], include=["metadatas"])
            if not current["ids"]:
                return False
            
            current_metadata = current["metadatas"][0]
            
            # Update fields
            new_title = title or current_metadata.get("title", "")
            new_content = content or current_metadata.get("content", "")
            new_metadata = {**current_metadata, **(metadata or {})}
            new_metadata["updated_at"] = datetime.now().isoformat()
            
            # Get new embedding
            text_for_embedding = f"{new_title}. {new_content}"
            new_embedding = self._get_embedding(text_for_embedding)
            
            if not new_embedding:
                return False
            
            # Update in ChromaDB
            self.collection.update(
                ids=[item_id],
                embeddings=[new_embedding],
                documents=[text_for_embedding],
                metadatas=[new_metadata]
            )
            return True
            
        except Exception as e:
            print(f"Error updating item: {e}")
            return False
    
    def reset_collection(self):
        """Reset the entire collection (use with caution)"""
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Anomaly detection patterns and rules"}
            )
            print(f"Reset collection: {self.collection_name}")
        except Exception as e:
            print(f"Error resetting collection: {e}")

def setup_vector_knowledge_base():
    """Setup the vector knowledge base with initial data"""
    rag = VectorRAG()
    
    # Clear existing data for fresh setup
    rag.reset_collection()
    
    # Add comprehensive patterns
    patterns = [
        {
            "category": "patterns",
            "title": "Missing Event Sequence Pattern",
            "content": "Common pattern where waybills are missing critical events in the sequence. Most frequently missing 'At Border' event for cross-border shipments, or 'Closed' event after 'Delivered'. Resolution involves checking customs documentation, terminal records, or inserting missing events with appropriate timestamps. Success rate: 91%",
            "metadata": {"success_rate": 0.91, "frequency": "high", "anomaly_types": ["MISSING_STEP"]}
        },
        {
            "category": "patterns", 
            "title": "ID Inconsistency Pattern",
            "content": "Pattern where multiple CarId or CSNId values appear across events for the same waybill. This indicates data quality issues or equipment changes. Resolution priority: use CarId from 'Created' event (highest priority), then majority value, then earliest event with ID. Success rate: 87%",
            "metadata": {"success_rate": 0.87, "frequency": "medium", "anomaly_types": ["CARID_INCONSISTENT", "CSNID_INCONSISTENT"]}
        },
        {
            "category": "patterns",
            "title": "Sequence Error Pattern", 
            "content": "Events occurring out of chronological order, often due to system delays, manual entry errors, or timezone issues. Common examples: 'In Transit' before 'Picked Up', 'Delivered' before 'Arrived'. Resolution: reorder events based on timestamps and business logic. Success rate: 89%",
            "metadata": {"success_rate": 0.89, "frequency": "high", "anomaly_types": ["SEQUENCE_ERROR"]}
        },
        {
            "category": "patterns",
            "title": "Terminal Conflict Pattern",
            "content": "Both 'Delivered' and 'Cancelled' events present for the same waybill, indicating conflicting terminal states. This requires manual review to determine the correct final status. Resolution: review terminal records, customer confirmation, and business rules. Success rate: 85%",
            "metadata": {"success_rate": 0.85, "frequency": "low", "anomaly_types": ["TERMINAL_CONFLICT"]}
        },
        {
            "category": "patterns",
            "title": "Multiple Delivered Events Pattern",
            "content": "Multiple 'Delivered' events for the same waybill, often due to system duplicates or partial deliveries. Resolution: merge duplicate events, keep the most plausible single 'Delivered' event based on timestamps and location. Success rate: 92%",
            "metadata": {"success_rate": 0.92, "frequency": "medium", "anomaly_types": ["MULTI_DELIVERED"]}
        },
        {
            "category": "patterns",
            "title": "Post-Terminal Activity Pattern",
            "content": "Events occurring after a terminal event (Delivered or Cancelled), indicating data quality issues or system errors. Resolution: review event timestamps, validate terminal status, and remove or correct post-terminal events. Success rate: 88%",
            "metadata": {"success_rate": 0.88, "frequency": "low", "anomaly_types": ["POST_TERMINAL_ACTIVITY"]}
        }
    ]
    
    # Add business rules
    rules = [
        {
            "category": "rules",
            "title": "CPKC Event Sequence Standard",
            "content": "Required canonical sequence: Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed. Terminal events: Closed (always terminal), Cancelled (terminal, mutually exclusive with Delivered). Exceptions: Direct terminal shipments may skip 'Picked Up', cross-border shipments MUST have 'At Border' event. All events must be chronologically ordered.",
            "metadata": {"version": "2.1", "effective_date": "2025-01-01", "type": "sequence_validation"}
        },
        {
            "category": "rules",
            "title": "Equipment ID Consistency Rules", 
            "content": "CarId: Must be unique per shipment, format CPKC-XXXX. CSNId: Must be consistent across all events, format CSN-CPKC-XXXX-YYYY-MM-A. If multiple values detected, flag as anomaly requiring manual review. Resolution priority: earliest 'Created' event, then majority value, then earliest event with ID.",
            "metadata": {"version": "1.8", "effective_date": "2024-12-01", "type": "id_validation"}
        },
        {
            "category": "rules",
            "title": "Cross-Border Shipment Rules",
            "content": "All cross-border shipments MUST have 'At Border' event. Missing 'At Border' indicates data quality issue or customs processing delay. Check customs documentation for border crossing timestamps. Terminal shipments may have different event sequences.",
            "metadata": {"version": "1.5", "effective_date": "2024-11-01", "type": "border_validation"}
        },
        {
            "category": "rules",
            "title": "Timestamp Validation Rules",
            "content": "All event timestamps must be in chronological order. Negative duration between events indicates data quality issues. Events cannot occur after terminal events (Delivered/Cancelled). Timezone consistency required across all events.",
            "metadata": {"version": "1.3", "effective_date": "2024-10-01", "type": "timestamp_validation"}
        }
    ]
    
    # Add historical cases
    cases = [
        {
            "category": "cases",
            "title": "WB3005 Missing At Border Resolution",
            "content": "Waybill WB3005 had missing 'At Border' event for cross-border shipment. Resolution: Retrieved customs documentation, found border crossing timestamp, inserted 'At Border' event. Outcome: Successfully resolved, customer confirmed delivery. Resolution time: 12 minutes.",
            "metadata": {"waybill_id": "WB3005", "outcome": "success", "resolution_time": 12, "anomaly_type": "MISSING_STEP"}
        },
        {
            "category": "cases", 
            "title": "WB4002 CarId Inconsistency Resolution",
            "content": "Waybill WB4002 had multiple CarId values across events. Resolution: Applied priority rule, used CarId from 'Created' event (CPKC-1001), updated all events to consistent CarId. Outcome: Successfully resolved, data quality improved. Resolution time: 8 minutes.",
            "metadata": {"waybill_id": "WB4002", "outcome": "success", "resolution_time": 8, "anomaly_type": "CARID_INCONSISTENT"}
        },
        {
            "category": "cases",
            "title": "WB5001 Sequence Error Resolution", 
            "content": "Waybill WB5001 had 'In Transit' event before 'Picked Up' event. Resolution: Reordered events based on timestamps, validated with terminal records. Outcome: Successfully resolved, sequence corrected. Resolution time: 15 minutes.",
            "metadata": {"waybill_id": "WB5001", "outcome": "success", "resolution_time": 15, "anomaly_type": "SEQUENCE_ERROR"}
        }
    ]
    
    # Add all knowledge items
    all_items = patterns + rules + cases
    
    print(f"Adding {len(all_items)} knowledge items to vector database...")
    
    for item in all_items:
        item_id = rag.add_knowledge(
            category=item["category"],
            title=item["title"], 
            content=item["content"],
            metadata=item["metadata"]
        )
        if item_id:
            print(f"✓ Added: {item['title']}")
        else:
            print(f"✗ Failed: {item['title']}")
    
    stats = rag.get_knowledge_stats()
    print(f"\nVector knowledge base setup complete!")
    print(f"Total items: {stats['total_items']}")
    print(f"Collection: {stats['collection_name']}")
    print(f"Embedding model: {stats['embedding_model']}")
    
    return rag

if __name__ == "__main__":
    # Test the vector RAG system
    print("🚀 Setting up Vector RAG system...")
    rag = setup_vector_knowledge_base()
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    
    test_queries = [
        "missing event sequence",
        "carid inconsistency", 
        "sequence error",
        "anomaly detection waybill analysis",
        "cross border shipment rules"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag.search_knowledge(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (similarity: {result['similarity_score']:.3f})")
            print(f"     Category: {result['category']}")
            print(f"     Content: {result['content'][:100]}...")
