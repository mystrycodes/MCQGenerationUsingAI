from langchain_community.vectorstores import Chroma

from langchain_community import embeddings

from langchain_ollama import OllamaLLM

from langchain_core.runnables import RunnablePassthrough

from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import ChatPromptTemplate

from langchain.text_splitter import CharacterTextSplitter

from langchain.schema import Document


def generateMCQ(text,number_of_questions):
    print(type(text))
    print(text)

    # Initializing the model, here we use the mistral model
    local_model = OllamaLLM(model="mistral")
    
    # Splitting the text into chunks of size 7500 each
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
    
    # Creating a document-like structure from the  text
    document_list = [Document(page_content=text)]
    
    # Split the document into smaller chunks
    document_splits = text_splitter.split_documents(document_list)
    
    # Convert text chunks into embeddings and store in vector database
    vectorstore = Chroma.from_documents(
        documents=document_splits,
        collection_name="rag-chroma",
        embedding=embeddings.OllamaEmbeddings(model='nomic-embed-text'),
    )
    
    retriever = vectorstore.as_retriever()
    
    # Define the RAG template
    after_rag_template = prompt = f"""
    You are an AI assistant helping the user generate multiple-choice questions (MCQs) based on the following text:
    '{text}'
    Please generate {number_of_questions} MCQs from the text. Each question should have:
    - A clear question
    - Four answer options (labeled A, B, C, D)
    - The correct answer clearly indicated
    Format:
    ## MCQ
    Question: [question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Correct Answer: [correct option]
    """
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    
    # Define the RAG chain
    after_rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | after_rag_prompt
        | local_model
        | StrOutputParser()
    )
    
    # Return the response for the provided question
    return after_rag_chain.invoke(f"generate {number_of_questions} multiple choice questions")

print(generateMCQ('''Donald John Trump (born June 14, 1946) is an American politician, media personality, and businessman who served as the 45th president of the United States from 2017 to 2021. In November 2024, he was re-elected to a second, non-consecutive term as president, and is the president-elect.

# Born in New York City, Trump graduated with a bachelor's degree in economics from the University of Pennsylvania in 1968. After becoming president of the family real estate business in 1971, Trump renamed it the Trump Organization and reoriented the company toward building and renovating skyscrapers, hotels, casinos, and golf courses. After a series of business failures in the late 1990s, he launched side ventures, mostly licensing the Trump name. From 2004 to 2015, he produced and hosted the reality television series The Apprentice. He and his businesses have been involved in more than 4,000 legal actions, including six business bankruptcies.

# Trump won the 2016 presidential election as the Republican Party nominee, defeating the Democratic Party candidate, Hillary Clinton, while losing the popular vote,[a] and became the first U.S. president without prior military or government service. The Mueller investigation later determined that Russia interfered in the 2016 election to help Trump. His campaign positions were described as populist, protectionist, and nationalist. His election and policies sparked numerous protests and led to the creation of Trumpism: a political movement. Trump promoted conspiracy theories and made many false and misleading statements during his campaigns and presidency, to a degree unprecedented in American politics. Many of his comments and actions have been characterized as racially charged, racist, and misogynistic.''',5))
