from collections import Counter, defaultdict
import re
from llm import ask_llm
import json

# --- Feel free to expand these ---
EMOTION_KEYWORDS = {
    "stressed": ["overwhelmed", "stressed", "anxious", "pressure", "tired", "burned out"],
    "sad": ["sad", "down", "lonely", "empty", "hopeless"],
    "positive": ["happy", "excited", "great", "good", "love", "proud"],
    "angry": ["angry", "frustrated", "annoyed", "mad"],
    "uncertain": ["maybe", "not sure", "i guess", "kind of", "confused"],
}


def detect_emotion(text: str):
    """Return (state, intensity) for a single message."""
    t = text.lower()
    scores = Counter()

    for emotion, words in EMOTION_KEYWORDS.items():
        for w in words:
            if re.search(rf"\b{re.escape(w)}\b", t):
                scores[emotion] += 1

    if not scores:
        return None, 0.0

    emotion, count = scores.most_common(1)[0]
    intensity = min(1.0, count / 3)
    intensity = max(0.35, intensity)   # <-- add this floor
    return emotion, intensity



def update_user_emotion(memory: dict, user_input: str, window: int = 6) -> bool:
    """
    Updates:
      memory['emotions']['user_state']
      memory['emotions']['user_intensity']
      memory['emotions']['user_certainty']
      memory['emotions']['user_scores']
    Returns True if an emotion was detected in THIS message.
    """
    memory.setdefault("conversation", [])
    memory.setdefault("emotions", {})

    msg_state, msg_intensity = detect_emotion(user_input)
    detected = msg_state is not None

    memory["conversation"].append({
        "text": user_input,
        "emotion": msg_state,
        "intensity": float(msg_intensity or 0.0)
    })

    recent = memory["conversation"][-window:]
    n = len(recent)

    scores = defaultdict(float)
    total = 0.0

    for i, item in enumerate(recent):
        emo = item.get("emotion")
        if not emo:
            continue

        intensity = max(0.2, float(item.get("intensity", 0.0)))
        weight = (i + 1) / n  # oldest small, newest big (normalized)

        s = weight * intensity
        scores[emo] += s
        total += s

    if total <= 1e-9:
        # gentle decay toward neutral instead of hard reset
        prev_int = memory["emotions"].get("user_intensity", 0.0)
        memory["emotions"]["user_state"] = "neutral"
        memory["emotions"]["user_intensity"] = round(prev_int * 0.75, 2)
        memory["emotions"]["user_certainty"] = 0.0
        memory["emotions"]["user_scores"] = {}
        return detected

    dominant = max(scores, key=scores.get)
    dominant_score = scores[dominant]

    # certainty = how dominant the top emotion is among emotional content
    certainty = dominant_score / total  # 0..1

    # raw intensity (bounded) = emotional mass per message (normalize)
    raw_intensity = min(1.0, (total / n) * 1.8)  # tune 1.8 if needed

    # smooth intensity both up and down
    prev = memory["emotions"].get("user_intensity", 0.0)
    alpha = 0.35
    intensity = alpha * raw_intensity + (1 - alpha) * prev

    memory["emotions"]["user_state"] = dominant
    memory["emotions"]["user_intensity"] = round(float(intensity), 2)
    memory["emotions"]["user_certainty"] = round(float(certainty), 2)
    memory["emotions"]["user_scores"] = {k: round(v / total, 3) for k, v in scores.items()}

    return detected


def compute_leo_stance(memory: dict) -> dict:
    """
    Complements user emotion (does not mirror).
    Writes memory["emotions"]["leo_stance"] and returns it.
    """
    emo = memory.setdefault("emotions", {})
    user_state = emo.get("user_state", "neutral") or "neutral"
    intensity = float(emo.get("user_intensity", 0.0) or 0.0)   # 0..1
    certainty = float(emo.get("user_certainty", 0.0) or 0.0)   # 0..1

    # How strongly to apply the stance (prevents tone-flipping)
    apply = max(0.0, min(1.0, 0.15 + 0.55 * certainty + 0.45 * intensity))

    # Neutral baseline
    stance = {
        "tone": "neutral",      # calm/warm/upbeat/neutral/firm/playful
        "goal": "support",      # deescalate/energize/focus/celebrate/clarify/support
        "energy": 0.45,         # 0..1
        "directness": 0.60,     # 0..1
        "support": 0.55,        # 0..1
        "challenge": 0.30,      # 0..1
        "apply": round(apply, 2)
    }

    # Target stance by user emotion (complement rules)
    if user_state == "stressed":
        target = {"tone":"calm","goal":"deescalate","energy":0.25,"directness":0.55,"support":0.85,"challenge":0.15}
    elif user_state == "angry":
        target = {"tone":"steady","goal":"deescalate","energy":0.30,"directness":0.60,"support":0.75,"challenge":0.20}
    elif user_state == "sad":
        target = {"tone":"warm","goal":"energize","energy":0.55,"directness":0.50,"support":0.90,"challenge":0.20}
    elif user_state == "uncertain":
        target = {"tone":"clear","goal":"clarify","energy":0.45,"directness":0.75,"support":0.55,"challenge":0.25}
    elif user_state == "positive":
        # complement: grounded + channel into plan (not mirror hype)
        target = {"tone":"grounded","goal":"focus","energy":0.55,"directness":0.70,"support":0.60,"challenge":0.40}
    else:
        target = {"tone":"neutral","goal":"support","energy":0.45,"directness":0.65,"support":0.55,"challenge":0.30}

    # Blend toward target
    def lerp(a, b, t): return a + (b - a) * t
    for k in ["energy","directness","support","challenge"]:
        stance[k] = round(lerp(stance[k], target[k], apply), 2)

    # Only adopt categorical tone/goal when apply is high enough
    if apply >= 0.55:
        stance["tone"] = target["tone"]
        stance["goal"] = target["goal"]

    emo["leo_stance"] = stance
    return stance


def apply_emotional_decay(memory, detected):
    emotions = memory['emotions']

    if detected:
        return

    decay = 0.08 if emotions['state'] == 'calm' else 0.12
    emotions['intensity'] = max(0.2, emotions['intensity'] - 0.08)

    if emotions['intensity'] <= 0.3:
        emotions['state'] = 'calm'

def get_emotion_hint(user_input):
        prompt = f"""
        Analyze the user's message and suggest emotional signals.
        Respond ONLY in JSON.

        User message: "{user_input}"

        {{
        "state": one of ["calm", "stressed", "positive", "uncertain", "angry"],
        "confidence": float between 0.0 and 1.0
        }}
        """
        response = ask_llm(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

def blend_emotion_hint(memory, hint):
    if not hint:
        return 
    
    emotions = memory['emotions']
    state = hint.get('state')
    confidence = hint.get('confidence', 0)

    if confidence < 0.55:
        return

    if emotions['intensity'] > 0.7:
        return

    if state != emotions['state']:
        emotions['state'] = state
        emotions['intensity'] = max(emotions['intensity'], confidence * 0.6)
