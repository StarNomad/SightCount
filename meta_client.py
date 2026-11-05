"""SightCount scene-interpretation layer.

Real path: Meta Model API (dev.meta.ai), OpenAI-compatible Chat Completions
  POST {META_MODEL_API_BASE | https://api.meta.ai/v1}/chat/completions
  Authorization: Bearer <META_MODEL_API_KEY>
  model: {META_MODEL_NAME | muse-spark-1.3}

The key is read ONLY from the META_MODEL_API_KEY environment variable.
It is never hardcoded, never written to disk, and never logged.
If no key is set, interpret() returns a clearly-labelled local fallback so
the app still runs and can be demoed. The real call path is unit-tested
with a mock HTTP opener (see tests/test_meta_client.py).
"""

import json
import os
import urllib.request
import urllib.error

DEFAULT_BASE = "https://api.meta.ai/v1"
DEFAULT_MODEL = "muse-spark-1.3"


def local_fallback(scene):
    """Rule-based interpretation from count/grouping stats only.

    Labelled LOCAL FALLBACK in the UI. It invents no people, moods, or
    identities; it only summarises the numbers the counter measured.
    """
    count = scene.get("count", 0)
    groups = scene.get("groups", 0)
    spread = scene.get("spread", "unknown")
    if count == 0:
        mood = "No audience detected in this frame."
        attention = "Nothing to attend to; the space reads empty."
    elif count <= 3:
        mood = "A small, quiet audience."
        attention = "Attention looks focused and unhurried at this size."
    elif count <= 10:
        mood = "A modest crowd, conversational in scale."
        attention = "Attention is likely split between the stage/screen and neighbours."
    else:
        mood = "A busy, energetic crowd."
        attention = "Attention is dispersed; a strong focal point matters more."
    return {
        "source": "LOCAL FALLBACK (no Meta API key set)",
        "mood": mood,
        "attention": attention,
        "grouping": f"{groups} cluster(s) detected by proximity; spread: {spread}.",
        "happening": (
            "Fallback summary only: this frame shows an audience of "
            f"about {count} counted blobs. With a Meta API key set, "
            "Muse Spark interprets the actual scene instead."
        ),
    }


def build_prompt(scene):
    return (
        "You are interpreting one audience scene frame for SightCount, "
        "a real-time audience-intelligence app. Do NOT invent identities, "
        "names, or demographic claims. From the measured data only, "
        "describe in 3 short lines: (1) crowd mood, (2) attention, "
        "(3) grouping and what appears to be happening.\n"
        f"Measured data: counted blobs={scene.get('count')}, "
        f"clusters={scene.get('groups')}, spread={scene.get('spread')}, "
        f"source_mode={scene.get('mode')}, note={scene.get('note', '')}"
    )


def call_meta_model(scene, opener=None):
    """Call the Meta Model API. Returns (interpretation_dict, error_or_None).

    `opener` is an injectable callable(url, data, headers) -> (status, body)
    used by tests; in production it is None and urllib is used.
    """
    key = os.environ.get("META_MODEL_API_KEY", "").strip()
    if not key:
        return None, "no_api_key"
    base = os.environ.get("META_MODEL_API_BASE", DEFAULT_BASE).rstrip("/")
    model = os.environ.get("META_MODEL_NAME", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You interpret audience scenes briefly and honestly."},
            {"role": "user", "content": build_prompt(scene)},
        ],
        "max_completion_tokens": 400,
        "temperature": 0.7,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }
    url = base + "/chat/completions"
    try:
        if opener is not None:
            status, body = opener(url, data, headers)
        else:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                status, body = resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return None, f"meta_api_http_{e.code}"
    except Exception as e:  # network / timeout: fall back, never crash the app
        return None, f"meta_api_error:{type(e).__name__}"
    try:
        parsed = json.loads(body)
        text = parsed["choices"][0]["message"]["content"]
    except Exception:
        return None, "meta_api_bad_response"
    return {
        "source": f"META MODEL API ({model})",
        "mood": "See interpretation below.",
        "attention": "See interpretation below.",
        "grouping": "See interpretation below.",
        "happening": text,
    }, None


def interpret(scene, opener=None):
    """Public entry: real Meta interpretation, or labelled local fallback."""
    result, err = call_meta_model(scene, opener=opener)
    if result is not None:
        return result
    fallback = local_fallback(scene)
    if err and err != "no_api_key":
        fallback["happening"] += f" (Meta API call failed: {err}; showing fallback.)"
    return fallback
