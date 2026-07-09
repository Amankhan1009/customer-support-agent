# Customer Support Agent with LangGraph

A modular, stateful, containerized, and publicly deployed Agentic AI customer support system built with LangGraph.

The application demonstrates hybrid intent routing, specialized LangGraph subgraphs, persistent conversation state, context-aware LLM fallback routing, conditional workflows, error handling, human escalation, real human-in-the-loop execution, REST API integration, an interactive Streamlit interface, automated testing, configurable checkpoint backends, production PostgreSQL persistence, multi-platform Docker deployment, and public cloud deployment.

## Live Deployment

### Streamlit Application

https://customer-support-agent-frontend.onrender.com

### FastAPI Backend

https://customer-support-agent-4960.onrender.com

### Swagger API Documentation

https://customer-support-agent-4960.onrender.com/docs

> The application is deployed using Render free-tier services. Free services may spin down after inactivity, so the first request can take additional time while the service starts.

## Repository and Docker Images

### GitHub Repository

https://github.com/Amankhan1009/customer-support-agent

### Docker Hub Images

API:

https://hub.docker.com/r/amankhan1009/customer-support-agent-api

Frontend:

https://hub.docker.com/r/amankhan1009/customer-support-agent-frontend

Both Docker images are published as multi-platform images supporting:

```text
linux/amd64
linux/arm64
```

Docker automatically selects the correct image variant for the host architecture.

## Features

- Natural-language customer support queries
- Hybrid deterministic and LLM-based intent routing
- Deterministic classification for clear customer requests
- Context-aware LLM fallback routing for ambiguous requests
- Structured LLM output for reliable intent classification
- Conditional routing using LangGraph
- Specialized Billing, Technical, Account, and General support subgraphs
- Shared LangGraph state across workflows
- Configurable SQLite and PostgreSQL checkpoint backends
- SQLite checkpoint persistence for local development
- PostgreSQL checkpoint persistence for production deployment
- Persistent conversation and workflow state
- Human escalation for unresolved and sensitive requests
- Real human-in-the-loop execution using `interrupt()`
- Resume paused workflows using `Command(resume=...)`
- Persistent interrupted workflows across application and container restarts
- Conversation state recovery after API redeployment or restart
- FastAPI REST API
- Interactive Streamlit chat interface
- Human-review interface for interrupted workflows
- Conversation thread isolation using `thread_id`
- Unit, workflow, and API integration tests
- Environment-based configuration
- Application logging
- Dockerized API and frontend services
- Docker Compose orchestration
- Multi-platform Docker images for AMD64 and ARM64 systems
- Public cloud deployment using Render
- Managed PostgreSQL persistence using Neon

## High-Level Architecture

```text
                              Customer
                                 |
                                 v
                     Streamlit Frontend Service
                         Render Web Service
                                 |
                                 | HTTPS
                                 v
                       FastAPI Backend Service
                         Render Web Service
                                 |
                                 v
                       LangGraph Parent Graph
                                 |
                                 v
                           Receive Query
                                 |
                                 v
                   Deterministic Intent Classifier
                                 |
                      +----------+----------+
                      |                     |
                 Clear Intent         Ambiguous Intent
                      |                     |
                      |                     v
                      |          Context-Aware LLM Classifier
                      |                     |
                      +----------+----------+
                                 |
                                 v
                        Conditional Routing
                                 |
              +------------------+------------------+
              |                  |                  |
              v                  v                  v
       Billing Subgraph   Technical Subgraph   Account Subgraph
              |
              +--------------------------+
                                         |
                                         v
                                  General Subgraph
                                         |
                                         v
                              Resolution / Escalation
                                         |
                               +---------+---------+
                               |                   |
                            Resolved           Escalation
                               |                   |
                               v                   v
                       Final Response      Human Support Node
                                                   |
                                                   v
                                              interrupt()
                                                   |
                                                   v
                                      PostgreSQL Checkpoint Saved
                                                   |
                                                   v
                                         Human Support Review
                                                   |
                                                   v
                                      Command(resume=response)
                                                   |
                                                   v
                                           Graph Resumes
                                                   |
                                                   v
                                            Final Response

                                 |
                                 v
                         Neon PostgreSQL
                    Persistent LangGraph Checkpoints
```

## Application Architecture

The application is separated into independent frontend, API, orchestration, workflow, persistence, and infrastructure layers.

