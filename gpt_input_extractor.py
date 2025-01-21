import json
from openai import OpenAI
from config import OPENAI_API_KEY

class GPTInputExtractor:
    """Handles extraction of information using GPT-4."""
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.extraction_prompts = {
            'num_rooms': """Extract the number of bedrooms from the text. Return a JSON in this format: 
                          {"number": <extracted_number>}. Convert word numbers to digits. 
                          Example: "I have four bedrooms" -> {"number": 4}""",
            
            'appliances': """Extract the number of appliances from the text. Return a JSON in this format: 
                           {"number": <extracted_number>}. Convert word numbers to digits.
                           Example: "We use three appliances" -> {"number": 3}""",
            
            'electric_bill': """Extract the monthly bill amount from the text. Return a JSON in this format: 
                              {"amount": <extracted_number>}. Remove any currency symbols and convert word numbers to digits.
                              Example: "We pay $200 monthly" -> {"amount": 200}""",
            
            'location': """Extract the location from the text. Return a JSON in this format: 
                         {"location": <extracted_location>}.
                         Example: "I live in New York" -> {"location": "New York"}"""
        }

    def extract_information(self, text: str, field_type: str) -> any:
        """Extract information using GPT-4 based on the field type."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.extraction_prompts[field_type]},
                    {"role": "user", "content": text}
                ],
                temperature=0
            )
            
            try:
                extracted_data = json.loads(response.choices[0].message.content)
                
                if field_type in ['num_rooms', 'appliances']:
                    return extracted_data.get('number')
                elif field_type == 'electric_bill':
                    return extracted_data.get('amount')
                else:  # location
                    return extracted_data.get('location')
            except json.JSONDecodeError:
                return None
        except Exception as e:
            return None