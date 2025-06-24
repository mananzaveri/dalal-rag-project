from datasets import load_dataset
from langchain.docstore.document import Document
from typing import List, Dict, Tuple, Set
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os


def load_dataset_splits(dataset_name: str) -> Dict:
    """
    Load all splits from the specified dataset.
    
    Args:
        dataset_name: Name of the HuggingFace dataset to load
        
    Returns:
        Dictionary containing all dataset splits
    """
    return load_dataset(dataset_name)


def convert_to_documents(data: Dict) -> List[Document]:
    """
    Convert dataset samples to LangChain Documents.
    
    Args:
        data: Dataset split containing the samples
        
    Returns:
        List of LangChain Documents
    """
    return [
        Document(page_content=sample["english"])
        for sample in data
        if sample["english"].strip()
    ]


def process_split(data: Dict, split_name: str) -> List[Document]:
    """
    Process a single dataset split and convert it to documents.
    
    Args:
        data: Dataset split to process
        split_name: Name of the split being processed
        
    Returns:
        List of LangChain Documents from this split
    """
    print()
    print(f"Processing {split_name} split:")
    print("Available fields:", data.column_names)
    print("Example row:", data[0])
    
    docs = convert_to_documents(data)
    print(f"Loaded {len(docs)} documents from {split_name} split.")
    return docs


def find_duplicates(docs: List[Document]) -> Tuple[List[Tuple[int, int, str]], Set[int]]:
    """
    Find duplicate sentences in the documents.
    
    Args:
        docs: List of LangChain Documents to check
        
    Returns:
        Tuple containing:
        - List of (original_index, duplicate_index, content) tuples
        - Set of duplicate indices
    """
    seen_sentences = {}  # Dictionary to store sentence -> first index mapping
    duplicates = []  # List to store (original_index, duplicate_index, content) tuples

    for i, doc in enumerate(docs):
        content = doc.page_content
        if content in seen_sentences:
            original_index = seen_sentences[content]
            duplicates.append((original_index, i, content))
        else:
            seen_sentences[content] = i

    duplicate_indices = {dup_idx for _, dup_idx, _ in duplicates}
    return duplicates, duplicate_indices


def print_duplicate_info(duplicates: List[Tuple[int, int, str]]) -> None:
    """
    Print information about found duplicates.
    
    Args:
        duplicates: List of (original_index, duplicate_index, content) tuples
    """
    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate sentences:")
        for orig_idx, dup_idx, content in duplicates[:5]:
            print(f"Original (index {orig_idx}): {content}")
            print(f"Duplicate (index {dup_idx}): {content}")
            print("-" * 80)
        if len(duplicates) > 5:
            print(f"... and {len(duplicates) - 5} more duplicate pairs")
    else:
        print("\nNo duplicate sentences found!")


def remove_duplicates(docs: List[Document], duplicate_indices: Set[int]) -> List[Document]:
    """
    Remove duplicate documents from the list.
    
    Args:
        docs: List of LangChain Documents
        duplicate_indices: Set of indices to remove
        
    Returns:
        List of Documents with duplicates removed
    """
    return [doc for i, doc in enumerate(docs) if i not in duplicate_indices]


def split_documents(docs: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Split documents into smaller chunks.
    
    Args:
        docs: List of Documents to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunked Documents
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    print()
    print(f"Split {len(docs)} documents into {len(chunks)} chunks")
    return chunks


def create_embeddings(model_name: str = "intfloat/e5-small") -> HuggingFaceEmbeddings:
    """
    Create a HuggingFace embeddings model.
    
    Args:
        model_name: Name of the HuggingFace model to use
        
    Returns:
        HuggingFaceEmbeddings instance
    """
    return HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vectorstore(chunks: List[Document], embedding_model: HuggingFaceEmbeddings, persist_dir: str = None) -> Chroma:
    """
    Create and persist a Chroma vector store.
    
    Args:
        chunks: List of Documents to store
        embedding_model: Embedding model to use
        persist_dir: Directory to persist the vector store (defaults to ./vectorstore in the backend directory)
        
    Returns:
        Chroma vector store instance
    """
    if persist_dir is None:
        # Get the backend directory (two levels up from this file: data -> backend)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)  # rag_app/app/backend
        persist_dir = os.path.join(backend_dir, "vectorstore")
    
    # Create the directory if it doesn't exist
    os.makedirs(persist_dir, exist_ok=True)
    
    print()
    print(f"Creating vector store with {len(chunks)} chunks...")
    print(f"Vector store will be saved to: {persist_dir}")
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    print(f"Vector store created and persisted to {persist_dir}")
    return vectorstore


def main():
    # Load dataset
    dataset = load_dataset_splits("buddhist-nlp/tatpa-noisy")
    
    # Process all splits
    all_docs = []
    for split in ['train', 'validation', 'test']:
        split_docs = process_split(dataset[split], split)
        all_docs.extend(split_docs)
    
    print()
    print(f"Total documents loaded: {len(all_docs)}")
    
    # Find and handle duplicates
    duplicates, duplicate_indices = find_duplicates(all_docs)
    print_duplicate_info(duplicates)
    
    # Remove duplicates if any were found
    if duplicates:
        all_docs = remove_duplicates(all_docs, duplicate_indices)
        print()
        print(f"After removing duplicates: {len(all_docs)} documents remaining")
        print(f"Removed {len(duplicate_indices)} duplicate documents")
    
    # Split documents into chunks
    chunks = split_documents(all_docs)
    
    # Create embeddings
    embedding_model = create_embeddings()
    
    # Create and persist vector store
    vectorstore = create_vectorstore(chunks, embedding_model)
    
    return vectorstore


if __name__ == "__main__":
    main()