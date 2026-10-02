from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from langgraph.types import Command

from api.schemas import (
    MessageHistoryItem,
    ResumeRequest,
    SupportRequest,
    SupportResponse,
    ThreadHistoryResponse,
    UserThreadItem,
)
from auth.router import router as auth_router
from auth.security import (
    get_current_user,
    get_user_threads,
    init_user_db,
    save_user_thread,
)
from config.checkpointer import close_checkpointer, create_checkpointer
from config.logging import configure_logging
from graph.builder import build_graph


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_user_db()

    checkpointer, resource = create_checkpointer()

    app.state.graph = build_graph(
        checkpointer=checkpointer,
    )
    app.state.checkpointer_resource = resource

    yield

    close_checkpointer(resource)


app = FastAPI(
    title="Customer Support Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


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
def create_support_request(
    request: SupportRequest,
    current_user: dict = Depends(get_current_user),
):
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
    save_user_thread(
        username=current_user["username"],
        thread_id=request.thread_id,
        title=request.message[:45],
    )

    return build_response(
        graph,
        request.thread_id,
        result,
    )


@app.get(
    "/support/threads",
    response_model=list[UserThreadItem],
)
def list_user_threads(
    current_user: dict = Depends(get_current_user),
):
    threads = get_user_threads(current_user["username"])
    if not threads:
        default_tid = f"customer-{current_user['username']}"
        threads = [{"thread_id": default_tid, "title": "Main Conversation"}]
    return [UserThreadItem(**t) for t in threads]


@app.get(
    "/support/{thread_id}",
    response_model=SupportResponse,
)
def get_support_status(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
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

@app.get(
    "/support/{thread_id}/history",
    response_model=ThreadHistoryResponse,
)
def get_thread_history(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    graph = app.state.graph
    config = get_config(thread_id)

    snapshot = graph.get_state(config)

    if not snapshot.values:
        return ThreadHistoryResponse(
            thread_id=thread_id,
            messages=[],
            waiting_for_human=False,
            interrupt_data=None,
        )

    formatted_messages = []
    for msg in snapshot.values.get("messages", []):
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
            content = msg.content
        elif isinstance(msg, dict):
            role = "user" if msg.get("type") == "human" or msg.get("role") == "user" else "assistant"
            content = msg.get("content", "")
        else:
            continue
        formatted_messages.append(MessageHistoryItem(role=role, content=str(content)))

    waiting_for_human = bool(snapshot.interrupts)
    interrupt_data = snapshot.interrupts[0].value if snapshot.interrupts else None

    return ThreadHistoryResponse(
        thread_id=thread_id,
        messages=formatted_messages,
        waiting_for_human=waiting_for_human,
        interrupt_data=interrupt_data,
    )

@app.post(
    "/support/resume",
    response_model=SupportResponse,
)
def resume_support_request(
    request: ResumeRequest,
    current_user: dict = Depends(get_current_user),
):
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