import json
import time
from scipy.spatial.distance import cosine
from embedding_utils import embed_text  # make sure you have this
import json
import numpy as np

MEMORY_FILE = "memory.json"

def get_relevant_memory(memory, user_input_embedding, top_k=3):
    """Return top-k semantically similar past interactions."""
    interactions = memory.get("interactions", [])
    scored = []

    for item in interactions:
        stored_embedding = item['embedding']
        similarity = 1 - cosine(user_input_embedding, stored_embedding)
        scored.append((similarity, item))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in scored[:top_k]]

def adjust_action_scores(memory, base_scores, user_input_embedding):
    """Bias action scores based on past similar interactions."""
    relevant = get_relevant_memory(memory, user_input_embedding)

    for past in relevant:
        action = past['action']
        if past['success']:
            base_scores[action] = base_scores.get(action, 0) + 0.5
        else:
            base_scores[action] = base_scores.get(action, 0) - 0.5

    return base_scores

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory = {}

    # Set defaults if missing
    memory.setdefault('facts', {})
    memory.setdefault('context', {'last_action': None, 'last_emotion': 'calm', 'turns_since_emotion_hint': 0})
    memory.setdefault('emotions', {'state': 'calm', 'intensity': 0.3})
    memory.setdefault('preferences', {})
    memory.setdefault('feedback', [])
    memory.setdefault("conversation", [])
    memory.setdefault("emotions", {
    "user_state": "neutral",
    "user_intensity": 0.0,
    "leo_state": "neutral",
    "leo_intensity": 0.5
    })
    return memory


def save_memory(memory):
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2, default=convert)

def add_interaction(memory, user_input, action, embedding, response="", success=True, needs_feedback=False):
    """Append a new interaction to the feedback list."""
    interaction = {
        "input": user_input,
        "action": action,
        "embedding": embedding,
        "response": response,
        "success": success,
        "needs_feedback": needs_feedback,
        "timestamp": int(time.time())
    }
    memory.setdefault('feedback', []).append(interaction)
    save_memory(memory)

def record_feedback(memory, user_input, action, embedding, success=True, needs_feedback=False):
    """
    Record the user's input, action taken, and semantic embedding for learning.
    """
    if "feedback" not in memory:
        memory["feedback"] = []

    memory["feedback"].append({
        "input": user_input,
        "action": action,
        "embedding": embedding,
        "success": success,
        "needs_feedback": needs_feedback
    })