```text
Browser
   |
   v
Streamlit Frontend
   |
   | HTTPS / REST
   v
FastAPI Backend
   |
   v
LangGraph Application
   |
   +----------------------------+
   |                            |
   v                            v
Specialized Subgraphs     Human-in-the-Loop
   |                            |
   v                            v
Support Resolution       interrupt() / resume
                                |
                                v
                       Configurable Checkpointer
                                |
                     +----------+----------+
                     |                     |
                     v                     v
                  SQLite              PostgreSQL
             Local Development     Production Deployment
                                          |
                                          v
                                  Neon PostgreSQL
```

The Streamlit frontend acts as a thin API client and never directly invokes the LangGraph application.

This separation allows the backend agent system to be consumed by other clients without changing the graph implementation.

## Production Deployment Architecture

The publicly deployed application uses separate frontend and backend services.

```text
                           Internet
                              |
                              v
                   Streamlit Frontend
                        Render
                              |
                              | HTTPS
                              v
                     FastAPI REST API
                        Render
                              |
                              v
                     LangGraph Workflows
                              |
                              v
                 PostgreSQL LangGraph Saver
                              |
                              | TLS Connection
                              v
                      Neon PostgreSQL
                              |
                              v
               Persistent Workflow Checkpoints
```

### Production Components

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | Streamlit on Render | Customer chat interface and human-review UI |
| Backend | FastAPI on Render | REST API and LangGraph execution |
| Agent Orchestration | LangGraph | Stateful workflow execution and routing |
| LLM | Groq API | Ambiguous intent classification |
| Production Persistence | Neon PostgreSQL | Durable LangGraph checkpoints |
| Local Persistence | SQLite | Lightweight local checkpoint backend |
| Containers | Docker | Reproducible application packaging |
| Container Registry | Docker Hub | Published multi-platform images |
| Testing | Pytest | Classifier, workflow, HITL, and API verification |

## Routing Strategy

The system uses hybrid routing to avoid unnecessary LLM calls while still supporting ambiguous natural-language requests.

### Deterministic Routing

Clear customer requests are classified using deterministic keyword-based logic.

Examples:

```text
"I was charged twice."
→ billing

"The application keeps crashing."
→ technical

"I cannot log into my account."
→ account

"Tell me about your pricing."
→ general
```

Deterministic routing provides:

- Low latency
- Predictable behavior
- Reduced LLM API usage
- Lower inference cost
- Easy automated testing

### Context-Aware LLM Fallback Routing

When deterministic classification cannot confidently identify an intent, the request is routed to an LLM classifier.

The classifier uses structured output and returns exactly one supported intent:

- `billing`
- `technical`
- `account`
- `general`
- `unknown`

```text
Customer Message
      |
      v
Deterministic Classifier
      |
      v
Classification Unresolved
      |
      v
Context-Aware LLM Classifier
      |
      v
Structured Intent
      |
      v
Specialized Subgraph
```

Persisted conversation context can be provided to the LLM classifier for ambiguous follow-up requests.

Example:

```text
Customer: I was charged twice for my subscription.
Agent: Duplicate charge issue identified.

Customer: It happened again.
```

The previous conversation context can help the LLM understand that the follow-up message is related to billing.

## Specialized LangGraph Workflows

Each major support domain is implemented as an independent LangGraph subgraph.

### Billing Workflow

Handles:

- Duplicate charges
- Refund requests
- Payment failures
- Other billing-related requests

The workflow classifies the billing issue and conditionally routes execution to the appropriate billing handler.

### Technical Workflow

Handles:

- Application errors
- Performance issues
- Feature issues
- Unsupported technical problems

The workflow performs issue classification, technical diagnosis, and resolution-status routing.

Unresolved technical issues are escalated to the parent graph's human-support workflow.

### Account Workflow

Handles:

- Login problems
- Password resets
- Unauthorized account access
- Account deletion
- Other account-management requests

Sensitive account requests are escalated for human review.

### General Workflow

Handles:

- Pricing questions
- Product questions
- General service questions

## Human-in-the-Loop Execution

The application implements real LangGraph human-in-the-loop execution.

When a request requires human review:

```text
Customer Request
       |
       v
Specialized Workflow
       |
       v
Escalation Required
       |
       v
Human Support Workflow
       |
       v
interrupt()
       |
       v
Graph Execution Pauses
       |
       v
Checkpoint Persisted
       |
       v
API Returns human_review_required
       |
       v
Streamlit Displays Escalation Details
       |
       v
Human Reviews Request
       |
       v
POST /support/resume
       |
       v
Command(resume=human_response)
       |
       v
Saved Checkpoint Loaded
       |
       v
Graph Execution Continues
       |
       v
Final Response
```

