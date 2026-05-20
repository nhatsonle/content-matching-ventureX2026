# Implementation Plan: LLM Provider Selection (Google, xAI, OpenAI)

## Phase 1: Environment and Settings Configuration
- [ ] Add `openai_model` configuration to `backend/config.py`.
- [ ] Add `OPENAI_API_KEY` and `OPENAI_MODEL` placeholders to `backend/.env`.

## Phase 2: LLM Client Instantiation
- [ ] Update `backend/llm.py` to import `ChatOpenAI` and instantiate `openai_llm` if a valid key is provided.

## Phase 3: Pydantic & API Route Changes
- [ ] Add the `provider` field to the `BriefRequest` model in `backend/models.py`.
- [ ] Modify `/match` API route in `backend/main.py` to catch `ValueError` during execution and return an HTTP 400 response.

## Phase 4: Explanation Agent Updates
- [ ] Update `backend/explanation.py` to instantiate `openai_agent` if `openai_llm` is available.
- [ ] Update `generate_explanation` to select the agent based on `brief.provider` and raise a `ValueError` if the corresponding agent is not configured.

## Phase 5: Frontend Integration
- [ ] Update `provider: string` inside the `BriefRequest` type in `frontend/src/lib/data/types.ts`.
- [ ] Update `frontend/src/components/match-engine/BriefForm.tsx` to add a Select dropdown for Model Provider and bind it to the request payload.

## Phase 6: Testing & Verification
- [ ] Test form submission with each provider (valid/invalid configurations) and verify correct error messages or successful responses.
