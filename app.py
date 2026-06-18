import streamlit as st
import networkx as nx

from config import CURRENT_DATE, PERSONAS

st.set_page_config(
    page_title="Group Chat Scheduler",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Per-speaker visual identity ──────────────────────────────────────────────
SPEAKER_META: dict[str, dict] = {
    "Alex":  {"color": "#7B5EA7", "align": "right"},
    "Bob":   {"color": "#4A90D9", "align": "left"},
    "Annie": {"color": "#5CB85C", "align": "left"},
    "Cindy": {"color": "#E8940A", "align": "left"},
}

st.markdown(
    """
    <style>
    /* Remove default top padding so the two panels start at the same height */
    .block-container { padding-top: 1.5rem; }

    .chat-bubble {
        padding: 8px 12px;
        border-radius: 12px;
        margin-bottom: 6px;
        max-width: 85%;
        font-size: 0.92rem;
        line-height: 1.45;
        word-wrap: break-word;
    }
    .bubble-left  { background: #f0f2f6; margin-right: auto; }
    .bubble-right { background: #dce8ff; margin-left: auto; text-align: right; }

    .speaker-label {
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 2px;
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
    /* Tighten the radio row */
    div[data-testid="stRadio"] > div { gap: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session state initialisation ─────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "messages": [],
        "graph": nx.DiGraph(),
        "conflicts": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ── Helper: render one chat bubble ───────────────────────────────────────────
def render_bubble(role: str, content: str) -> None:
    meta = SPEAKER_META.get(role, {"color": "#888", "align": "left"})
    css_class = "bubble-right" if meta["align"] == "right" else "bubble-left"
    st.markdown(
        f"""
        <div class="chat-bubble {css_class}">
            <div class="speaker-label" style="color:{meta['color']};">{role}</div>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Two-panel layout ─────────────────────────────────────────────────────────
col_chat, col_graph = st.columns([55, 45])

# ── LEFT: Chat panel ─────────────────────────────────────────────────────────
with col_chat:
    st.markdown(
        f'<h3 style="margin-bottom:0.25rem;">Group Chat'
        f'<span class="date-badge">Today: {CURRENT_DATE.strftime("%A, %B %d %Y")}</span>'
        f"</h3>",
        unsafe_allow_html=True,
    )

    selected_persona = st.radio(
        "Reply from:",
        options=["Auto"] + PERSONAS,
        horizontal=True,
        key="persona_selector",
    )

    st.divider()

    # Scrollable message thread
    chat_area = st.container(height=460, border=False)
    with chat_area:
        if not st.session_state["messages"]:
            st.caption("No messages yet — type below to start the conversation.")
        for msg in st.session_state["messages"]:
            render_bubble(msg["role"], msg["content"])

    # Message input form (clear_on_submit keeps the field tidy)
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Message",
            placeholder="Type a message as Alex…",
            label_visibility="collapsed",
        )
        send = st.form_submit_button("Send", use_container_width=True)

    if send and user_input.strip():
        st.session_state["messages"].append(
            {"role": "Alex", "content": user_input.strip()}
        )
        # Phase 3: persona_agent.get_reply() called here
        # Phase 4: extraction_agent.extract() called here
        # Phase 6: conflict_agent.scan() called here
        st.rerun()

# ── RIGHT: Graph + alert panel ───────────────────────────────────────────────
with col_graph:
    st.markdown("### Knowledge Graph")

    graph_placeholder = st.empty()
    graph_placeholder.info(
        "The knowledge graph will render here automatically once scheduling "
        "events are detected in the conversation."
    )

    st.divider()

    st.markdown("#### Conflict Alerts")
    if st.session_state["conflicts"]:
        for conflict in st.session_state["conflicts"]:
            st.warning(conflict)
    else:
        st.success("No conflicts detected.")
