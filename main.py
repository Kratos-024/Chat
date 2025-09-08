import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
import dotenv
from textSplitter import GetYoutubeVideo
from embeddingGenerator import EmbeddingGenerator
from langchain_core.output_parsers import StrOutputParser

dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
video_id = 'wjZofJX0v4M'
vector_dir = "video_vectors"

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

if os.path.exists(os.path.join(vector_dir, "index.faiss")):
    print("📂 Loading existing FAISS index...")
    embeddedTranscripts = FAISS.load_local(
        vector_dir,
        embeddings_model,
        allow_dangerous_deserialization=True
    )
else:
    print("⚡ Creating new FAISS index...")
    uTubeVideoInstance = GetYoutubeVideo(video_id)
    transcripts = uTubeVideoInstance.transcriptMaker()
    embeddingGenerator = EmbeddingGenerator()
    embeddedTranscripts = embeddingGenerator.generateEmbedsForDocument(transcripts)

prompt = PromptTemplate(
    input_variables=['context',"question"],
    template='You are a teacher. Reply only from the context of this query: {context}\n Question: {question}'
)

model = ChatGoogleGenerativeAI(
    model='gemini-2.5-pro',
    api_key=GEMINI_API_KEY
)
question='"What are weights? '

# retriever = embeddedTranscripts.as_retriever(search_type='similarity', search_kwargs={"k": 10})
# results = retriever.invoke(question)
# context=''

# for result in results:
#     context+=result.page_content + ' start: ' + result.start+ ' end: ' + result.end
# final_question=question +' and does the instructor taught it? if yes what is the timestamp?'
# final_prompt = prompt.invoke({'context':context,'question':final_question})

# answer = model.invoke(final_prompt)
# print(answer)
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

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
question = "What are weights? Did the instructor explain it, and if yes, what timestamp?"
answer = qa_chain.invoke(question)
print(answer)

