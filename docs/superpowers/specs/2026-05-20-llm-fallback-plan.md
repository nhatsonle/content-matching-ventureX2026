# Implementation Plan: Google GenAI to xAI (Grok) LLM Fallback

This plan details the step-by-step tasks required to implement the fallback LLM configuration from Google GenAI to xAI Grok.

## Steps

### Step 1: Update Dependencies
1. Open `backend/pyproject.toml` and add `"langchain-xai"` to the `dependencies` list.
2. Open `backend/requirements.txt` and add `langchain-xai` to the end of the file.
3. Run the installation command to ensure dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configure Environment and Settings
1. Open `backend/.env` and add:
   ```env
   XAI_API_KEY=your_xai_api_key_here
   XAI_MODEL=grok-2-latest
   ```
2. Open `backend/config.py` and modify the `Settings` class:
   - Add `xai_api_key: Optional[str] = None`
   - Add `xai_model: str = "grok-2-latest"`

### Step 3: Implement LLM Factory / Instances
1. Open `backend/llm.py`.
2. Rename `llm` to `google_llm`.
3. Import `ChatXAI` from `langchain_xai`.
4. Initialize `xai_llm` if `settings.xai_api_key` is present.

### Step 4: Implement Agent Fallback Logic
1. Open `backend/explanation.py`.
2. Import `google_llm` and `xai_llm` from `llm` instead of `llm`.
3. Create `google_agent` using `google_llm`.
4. Create `xai_agent` using `xai_llm` if it is initialized.
5. In `generate_explanation()` -> `_invoke()`:
   - Wrap the `google_agent.invoke(...)` call in a `try-except` block.
   - On exception:
     - Print/log the exception message.
     - Call `xai_agent.invoke(...)` as fallback if `xai_agent` is configured.
     - Raise a descriptive error if fallback is not configured.

### Step 5: Verification & Testing
1. Run `python explanation.py` to test the script execution using Google GenAI.
2. Temporarily set an invalid key or trigger an exception on Google GenAI to verify that it successfully falls back to xAI Grok (and logs the event).
3. Test end-to-end endpoint `POST /match` using a curl command.
