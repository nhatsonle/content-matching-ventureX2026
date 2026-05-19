# Design Spec: Google GenAI to xAI (Grok) LLM Fallback

## Background & Goal
Currently, the backend matching engine uses Google GenAI (`ChatGoogleGenerativeAI`) to generate Vietnamese-language casting recommendations and fit explanations. To improve system resilience and provide redundancy, we want to allow falling back to xAI (Grok) when Google GenAI encounters errors, such as rate limits or API key/network issues. We have separate keys for Google GenAI and xAI.

## Requirements
1. Use Google GenAI (`ChatGoogleGenerativeAI`) as the primary model.
2. If Google GenAI fails, catch the exception, log the failure, and fall back to xAI Grok using `langchain-xai`.
3. Support configuration parameters for xAI API Key and Model in the `.env` file and settings configuration.
4. Integrate dependencies cleanly via `requirements.txt` and `pyproject.toml`.

## Design Details

### 1. Dependencies
Add `langchain-xai` to the backend dependencies:
- In `backend/requirements.txt`: `langchain-xai`
- In `backend/pyproject.toml`: Add `"langchain-xai"` to the dependencies list.

### 2. Configuration Settings
Extend the `Settings` class in `backend/config.py` and add environment variables to `backend/.env`:
- **New Environment Variable**: `XAI_API_KEY` (required for xAI), `XAI_MODEL` (optional, defaults to `grok-2-latest`).
- **Pydantic Settings**:
  - `xai_api_key: Optional[str] = None`
  - `xai_model: str = "grok-2-latest"`

### 3. LLM Setup (`backend/llm.py`)
Expose both primary and fallback LLM instances or configure them so they can be consumed by the agent.
- Keep `google_llm` as standard client.
- Add `xai_llm` instance using `ChatXAI` from `langchain_xai` if `xai_api_key` is provided.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI
from config import settings

google_llm = ChatGoogleGenerativeAI(
    model=settings.model,
    google_api_key=settings.google_api_key,
    temperature=settings.temperature,
    max_tokens=settings.max_tokens,
    timeout=settings.timeout,
    max_retries=settings.max_retries,
    api_key=settings.google_api_key,
)

xai_llm = None
if settings.xai_api_key:
    xai_llm = ChatXAI(
        model=settings.xai_model,
        xai_api_key=settings.xai_api_key,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
    )
```

### 4. Agent Execution with Fallback (`backend/explanation.py`)
Create separate deep agents for Google and xAI. When generating explanations, try invoking the Google agent first. If an exception occurs, catch it and fall back to the xAI agent.

- **Initialization**:
  ```python
  google_agent = create_deep_agent(model=google_llm, tools=[search_web], system_prompt=SYSTEM_PROMPT)
  
  xai_agent = None
  if xai_llm:
      xai_agent = create_deep_agent(model=xai_llm, tools=[search_web], system_prompt=SYSTEM_PROMPT)
  ```

- **Execution Flow** in `generate_explanation`'s `_invoke()`:
  ```python
  def _invoke():
      try:
          print("Attempting explanation generation using Google GenAI...")
          response = google_agent.invoke({"messages": HumanMessage(content=prompt)})
          if isinstance(response.content, list):
              return response.content[0].text
          return response.content
      except Exception as e:
          print(f"Google GenAI failed with error: {e}. Falling back to xAI (Grok)...")
          if not xai_agent:
              raise RuntimeError("xAI Grok agent is not configured (missing XAI_API_KEY). Fallback aborted.") from e
          
          response = xai_agent.invoke({"messages": HumanMessage(content=prompt)})
          if isinstance(response.content, list):
              return response.content[0].text
          return response.content
  ```

## Self-Review Check
- **Placeholder scan**: None. Configuration default model and keys are clearly specified.
- **Internal consistency**: The fallback flow relies on independent agent instances configured with different models/keys. This ensures that even if one SDK/API has issues, the other can run cleanly.
- **Scope check**: This is a simple, highly focused spec for the requested fallback behavior.
- **Ambiguity check**: The fallback is triggered on any exception during Google GenAI agent execution and will print clear log messages.
