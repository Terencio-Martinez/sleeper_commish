import json
import logging
import os
from dataclasses import dataclass

from openai import OpenAI
from pydantic import BaseModel, Field

from app.ai.prompts import TRADE_SYSTEM_PROMPT, render_trade_user_prompt
from app.commissioner.rules import TradeEvidence


log = logging.getLogger(__name__)


PROVIDERS: dict[str, dict] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "api_key_env": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_model": "meta-llama/llama-3.3-70b-instruct",
    },
}


class TradeJudgment(BaseModel):
    decision: str = Field(description="One of: ALLOW, VETO, ESCALATE")
    confidence: float = Field(ge=0.0, le=1.0)
    risk_level: str = Field(description="One of: LOW, MEDIUM, HIGH")
    reasoning: str
    evidence: list[str]
    recommended_action: dict | None = None
    human_approval_required: bool


@dataclass
class JudgeResult:
    decision: str
    confidence: float
    risk_level: str
    reasoning: str
    evidence: list[str]
    recommended_action: dict | None
    human_approval_required: bool
    model_name: str
    raw_response: dict


class AIClient:
    def __init__(self) -> None:
        provider = (os.getenv("AI_PROVIDER") or "openai").lower()
        cfg = PROVIDERS.get(provider)
        if cfg is None:
            raise ValueError(
                f"unknown AI_PROVIDER={provider!r}; "
                f"expected one of {sorted(PROVIDERS)}"
            )

        self.provider = provider
        self.model = (
            os.getenv("AI_MODEL")
            or os.getenv("COMMISSIONER_MODEL")   # legacy fallback
            or cfg["default_model"]
        )
        self.base_url = os.getenv("AI_BASE_URL") or cfg["base_url"]

        api_key = os.getenv("AI_API_KEY") or os.getenv(cfg["api_key_env"])
        if not api_key:
            raise RuntimeError(
                f"no API key for provider '{provider}': "
                f"set AI_API_KEY, or {cfg['api_key_env']}"
            )

        self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        log.info("AI client: provider=%s model=%s base=%s",
                 self.provider, self.model, self.base_url)

    # ------------------------------------------------------------------
    # Low-level call: structured outputs, falling back to JSON mode.
    # ------------------------------------------------------------------
    def _structured(self, system: str, user: str, schema_cls):
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format=schema_cls,
            temperature=0.2,
        )
        return completion.choices[0].message.parsed, completion.model_dump()

    def _json_mode(self, system: str, user: str, schema_cls):
        schema = schema_cls.model_json_schema()
        augmented = (
            f"{system}\n\n"
            "Respond with a single valid JSON object and nothing else — no prose, "
            "no markdown fences. It must validate against this JSON schema:\n"
            f"{json.dumps(schema, indent=2)}"
        )
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": augmented},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = completion.choices[0].message.content
        data = json.loads(content)
        return schema_cls.model_validate(data), completion.model_dump()

    def _judge(self, system: str, user: str, schema_cls):
        try:
            parsed, raw = self._structured(system, user, schema_cls)
            if parsed is not None:
                return parsed, raw
            log.info("structured output returned null parsed; using JSON mode")
        except Exception as e:
            log.warning("structured output failed (%s); using JSON mode", e)
        return self._json_mode(system, user, schema_cls)

    # ------------------------------------------------------------------
    # Domain method
    # ------------------------------------------------------------------
    def judge_trade(self, evidence: TradeEvidence) -> JudgeResult:
        parsed, raw = self._judge(
            TRADE_SYSTEM_PROMPT,
            render_trade_user_prompt(evidence),
            TradeJudgment,
        )
        return JudgeResult(
            decision=parsed.decision,
            confidence=parsed.confidence,
            risk_level=parsed.risk_level,
            reasoning=parsed.reasoning,
            evidence=parsed.evidence,
            recommended_action=parsed.recommended_action,
            human_approval_required=parsed.human_approval_required,
            model_name=f"{self.provider}:{self.model}",
            raw_response=raw,
        )


_client: AIClient | None = None


def get_ai_client() -> AIClient:
    """Lazy singleton so importing this module never requires env vars."""
    global _client
    if _client is None:
        _client = AIClient()
    return _client


def judge_trade(evidence: TradeEvidence) -> JudgeResult:
    """Module-level entry point — keeps app.commissioner.cases unchanged."""
    return get_ai_client().judge_trade(evidence)