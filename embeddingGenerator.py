from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

class EmbeddingGenerator:
    def __init__(self):
        pass

    def generateEmbedsForDocument(self, transcripts):
        try:
            embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            documents = [
                Document(
                    page_content=f"{t['text']} (timestamp: {t['start']}–{t['end']})",
                    metadata={
                        "start": t['start'],
                        "end": t['end'],
                        "title": transcripts['title'],
                        "videoLength": transcripts['videoLength']
                    }
                )
                for t in transcripts['transcripts']
            ]

            vectorstore = FAISS.from_documents(documents, embeddings_model)
            vectorstore.save_local("video_vectors")

            return vectorstore

        except Exception as e:
            print(e)
