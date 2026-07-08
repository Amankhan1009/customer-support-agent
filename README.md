# Customer Support Agent with LangGraph

A modular, stateful, and containerized Agentic AI customer support system built with LangGraph.

The application demonstrates hybrid intent routing, specialized subgraphs, persistent conversation state, context-aware LLM fallback routing, conditional workflows, error handling, human escalation, real human-in-the-loop execution, REST API integration, an interactive Streamlit interface, automated testing, and multi-platform Docker deployment.

## Repository and Docker Images

**GitHub Repository**

https://github.com/Amankhan1009/customer-support-agent

**Docker Hub Images**

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

* Natural-language customer support queries
* Hybrid deterministic and LLM-based intent routing
* Deterministic classification for clear customer requests
* Context-aware LLM fallback routing for ambiguous requests
* Structured LLM output for reliable intent classification
* Conditional routing using LangGraph
* Specialized Billing, Technical, Account, and General support subgraphs
* Shared LangGraph state across workflows
* SQLite checkpoint persistence
* Persistent conversation message history
* Human escalation for unresolved and sensitive requests
* Real human-in-the-loop execution using `interrupt()`
* Resume paused workflows using `Command(resume=...)`
* Persistent interrupted workflows across application restarts
* FastAPI REST API
* Interactive Streamlit chat interface
* Human-review interface for interrupted workflows
* Conversation thread isolation using `thread_id`
* Unit, workflow, and API integration tests
* Environment-based configuration
* Application logging
* Dockerized API and frontend services
* Docker Compose orchestration
* Persistent Docker volume for SQLite checkpoints
* Multi-platform Docker images for AMD64 and ARM64 systems

## Architecture

```text
                            Customer
                               |
                               v
                       Streamlit Chat UI
                            :8501
                               |
                          HTTP Requests
                               |
                               v
                         FastAPI Backend
                            :8000
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
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
      Billing Subgraph  Technical Subgraph  Account Subgraph
             |
             +--------------------------+
                                        |
                                        v
                                 General Subgraph

                               |
                               v
                    Resolution / Escalation Decision
                               |
                      +--------+--------+
                      |                 |
                   Resolved         Escalation
                      |                 |
                      v                 v
             Finalize Response   Human Support Workflow
                                        |
                                        v
                                    interrupt()
                                        |
                                        v
                              SQLite Checkpoint Saved
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
                              Finalize Response
```

## Application Architecture

The application is separated into independent frontend, API, orchestration, workflow, persistence, and infrastructure layers.

```text
Browser
   |
   v
Streamlit Frontend
   |
   | HTTP
   v
FastAPI REST API
   |
   v
LangGraph Application
   |
   +---------------------------+
   |                           |
   v                           v
Specialized Subgraphs    Human-in-the-Loop
   |                           |
   v                           v
Support Resolution       interrupt() / resume
   |
   v
SQLite Checkpointer
```

The Streamlit frontend acts as a thin API client and never directly invokes the LangGraph application.

This separation allows the backend agent system to be consumed by other clients without changing the graph implementation.

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

* Low latency
* Predictable behavior
* Reduced LLM API usage
* Lower inference cost
* Easy automated testing

### Context-Aware LLM Fallback Routing

When deterministic classification cannot confidently identify an intent, the request is routed to an LLM classifier.

The classifier uses structured output and returns exactly one supported intent:

* `billing`
* `technical`
* `account`
* `general`
* `unknown`

Example:

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

* Duplicate charges
* Refund requests
* Payment failures
* Other billing-related requests

The workflow classifies the billing issue and conditionally routes execution to the appropriate billing handler.

### Technical Workflow

Handles:

* Application errors
* Performance issues
* Feature issues
* Unsupported technical problems

The workflow performs issue classification, technical diagnosis, and resolution-status routing.

Unresolved technical issues are escalated to the parent graph's human-support workflow.

### Account Workflow

Handles:

* Login problems
* Password resets
* Unauthorized account access
* Account deletion
* Other account-management requests

Sensitive account requests are escalated for human review.

### General Workflow

Handles:

* Pricing questions
* Product questions
* General service questions

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
SQLite Checkpoint Saved
       |
       v
API Returns human_review_required
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

Because execution state is persisted using SQLite checkpointing, interrupted workflows can survive application restarts.

## Persistence and Conversation Context

LangGraph checkpointing is implemented using SQLite.

Each conversation is identified by a unique `thread_id`.

```text
customer-a1b2c3d4
        |
        v
Conversation History + Graph Checkpoints

customer-x9y8z7w6
        |
        v
Independent Conversation History + Graph Checkpoints
```

The shared LangGraph state stores conversation messages using the `add_messages` reducer.

Conversation context is provided to the LLM fallback classifier when deterministic routing cannot confidently determine the latest customer intent.

Starting a new conversation from the Streamlit UI:

* Creates a new thread ID
* Clears visible messages from the current Streamlit session
* Does not delete existing SQLite checkpoints

## Streamlit User Interface

The project includes an interactive Streamlit frontend.

