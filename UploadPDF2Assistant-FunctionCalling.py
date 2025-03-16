## Change it to use opeanai responses api. Please upgrade your openai library to minimal 1.66.3

import time
import json
import sys
from openai import OpenAI
import tkinter as tk
from tkhtmlview import HTMLLabel

# Set Constants and control some for future use
timeout_seconds = 90  # force stop after timeout_seconds reached
wait_time = 3
pause_time = 1
content_length = 5000
enable_logging = True

# Replace match-case with a dictionary for better readability and maintenance
language_map = {
    1: "Malay",
    2: "Chinese",
    3: "Japanese",
    4: "Korean",
    5: "German",
    6: "Indonesian",
    7: "Vietnamese",
    8: "Thai",
    9: "Filipino",
    10: "Khmer"
}

# Language selection (default to English if not found)
language_code = 5
language = language_map.get(language_code, "English")

# OpenAI tools configuration
tools = [{
    "type": "function",
    "name": "generate_email_body",
    "description": "Return email body with basic HTML structure",
    "parameters": {
        "type": "object",
        "required": ["body"],
        "properties": {
            "body": {
                "type": "string",
                "description": "Body content of the email in HTML format"
            }
        },
        "additionalProperties": False
    }
}]


class TimeoutExpired(Exception):
    pass


def log_message(message, obj=None):
    """Print log message if logging is enabled."""
    if enable_logging:
        print(message)
        if obj is not None:
            if hasattr(obj, 'model_dump_json'):
                print(json.loads(obj.model_dump_json()))
            else:
                print(obj)


def read_api_key_from_file(file_path, start_with):
    """Read API key from file that starts with specified prefix."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(start_with):
                    return line.strip().split(':', 1)[1].strip()
        raise ValueError(f"Key not found starting with '{start_with}' in file '{file_path}'")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(str(e))
        sys.exit(1)


def upload_file(client, file_path):
    """Upload a file to OpenAI."""
    with open(file_path, "rb") as file:
        uploaded_file = client.files.create(file=file, purpose='user_data')
        return uploaded_file


def remove_file(client, file_id):
    """Delete a file from OpenAI."""
    try:
        return client.files.delete(file_id)
    except Exception as e:
        print(f"Error removing file {file_id}: {e}")
        return None


def check_timeout(start_time, timeout):
    """Check if operation has timed out."""
    if time.time() - start_time > timeout:
        raise TimeoutExpired(f"Operation timed out after {timeout} seconds")


def render_html_with_tkinter(html_string):
    """Render HTML content in a tkinter window."""
    root = tk.Tk()
    root.title("Marketing Summary")
    root.geometry("1024x768")
    
    html_label = HTMLLabel(root, html=html_string)
    html_label.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()


def extract_html_from_response(response):
    """Extract HTML content from OpenAI API response."""
    if not response.output or len(response.output) == 0:
        print("No output received or output is empty from model.")
        return None
        
    function_call = response.output[0]
    if function_call.type != "function_call" or function_call.name != "generate_email_body":
        print("No function_call found or wrong function name in the output")
        return None
        
    arguments = json.loads(function_call.arguments)
    html_output = arguments.get("body")
    
    if not html_output:
        print("No 'body' key found in function call arguments.")
        return None
        
    return html_output


def main():
    file_path = r"d:\\temp\\pdf6.pdf"
    api_key = read_api_key_from_file(r"d:\codes\keys\keys.txt", 'OPENAPI-ALL-Access:')
    client = OpenAI(api_key=api_key)
    file_id = None
    
    try:
        # Step 1: Upload the file
        uploaded_file = upload_file(client, file_path)
        file_id = uploaded_file.id
        log_message(f"File Upload Success - ID: {file_id}", uploaded_file)
        
        # Step 2: Process with OpenAI
        start_time = time.time()
        
        try:
            response = client.responses.create(
                model="gpt-4o",
                input=[
                    {
                        "role": "system",
                        "content": """
                                You are a Marketing Expert, you will digest the file given and help generate content according to request.  
                                You will not include any placeholder.
                                You will Return in basic HTML structure
                                """
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": file_id,
                            },
                            {
                                "type": "input_text",
                                "text": f"Please analyze this PDF content, it's marketing material. Generate a concise summary in html format using the generate_email_body function. Language: {language}, length of message around {content_length} characters.",
                            },
                        ]
                    }
                ], 
                tools=tools
            )
            
            # Check for timeout after API call
            check_timeout(start_time, timeout_seconds)
            log_message("Raw Response:", response)
            
            # Extract and render HTML
            html_output = extract_html_from_response(response)
            if html_output:
                render_html_with_tkinter(html_output)
                return 0  # Success
            else:
                return 1  # Failed to extract HTML
                
        except TimeoutExpired as e:
            print(str(e))
            return 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    finally:
        # Clean up - always try to remove the file
        if file_id:
            remove_result = remove_file(client, file_id)
            log_message("File Delete Success" if remove_result else "File removal failed or already removed")
            

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
