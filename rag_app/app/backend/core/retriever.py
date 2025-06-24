from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
import os

class RAGRetriever:
    def __init__(self):
        # Get the correct path to the vector store
        current_dir = os.path.dirname(os.path.abspath(__file__))
        core_dir = os.path.dirname(current_dir)  # rag_app/app/backend/core
        backend_dir = os.path.dirname(core_dir)  # rag_app/app/backend
        vectorstore_dir = os.path.join(backend_dir, "vectorstore")
        
        print(f"DEBUG: Vectorstore path = {vectorstore_dir}")
        print(f"DEBUG: Path exists = {os.path.exists(vectorstore_dir)}")

        # Load vectorstore
        self.embedding = HuggingFaceEmbeddings(
            model_name="intfloat/e5-small",
            encode_kwargs={"normalize_embeddings": True}
        )
        self.vectorstore = Chroma(persist_directory=vectorstore_dir, embedding_function=self.embedding)

        # Use Mistral via Ollama
        self.llm = OllamaLLM(model="mistral")

        # Set up RAG chain with improved retriever configuration
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 10  # Retrieve more documents initially
            }
        )

        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )

    def deduplicate_documents(self, documents):
        """Remove duplicate documents based on their content."""
        seen_contents = set()
        unique_docs = []
        for doc in documents:
            content = doc.page_content.strip()
            if content not in seen_contents:
                seen_contents.add(content)
                unique_docs.append(doc)
        return unique_docs

    def get_response(self, query: str):
        """Get a response for a given query using the RAG system."""
        try:
            response = self.rag_chain.invoke({"query": query})
            
            # Deduplicate source documents
            unique_source_docs = self.deduplicate_documents(response["source_documents"])
            
            # Get similarity scores by doing a direct similarity search
            query_similar_docs = self.vectorstore.similarity_search_with_score(query, k=50)
            
            # Match source documents with their similarity scores
            source_docs_with_scores = []
            for doc in unique_source_docs:
                similarity_score = 0.0
                # Find matching document in similarity search results
                for similar_doc, score in query_similar_docs:
                    if similar_doc.page_content.strip() == doc.page_content.strip():
                        similarity_score = score
                        break
                
                source_docs_with_scores.append({
                    "content": doc.page_content,
                    "similarity_score": similarity_score
                })
            
            return {
                "answer": response["result"],
                "source_documents": [doc["content"] for doc in source_docs_with_scores],
                "source_scores": [doc["similarity_score"] for doc in source_docs_with_scores],
                "success": True
            }
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "source_documents": [],
                "source_scores": [],
                "success": False
            }

# Create a global instance for easy import
retriever = RAGRetriever()

# Test code - only runs if this file is executed directly
if __name__ == "__main__":
    
    # Test the retriever with a sample query
    test_query = "What is the Sāṃkhya theory mentioned in the dataset?"
    
    # Debug: Check vectorstore contents
    print(f"Vectorstore collection count: {retriever.vectorstore._collection.count()}")
    
    # Debug: Test retrieval directly
    print("\nTesting direct retrieval...")
    docs = retriever.retriever.invoke("Sāṃkhya")
    print(f"Retrieved {len(docs)} documents directly")
    
    # Debug: Test similarity search directly
    print("\nTesting similarity search directly...")
    similar_docs = retriever.vectorstore.similarity_search("Sāṃkhya", k=3)
    print(f"Similarity search found {len(similar_docs)} documents")
    
    # Test the full RAG system
    result = retriever.get_response(test_query)
    
    print("\nAnswer:", result["answer"])
    print(f"\nSuccess: {result['success']}")
    print(f"Number of source documents: {len(result['source_documents'])}")
    
    if result["source_documents"]:
        print("\nSource Documents (sorted by similarity score, highest to lowest):")
        
        # Create list of (document, score) tuples and sort by score
        docs_with_scores = list(zip(result["source_documents"], result["source_scores"]))
        docs_with_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score, highest first
        
        for i, (doc, score) in enumerate(docs_with_scores, 1):
            print("-" * 80)
            print(f"Document {i} (Similarity Score: {score:.4f}):")
            print(doc)
    else:
        print("\nNo source documents found.")