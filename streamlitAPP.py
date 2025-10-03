import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from src.mcqgenerator.MCQgenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# Load example response schema used by the prompt
with open('/Users/adityaalok/Desktop/MCQGenerator/Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# creating the title for the mcq
st.title("MCQ Generator using langchain")

# creating form
with st.form("user_input"):
    uploaded_file = st.file_uploader("Upload a txt or PDF file")
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
    subject = st.text_input("Insert subject", max_chars=20)
    tone = st.text_input("complexity level of Questions", max_chars=20, placeholder="simple")
    button = st.form_submit_button("Create MCQs")

if button:
    if uploaded_file is None or not subject or not tone:
        st.error("Please provide a file, subject, and tone.")
    else:
        with st.spinner("Generating MCQs and evaluation..."):
            try:
                # Read input text from uploaded file
                text = read_file(uploaded_file)

                # Prepare inputs for the chain
                inputs = {
                    "text": text,
                    "number": int(mcq_count),
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON)
                }

                # Run the generation + evaluation chain
                result = generate_evaluate_chain(inputs)

                quiz_str = result.get("quiz") if isinstance(result, dict) else None
                review_str = result.get("review") if isinstance(result, dict) else None

                if not quiz_str:
                    st.error("Failed to generate quiz. Please check API key and input text.")
                    logging.error("Quiz generation returned empty result: %s", str(result))
                else:
                    # Show raw output for debugging
                    st.subheader("Raw LLM Output (for debugging)")
                    st.code(quiz_str, language="json")
                    
                    table_data = get_table_data(quiz_str)
                    if not table_data:
                        st.error("Could not parse the generated MCQs. The raw output is shown above for debugging.")
                        st.info("The LLM may have included extra text or formatting. Try again or check the output format.")
                    else:
                        df = pd.DataFrame(table_data)
                        st.subheader("Generated MCQs")
                        st.dataframe(df, use_container_width=True)

                        # Optional CSV download
                        csv_bytes = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="Download MCQs as CSV",
                            data=csv_bytes,
                            file_name="generated_mcqs.csv",
                            mime="text/csv"
                        )

                    if review_str:
                        st.subheader("Quiz Evaluation")
                        st.write(review_str)

            except Exception as e:
                logging.exception("Error during MCQ generation")
                st.error("An error occurred while generating MCQs.")
                st.code("\n".join(traceback.format_exception(type(e), e, e.__traceback__)))