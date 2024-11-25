import fitz  # PyMuPDF
import torch
from transformers import AutoModel, AutoTokenizer, pipeline
from nltk.tokenize import sent_tokenize
import re
import json
from pinecone import Pinecone
import os
import numpy as np
from typing import List, Tuple, Dict, Any
from datetime import datetime
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import time
from functools import partial
from itertools import islice
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys
from pathlib import Path
import warnings

# Suppress specific FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, message=r"`clean_up_tokenization_spaces` was not set")

os.environ['PINECONE_API'] = '37634895-154e-4769-a10f-6aaf9267ba77'
pc = Pinecone(api_key=os.getenv('PINECONE_API'))
index = pc.Index("apna-waqeel3")

# Set multiprocessing start method
mp.set_start_method('spawn', force=True)

# Initialize device and models once
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

model_name = "intfloat/multilingual-e5-large"
model = AutoModel.from_pretrained(model_name).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name)

from transformers import BertForMaskedLM
corrector = BertForMaskedLM.from_pretrained(
    "bert-base-uncased",
    output_attentions=False,
    output_hidden_states=False
).to(device)
corrector_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG to capture more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def context_aware_correction(text):
    """Modified correction function to reduce token handling complexity"""
    max_length = 512
    words = text.split()
    corrected_text = []
    
    for i in range(0, len(words), max_length):
        batch = words[i:i + max_length]
        text_chunk = " ".join(batch)
        
        # Simple cleaning instead of token-by-token correction
        cleaned_chunk = re.sub(r'[^\w\s]', ' ', text_chunk)
        cleaned_chunk = re.sub(r'\s+', ' ', cleaned_chunk).strip()
        corrected_text.append(cleaned_chunk)
    
    return " ".join(corrected_text)

def preprocess_text(text):
    """Simplified preprocessing to focus on essential cleaning"""
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Only apply correction for text chunks larger than a threshold
    if len(text.split()) > 10:  # Only correct substantial text
        text = context_aware_correction(text)
    
    return text.strip()

def extract_text_from_page(page):
    page_text = page.get_text()
    cleaned_text = preprocess_text(page_text)
    return cleaned_text

def validate_metadata(metadata: Dict[str, Any]) -> Tuple[bool, str]:
    required_fields = ['file_name', 'page_number', 'text', 'date_processed']
    missing_fields = [field for field in required_fields if not metadata.get(field)]
    if missing_fields:
        return False, f"Missing required metadata fields: {', '.join(missing_fields)}"
    if not metadata['text'] or len(metadata['text'].strip()) == 0:
        return False, "Empty text in metadata"
    return True, "Metadata valid"

def extract_metadata_from_pdf(pdf_path, page_num, page_text):
    try:
        file_name = os.path.basename(pdf_path)
        metadata = {
            'file_name': file_name,
            'tags': ['law', 'document'],
            'source': pdf_path,
            'document_type': 'legal',
            'language': 'urdu',
            'page_number': page_num,  # Ensure page_number is set
            'text': page_text,
            'date_processed': datetime.now().isoformat(),
            'document_category': 'legislation',
            'text_length': len(page_text) if page_text else 0,
            'processing_status': 'processed'
        }
        is_valid, message = validate_metadata(metadata)
        if not is_valid:
            print(f"Metadata validation failed for {file_name}, page {page_num}: {message}")
            return None
        return metadata
    except Exception as e:
        print(f"Error creating metadata for {pdf_path}, page {page_num}: {e}")
        return None

def get_embeddings(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        inputs = tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True)
        # Move inputs to GPU
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Move embeddings back to CPU for numpy operations
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        
        # Filter out any NaN embeddings
        valid_embeddings = [emb.tolist() if not np.isnan(emb).any() else None for emb in embeddings]
        all_embeddings.extend(valid_embeddings)
    
    return all_embeddings

MAX_METADATA_SIZE = 10000

def process_single_pdf(pdf_path: str, batch_size: int = 5) -> List[Tuple]:
    global model, tokenizer, corrector
    
    try:
        print(f"Processing single PDF: {pdf_path}")
        results = []
        document = fitz.open(pdf_path)
        
        # Collect all pages first
        pages_text = []
        page_info = []
        
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            page_text = extract_text_from_page(page)
            pages_text.append(page_text)
            page_info.append((pdf_path, page_num))
        
        # Process all embeddings at once using GPU
        all_embeddings = get_embeddings(pages_text, batch_size=32)
        for (path, num), text, embedding in zip(page_info, pages_text, all_embeddings):
            if embedding is not None:
                base_metadata = extract_metadata_from_pdf(path, num, text)
                if base_metadata: 
                    vector_id = f'{base_metadata["file_name"]}-page-{num}'
                    results.append((vector_id, embedding, base_metadata))
                else:
                    print(f"Failed to create metadata for {path}, page {num}")
            else:
                print(f"Invalid embedding for {path}, page {num}")
        print(f"Finished processing single PDF: {pdf_path}")
        return results
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

