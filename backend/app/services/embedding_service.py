from typing import List

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingService:
    """
    Creates semantic embeddings for text using
    Sentence Transformers.
    """

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            raise ValueError(
                "Text list cannot be empty."
            )

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            raise ValueError(
                "No valid text was provided."
            )

        embeddings = self.model.encode(
            cleaned_texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()


embedding_service = EmbeddingService()