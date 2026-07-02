import json
import os

MAX_REPORT_CHARS = 12000

PROMPT_TEMPLATE = """You are an analyst extracting cause information from investigation reports.

Read the report below and extract the following:
1. confirmed_cause: The cause explicitly stated as confirmed or determined. Empty string if none.
2. probable_cause: The most likely cause identified when a confirmed cause is absent or inconclusive. Empty string if none.
3. confidence: One of "confirmed", "probable", or "not_determinable".
   - "confirmed": the report explicitly states a determined or confirmed cause
   - "probable": the report identifies a most likely cause but does not confirm it
   - "not_determinable": the report cannot identify a cause
4. reasoning: One sentence explaining your determination.

REPORT:
{report_text}

Respond with a JSON object only, no other text:
{{
  "confirmed_cause": "...",
  "probable_cause": "...",
  "confidence": "confirmed" | "probable" | "not_determinable",
  "reasoning": "..."
}}"""


def _build_prompt(report_text: str) -> str:
    truncated = report_text[:MAX_REPORT_CHARS]
    return PROMPT_TEMPLATE.format(report_text=truncated)


def _parse_result(text: str) -> dict:
    return json.loads(text.strip())


def _extract_with_openai(report_text: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": _build_prompt(report_text)}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return _parse_result(response.choices[0].message.content)


def _extract_with_anthropic(report_text: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=512,
        messages=[{"role": "user", "content": _build_prompt(report_text)}],
    )
    return _parse_result(message.content[0].text)


def extract_cause(report_text: str) -> dict:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "anthropic":
        return _extract_with_anthropic(report_text)
    return _extract_with_openai(report_text)
