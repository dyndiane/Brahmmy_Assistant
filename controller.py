import lmstudio as lms
import re
import subprocess
import os
import paramiko
from scp import SCPClient
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.document_loaders import PyPDFLoader
import cv2
import warnings

# Suppress paramiko deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="paramiko")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")

def detect_image(image_path):
    with lms.Client() as client:
        image_handle = client.files.prepare_image(image_path)
        model = client.llm.model("gemma-3-12b-it")
        chat = lms.Chat("you are an electrical/ electronics technician teaching electronic components")
        chat.add_user_message("Enumerate the object(s) no need for description and explanation detected in the image", images=[image_handle])
        prediction = model.respond(chat)
        return prediction
    
def load_pdf_documents(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20
    )
    return splitter.split_documents(documents)

def create_db(docs, db_file):
    embedding = OpenAIEmbeddings(
        openai_api_base="http://localhost:1234/v1",
        api_key="lm-studio",
        model="text-embedding-gte-large",
        check_embedding_ctx_length=False
    )
    vector_store = FAISS.from_documents(docs, embedding=embedding)
    vector_store.save_local(db_file)
    return vector_store

def create_or_append_db(docs, db_file):
    embedding = OpenAIEmbeddings(
        openai_api_base="http://localhost:1234/v1",
        api_key="lm-studio",
        model="text-embedding-gte-large",
        check_embedding_ctx_length=False
    )
    
    if os.path.exists(db_file):
        try:
            print("Appending to existing vector store...")
            vector_store = FAISS.load_local(db_file, embedding, allow_dangerous_deserialization=True)
            vector_store.add_documents(docs)
        except AssertionError:
            print("Dimension mismatch detected. Creating new vector store...")
            # If dimensions don't match, create a new store
            vector_store = FAISS.from_documents(docs, embedding=embedding)
    else:
        print("Creating a new vector store...")
        vector_store = FAISS.from_documents(docs, embedding=embedding)
    
    vector_store.save_local(db_file)
    return vector_store

def load_db(db_file):
    embedding = OpenAIEmbeddings(
        openai_api_base="http://localhost:1234/v1",
        api_key="lm-studio",
        model="text-embedding-gte-large",
        check_embedding_ctx_length=False
    )
    return FAISS.load_local(db_file, embedding, allow_dangerous_deserialization=True)

def create_chain(vector_store, image_path, system_prompt=None):
    model = ChatOpenAI(base_url="http://localhost:1234/v1", model_name="deepseek-coder-6.7b-instruct", api_key="lm-studio", temperature=0)
    # Optionally detect image objects
    additional_context = ""
    if image_path:
        additional_context = detect_image(image_path)
    else:
        additional_context = ""
    
    # Use provided system prompt or default
    base_prompt = system_prompt if system_prompt else "You are a helpful university chatbot."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         f"{base_prompt}\n"
         "Context: {context}\n"
         f"Additional visual context: {additional_context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=retriever,
        prompt=retriever_prompt
    )
    retrieval_chain = create_retrieval_chain(history_aware_retriever, chain)
    return retrieval_chain

def process_chat(chain, question, chat_history):
    response = chain.invoke({
        "input": question,
        "chat_history": chat_history
    })
    return response["answer"]

def process_chat(chain, question, chat_history):
    response = chain.invoke({
        "input": question,
        "chat_history": chat_history
    })
    return response["answer"]