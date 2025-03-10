from flask import Flask, render_template, request, jsonify
import os
import json
import base64
from mistralai import Mistral
from dotenv import load_dotenv
app = Flask(__name__)

# Define directories for storing images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

def get_chat_response(image_path):
    # Getting the base64 string
    base64_image = encode_image(image_path)

    # Retrieve the API key from environment variables
    api_key = os.environ["MISTRAL_API_KEY"]

    # Specify model
    model = "pixtral-12b-2409"

    # Initialize the Mistral client
    client = Mistral(api_key=api_key)

    # Define the messages for the chat
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze this receipt and extract the following information in a structured dictionary format:"
                            "'store_name': The name of the store."
                            "'date': The invoice date."
                            "'invoice_code': The unique invoice number found on the receipt."
                            "'products': A list of dictionaries, each containing:"
                            "'name': The product name."
                            "'amount': The price of the product."
                            "Return the response as a valid JSON object with no additional text, explanations, or formatting. The response must start with '{' and end with '}'."
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]

    # Get the chat response
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )

    # Extract the response text
    response_text = chat_response.choices[0].message.content

    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove first 7 characters (` ```json `)
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove last 3 characters (` ``` `)

    try:
        # Convert response text to JSON
        print(response_text)
        parsed_json = json.loads(response_text)
        return parsed_json
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON ->", response_text)
        return {"error": "Invalid JSON response from AI"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    Upload an image and return extracted text in JSON format.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded image
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Perform OCR
    extracted_text = get_chat_response(file_path)

    if extracted_text is not None:
        try:
            json_data = jsonify({"extracted_text": extracted_text})
            print(f"DEBUG: JSON Response:{json_data}")
            return json_data
        except Exception as e:
            print("Error serializing JSON:", e)
            return jsonify({"error": "JSON serialization failed"}), 500
    else:
        return jsonify({"error": "OCR processing failed"}), 500



if __name__ == '__main__':
    app.run(debug=True)
