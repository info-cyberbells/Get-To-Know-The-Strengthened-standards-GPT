### Architectural Design of the Chatbot

#### Preloaded Content

- **Existing Setup:** 
    - Preloaded markdown files (e.g., Strengthened Aged Care Quality Standards) are ingested into the OpenAI Assistant's knowledge base.
    - The Assistant's knowledge can be updated quickly if policy or guidance changes.
- **Purpose:** 
    - Provides authoritative responses based on predefined policies and guidance.

#### API Endpoints

The backend provides the following endpoints:

- `GET /test` - Test endpoint to verify server is running.
- `GET /api/v1/assistant/threads` - Create a new conversation thread.
- `POST /api/v1/assistant/chat` - Send a message to the assistant.
- `POST /api/v1/assistant/chat-file` - Send a message with a file attachment.

#### User-Uploaded Documents

- **Processing:** 
    - Users can upload PDFs/DOCX files.
    - Files are processed through text extraction and intelligent chunking.
- **Embedding Generation:**
    - Document chunks are converted to vector embeddings.
    - Embeddings capture semantic meaning for accurate retrieval.
- **Storage:** 
    - For MVP, uses an in-memory vector store for efficient similarity search.
    - Can be extended to persistent storage solutions as needed.

#### Chatbot Interaction

### Workflows

**Workflow 1: Basic Standards Query**

When a user asks about the Strengthened Standards without uploading documents:

1. User sends a query via the `/chat` endpoint.
2. The system:
   - Forwards the query to the OpenAI Assistant
   - Assistant provides authoritative response based on preloaded Standards
3. User receives comprehensive guidance about the Standards.

**Workflow 2: Context-Aware Standards Application**

This workflow handles queries about how the Standards apply to an organization's specific context:

1. **Document Processing Stage**
   - User uploads document(s) via `/chat-file` endpoint
   - System:
     * Extracts text from PDFs/DOCX
     * Performs intelligent chunking
     * Generates embeddings
     * Stores in vector database

2. **Query Enhancement Stage**
   - When user asks a question, system:
     * Searches vector database for relevant document chunks
     * Scores and ranks chunks by relevance
     * Retrieves top matches above similarity threshold

3. **Context Integration Stage**
   - System creates enhanced query combining:
     * User's original question
     * Relevant context from their documents
   - Enhanced query is structured to guide the Assistant to:
     * Explain Standards application to specific situation
     * Reference relevant organizational documents
     * Identify alignments and gaps
     * Provide implementation guidance

4. **Response Generation Stage**
   - Assistant processes enhanced query
   - Generates unified response that naturally integrates:
     * Authoritative Standards knowledge
     * Organization-specific context
     * Practical implementation guidance
   - Response maintains natural flow while weaving together both sources

This architecture ensures:
- Single source of truth for Standards (OpenAI Assistant)
- Efficient document processing and retrieval
- Natural integration of general and specific knowledge
- Contextually relevant and actionable responses

### Technical Components

1. **Document Processor**
   - Handles file upload and text extraction
   - Implements intelligent chunking strategies
   - Generates embeddings using OpenAI's API

2. **Vector Store**
   - Manages document embeddings
   - Provides efficient similarity search
   - Supports relevance scoring

3. **Query Handler**
   - Orchestrates the workflow
   - Manages context integration
   - Handles Assistant interaction

4. **Response Formatter**
   - Structures final response
   - Ensures consistent output format
   - Handles error cases

### Diagram Preview

To preview the diagram, you can:

- Install the "Markdown Preview Mermaid Support" extension in VS Code.
- Use the "Mermaid Preview" extension.
- Copy the code into an online Mermaid editor like [Mermaid Live Editor](https://mermaid.live).