The workflow does not restart from the beginning after human review.

LangGraph resumes execution from the persisted checkpoint.

With the PostgreSQL backend, interrupted and completed workflows survive API container restarts and service redeployments.

## Persistence Architecture

The application supports configurable checkpoint backends.

The active backend is selected using:

```text
CHECKPOINTER_BACKEND
```

Supported values:

```text
sqlite
postgres
```

### SQLite Backend

SQLite is used for lightweight local development.

```text
LangGraph
    |
    v
SqliteSaver
    |
    v
support_checkpoints.db
```

Benefits:

- No external database required
- Easy local development
- Simple debugging
- Persistent state across local application restarts

### PostgreSQL Backend

PostgreSQL is used for production deployment.

```text
LangGraph
    |
    v
PostgresSaver
    |
    v
Neon PostgreSQL
```

Benefits:

- Durable external persistence
- Workflow state survives container restarts
- Suitable for ephemeral cloud containers
- Centralized checkpoint storage
- Better foundation for production deployment

### Checkpointer Factory

Checkpointer creation is centralized in:

```text
config/checkpointer.py
```

The application selects the backend from environment configuration rather than hard-coding persistence logic inside the API layer.

Conceptually:

```text
Application Startup
       |
       v
Read CHECKPOINTER_BACKEND
       |
       +----------------+
       |                |
       v                v
    sqlite           postgres
       |                |
       v                v
SqliteSaver      PostgresSaver
       |                |
       +--------+-------+
                |
                v
         Compile LangGraph
```

This keeps the graph implementation independent from the persistence infrastructure.

## Production Persistence Verification

Production checkpoint persistence was verified against the deployed Render API and Neon PostgreSQL database.

The verification flow:

```text
Submit Technical Request
          |
          v
Technical Workflow Cannot Resolve Issue
          |
          v
LangGraph interrupt()
          |
          v
API Returns human_review_required
          |
          v
Checkpoint Persisted in Neon PostgreSQL
          |
          v
Retrieve Thread Status
          |
          v
Human Review Submitted
          |
          v
Command(resume=...)
          |
          v
Workflow Completes
          |
          v
Restart API Service
          |
          v
Retrieve Same thread_id
          |
          v
Completed State Successfully Recovered
```

Verified production response after API service restart:

```json
{
  "thread_id": "customer-32211228",
  "status": "completed",
  "response": "A human support engineer reviewed the issue and will investigate it further.",
  "interrupt_data": null
}
```

This confirms that workflow state is persisted externally and is not tied to the lifecycle of the Render container.

## Conversation Threads

Each conversation is identified using a unique `thread_id`.

Example:

```text
customer-a1b2c3d4
        |
        v
Conversation State + Graph Checkpoints

customer-x9y8z7w6
        |
        v
Independent Conversation State + Graph Checkpoints
```

The shared LangGraph state stores conversation messages using the `add_messages` reducer.

Conversation context can be provided to the LLM fallback classifier when deterministic routing cannot confidently determine the latest customer intent.

Starting a new conversation from the Streamlit UI:

- Creates a new thread ID
- Clears visible messages from the current Streamlit session
- Does not delete previously persisted checkpoints

## Streamlit User Interface

The project includes an interactive Streamlit frontend.

```text
Streamlit UI
      |
      | HTTP / HTTPS
      v
FastAPI
      |
      v
LangGraph
```

The frontend intentionally acts as a thin API client.

It does not directly import or invoke the LangGraph application.

### UI Features

- Chat-based customer support interface
- Automatically generated conversation thread IDs
- Visible customer and support messages
- Start New Conversation button
- Human-review-required status
- Escalation details
- Human support response input
- Resume interrupted workflows
- Configurable backend API URL
- Public cloud deployment

## REST API

The FastAPI backend exposes four primary endpoints.

### Health Check

```text
GET /health
```

### Submit Support Request

```text
POST /support
```

Example request:

```json
{
  "thread_id": "customer-1",
  "message": "I was charged twice."
}
```

Completed response:

```json
{
  "thread_id": "customer-1",
  "status": "completed",
  "response": "We identified your request as a duplicate charge issue. The duplicate transaction will need to be reviewed.",
  "interrupt_data": null
}
```

Human-review response:

