from typing import List
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import os

class Embeddings:
    def __init__(self, model_id: str, HUGGINGFACE_API_KEY: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=HUGGINGFACE_API_KEY)
        self.model = AutoModel.from_pretrained(model_id, token=HUGGINGFACE_API_KEY)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
 
    def get_embeddings(self, titles:List[str], texts: List[str], embedding_directory: str) -> List[np.ndarray]:
        os.makedirs(embedding_directory, exist_ok=True)
        embeddings = []

        for title, text in zip(titles, texts):
            file_path = os.path.join(embedding_directory, title.replace(' ', '_') + '.npy')

            if os.path.exists(file_path):
                embedding = np.load(file_path, allow_pickle=True).tolist()
                embeddings.extend(embedding)
            else:
                inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.model(**inputs)

                embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
                embeddings.append(embedding.astype(np.float32))
            
                np.save(file_path, [embedding])

        return embeddings

    def get_embeddings_query(self, texts: List[str]) -> List[np.ndarray]:
        embeddings = []

        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
            embeddings.append(embedding.astype(np.float32))
        
        return embeddings