from flask import Flask, request, render_template, send_file
import os
import pdfplumber
import docx
import csv
from werkzeug.utils import secure_filename
import  google.generativeai as genai
from fpdf import FPDF
from MCQgeneration import generateMCQ

os.environ["GEMINI_API_KEY"]="AIzaSyClnUp_nEs9xIEgDWb0b-rOiR8TdrzkR7M"
genai.configure(api_key = os.environ['GEMINI_API_KEY'])

model = genai.GenerativeModel("models/gemini-1.5-pro")


app = Flask(__name__)
app.config['TRANSFER_FOLDER']='transfer/'
app.config['TRANSMIT_FOLDER']='transmit/'
app.config['PERMITTED_EXTENSIONS']={'pdf','txt','docx'}


# custom functions

def acceptable_files(fname):
    return '.' in fname and fname.rsplit('.',1)[1].lower() in app.config['PERMITTED_EXTENSIONS']

def get_text(file_path):
    file_name, extension = os.path.splitext(file_path)
    text = ""
    if extension == '.pdf':
        with pdfplumber.open(file_path) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
    elif extension == '.txt':
        with open(file_path) as f:
            text = f.read()
    elif extension == '.docx':
        doc = docx.Document(file_path)
        text = "".join([para.text for para in doc.paragraphs ])
    return text

def Question_mcqs_generator(text,num_of_ques):
    prompt = f"""
    You are an AI assistant helping the user generate multiple-choice questions (MCQs) based on the following text:
    '{text}'
    Please generate {num_of_ques} MCQs from the text. Each question should have:
    - A clear question
    - Four answer options (labeled A, B, C, D)
    - The correct answer clearly indicated
    Format:
    ## MCQ
    Question: [question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Correct Answer: [correct option]
    """
    response = model.generate_content(prompt)
    return response

def save_mcqs_to_text_file(mcqs, fname):
    storage_path = os.path.join(app.config['TRANSMIT_FOLDER'], fname)
    with open(storage_path, 'w') as f:
        f.write(mcqs)
    return storage_path

def save_mcqs_to_pdf_file(mcqs, fname):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)  # Add a line break

    path = os.path.join(app.config['TRANSMIT_FOLDER'], fname)
    pdf.output(path)
    return path

# Endpoints:
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generateMCQS',methods=['POST'])
def generate_questions():
    if 'file' not in request.files:
        return "No ATTACHMENT!!"
    file = request.files['file']
    if file and acceptable_files(file.filename):
        f_name = secure_filename(file.filename)
        f_path = os.path.join(app.config['TRANSFER_FOLDER'],f_name)
        file.save(f_path)
        text = get_text(f_path)

        if text:
            number_of_questions = int(request.form['num_questions'])
            # mcqs = Question_mcqs_generator(text,number_of_questions).text
            mcqs = generateMCQ(text,number_of_questions)
            # Saving the questions generated to text and pdf files
            text_file = f"MCQS_{f_name.rsplit('.', 1)[0]}.txt"
            pdf_file = f"MCQS_{f_name.rsplit('.', 1)[0]}.pdf"
            save_mcqs_to_text_file(mcqs, text_file)
            save_mcqs_to_pdf_file(mcqs, pdf_file)
            return render_template('results.html',mcqs=mcqs, text_file=text_file, pdf_file=pdf_file)


    return render_template('results.html')


@app.route('/download/<fname>')
def download(fname):
    path = os.path.join(app.config['TRANSMIT_FOLDER'],fname)
    return send_file(path,as_attachment=True)

if __name__=='__main__':
    if not os.path.exists(app.config['TRANSFER_FOLDER']):
        os.makedirs(app.config['TRANSFER_FOLDER'])
    
    if not os.path.exists(app.config['TRANSMIT_FOLDER']):
        os.makedirs(app.config['TRANSMIT_FOLDER'])
    app.run(debug=True)