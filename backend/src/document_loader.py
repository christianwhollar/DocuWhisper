import os
from typing import List

class DocumentLoader:
    def __init__(self, directory: str):
        self.directory = directory

    def load_documents(self) -> List[str]:
        """
        
        """
        titles, documents = [], []

        for filename in os.listdir(self.directory):

            if filename.endswith('.txt'):

                title = filename.split('.txt')[0]
                title = title.replace('_', ' ')
                titles.append(title)

                with open(os.path.join(self.directory, filename), 'r') as file:
                    documents.append(file.read())

        return titles, documents