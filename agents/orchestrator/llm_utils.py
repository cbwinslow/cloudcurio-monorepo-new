import os
import google.generativeai as genai
import sys
from typing import Optional # Import Optional

PROMPT_DIR = "prompts/gemini" # Assuming Gemini prompts for now

def load_prompt_template(template_name: str) -> str:
    """Loads a prompt template from the prompts directory."""
    try:
        with open(os.path.join(PROMPT_DIR, template_name), 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Prompt template {template_name} not found in {PROMPT_DIR}.", file=sys.stderr)
        sys.exit(1)

def generate_gemini_response(prompt: str, api_key: Optional[str] = None) -> str:
    """Generates a response from the Gemini API."""
    if api_key is None:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    if not api_key:
        print("GOOGLE_GEMINI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Use gemini-1.5-flash as default

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating Gemini response: {e}", file=sys.stderr)
        sys.exit(1)

# You can add similar functions for OpenRouter if needed
# def generate_openrouter_response(prompt: str, api_key: Optional[str] = None) -> str:
#     pass
