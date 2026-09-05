import os
import time
import logging
import streamlit as st
import google.genai as genai

# Configure Page Layout
st.set_page_config(
    page_title="Draftly AI Content Engine",
    page_icon="⚡",
    layout="wide"
)

# Custom Exceptions
class GeminiError(Exception): pass
class GeminiConfigurationError(GeminiError): pass
class GeminiQuotaError(GeminiError): pass
class GeminiServiceError(GeminiError): pass

def classify_gemini_error(error: Exception) -> GeminiError:
    msg = str(error).lower()
    if any(t in msg for t in ["api key", "unauthorized", "authenticated", "401", "403"]):
        return GeminiConfigurationError("API Key Configuration Error. Please verify key access.")
    if any(t in msg for t in ["quota", "rate limit", "429"]):
        return GeminiQuotaError("API Rate limit exceeded. Please retry in a few moments.")
    return GeminiServiceError("Gemini Engine service unavailable. Check network setup.")

def get_gemini_client() -> genai.Client:
    api_key = "AQ.Ab8RN6K3qTrccvPoTqKIwcaZLqr8CLNvK98VeuXRRfLm5SQCKA"
    if not api_key:
        raise GeminiConfigurationError("API Key missing.")
    return genai.Client(api_key=api_key)

def build_prompt(content_type: str, topic: str, tone: str, length: str, audience: str, details: str) -> str:
    prompt = f"""
[SYSTEM INSTRUCTION: DRAFTLY AI CONTENT ENGINE v2.5]
Generate production-ready content for:
- Format: {content_type}
- Topic: {topic}
- Target Audience: {audience or 'General Audience'}
- Tone: {tone or 'Engaging & Authoritative'}
- Target Depth: {length or 'Standard'}
"""
    if details:
        prompt += f"\n[ADDITIONAL DETAILS & CONSTRAINTS]\n{details}\n"

    if content_type == "YouTube Video Script":
        prompt += """
[REQUIRED OUTPUT STRUCTURE]
1. 3 Viral HIGH-CTR Title Options.
2. Hook (0-15s) with explicit visual [Visual: ...] & verbal cues.
3. Detailed Scene & Beat breakdown with spoken host narration.
4. Outro & High-converting Call To Action (CTA).
"""
    elif content_type == "Social Media Post":
        prompt += """
[REQUIRED OUTPUT STRUCTURE]
1. Pattern Interrupt Hook line.
2. Readable caption body with bullet points & clean spacing.
3. Engagement question for comment drive.
4. 5-8 targeted hashtags.
"""
    else:
        prompt += """
[REQUIRED OUTPUT STRUCTURE]
1. SEO Title & Meta Description.
2. Key Takeaways summary block.
3. Comprehensive H2/H3 body content.
4. Strategic Conclusion & Next Steps CTA.
"""
    return prompt

# Streamlit UI Rendering
st.title("⚡ Draftly AI Content Engine")
st.caption("Topcoder Contest Submission | Powered by Google Gemini 2.5 Flash")

with st.sidebar:
    st.header("⚙️ Output Settings")
    content_type = st.selectbox(
        "Content Format",
        ["YouTube Video Script", "Social Media Post", "SEO Content"]
    )
    tone = st.text_input("Tone/Voice", placeholder="e.g., Energetic, Professional")
    length = st.selectbox("Output Depth", ["Short", "Standard", "In-depth"])
    audience = st.text_input("Target Audience", placeholder="e.g., Content Creators")

topic = st.text_area("Core Topic / Prompt *", placeholder="Enter your topic or narrative brief here...")
details = st.text_area("Additional Context & Constraints (Optional)", placeholder="Add specific requirements or details...")

if st.button("Generate Content 🚀", type="primary"):
    if not topic.strip():
        st.error("Please enter a valid topic before generating.")
    else:
        with st.spinner("Executing Gemini AI Engine pipeline..."):
            try:
                client = get_gemini_client()
                formatted_prompt = build_prompt(content_type, topic, tone, length, audience, details)
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=formatted_prompt
                )
                
                st.success("Generation Complete!")
                st.markdown("### Output Result")
                st.markdown(response.text)
                
            except Exception as e:
                classified_err = classify_gemini_error(e)
                st.error(f"Error: {str(classified_err)}")
                