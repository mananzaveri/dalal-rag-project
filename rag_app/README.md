# RAG Application Setup Guide

This guide will help you set up the RAG (Retrieval-Augmented Generation) application on your local machine.

## Prerequisites

- Python 3.11 or higher
- Git
- Ollama (you have to download it from the internet for local LLM)

## Step 1: Clone and Navigate to Project

```bash
git clone <repository-url>
cd dalal-rag-project
```

## Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Make sure your virtual environment is activated
pip install -r requirements.txt
```

## Step 4: Set Up Ollama (Local LLM)

1. **Install Ollama** from [https://ollama.ai](https://ollama.ai)
2. **Pull the required model**:
   ```bash
   ollama pull llama2
   ```

## Step 5: Create Vectorstore

The application uses a vectorstore to store and retrieve document embeddings. You need to run the ingestion script to populate it:

```bash
# Navigate to the rag_app directory
cd rag_app

# Run the ingestion script
python app/backend/data/ingest_hf.py
```

This script will:
- Download a Buddhist NLP dataset from HuggingFace
- Process and clean the data
- Create embeddings using sentence-transformers
- Store them in a Chroma vectorstore at `app/vectorstore/`

**Note**: This process may take several minutes depending on your internet connection and processing power.



## Step 6: Run app/backend/core/retriever.py to see sample output

```bash
# From the rag_app directory
python app/backend/core/retriever.py
```



## Step 7: Run the Application (this is not yet functional)

```bash
# From the rag_app directory
python run.py
```

The application will start and be available at `http://localhost:8501`

## Project Structure

```
rag_app/
├── app/
│   ├── backend/
│   │   ├── core/          # Core RAG logic
│   │   ├── data/          # Data ingestion scripts
│   │   ├── services/      # Service layer
│   │   └── api/           # API endpoints
│   ├── frontend/          # Streamlit frontend
│   └── vectorstore/       # Chroma vector database
├── run.py                 # Main entry point
└── README.md
```

## Troubleshooting

### Virtual Environment Issues
- Make sure you're using Python 3.11+
- If you get permission errors, try: `python3 -m venv venv`

### Ollama Issues
- Ensure Ollama is running: `ollama serve`
- Check if the model is downloaded: `ollama list`

### Vectorstore Issues
- If the ingestion script fails, check your internet connection
- The vectorstore will be created in `app/vectorstore/` - make sure this directory is writable
- If you get memory errors, try running the ingestion script with a smaller dataset

### Dependencies Issues
- If you get import errors, make sure your virtual environment is activated
- Try upgrading pip: `pip install --upgrade pip`

## Development

To make changes to the application:

1. **Frontend changes**: Edit `app/frontend/frontend.py`
2. **Backend changes**: Edit files in `app/backend/`
3. **Data ingestion**: Modify `app/backend/data/ingest_hf.py`

## Contributing

1. Create a new branch for your changes
2. Make your changes
3. Test the application
4. Commit and push your changes
5. Create a pull request

## Support

If you encounter any issues, check the troubleshooting section above or contact the development team.
