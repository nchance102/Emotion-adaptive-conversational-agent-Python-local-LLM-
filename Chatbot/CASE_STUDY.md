Leo – Emotion-Adaptive Conversational Agent

Technical Case Study

1. Problem

Most conversational agents infer emotion from a single message and immediately react.
This produces unstable and often inappropriate behavior because human emotion is expressed gradually across multiple turns.

The goal of Leo is to model emotional state across a rolling conversation window and select an agent response strategy that complements the user’s emotional 
trajectory rather than simply mirroring it.

2. Design

Leo separates three concerns:

User emotional state

Tracked across recent turns using weighted history.

Each message contributes partial emotional evidence.

Newer messages are weighted more strongly.

Agent emotional stance

The agent maintains its own emotional posture (calm, encouraging, steady, etc.).

The stance is derived from the user’s emotional trend, not copied from it.

The agent complements distress with grounding behavior instead of amplifying it.

Action selection

The agent selects a behavioral mode (empathy, advice, steps, questioning, minimal response).

Actions are chosen using a scored policy layer rather than fixed rules.

3. Architecture

memory

Persistent conversation state, emotion history, feedback, and context.

emotions

Detects emotional signals per message.

Aggregates emotion over a rolling window.

Maintains both user emotion and agent stance.

decision

Scores available actions using emotional state, history, and learning signals.

actions

Instruction templates defining behavior constraints for each action.

llm

Handles prompt execution through a local LLM backend (Ollama).

4. Example

User conversation:

I’ve been really stressed with school lately
It just feels like everything is piling up
I don’t know if I can keep up

Leo’s emotion model accumulates stress across multiple turns rather than reacting to a single message.
The agent selects a grounding and supportive stance and prioritizes reflective and stabilizing actions over problem-solving.

As emotional intensity remains high, the decision policy continues to favor emotional validation and gentle guidance instead of rapid advice or task breakdowns.
