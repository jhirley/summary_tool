# Description: This file contains the code for the Summaries page of the Streamlit app, 
# it uses langchain and togeher.ai using openai LLM and direct openai for text to speech.

import os
import re
import uuid
import shutil
import requests
from dotenv import load_dotenv
from functools import lru_cache

import streamlit as st

## setting up the language model
from langchain_together import ChatTogether 
import openai

## import the documnent loaders from LangChain
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import  WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader

## import the prompt template and the LLMChain from LangChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


@lru_cache()
# get the api key from the environment variables or from the streamlit secrets file
def get_api_key(key_name):
    """Get the API keys from the environment variables or from the Streamlit secrets file.
    Args: 
        key_name (str): The name of the key to retrieve.
    Returns:
        str: The value of the API key.
    """

    # Load environment variables from .env file
    load_dotenv()
    if isinstance(key_name, list):
        keys = {}
        for key in key_name:
            api_key = os.getenv(key)
            if api_key:
                keys[key] = api_key
            else:
                keys[key] = st.secrets[key]
        return keys

    elif isinstance(key_name, str):
        api_key = os.getenv(key_name)
        if api_key:
            return api_key
        else:
            return st.secrets[key_name]

# Helper functions for file and directory operations
def create_directory(directory_path):
    """Creates a directory if it doesn't exist.

    Args:
        directory_path (str): The path to the directory to create.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


# Helper functions for file and directory operations
def delete_directory(directory_path):
    """Deletes a directory and its contents.

    Args:
        directory_path (str): The path to the directory to delete.
    """

    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)

######################################################################
# Initialize OpenAI client
OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_audio(text, voice):

    # audio_temp directory cleanup
    delete_directory("audio_temp")
    create_directory("audio_temp")

    try:
        # let's try to create the audio file
        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=text
            ) as  response:
            filenname = f"audio_temp/{uuid.uuid4()}.mp3"
            response.stream_to_file(filenname)

        # created the audio file
        return filenname
    except Exception as e:
        return f"Error: {str(e)}"
    
def create_voice_dropdown():

    # List of openai voices to choose from
    options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    # Create a dropdown
    selected_option = st.selectbox("Choose an option:", options)

    # Display the selected option
    st.write("You selected:", selected_option)
    return selected_option

## Function to determine the content type of the URL
def determine_content_type(url):
    try:
        response = requests.head(url)
        content_type = response.headers['Content-Type']
        if 'text/html' in content_type:
            return 'HTML'
        elif 'application/pdf' in content_type:
            return 'PDF'
        elif 'video/x-youtube-vid' in content_type:
            return 'YouTube Video'
        else:
            return 'Unknown'
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return 'Unknown'


######################################################################
# Access the environment variable
together_api_key = get_api_key('TOGETHER_API_KEY')

# Streamlit app layout
st.title("Summary Generator Tool")
st.write("This will take 3 kinds of URLs , a PDF, a website or youtube URL.  I will provide a summary of the transcript.")


col1, col2 = st.columns(2)
# Create a checkbox to enable text-to-speech
with col1:
    enable_tts = st.checkbox("Enable Text-to-Speech")

# If the checkbox is checked, run the function
if enable_tts:
    with col2:
        voice = create_voice_dropdown()

# Create a slider with values between 0 and 10
creativity_slider = st.sidebar.slider(
    "Creativity",
    min_value=0,
    max_value=10,
    value=1,
    step=1,
    key="creativity"
)

# Display the current value of the slider
st.write(f"Current creativity level: {creativity_slider}")
if creativity_slider == 0:
    hallucinations_score = 0
else:
    hallucinations_score = creativity_slider * 0.1

# Create a text input field for the user to enter the URL
url = st.text_input("Enter a website, a PDF or a YouTube video URL:")
# url_pattern = r'^(https?:\/\/)?([\w\-]+\.)+[\w\-]+(\/[\w\-.,@?^=%&:\/~+#]*)?$'
url_pattern = r'^(https?:\/\/)?([\w\-]+\.)+[\w\-]+(\/[\w\-.,@?^=%&:\/~+#]*)?$'
if re.match(url_pattern, url) is None:
    st.stop()

# Create a button to trigger the code generation
if st.button("Generate Summary"):
    
    with st.spinner("Processing..."):
        llm = ChatTogether(api_key=together_api_key, temperature=hallucinations_score, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")


        # Determine the content type of the URL
        content_type = determine_content_type(url)

        # Load the content based on the content type
        if content_type == 'HTML':
            loader = WebBaseLoader(url)
        elif content_type == 'PDF':
            loader = PyPDFLoader(url, extract_images=True)
        elif content_type == 'YouTube Video':
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)

        data = loader.load()

        # Create a prompt template for the description task
        description_template = PromptTemplate(
            input_variables=["transcript"],
            template="""
            Read through the entire transcript carefully.
                If the input is a youtube transcript treat is as document. If the transcript is a research paper, ensure that the summary captures the main idea of the paper and the key findings.
                Provide a concise summary of the main topic and purpose.
                Extract and list at least five and up ten most interesting or important points from the transcript. 
                For each point: State the key idea in a clear and concise manner.

                - Ensure your summary and key points capture the essence of the document without including unnecessary details.
                - Use clear, engaging language that is accessible to a general audience.
                - If the transcript includes any statistical data, expert opinions, or unique insights, 
                prioritize including these in your summary or key points.  If the transcript is formated as a resreasch paper with sections like abstract,introduction, menthods and conclusion.
            transcript: {transcript}    """
        )

        # Create the LLMChain with the prompt template and the LLM
        chain = LLMChain(prompt=description_template, llm=llm)

        # Run the chain with the provided video transcript
        summary = chain.invoke({
            "transcript": data[0].page_content
        })
        # If the checkbox is checked, run the function
        if enable_tts:
            text_audio = generate_audio(summary['text'], voice)
            st.audio(text_audio, format='audio/mp3', autoplay=True)
        # Access the content attribute of the AIMessage object
        st.write(summary['text'])

        st.divider()
        st.write(summary["transcript"])

 ######################################################################
 ### Hallucination Grader

    # Hallucination grader instructions
    hallucination_grader_prompt =  PromptTemplate(
        
        documents = summary["transcript"],
        generation = summary['text'],
        template=
        """FACTS: \n\n {documents} \n\n ANSWER: {generation}.
        You are a teacher grading a quiz. 
        You will be given FACTS and a ANSWER. 
        Here is the grade criteria to follow:
        (1) Ensure the ANSWER is grounded in the FACTS. 
        (2) Ensure the ANSWER does not contain "hallucinated" information outside the scope of the FACTS.
        Score:
        A score of yes means that the answer meets all of the criteria. This is the highest (best) score. 
        A score of no means that the answer does not meet all of the criteria. This is the lowest possible score you can give.
        Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 
        Avoid simply stating the correct answer at the outset.
        Return JSON with two two keys, binary_score is 'yes' or 'no' score to indicate whether the ANSWER is grounded in the FACTS. And a key, explanation, that contains an explanation of the score.""")

  
    # Create the LLMChain with the prompt template and the LLM
    h_chain = LLMChain(prompt=hallucination_grader_prompt, llm=llm)

    # summary = h_chain.invoke({
    #         "transcript": data[0].page_content
    #     })
    documents = summary["transcript"],
    generation = summary['text']
    
    summary = h_chain.invoke({
    'documents': documents,  # Replace with your actual documents variable
    'generation': generation  # Replace with your actual generation variable
})

    st.write('\n\n')
    st.write('### Hallucination Grader')
    st.write(summary['text'])

