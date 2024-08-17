# **Resume Summarizer Application**

### **Overview**

The **Resume Summarizer Application** is a web-based tool designed to streamline the recruitment process for NBK’s Talent Acquisition team. By automating the summarization of resumes, 
this application helps reduce manual workload, allowing the team to focus on more important tasks. The application is powered by artificial intelligence (AI) and can process 
resumes in various formats, extracting key information and presenting it in a concise, structured summary. While it was designed for the Talent Acquisition team at NBK, it can be used for 
and by anyone. 

---
![Home Page](/images/Home_Page.png)

---

![Summary Page](/images/Summary_Page.png)

---

### **Key Features**

- **Multi-Format Compatibility**: The application accepts resumes in the following formats:
  - PDF
  - DOCX
  - TXT
  - Image formats: JPG, JPEG, PNG
- **AI-Powered Summarization**: Leveraging the GPT-4o model, the application automatically generates summaries that include:
  - The candidate’s highest degree.
  - Work experience (including the number of years and relevant fields).
  - Key skills and certifications.
- **User-Friendly Interface**: A simple, intuitive design makes it easy for the Talent Acquisition team to upload resumes and review summaries.
- **Data Privacy & Security**: The application does not store any personal data once the resume is processed. Contact information is excluded from the summaries to protect
candidates' privacy.
- **Request Limit**: To manage system load, each user is limited to 50 requests per day. This ensures fair use and prevents system overload.

---

### **How It Works**

1. **Upload a Resume**: Users can upload resumes in supported formats through the web interface.
2. **Resume Processing**: The application extracts text using Optical Character Recognition (OCR) for images and other text extraction methods for non-image formats.
3. **AI-Generated Summary**: The AI model processes the extracted text and generates a summary that highlights the candidate's qualifications and work experience.
4. **Review and Input**: The Talent Acquisition team can review the summary and input the key data into MyNBK. The application may be expanded in the future to allow automatic profile updates
in the MyNBK database.

---

### **User Benefits**

- **Efficiency**: Speeds up the candidate assessment process by summarizing resumes in seconds.
- **Accuracy**: Ensures that critical information is captured consistently, reducing the risk of oversight.
- **Time-Saving**: Allows The Talent Acquisition team to focus on deeper candidate evaluation instead of manual resume review.

---

### **Privacy and Security**

- **No Data Storage**: The application does not retain any resume data after processing. All files are immediately discarded once the summary is generated.
- **Contact Information**: To further protect candidates’ privacy, the AI is configured not to include any personal contact information in the generated summaries.

---

### **Cost Estimations**

- **API Usage**: The GPT-4o API charges $2.50 per 1 million input tokens and $10 per 1 million output tokens. Processing 1,000 resumes costs approximately $12.50.
- **Deployment**: The application is deployed on Heroku at a cost of $7 per month ($84 per year).
- **Total Estimated Annual Cost**: $96.50.

---

## **Non-Technical Setup**

### **Prerequisites**
To run the Resume Summarizer Application locally, ensure that you have the following:
- Python 3.x installed
- Flask framework
- OpenAI API key
- Required Python libraries
  - `Flask`
  - `docx`
  - `PyPDF2`
  - `pytesseract`
  - `Pillow` (PIL)
  - `flask_limiter`

---

### **Setup Instructions**
Follow these steps to set up the application locally:

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd resume-summarizer
   ```

2. **Install Required Packages**
   Make sure to create a virtual environment and install the required Python packages:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   pip install -r requirements.txt
   ```

   The `requirements.txt` should contain:
   ```plaintext
   Flask
   openai
   docx
   PyPDF2
   Pillow
   pytesseract
   flask_limiter
   ```

3. **Set the OpenAI API Key**
   You need to have an OpenAI API key to run the GPT-4o model. You can set this as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

4. **Run the Application**
   Once everything is set up, run the Flask development server:
   ```bash
   python app.py
   ```

5. **Access the Application**
   The application will be accessible at `http://127.0.0.1:5000` in your web browser.

---

### **Usage Instructions**
1. **Upload a Resume**
   The home page allows you to upload resumes in formats such as **PDF, DOCX, TXT, JPG, JPEG, and PNG**. Simply select the file, click "Summarize," and let the AI generate a summary.
   
2. **View the Summary**
   Once the resume is processed, the system will display a concise summary of the candidate’s qualifications and work experience.

3. **Request Limit**
   The system has a request limit of 50 per day to prevent overuse.

---

## **Technical Details**

### **app.py**
The `app.py` file contains the core logic of the application. Below are the essential parts of the application, explained:

1. **Flask Setup and Rate Limiting**
   The app is built using **Flask** with a **Flask-Limiter** to manage request limits (50 requests per day per user). The app also utilizes the **OpenAI API** to generate summaries of resumes using **GPT-4o**.

2. **File Handling**
   The app supports multiple file formats. It uses libraries like **docx**, **PyPDF2**, and **pytesseract** to extract text from DOCX, PDF, and image files (JPG, PNG).

3. **AI Processing**
   The extracted text is sent to the GPT-4o API, which generates a structured summary by answering key questions about the candidate’s qualifications, experience, and skills.

4. **Error Handling**
   The app includes custom error handling for **rate limits** (HTTP 429), displaying a friendly message when the user exceeds the daily request limit.

---

### **Next Steps**

- **Integration with MyNBK**: The application can be expanded to automatically update candidate profiles within the MyNBK platform, further streamlining recruitment workflows.
- **Multi-Language Support**: Adding support for languages like **Arabic** will enhance accessibility for NBK’s diverse candidate pool.


