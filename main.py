from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
from openai import OpenAI

app = FastAPI()

# Load API key from environment
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=api_key)
assistant_id = "asst_MFiGmVkpJq3r3kjkSuDCZtsx"

class MessageRequest(BaseModel):
    content: str

@app.post("/chat")
def chat_with_assistant(request: MessageRequest):
    try:
        # 1. Create thread
        thread = client.beta.threads.create()
        thread_id = thread.id

        # 2. Add user message
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.content
        )

        # 3. Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # 4. Poll for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)

        # 5. Get latest assistant message
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        latest = messages.data[-1].content[0].text.value

        return {"response": latest}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
