import streamlit as st
from Backend.UserAuth import api_request
import re
from Backend.translations import get_text

def get_query(query_text):
    try:
        language = st.session_state.language
        #send request with question to server
        response = api_request("/ask/query", "POST", {"query_text": query_text, "language": language})
        #retrieve AI response
        return response["data"].get("response", ""), response["data"].get("context", "")
    except Exception as e:
        st.error(f"{get_text('server_connection_error', st.session_state.language)}")
        return None, None

def get_summary(query_text, word_num, complexity):
    try:
        language = st.session_state.language
        #send request with question to server
        response = api_request("/ask/summary", "POST", {"query_text": query_text, "word_num": word_num, "complexity": complexity, "language": language})
        #retrieve AI response
        return response["data"].get("response", ""), response["data"].get("context", "")
    except Exception as e:
        st.error(f"{get_text('server_connection_error', st.session_state.language)}")

def get_mcq(query_text, question_count, complexity):
    try:
        language = st.session_state.language
        #send request with question to server
        response = api_request("/ask/mcq", "POST", {"query_text": query_text, "question_count": question_count, "complexity": complexity, "language": language})
        #retrieve AI response
        return response["data"].get("response", ""), response["data"].get("context", "")
    except Exception as e:
        st.error(f"{get_text('server_connection_error', st.session_state.language)}")

#function to parse mcq
def parse_mcq_response(response_text):
    questions = []
    #question pattern
    pattern = r'\((\d+)\) Question: (.*?)\s*A: (.*?)\s*B: (.*?)\s*C: (.*?)\s*D: (.*?)\s*Answer: ([A-D])'
    #find all matches in the response text
    matches = re.findall(pattern, response_text, re.DOTALL)
    
    #loop through matches create dictionary for each question
    for match in matches:
        question_num, question_text, option_a, option_b, option_c, option_d, answer = match
        
        #create the dictionary for the question
        question_data = {
            "number": int(question_num),
            "question": question_text.strip(),
            "options": {
                "A": option_a.strip(),
                "B": option_b.strip(),
                "C": option_c.strip(),
                "D": option_d.strip()
            },
            "correct_answer": answer.strip()
        }
        #append the question data to the list
        questions.append(question_data)
    
    return questions

#function to handle option selection
def select_option(option):
    #check if is last question
    is_last_question = st.session_state.current_question == len(st.session_state.mcq_questions) - 1
    #check if this is a new answer
    new_answer = st.session_state.current_question not in st.session_state.user_answers
    
    #record the answer
    st.session_state.user_answers[st.session_state.current_question] = option
    
    #add to score if correct
    if option == st.session_state.mcq_questions[st.session_state.current_question]['correct_answer'] and new_answer:
        st.session_state.score += 1
    
    #set flag if this is the last question
    if is_last_question:
        st.session_state.last_question_answered = True