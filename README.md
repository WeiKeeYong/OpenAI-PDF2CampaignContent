# PDF to Campaign Content using OpenAI

This repository demonstrates a proof-of-concept (POC) workflow for creating campaign content from a PDF using OpenAI's API. The process involves uploading a PDF, linking it to a vector store, and requesting OpenAI to generate creative email content in HTML format.

## Workflow Overview

1. **Upload a PDF file**: Select a PDF file from your local machine.
2. **Send it to an OpenAI Assistant**: The pre-created assistant processes the file.
3. **Generate Content**: OpenAI returns an email body content in basic HTML, creatively designed for campaign purposes.
4. **Clean upt**: Delete the uploaded file.

## Prerequisites

- **OpenAI Assistant**: Create an OpenAI assistant and obtain the Assistant ID.
- **Vector Store**: Set up a vector store, attach it to the assistant for file search, and retrieve the Vector Store ID.

## Code Example

The Code  is written in Python and utilizes the OpenAI Python client. Key functionalities include:

- Reading API keys from a file.
- Uploading a PDF file and linking it to a vector store.
- Polling for processing status.
- Interacting with the OpenAI assistant to generate email body content in the specified language.
- Another file is using Open AI Assistant & Function Calling
