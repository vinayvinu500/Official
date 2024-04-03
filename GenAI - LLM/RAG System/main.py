# Libraries
import os, shutil
import tiktoken
from dotenv import find_dotenv, load_dotenv
from getpass import getpass
import streamlit as st
import numpy as np
import pandas as pd
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community import document_loaders
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# ================== Load the documents ======================= #
# Load the document
def load_document(file):
    """Functions links the PDFs using library called PyPDF into an array of documents where each document contains the page, content and metadata with a page number."""
    # prevent from circular dependencies and benefit from a more reliable refactoring of our code. | if we utilize the function and it will work because it contains everthing it int
    # from langchain.document_loaders import PyPDFLoader 
    
    # import json
    # from pathlib import Path
    name, ext = os.path.splitext(file) # file.split('/')[-2], file.split('/')[-1]

    loader = {
        '.pdf': document_loaders.PyPDFLoader(file),
        '.docx': document_loaders.Docx2txtLoader(file),
        '.txt': document_loaders.TextLoader(file),
        '.csv': document_loaders.CSVLoader(file),
        '.py': document_loaders.PythonLoader(file),
        '.html': document_loaders.BSHTMLLoader(file), # UnstructuredHTMLLoader(file)
        # '.json': json.loads(Path(file).read_text())
    } # url of the file or file path in a file system

    if ext not in loader.keys():
        print("Extension Doesn't Exists!")
        return None
    
    if ext == '.json':
        return loader[ext]
    
    print(f"Loading the '{file}'")
    data = loader[ext].load_and_split() if ext == '.pdf' else loader[ext].load() # this will return a list of langchain documents, one document for each page
    return data # data is splitted by pages and we can use indexes to display a specific page

# Load all the documents : https://python.langchain.com/docs/modules/data_connection/document_loaders/file_directory
def load_all_documents(dirpath):
    """Function accepts the directory path as an argument and return the list of documents(page_content, meta_data)"""
    name, ext = os.path.splitext(file) # file.split('/')[-2], file.split('/')[-1]

    loader = {
        '.pdf': document_loaders.DirectoryLoader(dirpath, show_progress=True, use_multithreading=True, loader_cls=document_loaders.PyPDFLoader),
        '.docx': document_loaders.DirectoryLoader(dirpath, show_progress=True, use_multithreading=True, loader_cls=document_loaders.Docx2txtLoader),
        '.txt': document_loaders.DirectoryLoader(dirpath, show_progress=True, use_multithreading=True, loader_cls=document_loaders.TextLoader, loader_kwargs={'autodetect_encoding':True}),
        '.csv': document_loaders.DirectoryLoader(dirpath, show_progress=True, use_multithreading=True, loader_cls=document_loaders.CSVLoader),
        '.py': document_loaders.DirectoryLoader(dirpath, show_progress=True, use_multithreading=True, loader_cls=document_loaders.PythonLoader)
    } # silent_errors=True which can silenced which could not be loaded

    if ext not in loader.keys():
        print("Extension Doesn't Exists!")
        return None

    data = loader[ext].load_and_split() if ext == '.pdf' else loader[ext].load()
    print(f"Documents: {len(data)}")
    return sorted(data, key=lambda x: x.page_content.split('\n')[0]) # sorted through title of the documents

# load from wikipedia
def load_wikipedia_documents(query, lang='en', load_max_docs=2):
    """Functions accepts three arguments <(query, lang, load_max_docs)> whereas query: question | lang: language of text | load_max_docs: maximum documents to return"""
    print("Function has been invoked and will take enough time to process based on the maximum document size %s..." %load_max_docs)
    loader = document_loaders.WikipediaLoader(query=query, lang=lang, load_max_docs=load_max_docs)
    data = loader.load()
    return data


# driver code: files
dirpath = "../files/MySQL"
file = "../files/MySQL/C3-WK01-DY02-PracticeExercise.pdf"
page = 2

# one document at a time
# data = load_document(file)
# print(f"Total '{len(data)}' Pages in the '{file.split('/')[-1]}'")
# print(f'There are "{len(data[page].page_content)}" characters at the {page} page.')
# print("Metadata:", data[page].metadata)
# print(f"Page {page}: {data[page].page_content}")

