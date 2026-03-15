import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class Vectorizer:
    """
    Handles embedding generation for skills.
    Uses SentenceTransformers if available natively, otherwise falls back to a 
    deterministic pseudo-random generator using numpy (e.g. for environments that 
    cannot compile PyTorch like Python 3.13 locally).
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension_size = 384 # Standard size for MiniLM
        self.model = None

        if HAS_SENTENCE_TRANSFORMERS:
            logger.info(f"Initializing real SentenceTransformer model: {model_name}")
            self.model = SentenceTransformer(model_name)
        else:
            logger.warning("SentenceTransformers not found; using Mock Vectorizer.")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate vector embeddings for a list of text documents.
        """
        if self.model:
            return self.model.encode(texts, convert_to_tensor=True).tolist()

        embeddings = []
        for text in texts:
            # Seed based on string length to give deterministic mock results
            np.random.seed(len(text))
            vector = np.random.rand(self.dimension_size).tolist()
            embeddings.append(vector)
            
        return embeddings