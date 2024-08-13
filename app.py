from flask import Flask, render_template, request
from openai import OpenAI
import os
from docx import Document
import PyPDF2
import pdfplumber

app = Flask(__name__)

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

# Function to interact with GPT-4o-Mini to read and summarize the resume
def gpt_read_resume(resume_text):
    # System message guiding the model
    system_message = {
        "role": "system",
        "content": """
        You are an AI assistant. Given the text of a resume, please read it carefully
        
        Summarize it in a few sentences and answer the following questions:
        What is the highest degree level they have?
        Do they have work experience?
        How many years of experience do they have?
        Are there any other important information that adds a value to the candidate (e.g. skills, certifications.)?
        
        Write your answers in one short paragraph.
        Do not mention their contact information. 
        """
    }

    messages = [system_message, {"role": "user", "content": resume_text}]
    summary = ""
    attempts = 0
    max_attempts = 4

    while attempts < max_attempts:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # choose the model
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
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
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
    else:
        return "Unsupported file format", 400

    summary = gpt_read_resume(resume_text)
    return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)