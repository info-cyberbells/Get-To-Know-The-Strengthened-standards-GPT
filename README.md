# Get To Know The Strengthened Standards GPT

## Quick Start Guide

### Prerequisites
- Python 3.x installed
- Node.js and npm (optional, for development)
- OpenAI API key
- Modern web browser (Chrome, Firefox, Edge recommended)

### Environment Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd get-to-know-the-strengthened-standards
```

2. Create and activate a Python virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your OpenAI credentials:
```env
OPENAI_API_KEY=your_api_key_here
ASSISTANT_ID=your_assistant_id_here
```

### Running the Application

The project now includes a development server that handles both frontend and backend with hot reloading:

```bash
python run_dev.py
```

This will:
- Start the FastAPI backend on `http://localhost:8000` with auto-reload
- Start the frontend server on `http://localhost:3000` with live reload
- Automatically refresh the browser when you make changes to frontend files
- Restart the backend when you make changes to Python files

Access the application:
1. Open `http://localhost:3000/guidance.html` in your browser
2. Login with the password specified in your `.env` file:
```env
LOGIN_PASSWORD=your_password_here
```
3. Navigate between:
   - Guidance page (documentation and overview)
   - Chatbot (AI assistant interface)
   - Prompt Gallery (example queries and templates)

### Alternative Manual Setup

If you prefer to run the servers separately:

#### Backend Only
```bash
# Windows
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# macOS/Linux
python3 -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Only
```bash
# From the frontend directory
python -m http.server 3000
```

### API Endpoints

The backend provides the following endpoints:

- `GET /test` - Test endpoint to verify server is running
- `GET /api/v1/assistant/threads` - Create a new conversation thread
- `POST /api/v1/assistant/chat` - Send a message to the assistant
- `POST /api/v1/assistant/chat-file` - Send a message with a file attachment

### Troubleshooting

1. Backend Issues:
   - Ensure Python 3.x is installed: `python --version`
   - Verify all dependencies are installed: `pip freeze`
   - Check `.env` file exists with correct credentials
   - Confirm port 8000 is not in use
   - Make sure to run the backend server from the project root directory, not from inside the backend directory

2. Frontend Issues:
   - Clear browser cache if changes aren't reflecting
   - Check browser console for JavaScript errors
   - Verify backend URL in frontend code matches your setup
   - If live reload isn't working, try restarting the development server

3. Common Fixes:
   - Restart the development server (`run_dev.py`)
   - Clear browser cache and cookies
   - Check network connectivity
   - Verify OpenAI API key is valid

### Development Notes

- Backend runs on FastAPI with OpenAI integration
- Frontend uses vanilla JavaScript with minimal dependencies
- File upload supports .doc and .docx formats
- Dark/Light mode preference is saved in localStorage
- Authentication state persists across page navigation
- Hot reloading enabled for both frontend and backend during development

For more detailed information about features, project structure, and technical specifications, see below.

#### Chatbot Interaction

### Workflows

**Workflow 1: User queries the chatbot and information from the preloaded markdown files is retrieved from the API Assistant.**

On application startup, preloaded markdown files are already loaded, processed, and indexed into the preloaded vector database.

1. User sends a query via the `/chat` endpoint.
2. The system:
     - **Queries Preloaded Assistant:** Retrieves authoritative information based on preloaded policies.
     - **Response Delivery:** The user receives a response with relevant details from the preloaded Standards.

**Workflow 2: User uploads a document and queries about its relationship to the Standards.**

On application startup, preloaded markdown files are already loaded into the OpenAI Assistant's knowledge base. When a user wants to understand how their organizational documents align with the Standards:

1. User uploads a PDF/DOCX file via the `/chat-file` endpoint.
2. The system:
   - Processes the file (text extraction, chunking)
   - Generates embeddings for the chunks
   - Stores them in the vector database

3. When the user asks a question, the system:
   - Searches the vector database for relevant chunks from their documents
   - Creates an enhanced query that includes:
     * The user's original question
     * Relevant context from their documents
   - Sends this to the Assistant, which provides a unified response that:
     * Explains how the Standards apply to their specific situation
     * References relevant parts of their documents
     * Identifies alignments and potential gaps
     * Provides practical implementation suggestions

4. The user receives a natural, integrated response that weaves together:
   - Authoritative knowledge about the Standards
   - Specific context from their organizational documents
   - Practical insights for implementation

This approach ensures responses are both authoritative (based on the Standards) and contextually relevant (incorporating the organization's specific practices and policies).

### Diagram Preview

To preview the diagram, you can:

- Install the "Markdown Preview Mermaid Support" extension in VS Code.
- Use the "Mermaid Preview" extension.
- Copy the code into an online Mermaid editor like [Mermaid Live Editor](https://mermaid.live).
