from typing import List, Tuple
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import os
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

class Embeddings:
    def __init__(self, model_id: str, HUGGINGFACE_API_KEY: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=HUGGINGFACE_API_KEY)
        self.model = AutoModel.from_pretrained(model_id, token=HUGGINGFACE_API_KEY)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
 
    def get_embeddings(self, titles: List[str], texts: List[str], embedding_directory: str, chunk_directory:str = "chunks") -> Tuple[List[np.ndarray], List[str]]:
        os.makedirs(embedding_directory, exist_ok=True)
        chunk_directory = f"{embedding_directory}/../{chunk_directory}"
        os.makedirs(chunk_directory, exist_ok=True)
        
        embeddings = []
        chunked_texts_with_titles = []

        for title, text in zip(titles, texts):
            sentences = sent_tokenize(text)
            chunked_texts = [' '.join(sentences[i:i + 3]) for i in range(0, len(sentences), 3)]

            for idx, chunk in enumerate(chunked_texts):
                chunk_title = f"{title.replace(' ', '_')}_{idx + 1}"
                chunked_text_with_title = f"{title}_Chunk_{idx + 1}: {chunk}"
                chunked_texts_with_titles.append(chunked_text_with_title)

                chunk_file_path = os.path.join(chunk_directory, chunk_title + '.txt')

                if not os.path.exists(chunk_file_path):
                    with open(chunk_file_path, 'w', encoding='utf-8') as chunk_file:
                        chunk_file.write(chunked_text_with_title)

                embedding_file_path = os.path.join(embedding_directory, chunk_title + '.npy')

                if os.path.exists(embedding_file_path):
                    embedding = np.load(embedding_file_path, allow_pickle=True).tolist()
                    embeddings.extend(embedding)
                else:
                    inputs = self.tokenizer(chunk, return_tensors='pt', padding=True, truncation=True, max_length=512)
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                    with torch.no_grad():
                        outputs = self.model(**inputs)

                    embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
                    embeddings.append(embedding.astype(np.float32))

                    np.save(embedding_file_path, [embedding])

        return embeddings, chunked_texts_with_titles

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