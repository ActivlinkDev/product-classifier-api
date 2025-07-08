from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
import time

app = FastAPI()

# Initialize OpenAI client once (make sure your API key is set as env var)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RequestBody(BaseModel):
    thread_id: str
    assistant_id: str
    user_message: str

@app.post("/run-assistant")
def run_assistant(data: RequestBody):
    thread_id = data.thread_id
    assistant_id = data.assistant_id
    user_message = data.user_message

    # Send user message
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # Start assistant run
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Wait for completion (simple polling)
    while run.status not in ["completed", "failed"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Fetch messages and return latest assistant reply
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    # Adjust this as per your message structure
    response_text = messages.data[-1].content[0].text.value

    return {"response": response_text}
