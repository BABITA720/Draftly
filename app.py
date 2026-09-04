import os
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types


st.set_page_config(
    page_title="Draftly — AI Content Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


CONTENT_TYPES = {
    "YouTube Video Script": {
        "icon": "▶",
        "description": "A ready-to-record script with a hook, beats, and a strong close.",
        "placeholder": "e.g. How to build a morning routine that actually sticks",
        "lengths": ["Short · 60–90 sec", "Standard · 5–7 min", "Deep dive · 10–15 min"],
        "default_length": "Standard · 5–7 min",
    },
    "Social Media Post": {
        "icon": "◎",
        "description": "Scroll-stopping copy shaped for your audience and platform.",
        "placeholder": "e.g. Announcing our new sustainable packaging",
        "lengths": ["Punchy · 1–2 sentences", "Standard · 100–150 words", "Story-led · 250–350 words"],
        "default_length": "Standard · 100–150 words",
    },
    "SEO Content": {
        "icon": "⌕",
        "description": "Search-friendly content with structure, intent, and natural keywords.",
        "placeholder": "e.g. A beginner's guide to indoor herb gardening",
        "lengths": ["Quick read · 500–700 words", "Standard · 1,000–1,400 words", "Comprehensive · 2,000+ words"],
        "default_length": "Standard · 1,000–1,400 words",
    },
}

TONES = [
    "Clear & professional",
    "Warm & conversational",
    "Bold & energetic",
    "Playful & witty",
    "Thoughtful & authoritative",
]


class GeminiConfigurationError(RuntimeError):
    """The app cannot initialize Gemini with the configured credentials."""


class GeminiAuthenticationError(RuntimeError):
    """Gemini rejected the configured API key or its permissions."""


class GeminiQuotaError(RuntimeError):
    """Gemini rejected the request because of quota or rate limits."""


class GeminiServiceError(RuntimeError):
    """Gemini could not complete the request because of a temporary failure."""


def get_api_key() -> str:
    """Read the key from Replit's environment, with Streamlit secrets as a fallback."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        try:
            api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        except Exception:
            api_key = ""
    return api_key


def classify_gemini_error(error: Exception) -> RuntimeError:
    """Convert provider errors into safe, actionable app-level messages."""
    message = str(error).lower()

    if any(term in message for term in ("quota", "rate limit", "resource exhausted", "429")):
        return GeminiQuotaError(
            "Gemini quota or rate limits were reached. Check your Google AI Studio "
            "usage and try again later."
        )

    if any(
        term in message
        for term in (
            "api key",
            "api_key",
            "invalid key",
            "invalid api",
            "unauthenticated",
            "authentication",
            "permission denied",
            "forbidden",
            "401",
            "403",
        )
    ):
        return GeminiAuthenticationError(
            "Gemini rejected the configured API key. Replace GEMINI_API_KEY in "
            "Replit Secrets with an active Google AI Studio key."
        )

    if any(
        term in message
        for term in (
            "connection",
            "deadline",
            "temporarily unavailable",
            "service unavailable",
            "timeout",
            "500",
            "502",
            "503",
        )
    ):
        return GeminiServiceError(
            "Gemini is temporarily unavailable. Check your connection and try again."
        )

    return GeminiServiceError("Gemini could not complete the request. Please try again.")


def get_client() -> genai.Client:
    api_key = "AQ.Ab8RN6LcfjD5wyE3RJg4hAcKI-og..."

    if not api_key:
        raise GeminiConfigurationError(
            "Gemini is not connected. Add GEMINI_API_KEY to Replit Secrets, then restart the app."
        )
    try:
        return genai.Client(api_key=api_key)
    except Exception as error:
        raise classify_gemini_error(error) from error


def build_prompt(
    content_type: str,
    topic: str,
    tone: str,
    length: str,
    audience: str,
    details: str,
) -> str:
    shared = f"""
Create polished, original {content_type.lower()} about:
TOPIC: {topic}
AUDIENCE: {audience or "a curious general audience"}
TONE: {tone}
LENGTH: {length}
ADDITIONAL CONTEXT: {details or "None provided"}

Write the final deliverable only. Do not mention these instructions or describe your process.
Make every line useful and specific to the topic. Avoid clichés, filler, and unsupported claims.
"""

    if content_type == "YouTube Video Script":
        return shared + """
Format the response as a production-ready YouTube script:
- Give it a compelling title and one-sentence premise.
- Include a hook for the opening 15 seconds.
- Use clear section headings, natural spoken language, and occasional [B-ROLL] or [ON SCREEN] cues.
- End with a memorable takeaway and a natural call to action.
"""
    if content_type == "Social Media Post":
        return shared + """
Format the response as a publish-ready social post:
- Start with a strong first line that earns attention without clickbait.
- Use readable line breaks and concrete language.
- Include one subtle call to action.
- Finish with 3–5 relevant hashtags on a separate line.
"""
    return shared + """
Format the response as helpful SEO content:
- Start with an SEO title, meta description, and a suggested primary keyword.
- Use a clear H1, H2, and H3 structure.
- Answer the searcher's likely questions directly and naturally.
- Include a short FAQ section with 3 questions and answers.
- Do not keyword-stuff or use markdown tables.
"""


def generate_content(
    content_type: str,
    topic: str,
    tone: str,
    length: str,
    audience: str,
    details: str,
) -> str:
    client = get_client()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=build_prompt(content_type, topic, tone, length, audience, details),
            config=types.GenerateContentConfig(
                temperature=0.78,
                max_output_tokens=8192,
            ),
        )
    except Exception as error:
        raise classify_gemini_error(error) from error
    result = response.text
    if not result:
        raise RuntimeError("Gemini returned an empty response. Try a more specific topic.")
    return result.strip()


def reset_draft() -> None:
    st.session_state["draft"] = ""
    st.session_state["last_meta"] = None


if "draft" not in st.session_state:
    st.session_state["draft"] = ""
if "last_meta" not in st.session_state:
    st.session_state["last_meta"] = None
if "history" not in st.session_state:
    st.session_state["history"] = []


with st.sidebar:
    st.title("Draftly")
    st.caption("AI Content Studio")
    st.divider()
    st.markdown("### Create something worth sharing")
    st.write(
        "Turn a rough idea into audience-ready content with Gemini. "
        "Choose a format, set the feel, and let the first draft do the heavy lifting."
    )
    st.divider()
    st.markdown("#### Studio notes")
    st.markdown(
        "- Be specific about the outcome you want\n"
        "- Add context, examples, or phrases to keep\n"
        "- Treat every draft as a starting point"
    )
    if st.session_state["history"]:
        st.divider()
        st.markdown(f"**{len(st.session_state['history'])} draft(s) this session**")
        if st.button("Clear session history", use_container_width=True):
            st.session_state["history"] = []
            st.session_state["draft"] = ""
            st.session_state["last_meta"] = None
            st.rerun()


st.title("Make your next idea impossible to ignore.")
st.write(
    "Generate scripts, social posts, and SEO content that sound like you — not a template."
)

tabs = st.tabs(["Create", "Draft history"])

with tabs[0]:
    st.markdown("### 01 · Choose your format")
    selected_type = st.radio(
        "Content format",
        list(CONTENT_TYPES.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )
    type_info = CONTENT_TYPES[selected_type]
    st.info(f"{type_info['icon']}  **{selected_type}**  ·  {type_info['description']}")

    with st.form("content_form"):
        st.markdown("### 02 · Shape the brief")
        topic = st.text_input(
            "What should we create?",
            placeholder=type_info["placeholder"],
            help="A clear topic or outcome gives Gemini a much stronger starting point.",
        )
        brief_col, audience_col = st.columns(2)
        with brief_col:
            tone = st.selectbox("Tone", TONES, index=1)
        with audience_col:
            audience = st.text_input(
                "Who is it for?",
                placeholder="e.g. First-time founders",
            )

        detail_col, length_col = st.columns([1.35, 1])
        with detail_col:
            details = st.text_area(
                "Useful context",
                placeholder="Add key points, a brand perspective, a CTA, examples, or anything the draft must include.",
                height=125,
            )
        with length_col:
            length = st.selectbox(
                "Length",
                type_info["lengths"],
                index=type_info["lengths"].index(type_info["default_length"]),
            )
            st.caption("You can always refine the draft after generating it.")

        generate_clicked = st.form_submit_button(
            "Generate draft  →",
            type="primary",
            use_container_width=True,
        )

    if generate_clicked:
        if not topic.strip():
            st.warning("Add a topic first so Draftly has something to work with.")
        else:
            with st.spinner("Draftly is thinking…"):
                try:
                    draft = generate_content(
                        selected_type,
                        topic.strip(),
                        tone,
                        length,
                        audience.strip(),
                        details.strip(),
                    )
                    st.session_state["draft"] = draft
                    st.session_state["last_meta"] = {
                        "type": selected_type,
                        "topic": topic.strip(),
                        "tone": tone,
                        "length": length,
                        "created": datetime.now().strftime("%b %d, %Y · %I:%M %p"),
                    }
                    st.session_state["history"].insert(0, {**st.session_state["last_meta"], "draft": draft})
                except GeminiConfigurationError as error:
                    st.error(str(error))
                except GeminiAuthenticationError as error:
                    st.error(str(error))
                except GeminiQuotaError as error:
                    st.warning(str(error))
                except GeminiServiceError as error:
                    st.error(str(error))
                except Exception:
                    st.error("We couldn't generate that draft. Please try again.")

    if st.session_state["draft"]:
        st.divider()
        meta = st.session_state["last_meta"]
        result_col, action_col = st.columns([3.6, 1])
        with result_col:
            st.markdown("### Your draft")
            st.caption(
                f"{meta['type']}  ·  {meta['tone']}  ·  {meta['length']}  ·  {meta['created']}"
            )
        with action_col:
            st.download_button(
                "Download .txt",
                data=st.session_state["draft"],
                file_name="draftly-content.txt",
                mime="text/plain",
                use_container_width=True,
            )
        st.text_area(
            "Generated content",
            value=st.session_state["draft"],
            height=520,
            label_visibility="collapsed",
        )
        if st.button("Start a new draft", on_click=reset_draft):
            st.rerun()

with tabs[1]:
    st.markdown("### Recent drafts")
    history = st.session_state["history"]
    if not history:
        st.info("Your generated drafts will appear here during this session.")
    else:
        st.caption("History is kept in this browser session and is not saved to a database.")
        for index, item in enumerate(history):
            with st.expander(f"{item['type']} · {item['topic']} · {item['created']}"):
                st.caption(f"{item['tone']} · {item['length']}")
                st.text_area(
                    "Draft",
                    value=item["draft"],
                    height=260,
                    key=f"history_{index}",
                    label_visibility="collapsed",
                )
                st.download_button(
                    "Download this draft",
                    data=item["draft"],
                    file_name=f"draftly-{index + 1}.txt",
                    mime="text/plain",
                    key=f"download_{index}",
                )