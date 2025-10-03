import os
import PyPDF2
import json
import traceback

# Optional fallback PDF text extractor (pdfminer)
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:
    pdfminer_extract_text = None

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            # Use PdfReader with strict=False to tolerate minor PDF errors
            pdf_reader = PyPDF2.PdfReader(file, strict=False)
            text = ""
            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text() or ""
                except Exception as page_err:
                    # Skip problematic pages but continue extracting others
                    traceback.print_exception(type(page_err), page_err, page_err.__traceback__)
                    page_text = ""
                text += page_text
            if not text.strip():
                # Try fallback with pdfminer if available
                if pdfminer_extract_text is not None:
                    try:
                        # Reset file pointer for a new read
                        file.seek(0)
                        miner_text = pdfminer_extract_text(file) or ""
                        if miner_text.strip():
                            return miner_text
                    except Exception as miner_err:
                        traceback.print_exception(type(miner_err), miner_err, miner_err.__traceback__)
                # If still empty, provide a clear, actionable error
                raise Exception(
                    "PDF has no extractable text. It may be a scanned/image-based PDF. "
                    "Use OCR to convert it to text or upload a .txt file."
                )
            return text

        except Exception as e:
            # Re-raise with context so upstream can show a helpful traceback
            raise Exception("error reading the PDF file") from e

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
        )

def extract_json_from_text(text):
    """Extract JSON from text that might contain extra formatting or text."""
    import re
    
    # Try direct parsing first
    try:
        return json.loads(text.strip())
    except:
        pass
    
    # Look for JSON blocks in markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except:
            pass
    
    # Look for JSON object boundaries
    start_idx = text.find('{')
    if start_idx != -1:
        # Find the matching closing brace
        brace_count = 0
        end_idx = start_idx
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx > start_idx:
            try:
                return json.loads(text[start_idx:end_idx])
            except:
                pass
    
    return None

def get_table_data(quiz_str):
    try:
        # Try to extract JSON from the text
        quiz_dict = extract_json_from_text(quiz_str)
        
        if not quiz_dict:
            raise Exception("Could not extract valid JSON from LLM output")
        
        quiz_table_data=[]
        
        # iterate over the quiz dictionary and extract the required information
        for key,value in quiz_dict.items():
            mcq=value["mcq"]
            options=" || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                 
                 ]
            )
            
            correct=value["correct"]
            quiz_table_data.append({"MCQ": mcq,"Choices": options, "Correct": correct})
        
        return quiz_table_data
        
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
