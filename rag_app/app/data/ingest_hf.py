from datasets import load_dataset
from langchain.docstore.document import Document

# Load dataset from Hugging Face
dataset = load_dataset("buddhist-nlp/tatpa-noisy")

# Access the split you want (e.g., "train")
data = dataset["train"]

# Preview structure
print(data.features)
print(data[0])

# Convert to LangChain Documents (example using a 'text' field)
docs = [
    Document(page_content=sample["text"])
    for sample in data if sample["text"].strip()
]

print(f"Loaded {len(docs)} LangChain documents.")
