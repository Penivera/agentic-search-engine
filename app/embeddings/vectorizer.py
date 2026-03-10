from sentence_transformers import SentenceTransformer
from typing import List

class Vectorizer:
    """
    Handles embedding generation for skills using SentenceTransformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate vector embeddings for a list of text documents.

        Args:
            texts (List[str]): List of documents to embed.

        Returns:
            List[List[float]]: List of embeddings as vectors.
        """
        return self.model.encode(texts, convert_to_tensor=True).tolist()

# Example usage:
# vectorizer = Vectorizer()
# embeddings = vectorizer.generate_embeddings(["Skill 1 description", "Skill 2 description"])