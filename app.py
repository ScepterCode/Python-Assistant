import streamlit as st
import google.generativeai as genai
import os

# Set up the page
st.set_page_config(page_title="Python Q&A Assistant", page_icon="🐍")
st.title("🐍 Python Data Science & ML Assistant")
st.caption("Ask any Python, Data Science, or Machine Learning question!")

# Configure Gemini with your API key
# You can either set it as an environment variable or directly in the code
API_KEY = "AIzaSyAKbqKUZvxYbrAgY0gwRX_dqUq7z2AP5Uw"
genai.configure(api_key=API_KEY)

# Response style selector in sidebar
response_style = st.sidebar.selectbox(
    "🎯 Response Style",
    ["Conversational", "Concise", "Elaborate"],
    help="Choose how detailed you want the responses to be"
)

# System prompts for different styles
STYLE_PROMPTS = {
    "Conversational": """You are a friendly Python tutor specializing in Data Science and Machine Learning. 
Have natural, engaging conversations with students. Be warm, encouraging, and relatable.
- Use a casual, friendly tone
- Ask follow-up questions to understand their needs
- Share tips and personal insights
- Keep explanations conversational but accurate
- Use analogies and real-world examples
- Show enthusiasm for teaching""",
    
    "Concise": """You are an expert Python programmer specializing in Data Science and Machine Learning.
Provide SHORT, DIRECT answers.
- Get straight to the point
- Use bullet points when listing items
- Minimal explanation unless asked
- Show code examples without lengthy descriptions
- Be precise and efficient
- Maximum 3-4 sentences unless code is involved""",
    
    "Elaborate": """You are an expert Python instructor specializing in Data Science and Machine Learning.
Provide COMPREHENSIVE, DETAILED explanations.
- Explain concepts thoroughly with context
- Include multiple code examples
- Cover edge cases and best practices
- Explain WHY things work, not just HOW
- Include practical tips and common pitfalls
- Provide alternative approaches when relevant
- Use clear structure with explanations before and after code"""
}

# Base expertise (common to all styles)
BASE_EXPERTISE = """

Your expertise includes:
- Python fundamentals and advanced concepts
- NumPy, Pandas, Matplotlib, Seaborn
- Scikit-learn, TensorFlow, PyTorch, Keras
- Statistical analysis and data visualization
- Machine learning algorithms and best practices
- Deep learning architectures
- Data preprocessing and feature engineering
- Model evaluation and optimization

Always provide working, tested code examples. Be helpful, patient, and educational."""

# Combine style-specific prompt with base expertise
SYSTEM_PROMPT = STYLE_PROMPTS[response_style] + BASE_EXPERTISE

# Initialize chat history and track style changes
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = None
    st.session_state.current_style = response_style

# Reset chat if style changes
if st.session_state.current_style != response_style:
    st.session_state.chat = None
    st.session_state.current_style = response_style
    st.info(f"✨ Switched to **{response_style}** mode!")

# Create chat session
if st.session_state.chat is None:
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat = model.start_chat(history=[])

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your Python question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Send message and stream response
            response = st.session_state.chat.send_message(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            full_response = "Sorry, there was an error processing your request."
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar with example questions
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Example Questions")

# Style-specific examples
EXAMPLE_QUESTIONS = {
    "Conversational": [
        "I'm new to Python, where should I start?",
        "Can you explain what machine learning is?",
        "I'm stuck with pandas DataFrames, help!",
        "What's your favorite Python library?",
        "How do I get better at coding?"
    ],
    "Concise": [
        "How to drop NaN values in pandas?",
        "Gradient descent formula",
        "Create a simple neural network",
        "List vs tuple difference",
        "Plot confusion matrix code"
    ],
    "Elaborate": [
        "Explain the mathematics behind gradient descent",
        "How does backpropagation work in neural networks?",
        "Complete guide to handling missing data",
        "Explain overfitting and how to prevent it",
        "Deep dive into pandas groupby operations"
    ]
}

examples = EXAMPLE_QUESTIONS[response_style]

for ex in examples:
    if st.sidebar.button(ex, key=ex):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": ex})
        
        # Get AI response immediately
        try:
            response = st.session_state.chat.send_message(ex, stream=False)
            full_response = response.text
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            error_msg = f"Sorry, there was an error processing your request: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.chat = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Model:** Gemini 2.0 Flash")
st.sidebar.markdown("**Powered by Google AI**")
