# Design Spec: LLM Provider Selection (Google, xAI, OpenAI)

## Background & Goal
Instead of using automatic fallback, we want to allow users to explicitly choose their preferred LLM provider (Google Gemini, xAI Grok, or OpenAI GPT) from the frontend match engine dashboard. The system should read the chosen provider from the request payload, check if the corresponding API key is configured, and route the request to the correct agent. If the requested provider's key is not configured, it should return a clear, user-facing error message.

## Requirements
1. Allow selecting between three providers:
   - Google Gemini (default)
   - xAI Grok
   - OpenAI GPT
2. Validate API key presence for the selected provider. If the key is missing or not configured, return an HTTP 400 Bad Request.
3. Support configuration parameters for OpenAI in the `.env` file (`OPENAI_API_KEY` and `OPENAI_MODEL`).
4. Update the frontend UI to display a dropdown/select element for the model provider.

## Design Details

### 1. Configuration Settings
Extend the `Settings` class in `backend/config.py` and environment variables in `backend/.env`:
- **New Environment Variable**: `OPENAI_MODEL` (optional, defaults to `gpt-4o-mini`). Note: `OPENAI_API_KEY` is already supported by `Settings` but we'll ensure it has a placeholder in `.env`.
- **Pydantic Settings**:
  - `openai_model: str = "gpt-4o-mini"`

### 2. LLM Client Setup (`backend/llm.py`)
- Import `ChatOpenAI` from `langchain_openai`.
- Add `openai_llm` instance using `ChatOpenAI`.

```python
from langchain_openai import ChatOpenAI

openai_llm = None
if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
    openai_llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
    )
```

### 3. Pydantic Models (`backend/models.py`)
- Update `BriefRequest` to include:
  - `provider: str = "google"` (supports `"google"`, `"xai"`, `"openai"`)

### 4. Agent Setup and Dynamic Routing (`backend/explanation.py`)
Pre-initialize agents for all configured providers:
- **Initialization**:
  ```python
  from llm import google_llm, xai_llm, openai_llm

  google_agent = create_deep_agent(model=google_llm, tools=[search_web], system_prompt=SYSTEM_PROMPT)

  xai_agent = None
  if xai_llm:
      xai_agent = create_deep_agent(model=xai_llm, tools=[search_web], system_prompt=SYSTEM_PROMPT)

  openai_agent = None
  if openai_llm:
      openai_agent = create_deep_agent(model=openai_llm, tools=[search_web], system_prompt=SYSTEM_PROMPT)
  ```

- **Execution Flow** in `generate_explanation`'s `_invoke()`:
  ```python
  def _invoke():
      # Select agent based on provider
      if brief.provider == "openai":
          if not openai_agent:
              raise ValueError("OpenAI API key is not configured on the server.")
          agent = openai_agent
      elif brief.provider == "xai":
          if not xai_agent:
              raise ValueError("xAI API key is not configured on the server.")
          agent = xai_agent
      else:
          if not google_agent:
              raise ValueError("Google API key is not configured on the server.")
          agent = google_agent

      response = agent.invoke({"messages": HumanMessage(content=prompt)})
      if isinstance(response.content, list):
          return response.content[0].text
      return response.content
  ```

### 5. API Error Handling (`backend/main.py`)
Wrap execution in `try-except ValueError` to return HTTP 400 Bad Request:
```python
@app.post("/match", response_model=MatchResponse)
def match(brief: BriefRequest):
    try:
        # existing retrieval & scoring...
        # generate_explanation will raise ValueError if provider not configured
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 6. Frontend Integration
- **Types (`frontend/src/lib/data/types.ts`)**: Add `provider: string` to `BriefRequest`.
- **UI Form (`frontend/src/components/match-engine/BriefForm.tsx`)**:
  - Add selector dropdown:
    ```tsx
    <label className="text-sm font-medium">Model Provider</label>
    <Select value={provider} onValueChange={setProvider}>
        <SelectItem value="google">Google Gemini</SelectItem>
        <SelectItem value="xai">xAI Grok</SelectItem>
        <SelectItem value="openai">OpenAI GPT</SelectItem>
    </Select>
    ```
  - Send `provider` inside brief payload.
