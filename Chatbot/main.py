from memory import load_memory, save_memory
from emotions import  update_user_emotion, apply_emotional_decay, get_emotion_hint, blend_emotion_hint
from decision import decide_action_with_learning
from actions import ACTION_DICT
from llm import ask_llm
import memory
from persona import persona
from embedding_utils import embed_text

def state_update(user_input, memory):
    update_user_emotion(memory, user_input)

    memory["context"]["last_message"] = user_input

def legacy_update(user_input, memory):
    """Update emotions and context as before."""
    emotion_detected = update_user_emotion(memory, user_input)

    if (
        not emotion_detected
        and memory['emotions']['intensity'] < 0.5
        and memory['context'].get('turns_since_emotion_hint', 0) > 2
    ):
        hint = get_emotion_hint(user_input)
        blend_emotion_hint(memory, hint)
        memory['context']['turns_since_emotion_hint'] = 0
    else:
        memory['context']['turns_since_emotion_hint'] = (
            memory['context'].get('turns_since_emotion_hint', 0) + 1
        )
    apply_emotional_decay(memory, emotion_detected)


def quick_acknowledgement(memory):
    user_state = memory['emotions']['user_state']
    user_intensity = memory['emotions']['user_intensity']

    if user_state in ("stressed", "sad") and user_intensity > 0.6:
        return "I hear you — that's a lot."
    if user_state == "positive" and user_intensity > 0.75:
        return "Love that."
    return None



def generate_response(user_input, memory):
    """Generate response with semantic learning and active feedback."""
    state_update(user_input, memory)

    print(
    "[EMO]",
    memory["emotions"]["user_state"],
    memory["emotions"]["user_intensity"],
    "=> Leo:",
    memory["emotions"]["leo_state"],
    memory["emotions"]["leo_intensity"]
    )

    # --- Decide action using semantic-aware learning ---
    action = decide_action_with_learning(user_input, memory, ACTION_DICT)
    memory['context'].update({
        'last_action': action,
        'last_emotion': memory['emotions']['state'],  
    })

    instructions = ACTION_DICT[action](memory)

    instructions_text = f"""
    Current mode: {instructions['mode']}
    Goal: {instructions['goal']}
    Constraints:
    """ + "\n".join(f"- {c}" for c in instructions['constraints'])

    system_prompt = f"""
    You are Leonardo ("Leo"), a calm, emotionally intelligent assistant.

    Hard rules:
    - Do NOT claim personal experiences.
    - Avoid clinical language like "from a technical standpoint" or "cognitive load".
    - Keep it concise (max 6 sentences).
    - Ask at most ONE question.
    - No pep-talk hype. No excessive exclamation points.

    User trend:
    - state: {memory['emotions']['user_state']}
    - intensity: {memory['emotions']['user_intensity']}

    Leo stance (complement):
    - state: {memory['emotions']['leo_state']}
    - intensity: {memory['emotions']['leo_intensity']}

    If user is stressed: validate briefly, then help them pick ONE next step.
    Reply format for stressed:
    1) 1 sentence validation
    2) 1 sentence grounding or reassurance
    3) 1 simple question OR 1 next step (not both)
    If user expresses uncertainty ("I don't know", "not sure"):
    - Offer two small options to choose from.
    - Ask: "Which one feels easiest?"
    """




    full_prompt = system_prompt + "\nUser: " + user_input
    ack = quick_acknowledgement(memory)
    llm_response = ask_llm(full_prompt)

    # --- Compute semantic embedding for the user's input ---
    input_vec = embed_text(user_input)

    # --- Record feedback for semantic learning ---
    if 'feedback' not in memory:
        memory['feedback'] = []
    memory['feedback'].append({
        'input': user_input,
        'action': action,
        'embedding': input_vec,
        'success': None,
        'needs_feedback': any(word in llm_response.lower() for word in ['i think', 'maybe', 'possibly', 'perhaps', 'not sure', 'assume'])
    })

    if ack:
        return f'{ack}\n{llm_response}'
    return llm_response


def main():
    memory = load_memory()
    memory["conversation"] = []
    memory["emotions"]["user_state"] = "neutral"
    memory["emotions"]["user_intensity"] = 0.0
    memory["emotions"]["leo_state"] = "neutral"
    memory["emotions"]["leo_intensity"] = 0.5

    print(f"{persona['name']}: Hello, how are you today?")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "goodbye":
            save_memory(memory)
            print(f"{persona['name']}: I'll remember this conversation.")
            break

        response = generate_response(user_input, memory)
        print(f"{persona['name']}: {response}")

        save_memory(memory)


if __name__ == "__main__":
    main()