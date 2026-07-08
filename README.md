# Customer Support Agent with LangGraph

A modular customer support application built with LangGraph that demonstrates hybrid intent routing, conditional workflows, specialized subgraphs, persistent conversation state, context-aware LLM fallback routing, error handling, human escalation, real human-in-the-loop execution, REST API integration, and an interactive Streamlit chat interface.

## Features

* Natural-language customer support queries
* Deterministic intent classification for clear requests
* LLM-based fallback routing for ambiguous requests
* Structured output for reliable LLM intent classification
* Conditional routing with LangGraph
* Specialized Billing, Technical, Account, and General support subgraphs
* Shared LangGraph state across workflows
* SQLite checkpoint persistence
* Persistent conversation message history
* Context-aware LLM fallback routing
* Human escalation for unresolved and sensitive requests
* Real human-in-the-loop execution using `interrupt()`
* Resume paused workflows using `Command(resume=...)`
* FastAPI REST API
* Interactive Streamlit chat interface
* Human-review interface for resuming interrupted workflows
* Unit, workflow, and API integration tests
* Environment-based configuration
* Application logging

## Architecture

```text
                         Customer
                            |
                            v
                    Streamlit Chat UI
                         :8501
                            |
                         HTTP API
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
              +-------------+-------------+
              |                           |
         Clear Intent               Ambiguous Intent
              |                           |
              |                           v
              |               Context-Aware LLM Classifier
              |                           |
              +-------------+-------------+
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

## Routing Strategy

The system uses a hybrid routing strategy to avoid unnecessary LLM calls while still handling ambiguous customer requests.

### Deterministic Routing

Clear customer requests are classified using keyword-based deterministic logic.

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

Deterministic routing is fast, predictable, inexpensive, and easy to test.

### LLM-Based Fallback Routing

When deterministic logic cannot confidently classify a request, the system routes the request to an LLM classifier.

The LLM classifier uses structured output to return one supported intent:

* `billing`
* `technical`
* `account`
* `general`
* `unknown`

Example:

```text
"My subscription cost was deducted two times."
        |
        v
Deterministic classifier unresolved
        |
        v
Context-aware LLM classifier
        |
        v
billing
        |
        v
Billing subgraph
```

The LLM fallback can use persisted conversation context for ambiguous follow-up requests.

## Specialized LangGraph Workflows

Each major support domain is implemented as a separate LangGraph subgraph.

### Billing Workflow

Handles:

* Duplicate charges
* Refund requests
* Payment failures
* Other billing requests

The workflow performs billing issue classification and conditionally routes the request to a specialized billing handler.

### Technical Workflow

Handles:

* Application errors
* Performance issues
* Feature issues
* Unsupported technical issues

The workflow performs technical issue classification, diagnosis, and resolution-status routing.

Unresolved technical issues are escalated to the parent graph's human-support workflow.

### Account Workflow

Handles:

* Login problems
* Password resets
* Unauthorized account access
* Account deletion
* Other account requests

Sensitive account requests are escalated to human support.

### General Workflow

Handles:

* Pricing questions
* Product questions
* General support questions

## Human-in-the-Loop

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
State Saved by SQLite Checkpointer
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
Graph Loads Saved Checkpoint
       |
       v
Execution Continues
       |
       v
Final Response
```

The paused workflow can survive application restarts because its execution state is persisted.

## Persistence and Conversation Context

LangGraph checkpointing is implemented using SQLite.

Every conversation is identified by a unique `thread_id`.

```text
customer-a1b2c3d4 → conversation history and checkpoints

customer-x9y8z7w6 → separate conversation history and checkpoints
```

The LangGraph shared state stores message history using the `add_messages` reducer.

Conversation context is provided to the LLM fallback classifier when deterministic routing cannot confidently determine the latest customer intent.

Starting a new conversation from the Streamlit UI creates a new thread ID and clears the visible UI messages. Existing conversation checkpoints are not deleted from SQLite.

## Streamlit User Interface

The project includes an interactive Streamlit frontend.

The frontend is intentionally implemented as a thin API client:

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

The frontend does not directly import or invoke the LangGraph application.

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

The FastAPI backend exposes the following endpoints.

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
│   └── technical_router.py
├── schemas/
│   └── routing.py
├── workflows/
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
├── .env.example
├── .gitignore
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

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the CLI Application

```bash
python app.py
```

## Run the FastAPI Backend

```bash
uvicorn api.main:app --reload
```

The API runs locally on port `8000`.

Swagger API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Run the Streamlit Frontend

Start the FastAPI backend first.

Then open another terminal and run:

```bash
streamlit run frontend/app.py
```

The Streamlit frontend runs locally on port `8501`.

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

## Tech Stack

* Python
* LangGraph
* LangChain
* Groq LLM API
* GPT-OSS 120B
* Pydantic
* SQLite
* FastAPI
* Uvicorn
* Streamlit
* Requests
* Pytest

## Current Limitations

This project is a learning-focused implementation designed to demonstrate LangGraph workflow orchestration and conditional routing.

Current limitations:

* Deterministic classifiers use keyword matching rather than production intent-classification models.
* Domain subgraphs do not independently resolve ambiguous follow-up requests using conversation history.
* SQLite is suitable for local development but is not ideal for horizontally scaled production deployments.
* Human review is implemented through the Streamlit interface rather than a dedicated authenticated support dashboard.
* Conversation checkpoints remain stored after starting a new conversation.
* Authentication and authorization are not implemented.
* Rate limiting is not implemented.
* Distributed tracing and production observability are not implemented.
* The Streamlit UI maintains visible chat messages in session state rather than loading complete conversation history from the backend.

## Learning Goals Demonstrated

This project demonstrates practical understanding of:

* LangGraph state management
* Nodes
* Edges
* Conditional edges
* Routing functions
* Deterministic workflows
* LLM-based routing
* Structured output
* Specialized subgraphs
* Shared state
* Persistence and checkpointing
* Conversation history
* Context-aware routing
* Error handling
* Escalation workflows
* Human-in-the-loop
* `interrupt()`
* `Command(resume=...)`
* FastAPI integration
* Streamlit frontend integration
* Automated testing
* Separation of concerns
* Environment-based configuration
* Application logging