```json
{
  "thread_id": "customer-2",
  "status": "human_review_required",
  "response": null,
  "interrupt_data": {
    "type": "human_support_review",
    "customer_message": "I have a strange technical problem.",
    "intent": "technical",
    "escalation_reason": "automatic_diagnosis_failed",
    "diagnostic_result": "The technical issue could not be diagnosed automatically."
  }
}
```

### Get Conversation Status

```text
GET /support/{thread_id}
```

### Resume Human Review

```text
POST /support/resume
```

Example request:

```json
{
  "thread_id": "customer-2",
  "human_response": "A support engineer reviewed your issue and will contact you shortly."
}
```

## Project Structure

```text
customer-support-agent/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── config/
│   ├── __init__.py
│   ├── checkpointer.py
│   ├── llm.py
│   ├── logging.py
│   └── settings.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── graph/
│   ├── __init__.py
│   ├── builder.py
│   └── state.py
├── nodes/
│   ├── __init__.py
│   ├── account_nodes.py
│   ├── billing_nodes.py
│   ├── error_nodes.py
│   ├── general_nodes.py
│   ├── human_support_nodes.py
│   ├── specialized_nodes.py
│   ├── support_nodes.py
│   └── technical_nodes.py
├── routers/
│   ├── __init__.py
│   ├── account_classifier.py
│   ├── account_router.py
│   ├── billing_classifier.py
│   ├── billing_router.py
│   ├── classification_router.py
│   ├── error_router.py
│   ├── escalation_router.py
│   ├── general_classifier.py
│   ├── general_router.py
│   ├── intent_classifier.py
│   ├── intent_router.py
│   ├── llm_classifier.py
│   ├── technical_classifier.py
│   └── technical_router.py
├── schemas/
│   ├── __init__.py
│   └── routing.py
├── workflows/
│   ├── __init__.py
│   ├── account/
│   │   ├── __init__.py
│   │   └── builder.py
│   ├── billing/
│   │   ├── __init__.py
│   │   └── builder.py
│   ├── general/
│   │   ├── __init__.py
│   │   └── builder.py
│   └── technical/
│       ├── __init__.py
│       └── builder.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_classifiers.py
│   └── test_workflows.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── Dockerfile.frontend
├── docker-compose.yml
├── app.py
├── README.md
└── requirements.txt
```

## Environment Variables

Create `.env` from the provided template:

```bash
cp .env.example .env
```

### Local SQLite Configuration

```text
GROQ_API_KEY=your_real_groq_api_key

CHECKPOINTER_BACKEND=sqlite

DATABASE_PATH=support_checkpoints.db

DATABASE_URL=

LOG_LEVEL=INFO
```

### PostgreSQL Configuration

```text
GROQ_API_KEY=your_real_groq_api_key

CHECKPOINTER_BACKEND=postgres

DATABASE_PATH=support_checkpoints.db

DATABASE_URL=your_postgresql_connection_string

LOG_LEVEL=INFO
```

Never commit the real `.env` file or expose API keys and database credentials.

## Local Installation

Clone the repository:

```bash
git clone https://github.com/Amankhan1009/customer-support-agent.git
cd customer-support-agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

macOS/Linux:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create and configure `.env`:

```bash
cp .env.example .env
```

Add your Groq API key and select the desired checkpoint backend.

## Run the CLI Application

```bash
python app.py
```

## Run the FastAPI Backend

```bash
uvicorn api.main:app --reload
```

The backend is available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run the Streamlit Frontend

Start the FastAPI backend first.

Open another terminal:

```bash
streamlit run frontend/app.py
```

The frontend is available at:

```text
http://localhost:8501
```

## Run with Docker Compose

Create `.env`:

```bash
cp .env.example .env
```

Configure the required environment variables.

Start both services:

```bash
docker compose up --build
```

Services:

```text
Frontend: http://localhost:8501
API:      http://localhost:8000
Swagger:  http://localhost:8000/docs
```

Stop the application:

```bash
docker compose down
```

### Docker Compose with SQLite

Set:

```text
CHECKPOINTER_BACKEND=sqlite
DATABASE_PATH=/data/support_checkpoints.db
```

SQLite checkpoints are persisted using the `support_data` Docker volume.

To delete the persisted SQLite checkpoint volume:

```bash
docker compose down -v
```

### Docker Compose with PostgreSQL

Set:

```text
CHECKPOINTER_BACKEND=postgres
DATABASE_URL=your_postgresql_connection_string
```

The API container connects to the configured PostgreSQL database.

Checkpoint state is stored externally and survives container recreation.

## Run Using Published Docker Images

Pull the images:

```bash
docker pull amankhan1009/customer-support-agent-api:latest