def process_pdfs_by_page(documents: List[str], batch_size: int = 5) -> None:
    chunks_size = 50  # Process documents in chunks
    
    print(f"Processing PDFs with metadata validation")
    
    for i in range(0, len(documents), chunks_size):
        chunk = documents[i:i + chunks_size]
        results = []
        
        # Process chunk of PDFs sequentially
        for pdf_path in tqdm(chunk, desc="Processing PDFs"):
            try:
                print(f"Processing PDF: {pdf_path}")
                document = fitz.open(pdf_path)
                pages_text = []
                page_info = []
                
                # Collect all pages from current PDF
                for page_num in range(document.page_count):
                    page = document.load_page(page_num)
                    page_text = extract_text_from_page(page)
                    if not page_text:
                        print(f"Skipping page {page_num} in {pdf_path} due to empty text")
                        continue
                    pages_text.append(page_text)
                    page_info.append((pdf_path, page_num))
                
                # Process all embeddings at once using GPU
                all_embeddings = get_embeddings(pages_text, batch_size=32)
                
                # Create results
                for (path, num), text, embedding in zip(page_info, pages_text, all_embeddings):
                    if embedding is not None:
                        metadata = extract_metadata_from_pdf(path, num, text)
                        if metadata:  # Only proceed if metadata is valid
                            vector_id = f'{metadata["file_name"]}-page-{num}'
                            results.append((vector_id, embedding, metadata))
                        else:
                            print(f"Skipping vector creation for {path}, page {num} due to invalid metadata")
                    else:
                        print(f"Invalid embedding for {path}, page {num}")
                
                # Upload to Pinecone when batch is full
                if len(results) >= batch_size:
                    if all(result[2] for result in results):  # Check all metadata is present
                        try:
                            index.upsert(vectors=results)
                            print(f"Successfully uploaded batch of {len(results)} vectors with valid metadata")
                        except Exception as e:
                            print(f"Error uploading batch: {e}")
                    else:
                        print("Skipping batch upload due to missing metadata")
                    results = []
                    
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
                continue
        
        # Upload remaining vectors with metadata validation
        if results and all(result[2] for result in results):
            try:
                index.upsert(vectors=results)
                print(f"Successfully uploaded final batch of {len(results)} vectors with valid metadata")
            except Exception as e:
                print(f"Error uploading final batch: {e}")
        elif results:
            print("Skipping final batch upload due to missing metadata")

def verify_pdf_exists(pdf_path: str) -> bool:
    """Verify if PDF file exists and is accessible"""
    try:
        path = Path(pdf_path)
        if not path.exists():
            print(f"File does not exist: {pdf_path}")
            return False
        if not path.is_file():
            print(f"Path is not a file: {pdf_path}")
            return False
        if not os.access(pdf_path, os.R_OK):
            print(f"File is not readable: {pdf_path}")
            return False
        return True
    except Exception as e:
        print(f"Error verifying PDF {pdf_path}: {str(e)}")
        return False

def bulk_process_pdfs(documents: List[str], chunk_size: int = 1000, batch_size: int = 100) -> None:
    """
    Process multiple PDFs in large chunks with batched uploads
    """
    print(f"Starting bulk processing of {len(documents)} documents")
    processed_count = 0
    failed_count = 0
    
    def process_chunk(pdf_paths):
        all_vectors = []
        chunk_processed = 0
        chunk_failed = 0
        
        for pdf_path in tqdm(pdf_paths, desc="Processing PDFs in chunk"):
            if not verify_pdf_exists(pdf_path):
                chunk_failed += 1
                continue
                
            try:
                print(f"Processing PDF: {pdf_path}")
                doc = fitz.open(pdf_path)
                
                # Verify document is readable
                if doc.page_count == 0:
                    print(f"Document has no pages: {pdf_path}")
                    chunk_failed += 1
                    continue
                
                for page_num in range(doc.page_count):
                    try:
                        page = doc.load_page(page_num)
                        page_text = extract_text_from_page(page)
                        if not page_text.strip():
                            print(f"No text extracted from page {page_num} in {pdf_path}")
                            continue
                        
                        metadata = extract_metadata_from_pdf(pdf_path, page_num, page_text)
                        if not metadata:
                            print(f"Invalid metadata for {pdf_path}, page {page_num}")
                            continue
                        
                        embedding = get_embeddings([page_text])[0]
                        if embedding:
                            vector_id = f'{metadata["file_name"]}-page-{page_num}'
                            all_vectors.append((vector_id, embedding, metadata))
                            chunk_processed += 1
                            print(f"Successfully processed: {pdf_path}, page {page_num}")
                        else:
                            print(f"Failed to create embedding for {pdf_path}, page {page_num}")
                            chunk_failed += 1
                        
                        # Upload to Pinecone when batch is full
                        if len(all_vectors) >= batch_size:
                            try:
                                index.upsert(vectors=all_vectors)
                                print(f"Successfully uploaded batch of {len(all_vectors)} vectors")
                                all_vectors = []
                            except Exception as e:
                                print(f"Error uploading batch: {e}")
                                chunk_failed += len(all_vectors)
                                all_vectors = []
                        
                    except Exception as e:
                        print(f"Error processing page {page_num} in {pdf_path}: {str(e)}")
                        chunk_failed += 1
                
            except Exception as e:
                chunk_failed += 1
                print(f"Error processing {pdf_path}: {str(e)}")
                continue
            
        return chunk_processed, chunk_failed

    # Process documents in large chunks
    for i in range(0, len(documents), chunk_size):
        chunk = documents[i:i + chunk_size]
        print(f"Processing chunk {i//chunk_size + 1} of {len(documents)//chunk_size + 1}")
        
        # Process the chunk and collect vectors
        chunk_processed, chunk_failed = process_chunk(chunk)
        processed_count += chunk_processed
        failed_count += chunk_failed
        
    print(f"Processing completed. Successfully processed: {processed_count}, Failed: {failed_count}")

# Modified main execution
if __name__ == "__main__":
    try:
        pdf_directory = r"C:\\Users\\Nouma\\Downloads\\Compressed\\archive_4"
        if not os.path.exists(pdf_directory):
            print(f"Directory does not exist: {pdf_directory}")
            sys.exit(1)
            
        documents = [os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        print(f"Found {len(documents)} PDF files")
        
        if not documents:
            print("No PDF files found in directory")
            sys.exit(1)
        
        bulk_process_pdfs(
            documents,
            chunk_size=1000,
            batch_size=100
        )
    except SystemExit as e:
        print(f"SystemExit: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")