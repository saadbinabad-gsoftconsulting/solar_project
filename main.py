import streamlit as st
from gpt_input_extractor import GPTInputExtractor
from recommendation import recommend_solar_system
from reviews_dashboard import display_reviews_dashboard

st.title("Solar System Recommendation Chatbot 🌞")
st.write("Let me help you find the perfect solar system for your needs!")

# Initialize session state
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'collected_data' not in st.session_state:
    st.session_state.collected_data = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'recommendation_made' not in st.session_state:
    st.session_state.recommendation_made = False
if 'show_reviews' not in st.session_state:
    st.session_state.show_reviews = False

# Navigation buttons
if st.button("Go to Reviews"):
    st.session_state.show_reviews = True
    st.session_state.current_question_index = 0  # Reset questions if navigating
    st.session_state.collected_data = {}
    st.session_state.chat_history = []
    st.session_state.recommendation_made = False

if st.button("Back to Recommendations"):
    st.session_state.show_reviews = False

# Display Reviews or Recommendations based on session state
if st.session_state.show_reviews:
    display_reviews_dashboard()
else:
    # Questions and their corresponding keys
    questions = [
        "How many bedrooms are there in your home?",
        "How many heavy appliances do you use?",
        "What is your average monthly electricity bill?",
        "What is your location? (City or region)"
    ]
    keys = ['num_rooms', 'appliances', 'electric_bill', 'location']

    # Initialize extractor
    extractor = GPTInputExtractor()

    # Display chat history
    for message in st.session_state.chat_history:
        if message['type'] == 'bot':
            st.write("🤖 " + message['content'])
        else:
            st.write("👤 " + message['content'])

    # Display current question if not all questions are answered
    if st.session_state.current_question_index < len(questions):
        st.write("🤖 " + questions[st.session_state.current_question_index])
        
        # User input
        user_input = st.text_input("Your response:", key=f"input_{st.session_state.current_question_index}")
        
        if st.button("Submit"):
            if user_input:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': user_input
                })
                
                # Extract information
                extracted_value = extractor.extract_information(
                    user_input, 
                    keys[st.session_state.current_question_index]
                )
                
                if extracted_value is not None:
                    # Store the extracted value
                    st.session_state.collected_data[keys[st.session_state.current_question_index]] = extracted_value
                    
                    # Move to next question
                    st.session_state.current_question_index += 1
                    
                    # Rerun to update the UI
                    st.rerun()
                else:
                    st.error("I couldn't understand your input. Please try again.")

    # Generate recommendation when all questions are answered
    elif not st.session_state.recommendation_made:
        recommendation = recommend_solar_system(
            num_rooms=st.session_state.collected_data['num_rooms'],
            appliances=st.session_state.collected_data['appliances'],
            electric_bill=st.session_state.collected_data['electric_bill'],
            location=st.session_state.collected_data['location']
        )
        
        # Add recommendation to chat history
        st.session_state.chat_history.append({
            'type': 'bot',
            'content': recommendation
        })
        
        st.session_state.recommendation_made = True
        st.rerun()

    # Add reset button after recommendation
    if st.session_state.recommendation_made:
        if st.button("Start New Recommendation"):
            # Reset all session state variables
            st.session_state.current_question_index = 0
            st.session_state.collected_data = {}
            st.session_state.chat_history = []
            st.session_state.recommendation_made = False
            st.rerun()

    # Add sidebar with collected information
    with st.sidebar:
        st.header("Collected Information")
        if st.session_state.collected_data:
            st.write("Number of Bedrooms:", st.session_state.collected_data.get('num_rooms', 'Not provided'))
            st.write("Number of Appliances:", st.session_state.collected_data.get('appliances', 'Not provided'))
            st.write("Monthly Electric Bill:", f"${st.session_state.collected_data.get('electric_bill', 'Not provided')}")
            st.write("Location:", st.session_state.collected_data.get('location', 'Not provided'))