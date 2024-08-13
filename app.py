from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Load OpenAI API key from environment variable
client = OpenAI(
    api_key=os.environ.get("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"),
)

# Raise an error if the OpenAI API key is not set
if not client:
    raise ValueError("The OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

def summarize_resume(resume_text, max_attempts=3):
    system_message = {
        "role": "system",
        "content": """
        You are an AI assistant specialized in summarizing resumes concisely. 
        Please provide a brief summary highlighting the candidate's education, experience, and key skills.
        """
    }

    messages = [system_message, {"role": "user", "content": resume_text}]
    summary = ""
    attempts = 0

    while attempts < max_attempts:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Ensure this is the correct model name
            messages=messages,
            max_tokens=150,  # Increase the summary length
            stop=["\n"]  # Add a stop sequence to gracefully end the output
        )

        # Extract the generated text
        generated_text = response.choices[0].message.content
        summary += generated_text

        # Check if the summary ends with a complete sentence
        if generated_text.strip().endswith(('.', '!', '?')):
            break
        else:
            # Append the generated text as the next part of the prompt for continuation
            messages.append({"role": "user", "content": generated_text})
        
        attempts += 1

    # Finalize and return the summary
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    resume_text = request.form['resume_text']
    summary = summarize_resume(resume_text)
    return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)