import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from textSplitter import GetYoutubeVideo
from embeddingGenerator import EmbeddingGenerator
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import dotenv
dotenv.load_dotenv()
import asyncio

GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
url = 'https://www.youtube.com/watch?v=yB2SWOetNM8'
vector_dir = f"video_vectors/{url.split('v=')[1]}"

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

model = ChatGoogleGenerativeAI(
    model='gemini-2.5-pro',
    api_key=GEMINI_API_KEY
)
question='"What are weights? '


if os.path.exists(os.path.join(vector_dir, "index.faiss")):
    print("Loading existing FAISS index...")
    embeddedTranscripts = FAISS.load_local(
        vector_dir,
        embeddings_model,
        allow_dangerous_deserialization=True
    )
else:
    print("Creating new FAISS index...")
    uTubeVideoInstance = GetYoutubeVideo(url)
    transcripts = uTubeVideoInstance.transcriptMaker()
    embeddingGenerator = EmbeddingGenerator()
    embeddedTranscripts = embeddingGenerator.generateEmbedsForDocument(transcripts,url.split('v=')[1])


retriever = embeddedTranscripts.as_retriever(
    search_type='similarity',
    search_kwargs={"k": 10}
)
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a teacher. Use the transcript below to answer the question.\n\n"
        "Transcript context (with timestamps):\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer (be clear and include timestamps if relevant):"
    ),
)
qa_chain = RetrievalQA.from_chain_type(
    llm=model,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": QA_PROMPT}
)

question = "Tell me what he is creating? and tell me the timestamp in hour:minutes the timing is in thousand idk what it is second or minutes"
answer = qa_chain.invoke(question)
print(answer)

