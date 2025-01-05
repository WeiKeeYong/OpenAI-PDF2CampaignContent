import sys
import time
from openai import OpenAI
import json
from IPython.display import display

#Set Constants and control
timeout_seconds = 60  # stop force exit
wait_time = 3
pause_time = 1
content_length = 1000
enable_logging = False


def show_json(obj):
    display(json.loads(obj.model_dump_json()))

def read_api_key_from_file(file_path, start_with):
    #This function read the file, and extract the key that starts with the start_with string
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

def cleanup_files(client, vector_store_file, uploaded_file):
    deleted_vector_store_file= client.beta.vector_stores.files.delete(
    file_id=vector_store_file.id,
    vector_store_id=vector_store_id
    )
    if deleted_vector_store_file.deleted : 
        client.files.delete(uploaded_file.id)
        if enable_logging: print(f"File Delete Success")
    else:
        if enable_logging: print(f"File Delete Failed")
    thread_deleted = client.beta.threads.delete(thread.id)
    if enable_logging: print(f"Thread Deleted: {thread_deleted}")

language = 99  
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
        language= "English"


# Read the OpenAI API key from a file
api_key = read_api_key_from_file('keys.txt', 'OPENAPI-ALL-Access:') #The file should contain the key in the format OPENAPI-ALL-Access:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"}, api_key=api_key)

# Define the vector store ID and file path
vector_store_id = "vs_uUtjmSe2KEMFxiMB6duWnCgj"
assistant_id = "asst_O4GIPNMRn9uy31UFRcIp7WDv"
file_path = r"d:\\temp\\pdf1.pdf"  #the PDF File you want to upload and analyze

# Upload the file and link it to the vector store
try:
    # Step 1: Upload the file
    with open(file_path, "rb") as file:
        uploaded_file = client.files.create(file=file, purpose="assistants")
    
    if enable_logging: print(f"File uploaded successfully! File ID: {uploaded_file.id}")
# Step 2: Add one file to the vector store
    vector_store_file = client.beta.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=uploaded_file.id
    )

    if enable_logging: print("File being added to vector store...")
    # Set timeout duration and start time
    start_time = time.time()

    # Polling until the file status is 'completed'
    while True:
        # Check if the operation has timed out
        if time.time() - start_time > timeout_seconds:
            print(f"Operation timed out after {timeout_seconds} seconds")
            sys.exit(1)  # Exit entire program with error code 1

        # Fetch the current status of the file
        try:
            updated_file = client.beta.vector_stores.files.retrieve(
                file_id=vector_store_file.id,
                vector_store_id=vector_store_id
            )
            if enable_logging: print(f"Current File Status: {updated_file.status}")

            # Check if the status indicates completion or error
            if updated_file.status == "completed":
                if enable_logging: print("File processing completed successfully!")
                time.sleep(pause_time) #wait 1 second before breaking the loop
                break
            elif updated_file.status == "failed":
                print(f"Error occurred: {updated_file.last_error}")
                sys.exit(2)  # Exit code 2 for API failure
            
            # Sleep for some time before polling again
            time.sleep(wait_time)  # Adjust the sleep time as necessary

        except Exception as e:
            print(f"API call failed: {str(e)}")
            break

    # Create a thread
    thread = client.beta.threads.create()
    
    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please analyze this PDF content and generate an email body using the generate_email_body function. Language: {language}, length of message around {content_length} characters.",
    )
    
    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_O4GIPNMRn9uy31UFRcIp7WDv"
    )
    if enable_logging: show_json(run)
    # Set timeout duration and start time
    start_time = time.time()

    # Wait for completion
    while True:
        if time.time() - start_time > timeout_seconds:
            print(f"Operation timed out after {timeout_seconds} seconds")
            sys.exit(1)  # Exit entire program with error code 1

        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if enable_logging: 
            print("---Run Status---")
            print( run_status.status )
            print("----------------")

        if run_status.status == 'requires_action':
            # Handle function calls
            if enable_logging: 
                print("Function Calls Data:")
                print(run_status.required_action.submit_tool_outputs.tool_calls)

            html_body = ""
            for tool in run_status.required_action.submit_tool_outputs.tool_calls:
                if tool.function.name == "generate_email_body": html_body = json.loads(tool.function.arguments)["body"]
            print(f"\nFunction Argument:\n{html_body}")
            cleanup_files(client, vector_store_file, uploaded_file)
            break
        elif run_status.status == 'completed':
            # Get messages id openai didn't return the function calling
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            if enable_logging: 
                print("------------------Raw AI Message---------------")
                show_json(messages)
                print("-----------------------------------------------\n")
            print("Assistant Response:\n")
            print(messages.data[0].content[0].text.value)
            cleanup_files(client, vector_store_file, uploaded_file)
            break
        elif run_status.status == 'failed':
            print(f"Run failed with error: {run_status.last_error}")
            break
        time.sleep(wait_time)

except Exception as e:
    print(f"An error occurred: {e}")