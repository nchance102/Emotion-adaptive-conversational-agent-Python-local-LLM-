from sentence_transformers import SentenceTransformer
import numpy as np

# Load a pre-trained model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    """Return a normalized embedding vector for a given text."""
    vec = model.encode(text)
    # Normalize for cosine similarity
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

def similarity(vec1, vec2):
    """Compute cosine similarity between two embedding vectors."""
    return float(np.dot(vec1, vec2))
