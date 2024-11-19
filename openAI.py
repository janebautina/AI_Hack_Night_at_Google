import weaviate
from dotenv import load_dotenv
import os
import requests
import json
import openai  # Import OpenAI library

# Load environment variables
load_dotenv("hack.env")
wcd_url = os.getenv("WCD_URL")  # Your Weaviate Cloud URL
wcd_api_key = os.getenv("WCD_API_KEY")  # Your Weaviate Cloud API Key
openai_api_key = os.getenv("OPENAI_APIKEY")  # Your OpenAI API Key

# Check if environment variables are set
if not wcd_url or not wcd_api_key or not openai_api_key:
    raise EnvironmentError("Environment variables WCD_URL, WCD_API_KEY, and OPENAI_APIKEY must be set.")

# Set up OpenAI API Key
openai.api_key = openai_api_key

# Function to generate trivia questions using OpenAI
def generate_trivia_question():
    prompt = "Generate a trivia question with its answer and category."
    
    # Use the new API methods that are compatible with version 1.0+
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # or "gpt-3.5-turbo", depending on the version
        prompt=prompt,
        max_tokens=150
    )

    # Parse the response
    generated_text = response['choices'][0]['text'].strip()
    question, answer, category = generated_text.split("\n")

    return {
        "question": question,
        "answer": answer,
        "category": category
    }
# Connect to Weaviate Cloud using v4 WeaviateClient
client = weaviate.Client(url=wcd_url, auth_client_secret=weaviate.auth.AuthApiKey(api_key=wcd_api_key))


# Check if the "Question" class exists in the schema
try:
    schema = client.schema.get()
    class_names = [cls['class'] for cls in schema.get("classes", [])]

    if "Question" not in class_names:
        print("Class 'Question' does not exist. Creating it now.")
        
        # Define the schema for the "Question" class
        question_class = {
            "class": "Question",
            "properties": [
                {"name": "question", "dataType": ["text"]},
                {"name": "answer", "dataType": ["text"]},
                {"name": "category", "dataType": ["text"]}
            ]
        }

        # Create the "Question" class in the schema
        client.schema.create_class(question_class)
        print("Class 'Question' created successfully.")
    else:
        print("Class 'Question' already exists in the schema.")

except Exception as e:
    print(f"Error checking or creating schema: {e}")

# Fetch the data (e.g., from a public JSON endpoint)
resp = requests.get("https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json")
data = json.loads(resp.text)

# Batch import objects into Weaviate
with client.batch() as batch:
    for d in data:
        batch.add_data_object({
            "answer": d["Answer"],
            "question": d["Question"],
            "category": d["Category"]
        }, class_name="Question")

# Example of generating a trivia question with OpenAI
trivia = generate_trivia_question()
print("Generated Trivia Question:")
print(f"Question: {trivia['question']}")
print(f"Answer: {trivia['answer']}")
print(f"Category: {trivia['category']}")

# Close the Weaviate client
client.close()

