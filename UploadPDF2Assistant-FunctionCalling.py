## Change it to use opeanai responses api. Please upgrade your openai library to minimal 1.66.3

import time, sys
from openai import OpenAI
import json
from IPython.display import display, HTML
from bs4 import BeautifulSoup
from tkhtmlview import HTMLLabel
import tkinter as tk

# Set Constants and control some for future use
timeout_seconds = 90  # stop force exit
wait_time = 3
pause_time = 1
content_length = 15000
enable_logging = False

language = 1
match language:
    case 1:
        language = "Malay"
    case 2:
        language = "Chinese"
    case 3:
        language = "Japanese"
    case 4:
        language = "Korean"
    case 5:
        language = "Indonesian"
    case 6:
        language = "Vietnamese"
    case 7:
        language = "Thai"
    case 8:
        language = "Filipino"
    case 9:
        language = "Khmer"
    case _:
        language = "English"


def show_json(obj):
    display(json.loads(obj.model_dump_json()))


def read_api_key_from_file(file_path, start_with):
    # This function read the file, and extract the key that starts with the start_with string
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(start_with):
                    api_key = line.strip().split(':')[1].strip()
                    return api_key
        raise ValueError(f"Key not found starting with '{start_with}' in file '{file_path}'")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(str(e))
        sys.exit(1)


def uploadfile(client, file):
    uploaded_file = client.files.create(file=file, purpose='user_data')
    return uploaded_file


def removefile(client, file_id):
    removefile = client.files.delete(file_id)
    return removefile


def render_html_with_tkinter(html_string):
    """
    Render HTML content in a tkinter window using tkhtmlview.
    """
    root = tk.Tk()
    root.title("Marketing Summary")
    root.geometry("1024x768")  # Set window size

    html_label = HTMLLabel(root, html=html_string)
    html_label.pack(fill=tk.BOTH, expand=True)  # Fill the window

    root.mainloop()

tools = [{
    "type": "function",
    "name": "generate_email_body",
    "description": "Return email body with basic HTML structure",
    "parameters":{
    "type": "object",
    "required": [
      "body"
    ],
    "properties": {
      "body": {
        "type": "string",
        "description": "Body content of the email in HTML format"
      }
    },
    "additionalProperties": False
  }
}]


file_path = r"d:\\temp\\pdf4.pdf"
api_key = read_api_key_from_file(r"d:\codes\keys\keys.txt", 'OPENAPI-ALL-Access:')  #The file should contain the key in the format OPENAPI-ALL-Access:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

client = OpenAI(api_key=api_key)
try:
    # Step 1: Upload the file
    with open(file_path, "rb") as file:
        uploaded_file = uploadfile(client, file)
        if enable_logging:
            print(f"File Upload Success")
            print(uploaded_file)

        file_id = uploaded_file.id
        if enable_logging:
            print(f"File ID: {file_id}")

        if file_id is not None:

            response = client.responses.create(
                model="gpt-4o",
                input=[
                    {
                        "role": "system",
                        "content": """
                                You are an Marketing Expert, you will digest the file given and help generate content according to request.  
                                You  will not include any placeholder.
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
                                "text": f"Please analyze this PDF content, it's marketing material.  Generate a concise summary in html format using the generate_email_body function. Language: {language}, length of message around {content_length} characters.",
                            },
                        ]
                    }
                ], tools=tools
                
            )
            if enable_logging:
                print("Raw Response:")
                show_json(response)  
                # print("\nOutput:") #When function_call is needed, we need to use response.output, not response.output_text
                # print(response.output)
                # print("\n")
                # print("\nOutput DIR:")
                # print(dir(response.output))
                # print("\n")
                # print("\nOutput Type:")
                # print(type(response.output))
                # print("\n")

            # Extract HTML from the function call arguments
            if response.output and len(response.output) > 0:
                function_call = response.output[0]
                if function_call.type == "function_call" and function_call.name == "generate_email_body":
                    arguments = json.loads(function_call.arguments)
                    html_output = arguments.get("body")

                    if html_output:
                        render_html_with_tkinter(html_output)
                    else:
                         print("No 'body' key found in function call arguments.")
                else:
                      print("No function_call found or wrong function name in the output")

            else:
                print("No output received or output is empty from model.")

            removefile(client, file_id)
            if enable_logging:
                print(f"File Delete Success")
        else:
            if enable_logging:
                print(f"File Not found, Delete Failed")
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)

