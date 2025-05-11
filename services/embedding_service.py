from sentence_transformers import SentenceTransformer
import numpy as np
import streamlit as st


class EmbeddingService:
    _model = None

    @classmethod
    @st.cache_resource
    def load_model(cls, model_name="all-MiniLM-L6-v2"):
        if cls._model is None:
            cls._model = SentenceTransformer(model_name)
        return cls._model

    @classmethod
    def get_embedding(cls, text: str) -> list[float]:
        model = cls.load_model()
        embedding = model.encode(text)
        return embedding.tolist()
