from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from db_connection import get_solar_info_collection
from config import OPENAI_API_KEY

PROMPT_TEMPLATE = """
Answer the question based only on the following data:
{data}
Answer the question: {question}.
Provide a detailed answer.
Do not provide any information not mentioned in the data. Also do not mention you are comparing anything from datasets. Make the response professional and warm, like based on our working we think best suited choice would be....
"""
prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

def recommend_solar_system(num_rooms, appliances, electric_bill, location):
    collection = get_solar_info_collection()
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    user_query = (
        f"No_of_Bedrooms: {num_rooms}, "
        f"No_of_Heavy_Appliances: {appliances}, "
        f"Monthly_Electricity_Bill: ${electric_bill}, "
        f"Location: {location}"
    )

    query_embedding = embeddings.embed_query(user_query)

    results = collection.aggregate([
        {
            "$vectorSearch": {
                "queryVector": query_embedding,
                "path": "Embeddings",
                "index": "default",
                "score": {"$meta": "vectorSearchScore"},
                "numCandidates": 100,
                "limit": 3
            }
        },
        {
            "$project": {"embedding": 0}
        }
    ])

    best_match_data = next(results, None)

    if best_match_data:
        best_match_text = (
            f"Bedrooms: {best_match_data['No_of_Bedrooms']}, Appliances: {best_match_data['No_of_Heavy_Appliances']}, "
            f"Bill: ${best_match_data['Monthly_Electricity_Bill']}, Location: {best_match_data['Location']}, "
            f"Suggested Solar System: {best_match_data['Suitable_Solar_System']}"
        )

        prompt = prompt_template.format_messages(data=best_match_text, question=user_query)
        model = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
        response_text = model.predict_messages(prompt)
        return response_text.content
    return "Sorry, I couldn't find a suitable recommendation based on your inputs."