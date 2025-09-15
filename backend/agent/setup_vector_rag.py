# Setup script for Vector RAG system
"""
This script sets up the Vector RAG system with OpenAI embeddings and ChromaDB.
Run this script to initialize the knowledge base and test the system.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all required dependencies are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        "chromadb",
        "openai", 
        "numpy",
        "langchain_core",
        "langchain_openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install chromadb openai numpy")
        return False
    
    print("✅ All requirements satisfied!")
    return True

def check_environment():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "LOGI_API_URL", 
        "LOGI_API_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} - MISSING")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return False
    
    print("✅ All environment variables set!")
    return True

def setup_vector_knowledge_base():
    """Setup the vector knowledge base"""
    print("\n🚀 Setting up Vector Knowledge Base...")
    
    try:
        from rag.core.vector_rag import setup_vector_knowledge_base
        rag = setup_vector_knowledge_base()
        return rag
    except Exception as e:
        print(f"❌ Error setting up vector knowledge base: {e}")
        return None

def test_vector_rag():
    """Test the vector RAG system"""
    print("\n🧪 Testing Vector RAG System...")
    
    try:
        from rag.tools.vector_rag_tools import search_anomaly_patterns, get_historical_cases, get_business_rules
        
        # Test search_anomaly_patterns
        print("\n1. Testing search_anomaly_patterns...")
        result = search_anomaly_patterns.invoke({
            "query": "missing event sequence",
            "top_k": 3
        })
        print(f"   Found {result['total_found']} results")
        for pattern in result['patterns']:
            print(f"   - {pattern['title']} (similarity: {pattern['similarity_score']:.3f})")
        
        # Test get_historical_cases
        print("\n2. Testing get_historical_cases...")
        result = get_historical_cases.invoke({
            "anomaly_type": "MISSING_STEP",
            "top_k": 2
        })
        print(f"   Found {result['count']} cases")
        for case in result['cases']:
            print(f"   - {case['title']} (similarity: {case['similarity_score']:.3f})")
        
        # Test get_business_rules
        print("\n3. Testing get_business_rules...")
        result = get_business_rules.invoke({
            "rule_category": "sequence",
            "query": "event sequence validation"
        })
        print(f"   Found {result['total_found']} rules")
        for rule in result['rules']:
            print(f"   - {rule['title']} (similarity: {rule['similarity_score']:.3f})")
        
        print("\n✅ Vector RAG system testing successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing vector RAG system: {e}")
        return False

def test_learning_system():
    """Test the vector learning system"""
    print("\n🧠 Testing Vector Learning System...")
    
    try:
        from rag.learning.vector_learning import get_learned_insights, get_learning_stats
        
        # Test get_learned_insights
        print("\n1. Testing get_learned_insights...")
        insights = get_learned_insights.invoke({"anomaly_type": "MISSING_STEP"})
        print(f"   Confidence: {insights['confidence']:.3f}")
        print(f"   Frequency: {insights['frequency']} ({insights['frequency_percentage']:.1f}%)")
        print(f"   Suggested Fix: {insights['suggested_fix']}")
        
        # Test get_learning_stats
        print("\n2. Testing get_learning_stats...")
        stats = get_learning_stats.invoke({})
        print(f"   Total Anomalies: {stats['learned_patterns']['total_anomalies']}")
        print(f"   Resolution Success Rate: {stats['learned_patterns']['resolution_success_rate']:.2%}")
        print(f"   Vector Knowledge Items: {stats['vector_knowledge_stats']['total_items']}")
        
        print("\n✅ Vector Learning system testing successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing vector learning system: {e}")
        return False

def test_agent():
    """Test the vector RAG-enhanced agent"""
    print("\n🤖 Testing Vector RAG-Enhanced Agent...")
    
    try:
        from agent_waybill_agentic_vector_rag import graph
        from langchain_core.messages import HumanMessage
        
        # Test with a simple waybill
        user_msg = HumanMessage(content="Check waybill WB3000 for anomalies using Vector RAG analysis")
        
        print("   Running agent with Vector RAG...")
        out = graph.invoke({"messages": [user_msg]}, config={"configurable": {"thread_id": "test-vector-rag"}})
        
        final = out["messages"][-1]
        if hasattr(final, 'content') and final.content:
            print("   ✅ Agent completed successfully!")
            print(f"   Response length: {len(final.content)} characters")
            return True
        else:
            print("   ❌ Agent did not return content")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Vector RAG System Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed: Missing requirements")
        return False
    
    # Check environment
    if not check_environment():
        print("\n❌ Setup failed: Missing environment variables")
        return False
    
    # Setup vector knowledge base
    rag = setup_vector_knowledge_base()
    if not rag:
        print("\n❌ Setup failed: Could not setup vector knowledge base")
        return False
    
    # Test vector RAG
    if not test_vector_rag():
        print("\n❌ Setup failed: Vector RAG testing failed")
        return False
    
    # Test learning system
    if not test_learning_system():
        print("\n❌ Setup failed: Vector Learning testing failed")
        return False
    
    # Test agent (optional - might fail if API is not available)
    print("\n🤖 Testing Agent (optional)...")
    try:
        test_agent()
    except Exception as e:
        print(f"   ⚠️  Agent test skipped: {e}")
        print("   (This is normal if LOGI_API_URL is not accessible)")
    
    print("\n" + "=" * 50)
    print("✅ Vector RAG System Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Update your langgraph.json to use the vector RAG agent:")
    print('   "agent": "./agent_waybill_agentic_vector_rag.py:graph"')
    print("2. Test with your waybill data:")
    print("   python agent_waybill_agentic_vector_rag.py")
    print("3. Monitor the enhanced confidence scores and similarity results")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
