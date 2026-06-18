import streamlit as st
import networkx as nx

from config import CURRENT_DATE, PERSONAS
from agents.persona_agent import get_reply
from agents.extraction_agent import extract

st.set_page_config(
    page_title="Group Chat Scheduler",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Per-speaker visual identity ──────────────────────────────────────────────
SPEAKER_META: dict[str, dict] = {
    "Alex":  {"color": "#7B5EA7", "bg": "#dce8ff", "align": "right"},
    "Bob":   {"color": "#4A90D9", "bg": "#f0f2f6", "align": "left"},
    "Annie": {"color": "#5CB85C", "bg": "#f0f2f6", "align": "left"},
    "Cindy": {"color": "#E8940A", "bg": "#f0f2f6", "align": "left"},
}

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }

    .dm-bubble {
        padding: 8px 13px;
        border-radius: 14px;
        margin-bottom: 5px;
        max-width: 78%;
        font-size: 0.92rem;
        line-height: 1.5;
        word-wrap: break-word;
        display: inline-block;
    }
    .bubble-row-left  { text-align: left;  width: 100%; }
    .bubble-row-right { text-align: right; width: 100%; }

    .speaker-name {
        font-size: 0.7rem;
        font-weight: 700;
        margin-bottom: 2px;
        display: block;
    }
    .date-badge {
        background: #e8f4f8;
        border: 1px solid #b8d8e8;
        border-radius: 8px;
        padding: 2px 10px;
        font-size: 0.72rem;
        color: #2c7fa8;
        margin-left: 10px;
        vertical-align: middle;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session state initialisation ─────────────────────────────────────────────
def _init_state() -> None:
    defaults: dict = {
        "conversations": {p: [] for p in PERSONAS},
        "graph": nx.DiGraph(),
        "conflicts": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ── Helper: render one DM bubble ─────────────────────────────────────────────
def render_bubble(role: str, content: str) -> None:
    meta = SPEAKER_META.get(role, {"color": "#888", "bg": "#eee", "align": "left"})
    row_class = "bubble-row-right" if meta["align"] == "right" else "bubble-row-left"
    st.markdown(
        f"""
        <div class="{row_class}">
            <span class="speaker-name" style="color:{meta['color']};">{role}</span>
            <span class="dm-bubble" style="background:{meta['bg']};">{content}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Two-panel layout ─────────────────────────────────────────────────────────
col_chat, col_graph = st.columns([55, 45])

# ── LEFT: DM conversation panel ──────────────────────────────────────────────
with col_chat:
    st.markdown(
        f'<h3 style="margin-bottom:0.5rem;">Messages'
        f'<span class="date-badge">Today: {CURRENT_DATE.strftime("%A, %B %d %Y")}</span>'
        f"</h3>",
        unsafe_allow_html=True,
    )

    tabs = st.tabs(PERSONAS)

    for tab, persona in zip(tabs, PERSONAS):
        with tab:
            thread = st.session_state["conversations"][persona]

            # Scrollable message thread
            chat_area = st.container(height=440, border=False)
            with chat_area:
                if not thread:
                    st.caption(f"No messages yet — say something to {persona}.")
                for msg in thread:
                    render_bubble(msg["role"], msg["content"])

            # Per-conversation input form
            with st.form(key=f"form_{persona}", clear_on_submit=True):
                user_input = st.text_input(
                    "Message",
                    placeholder=f"Message {persona}…",
                    label_visibility="collapsed",
                    key=f"input_{persona}",
                )
                send = st.form_submit_button("Send", use_container_width=True)

            if send and user_input.strip():
                msg_text = user_input.strip()

                with st.spinner(f"{persona} is typing…"):
                    _, reply = get_reply(persona, thread, msg_text)

                # Append both turns together after inference so the history
                # passed to get_reply never includes the current message.
                thread.append({"role": "Alex", "content": msg_text})
                thread.append({"role": persona, "content": reply})

                # Extract scheduling entities from the latest exchange and
                # update the shared knowledge graph (no-op until Phase 5).
                extract(persona, thread)

                # Phase 6: conflict_agent.scan() called here
                st.rerun()

# ── RIGHT: Unified graph + alert panel ───────────────────────────────────────
with col_graph:
    st.markdown("### Knowledge Graph")

    graph_placeholder = st.empty()
    graph_placeholder.info(
        "The unified knowledge graph will render here once scheduling "
        "events are detected across any conversation."
    )

    st.divider()

    st.markdown("#### Conflict Alerts")
    if st.session_state["conflicts"]:
        for conflict in st.session_state["conflicts"]:
            st.warning(conflict)
    else:
        st.success("No conflicts detected.")
