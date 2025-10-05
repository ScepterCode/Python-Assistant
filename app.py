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

# System prompt - this is where the magic happens
SYSTEM_PROMPT = """You are an expert Python programmer specializing in Data Science and Machine Learning.

Your expertise includes:
- Python fundamentals and advanced concepts
- NumPy, Pandas, Matplotlib, Seaborn
- Scikit-learn, TensorFlow, PyTorch, Keras
- Statistical analysis and data visualization
- Machine learning algorithms and best practices
- Deep learning architectures
- Data preprocessing and feature engineering
- Model evaluation and optimization

When answering:
1. Provide clear, working code examples
2. Explain concepts simply but thoroughly
3. Include best practices and common pitfalls
4. Suggest alternatives when relevant
5. If you're unsure about version-specific details, mention it
6. Format code properly with comments

Be helpful, patient, and educational. Students are learning from you."""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = None

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
st.sidebar.subheader("💡 Example Questions")
examples = [
    "How do I handle missing values in pandas?",
    "Explain gradient descent simply",
    "Show me how to build a simple neural network",
    "What's the difference between list and tuple?",
    "How do I plot a confusion matrix?"
]

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
st.sidebar.markdown("**Built by The Scepter**")