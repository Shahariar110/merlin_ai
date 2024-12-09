# Merlin: AI-Powered News Generator
Merlin is an AI-powered tool that fetches and summarizes news articles and creates engaging social media posts. It combines a Node.js backend for fetching news content and a Streamlit frontend for generating responses. The project integrates with APIs like Vectara and NewsAPI to provide an interactive and dynamic experience.

Features
• Fetch the latest news articles using NewsAPI.
• Summarize articles and provide concise insights using AI tools.
• Generate creative social media posts for platforms like Twitter, LinkedIn, etc.
• Simple and user-friendly UI powered by Streamlit.

## How to Use Merlin:
1. What to Ask Merlin

Merlin works best when you ask specific and relevant questions about news topics. It will fetch, summarize, and generate posts based on the topic you input.

## Do's:
"Get news about AI trends."
"Fetch the latest articles on climate change."
"Summarize news about Shah Rukh Khan."

## Don'ts:
Avoid questions like:
"How are you?"
"What’s the weather today?"
"Tell me a joke."
These will cause Merlin to overthink and fail to provide accurate results. Keep your questions focused on news-related topics.

# Setting Up Environment Variables
To run the project, you need to set up an environment file (api.env) containing your API keys and credentials.

Please follow the template given in the api.env.example file.

# Running the project

You can run the entire project by simply executing the Python script. The Streamlit frontend will automatically start the Node.js server in the background.

Steps to run:

1. Install necessary python dependencies using the following command:

pip install -r requirements.txt

2. Install Node.js dependencies:

npm install

3. Run the Python script:

streamlit run merlin.py

4. Open your browser and go to: http://localhost:8501.