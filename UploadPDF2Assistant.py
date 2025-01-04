import sys
import time
from openai import OpenAI

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

language = 6  
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
assistant_id = "asst_LH9K4B2vvKnb6ygIOyejG0Kv"
file_path = r"d:\\temp\\pdf1.pdf"  #the PDF File you want to upload and analyze

# Upload the file and link it to the vector store
try:
    # Step 1: Upload the file
    with open(file_path, "rb") as file:
        uploaded_file = client.files.create(file=file, purpose="assistants")
    
    print(f"File uploaded successfully! File ID: {uploaded_file.id}")
#----------using batch, can use for multiple files----------------
    # # Step 2: Create a file batch to add the file to the vector store
    # file_batch = client.beta.vector_stores.file_batches.create(
    #     vector_store_id=vector_store_id,
    #     file_ids=[uploaded_file.id]
    # )
    
    # print("File added to vector store successfully!")
    
    # # Polling until the batch status is no longer 'in_progress'
    # while True:
    #     # Fetch the current status of the file batch including the vector store ID
    #     updated_batch = client.beta.vector_stores.file_batches.retrieve(
    #         file_batch.id, vector_store_id=vector_store_id
    #     )
    #     print(f"Current File Batch Status: {updated_batch.status}")

    #     # Check if the status indicates completion
    #     if updated_batch.status != "in_progress":
    #         print("Batch processing completed.")
    #         print(f"File Counts: {updated_batch.file_counts}")
    #         break
        
    #     # Sleep for some time before polling again
    #     time.sleep(5)  # Adjust the sleep time as necessary
#-----------------

# Step 2: Add one file to the vector store
    vector_store_file = client.beta.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=uploaded_file.id
    )

    print("File being added to vector store...")

    # Polling until the file status is 'completed'
    while True:
        # Fetch the current status of the file
        updated_file = client.beta.vector_stores.files.retrieve(
            file_id=vector_store_file.id,
            vector_store_id=vector_store_id
        )
        print(f"Current File Status: {updated_file.status}")

        # Check if the status indicates completion or error
        if updated_file.status == "completed":
            print("File processing completed successfully!")
            break
        elif updated_file.status == "failed":
            print(f"Error occurred: {updated_file.last_error}")
            break
        
        # Sleep for some time before polling again
        time.sleep(5)  # Adjust the sleep time as necessary

    # Create a thread
    thread = client.beta.threads.create()
    
    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please analyze this PDF content and create a campaign emai body only with basic html, use only HTML tags support by email client, and be creative. I do not need any email body placeholder [] Just give me the Email body content. I need it in {language} language"
    )
    
    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_xSCfbkRlh5dqoclJznQjXiQR"
    )
    
    # Wait for completion
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            # Get messages
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            print("Assistant Response:\n")
            print(messages.data[0].content[0].text.value)
            deleted_vector_store_file= client.beta.vector_stores.files.delete(
            file_id=vector_store_file.id,
            vector_store_id=vector_store_id
            )
            if deleted_vector_store_file.deleted : 
                client.files.delete(uploaded_file.id)
                print(f"File Delete Success")
            else:
                print(f"File Delete Failed")
            break
        time.sleep(5)

except Exception as e:
    print(f"An error occurred: {e}")
