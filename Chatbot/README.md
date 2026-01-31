Leonardo(Leo) — Emotion-Adaptive Conversational Agent

Leo is a Python-based conversational agent that tracks a user’s emotional state across multiple turns and selects a complementary emotional response strategy rather than simply mirroring sentiment.
This project focuses on agent cognition and decision architecture, not UI.

What Leo demonstrates
Rolling emotional trend modeling over recent conversation turns
Separate modeling of user emotion and agent emotional stance
Complementary emotional response selection
Scored action-selection policy layer
Instruction-driven LLM prompting
Persistent memory and conversation state
Local LLM backend (Ollama)

Why this project exists
Most chatbots respond only to the current message.
Leo maintains emotional context across a conversation and adapts how it responds as the user’s emotional trajectory changes.

Quick demo

Requirements
Python 3.10+
Ollama running locally

Run
python main.py
Then chat directly with Leo in the terminal.

Try:
“I’ve been really stressed with school lately.”
“It just feels like everything is piling up.”

Observe how Leo’s emotional stance and response strategy evolve across turns.

Backend
Python
Ollama (local LLM)
Modular agent architecture (memory, emotions, decision policy, actions)