docker pull amankhan1009/customer-support-agent-frontend:latest
```

The images support:

```text
linux/amd64
linux/arm64
```

Docker automatically selects the appropriate image for the host architecture.

Create a network:

```bash
docker network create customer-support-network
```

### Run the API with SQLite

Create a persistent volume:

```bash
docker volume create customer-support-data
```

Run the API:

```bash
docker run -d \
  --name customer-support-api \
  --network customer-support-network \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_real_groq_api_key \
  -e CHECKPOINTER_BACKEND=sqlite \
  -e DATABASE_PATH=/data/support_checkpoints.db \
  -v customer-support-data:/data \
  amankhan1009/customer-support-agent-api:latest
```

### Run the API with PostgreSQL

```bash
docker run -d \
  --name customer-support-api \
  --network customer-support-network \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_real_groq_api_key \
  -e CHECKPOINTER_BACKEND=postgres \
  -e DATABASE_URL=your_postgresql_connection_string \
  amankhan1009/customer-support-agent-api:latest
```

### Run the Frontend

```bash
docker run -d \
  --name customer-support-frontend \
  --network customer-support-network \
  -p 8501:8501 \
  -e API_URL=http://customer-support-api:8000 \
  amankhan1009/customer-support-agent-frontend:latest
```

Open:

```text
http://localhost:8501
```

Stop and remove containers:

```bash
docker stop customer-support-frontend customer-support-api

docker rm customer-support-frontend customer-support-api
```

## Public Cloud Deployment

The application is publicly deployed using Render.

### Backend Service

The FastAPI backend runs as a Docker-based Render Web Service.

Production configuration:

```text
CHECKPOINTER_BACKEND=postgres
DATABASE_URL=<Neon PostgreSQL connection string>
GROQ_API_KEY=<Groq API key>
LOG_LEVEL=INFO
```

Health check:

```text
/health
```

The backend binds to the port provided by the Render `PORT` environment variable.

### Frontend Service

The Streamlit frontend runs as a separate Docker-based Render Web Service.

Configuration:

```text
API_URL=https://customer-support-agent-4960.onrender.com
```

The frontend communicates with the deployed backend over HTTPS.

### Production Database

Neon PostgreSQL is used as the external production checkpoint store.

This is necessary because Render free-tier containers use ephemeral local filesystems and do not provide persistent disks.

Using external PostgreSQL persistence ensures LangGraph checkpoints survive API container restarts and redeployments.

## Run Tests

```bash
pytest -v
```

The project currently includes 20 automated tests covering:

- Deterministic classifiers
- Billing workflow execution
- Technical workflow execution
- Account workflow execution
- General workflow execution
- Escalation decisions
- FastAPI endpoints
- Conversation status retrieval
- Human-in-the-loop interruption
- Workflow resume behavior
- API conflict responses
- API not-found responses

Current test status:

```text
20 passed
```

## Tech Stack

### Agent Orchestration

- LangGraph
- LangChain

### LLM Integration

- Groq LLM API
- GPT-OSS 120B
- Structured Output

### Backend

- FastAPI
- Uvicorn
- Pydantic

### Persistence

- SQLite
- PostgreSQL
- Neon
- LangGraph SQLite Checkpointer
- LangGraph PostgreSQL Checkpointer

### Frontend

- Streamlit
- Requests

### Testing

- Pytest
- FastAPI TestClient

### Infrastructure and Deployment

- Docker
- Docker Compose
- Docker Buildx
- Multi-platform OCI images
- Docker Hub
- Render

## Docker Image Architecture Support

Both published Docker images provide native variants for AMD64 and ARM64.

```text
customer-support-agent-api:latest
        |
        +── linux/amd64
        |
        └── linux/arm64


customer-support-agent-frontend:latest
        |
        +── linux/amd64
        |
        └── linux/arm64
