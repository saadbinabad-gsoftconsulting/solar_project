import streamlit as st
import pandas as pd
from datetime import datetime
from db_connection import get_reviews_collection
from gpt_input_extractor import GPTInputExtractor

reviews_collection = get_reviews_collection()
openai_client = GPTInputExtractor().client

def analyze_sentiment(review_text: str) -> str:
    """Analyze the sentiment of a review using GPT-4."""
    system_prompt = """You are a sentiment analyzer for solar system reviews. 
    Classify the sentiment of the review as either 'positive', 'negative', or 'neutral'.
    Return ONLY the classification as a single word without any additional text or explanation."""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": review_text}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        st.error(f"Error in sentiment analysis: {str(e)}")
        return "neutral"

def process_unclassified_reviews():
    """Process reviews that don't have sentiment classification."""
    try:
        # Find reviews without sentiment
        unclassified_reviews = reviews_collection.find({"sentiment": {"$exists": False}})
        processed_count = 0
        
        for review in unclassified_reviews:
            sentiment = analyze_sentiment(review['review_text'])
            
            # Update the review with sentiment
            reviews_collection.update_one(
                {"_id": review['_id']},
                {"$set": {"sentiment": sentiment}}
            )
            processed_count += 1
        
        return processed_count
    except Exception as e:
        st.error(f"Error processing reviews: {str(e)}")
        return 0

def get_sentiment_counts() -> dict:
    """Get counts of reviews by sentiment."""
    try:
        pipeline = [
            {"$group": {
                "_id": "$sentiment",
                "count": {"$sum": 1}
            }}
        ]
        results = list(reviews_collection.aggregate(pipeline))
        return {item["_id"]: item["count"] for item in results}
    except Exception as e:
        st.error(f"Error getting sentiment counts: {str(e)}")
        return {}

def get_recent_reviews(limit: int = 5) -> list:
    """Get the most recent reviews."""
    try:
        return list(reviews_collection.find().sort('timestamp', -1).limit(limit))
    except Exception as e:
        st.error(f"Error getting recent reviews: {str(e)}")
        return []

def display_reviews_dashboard():
    """Display the reviews dashboard in Streamlit."""
    st.title("Solar System Recommendation System ")
    
    # Create tabs for different sections
    tabs = st.tabs(["Recommendations", "Review Analysis"])
    
    with tabs[0]:
        # Display review statistics in the main recommendations tab
        st.header("Solar System Recommendations")
        
        # Your existing recommendation code goes here
        
        # Display review statistics
        st.subheader("Customer Review Statistics")
        sentiment_counts = get_sentiment_counts()
        
        # Create metrics for sentiment counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Positive Reviews", sentiment_counts.get('positive', 0), delta=f"{sentiment_counts.get('positive', 0)}%")
        with col2:
            st.metric("Negative Reviews", sentiment_counts.get('negative', 0), delta=f"{sentiment_counts.get('negative', 0)}%")
        with col3:
            st.metric("Neutral Reviews", sentiment_counts.get('neutral', 0), delta=f"{sentiment_counts.get('neutral', 0)}%")
    
    with tabs[1]:
        st.header("Review Analysis")
        
        # Add button to process unclassified reviews
        if st.button("Classify Unclassified Reviews"):
            with st.spinner("Processing reviews..."):
                processed_count = process_unclassified_reviews()
                if processed_count > 0:
                    st.success(f"Processed {processed_count} reviews successfully!")
                else:
                    st.info("No unclassified reviews found.")
        
        # Display sentiment distribution
        st.subheader("Sentiment Distribution")
        sentiment_counts = get_sentiment_counts()
        if sentiment_counts:
            df_sentiment = pd.DataFrame.from_dict(
                sentiment_counts, 
                orient='index',
                columns=['Count']
            )
            st.bar_chart(df_sentiment)
        
        # Display recent reviews
        st.subheader("Recent Reviews")
        recent_reviews = get_recent_reviews()
        
        for review in recent_reviews:
            # Convert timestamp string to datetime object
            timestamp = datetime.strptime(review['timestamp'], '%Y-%m-%d %H:%M:%S')  # Adjust format as needed
            with st.expander(f"Review from {timestamp.strftime('%Y-%m-%d %H:%M')}"):
                st.write("Review:", review['review_text'])
                if 'sentiment' in review:
                    sentiment_color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }
                    st.markdown(f"Sentiment: :{sentiment_color[review['sentiment']]}[{review['sentiment'].title()}]")
                else:
                    st.write("Sentiment: Not classified")