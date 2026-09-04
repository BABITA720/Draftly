# Draftly — AI Content Studio

Draftly is a Streamlit app that uses Google Gemini to turn content briefs into YouTube scripts, social media posts, and SEO content.

## Run & Operate

- `streamlit run app.py --server.port 5000` — run the Streamlit app
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required secret: `GEMINI_API_KEY` — Google Gemini API key

## Stack

- Python 3.13
- UI: Streamlit
- AI: Google Gemini (`google-genai`)

## Where things live

- `app.py` — Streamlit UI, prompt construction, Gemini generation, and session history
- `.streamlit/config.toml` — local Streamlit server settings
- `pyproject.toml` / `uv.lock` — Python dependencies

## Architecture decisions

- The app uses the user's `GEMINI_API_KEY` secret through the official `google-genai` SDK.
- Generated drafts and history are intentionally session-scoped; no database is needed for the first version.
- Prompts are format-aware so each output has a useful structure rather than generic paragraphs.

## Product

- Choose YouTube Video Script, Social Media Post, or SEO Content.
- Customize tone, audience, length, and additional context.
- Generate content with Gemini, edit it in place, download it as a text file, and revisit drafts within the current session.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
