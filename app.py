import os
import time
import streamlit as st
import google.genai as genai

# Set Google AI Studio Key directly in Environment
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6IfPm6qG5NQg-bNof6LgYKQ2vzaL0jRHpQM4usGfyTeeA"

# --- Page Configuration ---
st.set_page_config(
    page_title="Draftly | Enterprise AI Content Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Contest-Grade UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 48px;
    }
</style>
""", unsafe_allow_html=True)

# --- Gemini Client Initializer ---
def get_gemini_client():
    return genai.Client()

# --- Advanced Prompt Builder Engine ---
def build_contest_prompt(content_type: str, topic: str, tone: str, length: str, audience: str, details: str, language: str) -> str:
    prompt = f"""
[SYSTEM ROLE: SENIOR CONTENT ARCHITECT & COPYWRITER]
You are Draftly AI Engine v2.5, an enterprise-grade content generation system.
Generate a production-ready, highly engaging piece of content based on the parameters below.

[PARAMETERS]
- Output Format: {content_type}
- Core Topic: {topic}
- Target Audience: {audience or 'General Professional Audience'}
- Tone/Voice: {tone or 'Engaging, Authoritative & Concise'}
- Content Depth: {length}
- Target Language: {language}
"""
    if details:
        prompt += f"\n[ADDITIONAL CONSTRAINTS & CONTEXT]\n{details}\n"

    if content_type == "YouTube Video Script":
        prompt += """
[REQUIRED FORMATTING & STRUCTURE]
1. 💥 3 High-CTR Title Options (Optimized for YouTube Algorithm).
2. 🎣 Hook (0-15 Seconds) with explicit [Visual Cue] & [Audio Cue] directions.
3. 📜 Complete Scene-by-Scene Script Breakdown (Host Narration + Visual Directions).
4. 🚀 High-Converting Outro & Call To Action (CTA).
"""
    elif content_type == "Social Media Post (LinkedIn/Twitter)":
        prompt += """
[REQUIRED FORMATTING & STRUCTURE]
1. 🎯 Pattern Interrupt Hook Line.
2. 📖 Clean, Line-Spaced Body with Actionable Bullet Points.
3. 💬 Engagement Question (Designed to drive comment velocity).
4. 🏷️ 5-8 Relevant & Trending Hashtags.
"""
    elif content_type == "SEO Long-Form Article":
        prompt += """
[REQUIRED FORMATTING & STRUCTURE]
1. 📌 SEO Title & Meta Description (Under 160 characters).
2. 💡 Key Takeaways Box.
3. 📝 Structured Article Body with Proper H2 & H3 Markdown Headings.
4. 🏁 Strategic Conclusion & Next Steps / CTA.
"""
    elif content_type == "Email Newsletter":
        prompt += """
[REQUIRED FORMATTING & STRUCTURE]
1. ✉️ 3 High Open-Rate Subject Lines + Preview Text.
2. ⚡ Personal/Conversational Opening Hook.
3. 📌 Main Value Delivery (Structured into readable sections).
4. 🎯 Clear Single Call-To-Action (CTA) Button text.
"""
    return prompt

# --- App Layout & Header ---
st.markdown('<p class="main-header">⚡ Draftly AI Content Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Topcoder Contest Submission | Enterprise Multi-Format Generator powered by Gemini 2.5 Flash</p>', unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Engine Controls")
    
    content_type = st.selectbox(
        "Content Format",
        [
            "YouTube Video Script",
            "SEO Long-Form Article",
            "Social Media Post (LinkedIn/Twitter)",
            "Email Newsletter"
        ]
    )
    
    tone = st.selectbox(
        "Tone / Brand Voice",
        ["Authoritative & Professional", "Energetic & Viral", "Conversational & Friendly", "Educational & Technical"]
    )
    
    length = st.select_slider(
        "Output Depth",
        options=["Concise", "Standard", "In-depth Comprehensive"]
    )
    
    language = st.selectbox(
        "Target Language",
        ["English", "Hindi", "Hinglish", "Spanish", "French"]
    )
    
    audience = st.text_input("Target Audience", placeholder="e.g. Founders, Content Creators, Developers")

# --- Main Form Inputs ---
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_area(
        "Core Topic / Brief *",
        placeholder="e.g., How to build and scale a SaaS startup using AI tools in 2026...",
        height=140
    )

with col2:
    details = st.text_area(
        "Constraints & Context (Optional)",
        placeholder="e.g., Mention budget constraints, target beginner audience, include 3 specific tool recommendations...",
        height=140
    )

# --- Execution & Generation ---
if st.button("Generate Enterprise Draft 🚀", type="primary"):
    if not topic.strip():
        st.error("⚠️ Please provide a core topic or prompt before executing generation.")
    else:
        with st.spinner("⚡ Executing Gemini 2.5 Flash Pipeline & Structuring Response..."):
            try:
                start_time = time.time()
                client = get_gemini_client()
                
                formatted_prompt = build_contest_prompt(
                    content_type, topic, tone, length, audience, details, language
                )
                
                response = client.models.generate_content(
 model="gemini-1.5-flash",                contents=formatted_prompt
                )
                
                elapsed_time = round(time.time() - start_time, 2)
                
                st.success(f"✅ Generation Complete in {elapsed_time}s!")
                st.divider()
                
                # --- Result Display & Tools ---
                st.markdown("### 📄 Generated Output")
                output_text = response.text
                st.markdown(output_text)
                
                st.divider()
                
                # Download Options for Contest Showcase
                st.download_button(
                    label="📥 Download Draft (.txt)",
                    data=output_text,
                    file_name=f"draftly_{content_type.lower().replace(' ', '_')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ Execution Error: {str(e)}")
                