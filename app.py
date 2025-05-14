import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import re

# Load environment variables from .env
load_dotenv()
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_DEPLOYMENT")

PROMPT_LIBRARY_FILE = "prompts.json"

# --- Custom Branding ---
CUSTOM_LOGO = "https://upload.wikimedia.org/wikipedia/commons/9/90/Mercedes-Logo.svg"
PRIMARY_COLOR = "#6c63ff"
LIGHT_CARD = "#f8f9fa"
LIGHT_TEXT = "#222"

st.set_page_config(page_title="PromptCraft", layout="wide", page_icon=CUSTOM_LOGO)

st.markdown(f"""
    <style>
    @keyframes spinY {{
        0% {{ transform: rotateY(0deg); }}
        100% {{ transform: rotateY(360deg); }}
    }}
    .main-title {{ font-size:2.2rem; font-weight:700; margin-bottom:0.2em; color:{PRIMARY_COLOR}; display:flex; align-items:center; }}
    .main-title img {{ margin-right: 16px; border-radius: 50%; background: #fff; box-shadow: 0 2px 8px #ececec; animation: spinY 2.5s linear infinite; transform-origin: 50% 50%; }}
    .subtitle {{ color:{PRIMARY_COLOR}; font-size:1.1rem; margin-bottom:1em; }}
    .prompt-card {{ background: {LIGHT_CARD}; border-radius: 10px; padding: 1.2em 1em; margin-bottom: 1em; box-shadow: 0 2px 8px #ececec; color:{LIGHT_TEXT}; }}
    .output-card {{ background: #e8f5e9; border-radius: 10px; padding: 1em; margin-top: 1em; color:#222; }}
    .history-card {{ background: #f1f8ff; border-radius: 8px; padding: 0.7em 1em; margin-bottom: 0.5em; color:{LIGHT_TEXT}; }}
    .selected-history {{ border: 2px solid {PRIMARY_COLOR}; }}
    .stButton>button {{ background-color: {PRIMARY_COLOR}; color: #fff; border-radius: 6px; }}
    .stButton>button:hover {{ background-color: #5548c8; }}
    .stTextInput>div>div>input {{ background: #fff; color: {LIGHT_TEXT}; }}
    .stTextArea textarea {{ background: #fff; color: {LIGHT_TEXT}; }}
    .st-bb {{ color: {PRIMARY_COLOR}; }}
    .stMarkdown a {{ color: {PRIMARY_COLOR}; }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="main-title"><img src="{CUSTOM_LOGO}" width="48">PromptCraft: Prompt Refinement Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Refine, iterate, and perfect your LLM prompts with a professional workflow.</div>', unsafe_allow_html=True)

# --- Helper: Detect if more info is needed ---
def needs_more_info(response):
    triggers = [
        "please provide more details",
        "can you clarify",
        "input required",
        "please specify",
        "need more information",
        "could you elaborate"
    ]
    resp = response.lower()
    return any(trigger in resp for trigger in triggers)

# --- Structured Input Fields ---
def get_structured_fields():
    return [
        {"label": "Objective", "placeholder": "What are you trying to achieve?"},
        {"label": "Target Audience", "placeholder": "Who is this for?"},
        {"label": "Tone of Voice", "placeholder": "Formal, Friendly, Technical, etc."}
    ]

def generate_from_structured_input(fields):
    # Compose a prompt from the structured fields
    prompt = f"Objective: {fields['Objective']}\nAudience: {fields['Target Audience']}\nTone: {fields['Tone of Voice']}\n"
    return refine_prompt(prompt)

# Utility: Load prompt library
def load_prompt_library():
    if os.path.exists(PROMPT_LIBRARY_FILE):
        with open(PROMPT_LIBRARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_prompt_library(library):
    with open(PROMPT_LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(library, f, indent=2, default=str)

def refine_prompt(raw_prompt):
    system_prompt = (
        "You are a prompt engineering expert. "
        "Given a raw prompt, do ALL of the following: "
        "1. Extract the user's intent and any entities. "
        "2. Clarify ambiguities or missing context. "
        "3. Structure the prompt with persona, tone, and output format. "
        "4. Make it more specific and actionable. "
        "If any part of the prompt could be a user-supplied value, always use the {{variable}} format (e.g., {{audience}}, {{topic}}, {{goal}}, etc.). "
        "Return ONLY the improved prompt, no commentary."
    )
    try:
        with st.spinner("✨ Refining your prompt..."):
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_prompt}
                ]
            )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error refining prompt: {str(e)}]"

def get_prompt_output(refined_prompt, user_inputs):
    # Fill in variables in the prompt
    prompt_filled = refined_prompt
    for var, val in user_inputs.items():
        prompt_filled = prompt_filled.replace(f"{{{{{var}}}}}", val)
    # System prompt to ensure the LLM performs the task, not a guide
    system_prompt = (
        "You are an expert assistant. Perform the user's request as specified in the prompt. "
        "Do not explain, do not guide, just generate the output as requested."
    )
    try:
        with st.spinner("🚀 Generating output..."):
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_filled}
                ]
            )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error getting output: {str(e)}]"

def extract_variables(prompt):
    # Find all {{variable}} in the prompt
    return re.findall(r"{{(.*?)}}", prompt)

# Initialize session state
if 'prompt_history' not in st.session_state:
    st.session_state.prompt_history = []
if 'current_version' not in st.session_state:
    st.session_state.current_version = 0
if 'saved_prompts' not in st.session_state:
    st.session_state.saved_prompts = load_prompt_library()
if 'last_output' not in st.session_state:
    st.session_state.last_output = ""
if 'last_user_inputs' not in st.session_state:
    st.session_state.last_user_inputs = {}

# Sidebar: Show How to Use instructions
with st.sidebar:
    st.header("ℹ️ How to Use PromptCraft")
    st.markdown('''
1. **Enter your raw prompt** in the "Raw Prompt" box and click **Auto-Refine**.
2. **Edit the refined prompt** as needed.
3. If the app asks for more details, fill out the structured form.
4. In the **Generate Output** tab, fill any required variables and click **Generate Output** to see the result.
5. Use the **Prompt Library** tab to save and reuse your best prompts.
6. The **History** tab lets you revisit and restore previous prompt versions.
''')
    st.markdown('---')
    st.markdown('**Tip:** The Mercedes-Benz logo above spins for style!')

# --- Main Layout ---
tabs = st.tabs(["✏️ Refine", "📝 Output", "📚 Library", "🕒 History"])

# --- Refine Tab ---
with tabs[0]:
    st.markdown('<div class="prompt-card">', unsafe_allow_html=True)
    st.subheader("Raw Prompt", help="Paste or write your initial prompt here.")
    raw_prompt = st.text_area("Raw Prompt", key="raw_prompt", height=150, help="This is your starting point.")
    refine_clicked = st.button("✨ Auto-Refine", type="primary", help="Let the AI improve your prompt.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="prompt-card">', unsafe_allow_html=True)
    st.subheader("Refined Prompt", help="Edit and perfect the AI-refined prompt.")
    show_structured_form = False
    structured_response = None
    if st.session_state.prompt_history:
        refined_prompt = st.text_area(
            "Refined Prompt", value=st.session_state.prompt_history[st.session_state.current_version]["refined"], key="refined_prompt", height=150, help="You can further edit the refined prompt.")
        # Detect if more info is needed
        if needs_more_info(refined_prompt):
            show_structured_form = True
    else:
        refined_prompt = st.text_area("Refined Prompt", value="", key="refined_prompt", height=150, help="You can further edit the refined prompt.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Structured Input Form (for refinement) ---
    if show_structured_form:
        st.info("Please provide more details:")
        structured_fields = get_structured_fields()
        structured_answers = {}
        with st.form("structured_input_form", clear_on_submit=False):
            for field in structured_fields:
                structured_answers[field["label"]] = st.text_input(field["label"], placeholder=field["placeholder"])
            submitted = st.form_submit_button("Submit & Generate")
        if submitted and all(structured_answers.values()):
            with st.spinner("Generating refined prompt from your answers..."):
                structured_response = generate_from_structured_input(structured_answers)
            # Add to history and update current version
            new_version = {
                "timestamp": datetime.now().isoformat(),
                "raw": raw_prompt,
                "refined": structured_response
            }
            st.session_state.prompt_history.append(new_version)
            st.session_state.current_version = len(st.session_state.prompt_history) - 1
            st.rerun()

# --- Output Tab ---
with tabs[1]:
    st.markdown('<div class="prompt-card">', unsafe_allow_html=True)
    st.subheader("Generate Output", help="Test your refined prompt with or without variables.")
    if st.session_state.prompt_history:
        refined_prompt = st.session_state.prompt_history[st.session_state.current_version]["refined"]
    else:
        refined_prompt = ""
    variables = extract_variables(refined_prompt)
    user_inputs = {}
    if variables:
        for var in variables:
            user_inputs[var] = st.text_input(f"{var}", value=st.session_state.last_user_inputs.get(var, ""), key=f"var_{var}_{st.session_state.current_version}")
    generate_clicked = st.button("🚀 Generate Output", key=f"generate_output_{st.session_state.current_version}")
    output = ""
    if generate_clicked:
        output = get_prompt_output(refined_prompt, user_inputs)
        st.session_state.last_output = output
        st.session_state.last_user_inputs = user_inputs
    elif st.session_state.last_output and st.session_state.last_user_inputs == user_inputs:
        output = st.session_state.last_output
    if output and needs_more_info(output):
        st.info("More information required to generate a better output:")
        structured_fields = get_structured_fields()
        structured_answers = {}
        with st.form("structured_output_form", clear_on_submit=False):
            for field in structured_fields:
                structured_answers[field["label"]] = st.text_input(field["label"], placeholder=field["placeholder"])
            submitted = st.form_submit_button("Submit & Generate Output")
        if submitted and all(structured_answers.values()):
            with st.spinner("Generating output from your answers..."):
                prompt = f"Objective: {structured_answers['Objective']}\nAudience: {structured_answers['Target Audience']}\nTone: {structured_answers['Tone of Voice']}\n"
                output = get_prompt_output(prompt, {})
                st.session_state.last_output = output
        if output:
            st.markdown('<div class="output-card">', unsafe_allow_html=True)
            st.markdown("**Model Output:**")
            st.success(output)
            st.markdown('</div>', unsafe_allow_html=True)
    elif output:
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        st.markdown("**Model Output:**")
        st.success(output)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Library Tab ---
with tabs[2]:
    st.markdown('<div class="prompt-card">', unsafe_allow_html=True)
    st.subheader("Prompt Library", help="Save, search, and load your favorite prompts.")
    if st.session_state.prompt_history:
        save_title = st.text_input("Save current refined prompt as:", key="save_title")
        save_tags = st.text_input("Tags (comma separated):", key="save_tags")
        if st.button("💾 Save to Library"):
            st.session_state.saved_prompts.append({
                "title": save_title or f"Prompt {len(st.session_state.saved_prompts)+1}",
                "prompt": st.session_state.prompt_history[st.session_state.current_version]["refined"],
                "tags": [t.strip() for t in save_tags.split(",") if t.strip()],
                "timestamp": datetime.now().isoformat()
            })
            save_prompt_library(st.session_state.saved_prompts)
            st.success("Prompt saved to library!")
    st.markdown("---")
    st.markdown("### Saved Prompts")
    for idx, saved in enumerate(reversed(st.session_state.saved_prompts)):
        st.markdown(f"**{saved.get('title', 'Untitled')}**  ")
        st.code(saved["prompt"])
        st.markdown(f"Tags: {', '.join(saved.get('tags', []))}")
        if st.button(f"Load to Refiner", key=f"load_lib_{idx}"):
            st.session_state.prompt_history.append({
                "timestamp": datetime.now().isoformat(),
                "raw": saved["prompt"],
                "refined": saved["prompt"]
            })
            st.session_state.current_version = len(st.session_state.prompt_history) - 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- History Tab ---
with tabs[3]:
    st.markdown('<div class="prompt-card">', unsafe_allow_html=True)
    st.subheader("Prompt Version History", help="Browse and restore previous prompt versions.")
    for idx, version in reversed(list(enumerate(st.session_state.prompt_history))):
        selected = idx == st.session_state.current_version
        card_class = "history-card selected-history" if selected else "history-card"
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        label = f"Version {idx+1} ({version['timestamp'].split('T')[0]})"
        if st.button(f"Load {label}", key=f"load_{idx}"):
            st.session_state.current_version = idx
            st.rerun()
        st.code(f"Raw: {version['raw']}\n---\nRefined: {version['refined']}", language="markdown")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Refinement Logic ---
if refine_clicked and raw_prompt:
    refined = refine_prompt(raw_prompt)
    new_version = {
        "timestamp": datetime.now().isoformat(),
        "raw": raw_prompt,
        "refined": refined
    }
    st.session_state.prompt_history.append(new_version)
    st.session_state.current_version = len(st.session_state.prompt_history) - 1
    st.rerun()