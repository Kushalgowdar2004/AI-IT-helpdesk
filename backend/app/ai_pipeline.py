import os
import re
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ENABLE_ANTHROPIC = os.getenv("ENABLE_ANTHROPIC", "false").lower() in {"1", "true", "yes"}
if not ENABLE_ANTHROPIC:
    ANTHROPIC_API_KEY = None
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

CATEGORIES = ["Network", "Hardware", "Software", "Windows & OS", "Access & Accounts", "Email & Collaboration", "Security", "Other"]


def _safe_json(raw):
    cleaned = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.I).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        return json.loads(match.group(0)) if match else None


def classify(text):
    t = text.lower()
    rules = [
        ("Network", r"\b(vpn|wi[- ]?fi|network|internet|router|ethernet|bandwidth|connect\w*|internal website|company website|dns)\b"),
        ("Windows & OS", r"\b(windows|boot|blue screen|bsod|freeze|frozen|operating system|task manager|startup)\b"),
        ("Hardware", r"\b(laptop|monitor|keyboard|mouse|printer|hardware|battery|dock\w*|display|webcam|camera|microphone|usb)\b"),
        ("Access & Accounts", r"\b(password|login|log in|account\w*|mfa|2fa|access|permission\w*|locked|shared drive|folder)\b"),
        ("Software", r"\b(app|application|software|install\w*|crash\w*|update\w*|bug|license|cache)\b"),
        ("Email & Collaboration", r"\b(email\w*|mail\w*|calendar|slack|zoom|teams|meeting|video call\w*|quarantine|spam|outlook|mailbox)\b"),
        ("Security", r"\b(phishing|suspicious|malware|stolen|security|compromise|credential|usb device)\b"),
    ]
    for category, pattern in rules:
        if re.search(pattern, t):
            return category
    return "Other"


def priority_for(text):
    t = text.lower()
    if re.search(r"\b(critical|urgent|asap|outage|breach|security incident|data loss)\b|can't\s+(work|login|access)|cannot\s+(work|login|access)", t):
        return "High"
    if re.search(r"\b(slow|intermittent|occasionally|sometimes|minor)\b", t):
        return "Low"
    return "Medium"


def _steps(article):
    body = article.body.strip()
    # Preserve only actual KB content; split into readable troubleshooting actions.
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    return sentences[:4]


def _fallback_response(message, category, priority, kb_matches):
    if not kb_matches:
        return (
            "I couldn't find a close match in the current knowledge base, so I don't want to guess at a fix. "
            "Tell me your device, operating system, and exact error message, or submit a ticket for IT support.",
            False,
        )
    top = kb_matches[0]
    steps = _steps(top)
    response = (
        f"I found a relevant knowledge-base article: **{top.title}** ({top.id}).\n\n"
        f"**Category:** {category}  ·  **Priority:** {priority}\n\n"
        "Try these steps:\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)) +
        "\n\nIf the issue continues after these steps, I can help you create an IT ticket."
    )
    return response, top.score >= 0.20 and priority != "High"


def _fallback_analysis(title, description, kb_matches):
    text = f"{title} {description}"
    category = classify(text)
    priority = priority_for(text)
    response, resolved = _fallback_response(text, category, priority, kb_matches)
    return {
        "category": category,
        "priority": priority,
        "priority_reason": "Assessed from issue keywords and KB similarity",
        "resolved": resolved,
        "response": response,
    }


def _anthropic_analysis(title, description, department, device, kb_matches, image_base64=None, image_media_type=None):
    kb_context = "\n\n".join(f"[{a.id}] {a.title}\n{a.body}" for a in kb_matches) if kb_matches else "(no close match)"
    system = (
        "You are an internal IT helpdesk triage engine. Use only the retrieved KB excerpts. "
        "Return raw JSON with category, priority, priority_reason, resolved, and response."
    )
    content = [{"type": "text", "text": f"Ticket: {title}\nDescription: {description}\nDepartment: {department}\nDevice: {device}\n\nKB:\n{kb_context}"}]
    if image_base64 and image_media_type:
        content.insert(0, {"type": "image", "source": {"type": "base64", "media_type": image_media_type, "data": image_base64}})
    try:
        resp = httpx.post(
            ANTHROPIC_URL,
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 500, "system": system, "messages": [{"role": "user", "content": content}]},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        raw = next((b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"), "")
        parsed = _safe_json(raw)
        if parsed:
            return parsed
    except Exception as exc:
        print("Anthropic unavailable; using local RAG assistant:", exc)
    return _fallback_analysis(title, description, kb_matches)


def analyze_ticket(title, description, department, device, kb_matches, image_base64=None, image_media_type=None):
    if ANTHROPIC_API_KEY:
        return _anthropic_analysis(title, description, department, device, kb_matches, image_base64, image_media_type)
    return _fallback_analysis(title, description, kb_matches)


def _is_greeting(message):
    return bool(re.fullmatch(r"\s*(hi|hello|hey|good morning|good afternoon|good evening|hi there|hello there)\s*[!.]?\s*", message.lower()))


def chat_reply(session_history, kb_matches):
    latest = [m.get("content", "").strip() for m in session_history if m.get("role") == "user" and m.get("content")]
    message = latest[-1] if latest else ""
    context = " ".join(latest[-3:])

    if _is_greeting(message):
        return "Hi! I'm your IT helpdesk assistant. Tell me what is not working — Wi-Fi, VPN, laptop, software, account access, or email — and I'll search the knowledge base and guide you through the next steps."

    # Local-first assistant: no API key required.
    if not ANTHROPIC_API_KEY:
        if kb_matches:
            category = classify(context)
            priority = priority_for(context)
            response, _ = _fallback_response(message, category, priority, kb_matches)
            if len(latest) > 1:
                response = "I used your recent conversation context to refine the match.\n\n" + response
            return response
        return (
            "I couldn't find a close knowledge-base match yet. Tell me the device, operating system, "
            "and exact error message, plus what you've already tried. If the issue is blocking your work, "
            "you can submit a ticket and I'll route it to IT."
        )

    kb_context = "\n\n".join(f"[{a.id}] {a.title}\n{a.body}" for a in kb_matches) if kb_matches else "(no close match)"
    system = f"You are an internal IT helpdesk assistant. Be practical and concise. Ground troubleshooting in this KB:\n{kb_context}"
    try:
        resp = httpx.post(
            ANTHROPIC_URL,
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 400, "system": system, "messages": session_history},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return next((b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"), "")
    except Exception as exc:
        print("Anthropic unavailable; using local RAG assistant:", exc)
        category = classify(context)
        priority = priority_for(context)
        response, _ = _fallback_response(message, category, priority, kb_matches)
        return response
