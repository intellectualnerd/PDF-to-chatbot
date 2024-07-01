import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai
import numpy as np

# Configure the API key for Google Generative AI
gemini_api_key = "AIzaSyCO2idWHyU6f9yy4QAEZWqVHPdZdl4PUMI"
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text().lower()
    return text

def get_keywords_from_text(data):
    prompt = "Can you generate 10 key words according to this paragraph, comma-separated string? If you can't, just respond 'no, sorry'.\n" + data
    response = model.generate_content(prompt)
    try:
        keywords = response.text.split(", ")
    except ValueError:
        keywords = ["no, sorry"]
    return keywords

def process_pdf_text(text):
    cluster_paragraphs = text.split("\n\n")  # Example of splitting paragraphs, you can customize this
    chat_data = [{"data": data, "keywords": get_keywords_from_text(data)} for data in cluster_paragraphs]
    return chat_data

def get_relevant_data(chat_data, user_question):
    list_of_words = user_question.split()
    score_list = []
    for x in chat_data:
        score = sum(1 for y in x["keywords"] if y in list_of_words)
        score_list.append(score)
    indices = np.argsort(score_list)[-3:]  # Get top 3 matches
    ref_data = [chat_data[i]["data"] for i in indices]
    return ref_data

def get_answer(ref_data, user_question):
    prompt = "hello i have some paragraphs you need to understand it and answer the question.\n\n" + str(ref_data) + "\n\n my question: " + user_question
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("PDF Question Answering App")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        chat_data = process_pdf_text(text)
        st.write("PDF processed successfully. You can now ask questions about its content.")

        user_question = st.text_input("Ask a question about the PDF content:")
        if st.button("Get Answer") and user_question:
            ref_data = get_relevant_data(chat_data, user_question)
            answer = get_answer(ref_data, user_question)
            st.write("Answer:", answer)

if __name__ == "__main__":
    main()