```

This allows the application to run natively on:

- Intel/AMD Linux systems
- Windows systems using Linux containers
- Intel-based Macs
- Apple Silicon Macs
- ARM64 Linux systems

## Engineering Decisions

### Hybrid Routing Instead of LLM-Only Routing

Deterministic routing handles clear requests without requiring an LLM call.

The LLM is used only when deterministic classification cannot confidently determine the intent.

This improves predictability, latency, testability, and API cost efficiency.

### Specialized Subgraphs

Billing, Technical, Account, and General support domains are implemented as independent subgraphs.

This keeps workflow logic modular and makes individual support domains easier to extend and test.

### Thin Frontend Architecture

The Streamlit frontend communicates exclusively through the FastAPI API.

It does not directly invoke LangGraph.

This keeps the agent orchestration layer independent of the UI implementation.

### Configurable Persistence Backend

Persistence configuration is separated from graph construction and API request handling.

SQLite provides a lightweight development backend, while PostgreSQL provides durable external persistence for cloud deployment.

This avoids coupling the LangGraph application to one storage implementation.

### Persistent Human-in-the-Loop Execution

LangGraph checkpoints allow interrupted workflows to survive application restarts.

Human responses resume execution from saved graph state rather than restarting the workflow.

Production PostgreSQL checkpointing ensures workflow state remains available even when the API container is restarted or redeployed.

### External Persistence for Ephemeral Containers

The deployed backend does not rely on the Render container filesystem for production checkpoint persistence.

Neon PostgreSQL stores workflow state externally.

This allows state recovery independently of the lifecycle of the application container.

### Multi-Platform Container Images

Separate AMD64 and ARM64 image variants are published behind a single `latest` manifest.

Docker automatically selects the correct image variant for the host platform.

## Production Verification

The deployed system was tested end-to-end.

Verified behaviors:

- Public Streamlit frontend successfully communicates with the deployed FastAPI API
- Health endpoint returns a successful response
- Deterministic routing processes clear customer requests
- Human-review-required workflows pause using `interrupt()`
- Escalation metadata is displayed in the Streamlit UI
- Human responses resume execution using `Command(resume=...)`
- Completed workflow state is persisted in PostgreSQL
- Conversation status can be retrieved using `thread_id`
- Checkpoint state survives API service restart
- Completed conversations are successfully recovered from Neon PostgreSQL after container restart

## Current Limitations

This project is designed to demonstrate Agentic AI architecture, LangGraph workflow orchestration, HITL execution, persistence, containerization, and cloud deployment.

Current limitations:

- Deterministic classifiers use keyword matching rather than trained production intent-classification models.
- Domain subgraphs do not independently resolve all ambiguous follow-up requests using conversation history.
- The application does not provide an authenticated support-agent dashboard.
- Authentication and authorization are not implemented.
- Rate limiting is not implemented.
- Distributed tracing and production observability are not implemented.
- The Streamlit UI stores visible messages in session state instead of reconstructing complete conversation history from the backend.
- Starting a new conversation does not delete previously persisted checkpoints.
- Human-review operations are not protected by role-based access control.
- Render free-tier services may experience cold-start latency after periods of inactivity.
- The application is deployed as a single backend instance and does not demonstrate horizontal scaling.

## Learning Goals Demonstrated

This project demonstrates practical understanding of:

- LangGraph state management
- Nodes and edges
- Conditional routing
- Routing functions
- Deterministic workflows
- LLM-based fallback routing
- Structured output
- Specialized subgraphs
- Shared graph state
- Persistence and checkpointing
- Configurable checkpoint backends
- SQLite checkpoint persistence
- PostgreSQL checkpoint persistence
- Conversation history
- Context-aware routing
- Error handling
- Escalation workflows
- Human-in-the-loop execution
- `interrupt()`
- `Command(resume=...)`
- Workflow state recovery
- FastAPI integration
- REST API design
- Streamlit frontend integration
- Automated testing
- Separation of concerns
- Environment-based configuration
- Application logging
- Docker containerization
- Docker Compose orchestration
- Persistent external state
- Multi-platform Docker image publishing
- Public cloud deployment
- Ephemeral container architecture
- Managed PostgreSQL integration

## Future Improvements

Potential future improvements include:

- Authenticated customer and support-agent accounts
- Role-based access control for human-review operations
- Dedicated human-support dashboard
- Complete conversation-history reconstruction from persisted state
- Production-grade intent classification
- Additional specialized support workflows
- Rate limiting
- Request authentication
- Distributed tracing
- Metrics and monitoring
- Structured observability dashboards
- Automated CI/CD deployment pipeline
- Horizontal scaling and concurrency testing
- PostgreSQL connection-pool tuning
- Database migration management
- Automated production health and smoke tests

## Author

**Md Aman Alam**

GitHub:

https://github.com/Amankhan1009