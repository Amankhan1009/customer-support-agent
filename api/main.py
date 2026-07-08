import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from api.schemas import (
    ResumeRequest,
    SupportRequest,
    SupportResponse,
)
from graph.builder import build_graph


from config.logging import configure_logging
from config.settings import DATABASE_PATH

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)
    app.state.graph = build_graph(checkpointer=checkpointer)
    app.state.connection = connection

    yield

    connection.close()


app = FastAPI(
    title="Customer Support Agent API",
    version="1.0.0",
    lifespan=lifespan,
)


def get_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def build_response(
    graph,
    thread_id: str,
    result: dict,
) -> SupportResponse:
    config = get_config(thread_id)
    snapshot = graph.get_state(config)

    if snapshot.interrupts:
        interrupt_data = snapshot.interrupts[0].value

        return SupportResponse(
            thread_id=thread_id,
            status="human_review_required",
            interrupt_data=interrupt_data,
        )

    return SupportResponse(
        thread_id=thread_id,
        status="completed",
        response=result.get("response"),
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.post(
    "/support",
    response_model=SupportResponse,
)
def create_support_request(request: SupportRequest):
    graph = app.state.graph
    config = get_config(request.thread_id)

    snapshot = graph.get_state(config)

    if snapshot.interrupts:
        raise HTTPException(
            status_code=409,
            detail=(
                "This conversation is waiting for human review. "
                "Resume the existing request before submitting "
                "another message."
            ),
        )

    result = graph.invoke(
        {
            "customer_message": request.message,
        },
        config=config,
    )

    return build_response(
        graph,
        request.thread_id,
        result,
    )


@app.get(
    "/support/{thread_id}",
    response_model=SupportResponse,
)
def get_support_status(thread_id: str):
    graph = app.state.graph
    config = get_config(thread_id)

    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail="Conversation thread not found.",
        )

    if snapshot.interrupts:
        return SupportResponse(
            thread_id=thread_id,
            status="human_review_required",
            interrupt_data=snapshot.interrupts[0].value,
        )

    return SupportResponse(
        thread_id=thread_id,
        status="completed",
        response=snapshot.values.get("response"),
    )


@app.post(
    "/support/resume",
    response_model=SupportResponse,
)
def resume_support_request(request: ResumeRequest):
    graph = app.state.graph
    config = get_config(request.thread_id)

    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail="Conversation thread not found.",
        )

    if not snapshot.interrupts:
        raise HTTPException(
            status_code=409,
            detail="This conversation is not waiting for human review.",
        )

    result = graph.invoke(
        Command(resume=request.human_response),
        config=config,
    )

    return build_response(
        graph,
        request.thread_id,
        result,
    )