from dotenv import load_dotenv
import openai
import os
import pandas as pd
import sqlite3
from langchain import SQLDatabase,SQLDatabaseChain
from sqlalchemy import exc
import streamlit as st
from langchain.chat_models import ChatOpenAI
import qdrant_client
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings

#load data
df = pd.read_excel('data.xlsx')
#clean data
df.columns = df.columns.str.strip()
#create databse
connection = sqlite3.connect('demo.db')
#uplaod  data from file
df.to_sql('companies_data', connection, if_exists ='replace')
#close the connectin
connection.close()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

def generate_response(message):
    # Connect to the database
    dburi = "sqlite:///demo.db"
    db = SQLDatabase.from_uri(dburi)

    # Create an instance of LLM
    llm = ChatOpenAI()

    # Create an SQLDatabaseChain using the ChatOpenAI model and the database
    db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db)
    ai_response = db_chain.run(message)

    return ai_response

def get_text():
    # Get user input from text input field
    input_text = st.text_input("You: ", "", key="input")
    return input_text 
    

#ask to pdf

def get_vector_store():
    
    client = qdrant_client.QdrantClient(
        os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    embeddings = OpenAIEmbeddings()

    vector_store = Qdrant(
        client=client, 
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"), 
        embeddings=embeddings,
    )
    
    return vector_store 

def main():
    # Load environment variables
    load_dotenv()
    #st.sidebar.radio("Navigation",["Ask to your qdrant database","Query Database Like you Chat"])
    a =  st.sidebar.radio("Navigation",["Ask to your qdrant database","Query Database Like you Chat"])
    if a == "Ask to your qdrant database":
        #st.set_page_config(page_title="Ask")
        st.header("Ask to your qdrant database 💬")
    
    # creating vector store
        vector_store = get_vector_store()
    
    # create chain 
        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(),
         chain_type="stuff",
            retriever=vector_store.as_retriever()
        )
    
    # show user input
        user_question = st.text_input("Ask a question about your PDF:")
        if user_question:
            st.write(f"Question: {user_question}")
            answer = qa.run(user_question)
            st.write(f"Answer: {answer}")
    else:
   
    # Display header
        st.header('Query Database Like you Chat')

    # Get user input
        user_input = get_text()

        if user_input:
        # Generate response for the user input
            st.session_state["generated"] = generate_response(user_input)

        if st.session_state['generated']:
        # Display the generated response
            st.write(st.session_state['generated'])



if __name__ == '__main__':
    main()