import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests
from pydantic import Field, BaseModel
from PIL import Image
from io import BytesIO
from IPython.display import display
from vectara_agentic.agent import Agent
from vectara_agentic.tools import VectaraToolFactory
from vectara_agentic.agent import AgentStatusType
from vectara_agentic.tools import ToolsFactory
from PIL import Image
from huggingface_hub import InferenceClient
import subprocess
import json

load_dotenv("api.env",override=True)

api_key = str(os.environ['VECTARA_API_KEY'])
customer_id = str(os.environ['VECTARA_CUSTOMER_ID'])
corpus_id = str(os.environ['VECTARA_CORPUS_ID'])

# ========== SETUP VECTARA ==========
vec_factory = VectaraToolFactory(
  vectara_api_key = api_key,
  vectara_customer_id = customer_id,
  vectara_corpus_id = corpus_id
)

# ========== RAG TOOL ==========
class Query(BaseModel):
    query: str = Field(..., description="The user query.")

rag = vec_factory.create_rag_tool(
    tool_name = "rag",
    tool_description = """
    Given any questions about Black Holes, System Identification, or Melbourne's light rail transport
    or autonomous trams with deep learning, use this tool
    """,
    tool_args_schema = Query,
    summary_num_results = 10,
    n_sentences_before = 3,
    n_sentences_after = 3,
    mmr_diversity_bias = 0.1,
    include_citations = False
)

# ========== IMAGE GENERATION ==========
def gen_img(prompt: str = Field(description="Prompt for image generation."),) -> str:
    """
    Generates an image using Hugging Face's Stable Diffusion model API and displays it in a notebook.

    Args:
        prompt (str): The text prompt describing the image.

    Returns:
        None: Displays the generated image.
    """
    client = InferenceClient("black-forest-labs/FLUX.1-dev", token="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")

    try:
        image = client.text_to_image(prompt)
        image.show()

        return "Image has been generated"

    except requests.exceptions.RequestException as e:
        return "Image generation failed: {str(e)}"

# ========== AGENT INSTRUCTIONS ==========
instructions = """
  - You are a helpful content generator named Merlin, with expertise in generating text, image, memes, and videos for different platforms in different tones based on user's timeliness requirements.
  - Always respond politely.
  - Always use the rag tool to answer questions about Black Holes, System Identification, or Melbourne's light rail transport
  or autonomous trams with deep learning.
  - If the rag tool gives an error, use the standard_tools instead.
  - Always use the gen_img tool to generate image or picture as specified by User's query.
  - Always use the news tool to generate recent news about the keyword in User's query.
  - If the user greets you, tell them you can assist with generating content, images, and providing info about black holes, system ID, and Autonomous trams in Melbourne
  - Be **concise with your responses**, **do not overthink.**
"""
# ========== NEWS FETCHER ==========
NODE_API_URL = "http://localhost:3000/fetch-article"

def news(keyword: str = Field(description="Keyword for which news is to be fetched"),) -> str:
    """
    Use this tool to fetch the news for a relevant keyword
    """
    try:
        # Start the Node.js server in a subprocess
        process = subprocess.Popen(
            ["node", "news_fetcher.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        news = fetch_news(keyword)
        return news
    except Exception as e:
        st.error(f"Failed to start Node.js server: {e}")
        return None
        
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return None
    
def fetch_news(keyword):# str = Field(description="Keyword for which news is to be fetched"),) -> str:
    try:
        response = requests.get(NODE_API_URL, params={"keyword": keyword})
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ========== AGENT ==========
agent = Agent(
    tools=[rag]+ToolsFactory().standard_tools()+[ToolsFactory().create_tool(gen_img)]+[ToolsFactory().create_tool(news)],
    topic="Content Generation",
    custom_instructions=instructions,
    # update_func=update_func
)

# ========== GENERATE RESPONSE ==========
def generate_response(agent,query):
    return agent.chat(query)

# ========== CONFIGURE THE APP ==========
st.set_page_config(
    page_title="Merlin",
    layout="wide",  # Responsive layout
    initial_sidebar_state="collapsed",
)

# ========== SETUP LOGO AND TITLE ==========
LOGO_PATH = "merlin_logo.png"  # Replace with your actual logo path
if "logo_hidden" not in st.session_state:
    st.session_state["logo_hidden"] = False

# Display the title and logo initially
if not st.session_state["logo_hidden"]:
    col1, col2, col3 = st.columns([1.25, 1, 1])
    with col2:
        if LOGO_PATH:
            logo = Image.open(LOGO_PATH)
            st.image(logo,width=300,use_container_width=False)
        # st.markdown("<h1 style='text-align: center;'>Merlin</h1>", unsafe_allow_html=True)
    st.divider()

# ========== HANDLE USER INPUT ===========
# Store the conversation history
flag = 0
if "history" not in st.session_state:
    st.session_state["history"] = []
    flag = 1

if flag:
    st.markdown("**🪄 Merlin**: Hey there! 🪄 I'm Merlin, your magical AI assistant. Ask me anything!")
    st.divider()
    flag = 0


def clear_text():
    st.session_state["text"] = ""

# Text input for user prompt
with st.container():
    user_input = st.text_input(
        "Ask Merlin:",
        placeholder="Type your prompt here...",
        key="text",
    )
    st.button("Clear Prompt Box", on_click=clear_text)


if "text" not in st.session_state:
    st.session_state["text"] = ""
if user_input:
    response= generate_response(agent,user_input)
    st.session_state["history"].append({"user": user_input, "response": response})

# ========== DISPLAY CONVERSATION ==========
if st.session_state["history"]:
    for entry in reversed(st.session_state["history"]):  # Reverse the order of history
        st.markdown(f"**🧑 You**: {entry['user']}")
        st.markdown(f"**🪄 Merlin**: {entry['response']}")
        st.divider()

# ========== STYLING ==========
st.markdown(
    """
    <style>
    .block-container {
        padding: 1rem 2rem;
    }
    .text-input {
        margin-top: 10px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
