import streamlit as st
import wikipedia
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import base64
import io

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Proton Suite", page_icon="⚛️", layout="wide")

st.markdown("""
    <style>
        [data-testid='collapsedControl'] {display: none;}
        .stTextInput > div > div > input {color: #0066cc; border: 2px solid #0066cc; border-radius: 25px; padding-left: 20px;}
        h1 {color: #0066cc; text-align: center; font-weight: 800; margin-bottom: 0px;}
        div[data-testid="stPopover"] > button {
            border-radius: 12px; background-color: #f0f2f6; color: #0066cc; border: 1px solid #0066cc; font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE ---
image_input, vision_btn = None, False
wiki_wiki = wikipediaapi.Wikipedia(user_agent='ProtonSuite/1.2', language='en')

gemini_model = None

if "GENAI_API_KEY" in st.secrets and "OPENAI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
    openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Auto-Detect the best working Gemini Model
    best_model = 'gemini-1.5-flash'
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                best_model = m.name
                break
    except Exception:
        pass
        
    gemini_model = genai.GenerativeModel(best_model)
else:
    st.error("API Keys missing in secrets.toml!")

# --- 3. UI LAYOUT ---
st.markdown("<h1>⚛️ Proton AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-bottom: 30px;'>Universal Research Suite</p>", unsafe_allow_html=True)

ai_brain = st.segmented_control("Engine:", ["Proton Core", "GPT-5.4-Mini"], default="Proton Core")
topic = st.text_input("", placeholder="Ask Proton anything...", label_visibility="collapsed")

t_col1, t_col2, t_col3, t_col4 = st.columns([1, 1, 1, 4])
with t_col1:
    with st.popover("➕ Visual"):
        mode = st.radio("Mode:", ["Camera", "Upload"], horizontal=True)
        if mode == "Camera":
            image_input = st.camera_input("Scan Document or Problem")
        else:
            image_input = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])
        if image_input: 
            vision_btn = st.button("✨ Analyze Now")

with t_col2:
    with st.popover("📚 Source"):
        source_pref = st.radio("Primary Source:", ["Smart Search (Web)", "Proton Database (Wiki)"])
        deep_think = st.toggle("Enable Deep Research", value=True)

with t_col3:
    deep_dive = st.checkbox("🎯 Deep Dive Mode")

# --- 4. LOGIC ---
def get_ai_response(prompt, img=None):
    try:
        if "GPT" in ai_brain:
            if img:
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                res = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                        ]
                    }]
                )
                return res.choices[0].message.content
            else:
                res = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                return res.choices[0].message.content
        else:
            if img:
                res = gemini_model.generate_content([prompt, img])
            else:
                res = gemini_model.generate_content(prompt)
            return res.text
    except Exception as e:
        return f"⚠️ Engine Error: {e}. Try switching engines at the top."

if image_input and vision_btn:
    with st.spinner("Proton is analyzing..."):
        img = Image.open(image_input)
        result = get_ai_response("Analyze this image. If it is a problem, solve it step-by-step. If it is a document or diagram, explain it clearly with key insights.", img)
        st.markdown(result)

elif topic:
    with st.spinner(f"Querying {ai_brain}..."):
        context = ""
        if "Database" in source_pref:
            page = wiki_wiki.page(topic)
            if page.exists(): 
                context = f"Wiki Summary: {page.summary[:1000]}"
        
        full_prompt = f"Topic: {topic}\n{context}\nProvide a highly accurate, professional, and clear explanation."
        if deep_dive: 
            full_prompt += "\nInclude 3 thought-provoking follow-up questions or practical exercises to test understanding."
        
        st.markdown(get_ai_response(full_prompt))

st.divider()
st.caption("© 2026 Proton Research Labs | Universal Mode Enabled")