# list of documents
# data = load_all_documents(dirpath)
# data

# driver code: wikipedia
# data = load_wikipedia_documents('LLM(Large Language Models)')
# print(data[0].page_content)



# ================== Chunking ======================= #
# document chunking
def data_chunks(data, chunk_size=256, chunk_overlap=20):
    """Function accepts the document_loader object and returns the chunks and takes two additional arguments as chunk_size & chunk_overlap"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(data)
    # print(f"Chunk Size: {chunk_size}")
    # print(f"Chunk Overlap: {chunk_overlap}")
    # print(f"Total Chunks: {len(chunks)}")
    return chunks

# embedding costs: tokens 
def embedding_costs(chunks, model='text-embedding-3-small', price=0.02):
    """Function accepts text or document as chunks then calculates the embedding costs. By default it will embedd using model='text-embedding-3-small' with price=0.02 """
    enc = tiktoken.encoding_for_model(model)
    total_tokens = sum([len(enc.encode(page.page_content)) for page in chunks])
    embed_cost = total_tokens / 1000 * price
    # print(f"Total Tokens: {total_tokens}")
    # print(f"Embedding Cost in USD: {embed_cost:.6f}")
    return total_tokens, round(embed_cost, 6)

# document-chunks-tokens-embeddings calculator
def document_chunks_tokens_embeds_calculator(data, chunk_size=256, chunk_overlap=0, model='text-embedding-3-small', price=0.02):
    """Function accepts three arguments
    data: document_loaders object
    chunk_size & chunk_overlap
    model: describes embedding model
    # and prints chunk_size, chunk_overlap, chunks, total_chunks, tokens, total_tokens, embed_costs
    and returns chunk_size, chunk_overlap, chunks, total_chunks, tokens, total_tokens, embed_costs
    """
    if chunk_overlap is None:
        chunk_overlap = chunk_size // 2 + 1

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size, # should be higher and need to be experiemented
        chunk_overlap= chunk_overlap, # overlap between chunks needed to maintain some continuity between them
        length_function=len # indicates how the length of chunks is calculated
        # The default is to just count the number of characters, but because we work with LLMs and LLMs use tokens 
        # Instead it should be token counter 
    )
    chunks = text_splitter.split_documents(data)
    enc = tiktoken.encoding_for_model(model)
    tokens = [enc.encode(page.page_content) for page in chunks]
    total_tokens = sum(map(len, tokens))
    embed_cost = total_tokens / 1000 * price

    # print(f"Chunk Size: {chunk_size}")
    # print(f"Chunk Overlap: {chunk_overlap}")
    # print(f"Chunks: {chunks[:5]}")
    # print(f"Total Chunks: {len(chunks)}")
    # print(f"Tokens: {tokens[:5]}")
    # print(f"Total Tokens: {total_tokens}")
    # print(f"Embedding Cost in USD: {embed_cost:.6f}")
    return chunk_size, chunk_overlap, chunks, len(chunks), tokens, total_tokens, round(embed_cost, 6)
    """
    user = input("Are you want to continue...[Y/N | y/n]: ")
    if user in ('y', 'Y'):
        return chunk_size, chunk_overlap, chunks, len(chunks), tokens, total_tokens, round(embed_cost, 6)
    else:
        raise Exception("User has raised the error to prevent the process of embedding...")
    """

# driver code: chunks
# one document at a time
# data = load_document(file)
# print(f"Total '{len(data)}' Pages in the '{file.split('/')[-1]}'")

# chunks = data_chunks(data)
# print(f"There are {len(chunks)} chunks.")
# print(chunks[2].page_content)

# total_tokens, embed_costs = embedding_costs(chunks)
# print(f"Total Tokens: {total_tokens}")
# print(f"Embedding Cost in USD: {embed_costs:.6f}")

# chunk_size, chunk_overlap, chunks, total_chunks, total_tokens, embed_costs = document_chunks_tokens_embeds_calc(data)
    
# Use-Case: Customize 
# data = load_document(file)
# print(f"Total '{len(data)}' Pages in the '{file.split('/')[-1]}'")
# document_chunks_tokens_embeds_calculator(data) # chunk_size, chunk_overlap, chunks, total_chunks, total_tokens, embed_costs
# document_chunks_tokens_embeds_calculator(data, chunk_size=10, chunk_overlap=5) # chunk_size, chunk_overlap, chunks, total_chunks, total_tokens, embed_costs
# document_chunks_tokens_embeds_calculator(data, chunk_size=256, chunk_overlap=None) # chunk_size, chunk_overlap, chunks, total_chunks, total_tokens, embed_costs
# document_chunks_tokens_embeds_calculator(data, chunk_size=1) # chunk_size, chunk_overlap, chunks, total_chunks, total_tokens, embed_costs

# ================== Vector Store: Embeddings ======================= #
# create embeddings and vector store in chromadb
def create_embeddings_chroma(chunks, persist_directory='./Sessions/chromadb'):
    """Function which creates the embeddings (OpenAIEmbeddings class), Saves them in a chroma database and returns the vector store object"""
    print("Started Embeddings...", end=' ')
    embeddings = OpenAIEmbeddings(model='text-embedding-3-small', dimensions=1536)
    vector_store = Chroma.from_documents(chunks, embeddings, persist_directory=persist_directory)
    print("Done...", end='\n\n')
    return vector_store

# loading embeddings 
def load_embeddings_chroma(persist_directory='./Sessions/chromadb'):
    """Function will load the existing chroma db and return vector store object"""
    embeddings = OpenAIEmbeddings(model='text-embedding-3-small', dimensions=1536)
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vector_store

# Driver Code
# data = load_all_documents("../files/MySQL")
# chunks = data_chunks(data)
# vector_store = create_embeddings_chroma(chunks, './Sessions/chromadb')
# db = load_embeddings_chroma('./Sessions/chromadb')
# question = """What is the whole document about?"""
# answer = question_answer_bot(vector_store, question)
# print(answer['query'])
# print(answer['result'])

# ================== Vector Store: Embeddings ======================= #
def ask_question(question, vector_store, model='gpt-3.5-turbo', temperature=0, k=5):
    """Function takes five arguments 
    question as str type 
    vector_store: as Chroma object
    model: by default 'gpt-3.5-turbo'
    temperature: ranges from 0-2 by accurate-creative
    k: returns no of output text 

    as an output returns response object
    """
    llm = ChatOpenAI(model=model, temperature=temperature, streaming=True)
    retriever = vector_store.as_retriever(search='similarity', search_kwargs={'k':k})
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
    response = chain.invoke({'query': question})
    return response

def ask_with_memory(question, vector_store, chat_history=[], model='gpt-3.5-turbo', temperature=0, k=5): # vector_store=load_embeddings_chroma('./Sessions/chromadb')
    """Function takes five arguments 
    question as str type 
    vector_store: as Chroma object
    model: by default 'gpt-3.5-turbo'
    temperature: ranges from 0-2 by accurate-creative
    k: returns no of output text 

    as an output returns response object, chat_history
    """
    llm = ChatOpenAI(model=model, temperature=temperature, streaming=True)
    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k': k})
    conversation_retrieval_chain = ConversationalRetrievalChain.from_llm(llm, retriever)
    response = conversation_retrieval_chain({'question': question, 'chat_history': chat_history})
    chat_history.append((question, response['answer']))
    return response, chat_history 


# clear the history 
def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']

if __name__ == "__main__":

    # ================== Session Storage ======================= #
    # Use an absolute path to avoid confusion
    dir_session = os.path.abspath('Sessions')

    try:
        # Check if the directory exists
        if os.path.exists(dir_session):
            # Remove the directory and all its content
            shutil.rmtree(dir_session)

        # Create the directory again
        # Adding a check to ensure the directory was indeed deleted
        if not os.path.exists(dir_session):
            os.makedirs(dir_session)
        else:
            print("Directory still exists after deletion attempt. Check for potential issues.")

    except (PermissionError, FileNotFoundError,Exception)  as e:
        # print("File related errors are handled!")
        pass

    # ================== Enviromental variables ======================= #
    file = './.env' # new path to store new api_keys
    try: 
        keys = find_dotenv(file,raise_error_if_not_found=True)
        load_dotenv(keys, override=True)
        # print(os.environ.get('OPENAI_API_KEY'))
        # print("Initialize Sucessfull!")
    except:
        api_key = getpass("Enter OPENAI_API_KEY: ")
        os.environ['OPENAI_API_KEY'] = api_key
        load_dotenv(file, override=True)
        # print("Initialized New API_KEY..")

    # ================== UI: Streamlit App ======================= #
    favicon = './snaps/favicon - LLM Optimization Parameters.png'
    # st.image(favicon)
    st.set_page_config(page_title="RAG System - Q&A App", page_icon=favicon, layout="centered", initial_sidebar_state="auto", menu_items=None)
    st.subheader('🤖 RAG System - Q&A App ')

    # ================== Widget: Sidebar ======================= #
    with st.sidebar:
        # Authentication Purposes
        # api_key = st.text_input("OPENAI API KEY: ", type='password')
        # if api_key:
        #     os.environ['OPENAI_API_KEY'] = api_key
        #     print("Initialized New API_KEY..")
        
        # single / multiple file upload
        upload_files = st.file_uploader("Upload a file: ", type=['pdf', 'docx', 'txt', 'html', 'csv', 'py'], accept_multiple_files=True)  # contained in bytes IO buffer (BytesIO) in python memory in ram and not on disk  
        
        chunk_size = st.number_input('Chunk Size: ', min_value=1, max_value=2048, value=512, on_change=clear_history)
        chunk_overlap = st.number_input('Chunk Overlap: ', min_value=0, max_value=chunk_size, value=20, on_change=clear_history)
        k = st.number_input('K: ', min_value=1, max_value=20, value=3, on_change=clear_history)

        button = st.button('Add', on_click=clear_history)
        data_history = {'total_chunks': 0, 'total_tokens': 0, 'embedding_costs': 0}
        if upload_files and button:
            with st.spinner("Reading... Chunking... Embedding..."):
                for file in upload_files: 
                    file_bytes = file.read() # BytesIO
                    file_name = os.path.join('./files', file.name)
                    
                    with open(file_name, 'wb') as f:
                        f.write(file_bytes)
                    
                    data = load_document(file_name)
                    chunks = data_chunks(data=data, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                    total_tokens, embed_costs = embedding_costs(chunks)
                    
                    data_history['total_chunks'] += len(chunks)
                    data_history['total_tokens'] += total_tokens
                    data_history['embedding_costs'] += embed_costs

            # User Message Message
            message = st.chat_message(name="user", avatar='assistant')
            # chunk_size, chunk_overlap, chunks, total_chunks, tokens, total_tokens, embed_costs = document_chunks_tokens_embeds_calculator(data=total_data, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            col1, col2, col3 = message.columns(3)
            col1.metric("Total Chunks", data_history['total_chunks'])
            col2.metric("Total Tokens", data_history['total_tokens'])
            col3.metric("Embeddings Costs", round(data_history['embedding_costs'],4))

            # vector store
            vector_store = create_embeddings_chroma(chunks)

            # need to save the vector store between page reloads because I don't want to read and chunk the file and embed the chunks each time the user interacts with the widget
            st.session_state.vs = vector_store # storing chroma vector store in the session state as viz 

            # Sucess message
            st.success('File Uploaded... Chunked... Embedded Sucessfully!')

    question = st.text_input("Prompt: ") # can you tell me the context of the documents
    response = {'query': '', 'result': ''} # flexibility

    if 'history' not in st.session_state:
        st.session_state.history = ''
    
    # ================== Prompting: Q&A Section ======================= #
    if question and 'vs' in st.session_state:
        vector_store = st.session_state.vs
        response = ask_question(question=question, vector_store=vector_store, k=k)
        st.text_area(label="Response: ", value=response['result'])

    st.divider()

    # ================== History ======================= #
    h = st.session_state.history
    value = f"Prompt: {response['query']} \nResponse: {response['result']}"
    if response['query'] != '' or response['result'] != '':
        if response['query'] not in st.session_state.history:
            st.session_state.history = f"{value} \n\n {'-'*100} \n\n {st.session_state.history}\n\n"
    st.text_area(label='Chat History', value=h, key='history', height=500)