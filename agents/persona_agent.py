from __future__ import annotations

import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline as hf_pipeline

from config import MODEL_ID, PERSONA_SYSTEM_PROMPTS, CONTEXT_WINDOW, PERSONAS


@st.cache_resource(show_spinner="Loading language model…")
def _load_pipe():
    """Load Gemma once and cache it for the entire Streamlit session."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype="auto",
    )
    pipe = hf_pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        repetition_penalty=1.1,
        return_full_text=False,  # return only generated tokens, not the prompt
    )
    return pipe, tokenizer


def _pick_persona(selected: str, messages: list[dict]) -> str:
    """Resolve 'Auto' to a concrete persona via round-robin over recent replies."""
    if selected != "Auto":
        return selected
    last = next((m["role"] for m in reversed(messages) if m["role"] != "Alex"), None)
    if last is None or last not in PERSONAS:
        return PERSONAS[0]
    return PERSONAS[(PERSONAS.index(last) + 1) % len(PERSONAS)]


def _build_prompt(persona: str, messages: list[dict], current_message: str, tokenizer) -> str:
    """
    Format the conversation as a single-turn Gemma chat prompt.

    The system context and rolling history are embedded in the user turn so
    the model receives full scheduling context without needing multi-turn
    formatting (which can confuse smaller Gemma variants).
    """
    system_text = (
        f"{PERSONA_SYSTEM_PROMPTS[persona]}\n\n"
        "You are participating in a group scheduling chat with Alex, Bob, Annie, "
        "and Cindy. Reply ONLY as your character in 1-3 sentences. "
        "Do NOT prefix your reply with your own name."
    )

    # Build a readable history block from the rolling context window
    history_lines: list[str] = []
    for msg in messages[-CONTEXT_WINDOW:]:
        history_lines.append(f"{msg['role']}: {msg['content']}")

    history_block = "\n".join(history_lines)
    if history_block:
        user_content = (
            f"{system_text}\n\n"
            f"Conversation so far:\n{history_block}\n\n"
            f"Alex: {current_message}"
        )
    else:
        user_content = f"{system_text}\n\nAlex: {current_message}"

    chat_messages = [{"role": "user", "content": user_content}]

    return tokenizer.apply_chat_template(
        chat_messages,
        tokenize=False,
        add_generation_prompt=True,
    )


def _clean_reply(raw: str, persona: str) -> str:
    """Strip any leading 'PersonaName: ' the model might hallucinate."""
    text = raw.strip()
    prefix = f"{persona}:"
    if text.lower().startswith(prefix.lower()):
        text = text[len(prefix):].strip()
    # Also strip <end_of_turn> or similar Gemma artifacts
    for token in ("<end_of_turn>", "<eos>", "<|end|>"):
        text = text.replace(token, "").strip()
    return text


def get_reply(
    selected_persona: str,
    messages: list[dict],
    current_message: str,
) -> tuple[str, str]:
    """
    Generate a persona reply to Alex's latest message.

    Returns:
        (persona_name, reply_text)
    """
    pipe, tokenizer = _load_pipe()
    persona = _pick_persona(selected_persona, messages)
    prompt = _build_prompt(persona, messages, current_message, tokenizer)

    try:
        output = pipe(prompt)
        raw = output[0]["generated_text"]
        reply = _clean_reply(raw, persona)
    except Exception as exc:  # noqa: BLE001
        reply = f"[Model error: {exc}]"

    return persona, reply