```text
Streamlit UI
      |
      | HTTP Requests
      v
FastAPI
      |
      v
LangGraph
```

The frontend intentionally acts as a thin API client.

It does not directly import or invoke the LangGraph application.

### UI Features

* Chat-based customer support interface
* Automatically generated conversation thread IDs
* Visible customer and support messages
* Start New Conversation button
* Human-review-required status
* Escalation details
* Human support response input
* Resume interrupted workflows
* Configurable backend API URL

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
    "escalation_reason": "automatic_diagnosis_failed"
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

Configure:

```text
GROQ_API_KEY=your_real_groq_api_key
DATABASE_PATH=support_checkpoints.db
LOG_LEVEL=INFO
```

Never commit the real `.env` file.

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

Then add your Groq API key to `.env`.

## Run the CLI Application

```bash
python app.py
```

## Run the FastAPI Backend

```bash
uvicorn api.main:app --reload
```

The backend is available on port `8000`.

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

The frontend is available on port `8501`.

```text
http://localhost:8501
```

## Run with Docker Compose

The easiest way to run the complete application is Docker Compose.

Create `.env`:

```bash
cp .env.example .env
```

Add your Groq API key.

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

The SQLite checkpoint database is persisted using the `support_data` Docker volume.

To also delete the persisted checkpoint volume:

```bash
docker compose down -v
```

## Run Using Published Docker Images

The API and frontend images are published on Docker Hub.

Pull the images:

```bash
docker pull amankhan1009/customer-support-agent-api:latest

docker pull amankhan1009/customer-support-agent-frontend:latest
```

The images support both:

```text
linux/amd64
linux/arm64
```

Docker automatically selects the appropriate image for the host architecture.

To run the complete system using the published images, the services must share a Docker network so the frontend can communicate with the API.

Create a network:

```bash
docker network create customer-support-network
```

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
  -e DATABASE_PATH=/data/support_checkpoints.db \
  -v customer-support-data:/data \
  amankhan1009/customer-support-agent-api:latest
```

Run the frontend:

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

Stop and remove the containers:

```bash
docker stop customer-support-frontend customer-support-api

docker rm customer-support-frontend customer-support-api
```

## Run Tests

```bash
pytest -v
```

The project currently includes 20 automated tests covering:

* Deterministic classifiers
* Billing workflow execution
* Technical workflow execution
* Account workflow execution
* General workflow execution
* Escalation decisions
* FastAPI endpoints
* Conversation status retrieval
* Human-in-the-loop interruption
* Workflow resume behavior
* API conflict and not-found responses

Current test status:

```text
20 passed
```

## Tech Stack

### Agent Orchestration

* LangGraph
* LangChain

### LLM Integration

* Groq LLM API
* GPT-OSS 120B
* Structured Output

### Backend

* FastAPI
* Uvicorn
* Pydantic

### Persistence

* SQLite
* LangGraph SQLite Checkpointer

### Frontend

* Streamlit
* Requests

### Testing

* Pytest
* FastAPI TestClient

### Infrastructure

* Docker
* Docker Compose
* Docker Buildx
* Multi-platform OCI images

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

* Intel/AMD Linux systems
* Windows systems using Linux containers
* Intel-based Macs
* Apple Silicon Macs
* ARM64 Linux systems

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

### Persistent Human-in-the-Loop Execution

LangGraph checkpoints and SQLite persistence allow interrupted workflows to survive application restarts.

Human responses resume execution from the saved graph state rather than restarting the workflow.

### Multi-Platform Container Images

Separate AMD64 and ARM64 image variants are published behind a single `latest` manifest.

Docker automatically selects the correct image variant for the host platform.

## Current Limitations

This project is designed to demonstrate Agentic AI architecture and LangGraph workflow orchestration.

Current limitations:

* Deterministic classifiers use keyword matching rather than production intent-classification models.
* Domain subgraphs do not independently resolve ambiguous follow-up requests using conversation history.
* SQLite is suitable for local development but not ideal for horizontally scaled production deployments.
* Human review is implemented through the Streamlit interface instead of a dedicated authenticated support dashboard.
* Conversation checkpoints remain stored after starting a new conversation.
* Authentication and authorization are not implemented.
* Rate limiting is not implemented.
* Distributed tracing and production observability are not implemented.
* The Streamlit UI stores visible messages in session state instead of loading complete conversation history from the backend.

## Learning Goals Demonstrated

This project demonstrates practical understanding of:

* LangGraph state management
* Nodes and edges
* Conditional routing
* Routing functions
* Deterministic workflows
* LLM-based fallback routing
* Structured output
* Specialized subgraphs
* Shared graph state
* Persistence and checkpointing
* Conversation history
* Context-aware routing
* Error handling
* Escalation workflows
* Human-in-the-loop execution
* `interrupt()`
* `Command(resume=...)`
* FastAPI integration
* REST API design
* Streamlit frontend integration
* Automated testing
* Separation of concerns
* Environment-based configuration
* Application logging
* Docker containerization
* Docker Compose orchestration
* Persistent Docker volumes
* Multi-platform Docker image publishing
