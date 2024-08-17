from flask import Flask, render_template, request
from openai import OpenAI
import os
from docx import Document
import PyPDF2
import pdfplumber
from PIL import Image
import pytesseract

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Set up the rate limiter to allow 50 requests per day per IP address
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per day"]
)

# Load OpenAI API key from environment variable
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

if not client:
    raise ValueError("The OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# Function to extract text from a Word document
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

# Function to extract text from a PDF using PyPDF2 (fallback option)
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

# Function to interact with GPT-4o-Mini to read and summarize the resume
def gpt_read_resume(resume_text):
    # System message guiding the model
    # system_message = {
    #     "role": "system",
    #     "content": """
    #     Given the text of a resume, please read it carefully
        
    #     Summarize it in a few sentences and answer the following questions:
    #     1. What is the highest degree level they have?
    #     2. Do they have work experience? 
    #         a. If yes, write how many years of work experience they have.
    #         b. If no, write they have no formal work experience.
    #     3. How many years of experience do they have?
    #     4. Are there any other important information that adds a value to the candidate (e.g. skills, certifications.)?
        
    #     Write your answers in one short paragraph (100-120 words).
    #     Do not mention their contact information. 
    #     """
    # }

    # System message guiding the model
    system_message = {
        "role": "system",
        "content": """
        Given the text of a resume, please read it carefully
        
        Summarize it in a few sentences and answer the following questions:
        1. What is the highest degree level they have?
        2. Do they have work experience? 
            a. If yes, write how many years of work experience they have.
            b. If no, write they have no formal work experience.
        3. How many years of experience do they have?
        4. Are there any other important information that adds a value to the candidate (e.g. skills, certifications.)?
        
        Write your answers in one short paragraph (100-120 words).
        Do not mention their contact information. 

        Example 1: 
        "
        Khaled Alrashidi holds a Master’s degree in Electrical and Computer Engineering with a focus on Machine Learning and Data Science.
         Although the resume does not specify any formal work experience, Khaled has worked on numerous machine learning projects such as 
         a credit card fraud detector and a sentiment analysis of IMDB movie reviews, showcasing his hands-on expertise and skills in the field.
         In addition, he possesses valuable technical skills in Python, SQL, and C++, and has certifications in Data Science and MLOps.
         These elements, alongside his leadership awards, underscore his potential as a promising candidate.
         "

        """
    }

    messages = [system_message, {"role": "user", "content": resume_text}]
    summary = ""
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        response = client.chat.completions.create(
            # model="gpt-4o-mini-2024-07-18",  # choose the model
            model="gpt-4o-2024-08-06",  # choose the model
            messages=messages,
            max_tokens=200,  # the summary length
            stop=["\n"]  # Add a stop sequence to gracefully end the output
        )

        generated_text = response.choices[0].message.content

        summary += generated_text

        if generated_text.strip().endswith(('.', '!', '?')):
            break
        else:
            messages.append({"role": "user", "content": generated_text})
        
        attempts += 1

    return summary

@app.route('/')
@limiter.exempt
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
@limiter.limit("50 per day")
def summarize():
    file = request.files['file']
    file_extension = file.filename.split('.')[-1].lower()

    # Extract text based on file type
    if file_extension == 'pdf':
        resume_text = extract_text_from_pdf(file)
    elif file_extension == 'docx':
        resume_text = extract_text_from_docx(file)
    elif file_extension == 'txt':
        resume_text = file.read().decode('utf-8')
    elif file_extension in ['jpg', 'jpeg', 'png']:
        resume_text = extract_text_from_image(file)
    else:
        return "Unsupported file format", 400

    summary = gpt_read_resume(resume_text)
    return render_template('summary.html', summary=summary)

# Custom error handler for when the rate limit is exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('too_many_requests.html'), 429

if __name__ == '__main__':
    app.run(debug=True)