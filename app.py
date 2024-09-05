# Import necessary libraries and modules
from flask import Flask, render_template, request  # Flask modules for creating routes and handling requests
from openai import OpenAI  # OpenAI API to interact with GPT models
import os  # For accessing environment variables
from docx import Document  # For reading DOCX files (Microsoft Word format)
import PyPDF2  # For extracting text from PDF files
import pdfplumber  # Another library for working with PDFs (not used here, can be removed if unnecessary)
from PIL import Image  # For handling image files (e.g., JPG, PNG)
import pytesseract  # For extracting text from images using OCR

# Flask-Limiter for setting request limits to prevent abuse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask app
app = Flask(__name__)

# Set up the rate limiter to allow a maximum of 50 requests per day per IP address
limiter = Limiter(
    get_remote_address,  # Use the remote IP address of the client to limit requests
    app=app,  # Apply the limiter to this Flask app
    default_limits=["50 per day"]  # Default limit is 50 requests per day
)

# Load OpenAI API key from environment variable
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # Fetch the API key from the system's environment variables
)

# If the OpenAI API key is missing, raise an error
if not client:
    raise ValueError("The OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# Function to extract text from a Word document (DOCX format)
def extract_text_from_docx(docx_file):
    """
    Extracts text from a DOCX file using the python-docx library.

    Args:
    docx_file: A DOCX file object.

    Returns:
    A string containing the extracted text.
    """
    doc = Document(docx_file)
    text = '\n'.join([para.text for para in doc.paragraphs])  # Extract paragraphs and join them with line breaks
    return text

# Function to extract text from a PDF using PyPDF2
def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file using PyPDF2.

    Args:
    pdf_file: A PDF file object.

    Returns:
    A string containing the extracted text.
    """
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)  # Read the PDF file
    for page in pdf_reader.pages:
        text += page.extract_text()  # Extract text from each page
    return text

# Function to extract text from image files using OCR (Optical Character Recognition)
def extract_text_from_image(image_file):
    """
    Extracts text from an image file using pytesseract (OCR).

    Args:
    image_file: An image file object (e.g., JPG, PNG).

    Returns:
    A string containing the extracted text from the image.
    """
    image = Image.open(image_file)  # Open the image file
    text = pytesseract.image_to_string(image)  # Use Tesseract to extract text from the image
    return text

# Function to interact with GPT-4o and summarize the resume text
def gpt_read_resume(resume_text):
    """
    Sends the extracted resume text to GPT-4o model to generate a summary.

    Args:
    resume_text: A string containing the resume text.

    Returns:
    A string containing the generated summary.
    """
    # System message providing instructions to GPT on how to summarize the resume
    system_message = {
        "role": "system",
        "content": """
        Given the resume, please read it carefully.

        Summarize it in a few sentences and make sure to answer the following questions:
        1. What is the highest degree level they have?
        2. Do they have work experience (and how many years of work experience)? 
        3. Are there any other important information that adds value to the candidate (e.g. skills, certifications.)?
        
        Write your answers in one short paragraph (100-120 words).
        Do not mention their contact information.

        Example: Khaled holds a Master’s degree in Electrical Engineering with a focus on Machine Learning. 
        He has no formal work experience but has completed several relevant projects.
        He possesses valuable technical skills in Python, SQL, and C++, and has certifications in 
        Data Science and MLOps. These elements, alongside his leadership awards, underscore his 
        potential as a promising candidate.
"
        """
    }

    # Create the conversation messages with the system message and user resume text
    messages = [system_message, {"role": "user", "content": resume_text}]
    summary = ""  # To store the final summary
    attempts = 0  # Track the number of attempts to generate a complete summary
    max_attempts = 3  # Maximum number of attempts allowed

    # Loop to interact with GPT and generate the summary
    while attempts < max_attempts:
        response = client.chat.completions.create(
            # model="gpt-4o-2024-08-06",  # Specify the GPT model version
            model="gpt-4o-mini-2024-07-18",  # Specify the GPT model version
            messages=messages,  # Send the conversation history
            max_tokens=200,  # Limit the length of the summary
            stop=["\n"]  # Stop generating at the end of a sentence
        )

        # Extract generated text from the response
        generated_text = response.choices[0].message.content

        summary += generated_text  # Append the generated text to the summary

        # If the summary ends with a valid sentence, break the loop
        if generated_text.strip().endswith(('.', '!', '?')):
            break
        else:
            # If the sentence is incomplete, send it back to GPT for further processing
            messages.append({"role": "user", "content": generated_text})
        
        attempts += 1  # Increment the number of attempts

    return summary  # Return the final summary

# Define the route for the home page
@app.route('/')
@limiter.exempt  # Exempt the home page from rate limiting
def index():
    """
    Renders the home page where users can upload their resume file.
    """
    return render_template('index.html')

# Define the route to handle file upload and resume summarization
@app.route('/summarize', methods=['POST'])
@limiter.limit("50 per day")  # Limit to 50 requests per day per IP
def summarize():
    """
    Handles the file upload, extracts text from the file, and summarizes the resume.
    """
    file = request.files['file']  # Get the uploaded file
    file_extension = file.filename.split('.')[-1].lower()  # Extract the file extension

    # Determine the file type and extract text accordingly
    if file_extension == 'pdf':
        resume_text = extract_text_from_pdf(file)
    elif file_extension == 'docx':
        resume_text = extract_text_from_docx(file)
    elif file_extension == 'txt':
        resume_text = file.read().decode('utf-8')
    elif file_extension in ['jpg', 'jpeg', 'png']:  # New: Support for image formats
        resume_text = extract_text_from_image(file)
    else:
        return "Unsupported file format", 400  # Return an error if file format is unsupported

    # Generate the summary using GPT-4o
    summary = gpt_read_resume(resume_text)
    return render_template('summary.html', summary=summary)

# Custom error handler for rate limit exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    """
    Handles the case where the rate limit is exceeded (HTTP 429).
    """
    return render_template('too_many_requests.html'), 429

# Main entry point to run the Flask app
if __name__ == '__main__':
    
    # Run locally
    app.run(debug=True)  # Run the app in debug mode for easier troubleshooting during development

    # # Run on Heroku
    # port = int(os.environ.get('PORT', 5000))  # Read PORT from environment variable, or default to 5000
    # app.run(host='0.0.0.0', port=port, debug=True)  # Bind to 0.0.0.0 to ensure it works on Heroku
