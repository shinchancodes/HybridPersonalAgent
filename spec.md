## Overview & OutcomesVision: 
- Build a simulated group chat application where an AI orchestrates interactions between a user (Alex) and three distinct virtual personalities (Bob, Annie, Cindy).
- The system dynamically translates casual scheduling dialogue into a mathematical graph network to proactively resolve calendar conflicts.

## Success Metrics:
- 100% precision in extracting event entities (Date, Time, Person, Activity) from chat strings.
- Graph nodes and edges update deterministically within 1 second of text submission.
- The reasoning agent flags 100% of overlapping time frames or double-bookings.

## Scope & FeaturesIn-Scope:
- Streamlit Chat Interface: A cohesive UI displaying a group message thread.
- A selector or automated prompt routine allows Alex to prompt responses from Bob, Annie, or Cindy.
- Graph Extraction Agent: An LLM-backed utility that parses the chat history for planned commitments and maps them to a NetworkX graph.- Visual Knowledge Graph: A live-rendered network visualization displaying nodes (People, Events, Times) and their structural relationships.
- Asynchronous Reasoning Agent: A background processor that scans the network topology for temporal overlaps or conflicting geographic locations.
- Out-of-Scope:
Persistent calendar synchronization with external production providers (e.g., Google Calendar API, Microsoft Outlook).
Multi-user production deployment over standard user auth protocols.
Voice-to-text or localized native push notifications.

## User Scenarios & BehaviorUser Stories:
- As Alex, I want to chat with Annie about lunch tomorrow at 1:00 PM and Bob about a meeting at the same time so that the system warns me of the overlap before I finalize plans.
- As Alex, I want to look at a visual graph diagram so that I can clearly see which person is tied to which calendar commitment.
- User Flows:
  - Adding a Event: Alex types: "Hey Annie, let's grab coffee Friday at 3 PM." &rarr; Message posts to Streamlit view &rarr; Graph Builder Agent extracts variables &rarr; NetworkX graph draws new nodes: [Annie], [Coffee], [Friday 3:00 PM] &rarr; Graph visualizer redraws.Conflict Detection: Alex types: "Bob, let's do a sync this Friday at 3 PM." &rarr; Message posts &rarr; Graph updates &rarr; Reasoning agent discovers that Friday 3:00 PM has connections to two distinct event blocks &rarr; Streamlit sidebar flashes an amber alert: "Conflict Detected: Double-booked with Annie and Bob on Friday at 3:00 PM!"

## Constraints & DependenciesTech Stack:
- Frontend & Layout:
    - Streamlit for chat layouts and component state.
    - Graph Engine: NetworkX for programmatic graph generation.
    - Visualization: matplotlib or streamlit-aglgraph/pyvis for interactive node manipulation.
    - Agent Orchestration: LangChain or LangGraph to coordinate memory across personas and the background extractor.- Core LLM: Local Gemma **(google/gemma-4-E2B-it)** for entity extraction.
    - Enterprise/Design Constraints:
        - The single-page layout must stay strictly divided into a Chat Panel (left) and a Knowledge Graph/Alert Panel (right).
        - The execution of the conflict agent must not block user keystrokes or UI interactions.

## Technical Decisions & Architecture Principles:
- Single-Source-of-Truth Graph:
    - The Streamlit session state stores a single master NetworkX object.
    - The UI elements and reasoning agents rely entirely on this model.
- Deterministic Schema Extraction: 
    - The entity extractor enforces a strict JSON validation schema to prevent format variances.
- Architecture & Edge Cases:
    - Edge Case (Relative Time Mapping): Expressions like "tomorrow" or "next Monday" require anchoring against a fixed reference date token.
    - The application will track a simulated CURRENT_DATE field in the UI header.
    - Edge Case (Rescheduling):
        - If Alex says "Let's move our Tuesday meeting to Wednesday," the graph agent must drop the old relationship edges before painting the new coordinates.

## Verification & Acceptance Criteria Tests:
- Critical Path 1:
    - Submit a multi-turn dialogue exchange to verify that distinct personas maintain their unique communication tone (e.g., Annie is formal, Bob uses short sentences).
- Critical Path 2: Feed a 10-message conversational string containing complex dates to verify the extraction performance of the underlying pipeline.
- Acceptance Criteria:
    - The chat interface renders clear message profiles differentiating Alex, Bob, Annie, and Cindy.
    - The application adds nodes and edges to the visual graph window automatically when text instructions are sent
    - The evaluation script lists a conflict warning immediately whenever an overlap event occurs.