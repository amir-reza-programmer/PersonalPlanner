import faiss
import numpy as np
import os
import json


class FAISSIndex:
    _index = None
    _task_ids = []
    _index_path = "faiss_index.index"
    _id_path = "faiss_ids.json"

    @classmethod
    def get_index(cls, dim=384):
        if cls._index is None:
            if os.path.exists(cls._index_path):
                cls._index = faiss.read_index(cls._index_path)
                with open(cls._id_path, "r") as f:
                    cls._task_ids = json.load(f)
            else:
                cls._index = faiss.IndexFlatL2(dim)
                cls._task_ids = []
        return cls._index

    @classmethod
    def add_embedding(cls, embedding, task_id):
        index = cls.get_index()
        vector = np.array(embedding, dtype='float32').reshape(1, -1)
        index.add(vector)
        cls._task_ids.append(task_id)
        cls.save_index()

    @classmethod
    def save_index(cls):
        faiss.write_index(cls._index, cls._index_path)
        with open(cls._id_path, "w") as f:
            json.dump(cls._task_ids, f)

    @classmethod
    def search(cls, query_embedding, k=5, threshold=0.5):
        index = cls.get_index()
        vector = np.array(query_embedding, dtype='float32').reshape(1, -1)
        distances, indices = index.search(vector, k)

        matched_ids = []
        filtered_distances = []

        for i, distance in zip(indices[0], distances[0]):
            if i < len(cls._task_ids) and distance <= threshold:
                matched_ids.append(cls._task_ids[i])
                filtered_distances.append(distance)

        return matched_ids, filtered_distances
