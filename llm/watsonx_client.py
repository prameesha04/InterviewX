"""
IBM watsonx.ai LLM client using the ibm-watsonx-ai SDK.
Provides a thin wrapper around the Granite model for use by all agents.

Uses the /ml/v1/text/chat endpoint (chat completions) which is the current
non-deprecated API for ibm-watsonx-ai >= 1.7.x.
"""

import os
import httpx
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.client import HttpClientConfig
from ibm_watsonx_ai.foundation_models import ModelInference

# ---------------------------------------------------------------------------
# Module-level singleton — built once per process, reused across all calls.
# Avoids repeated IAM token exchanges and TCP connection overhead that caused
# WinError 10054 / timeout failures when three sequential Granite calls were
# made during /interview/start.
#
# A 60-second read timeout is wired into the underlying httpx client so that
# stalled requests raise promptly rather than waiting up to the SDK default
# of 1800 seconds.
# ---------------------------------------------------------------------------
_model_instance: "ModelInference | None" = None
_model_params: dict = {}

# Per-request read timeout (seconds). Connect timeout stays at the SDK default (10 s).
_REQUEST_TIMEOUT = httpx.Timeout(connect=10, read=60, write=60, pool=10)


def _build_credentials() -> Credentials:
    api_key = os.getenv("WATSONX_API_KEY")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    if not api_key:
        raise EnvironmentError(
            "WATSONX_API_KEY environment variable is not set. "
            "Copy .env.example to .env and fill in your credentials."
        )
    return Credentials(url=url, api_key=api_key)


def get_model(
    model_id: str = "ibm/granite-4-h-small",
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.9,
    repetition_penalty: float = 1.1,
) -> ModelInference:
    """
    Return a cached ModelInference instance for the specified Granite model.
    The instance is built once per process and reused on subsequent calls so
    that IAM authentication and TCP connection setup happen only once.

    All parameters can be overridden by callers that need different settings.
    Note: repetition_penalty is accepted but ignored by the chat endpoint;
    kept in the signature for backwards compatibility.
    """
    global _model_instance, _model_params

    if _model_instance is None:
        project_id = os.getenv("WATSONX_PROJECT_ID")
        if not project_id:
            raise EnvironmentError(
                "WATSONX_PROJECT_ID environment variable is not set."
            )

        credentials = _build_credentials()

        # Build an APIClient with a reduced read timeout (60 s) so that slow
        # or stalled Granite calls fail fast instead of hanging for 1800 s.
        api_client = APIClient(
            credentials=credentials,
            project_id=project_id,
            httpx_client=HttpClientConfig(timeout=_REQUEST_TIMEOUT),
        )

        _model_instance = ModelInference(
            model_id=model_id,
            api_client=api_client,
            project_id=project_id,
        )

    # Always update the generation params to honour per-call overrides.
    _model_params = {
        "max_tokens": max_new_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    # Keep params accessible on the instance for backwards compatibility.
    _model_instance._ix_params = _model_params
    return _model_instance


def generate_text(prompt: str, **kwargs) -> str:
    """
    High-level helper: generate text from a prompt using the default Granite model
    via the chat completions endpoint (/ml/v1/text/chat).

    kwargs are forwarded to get_model() to allow per-call parameter overrides.
    The 60-second read timeout is enforced at the httpx transport layer
    (configured in get_model) rather than at the call site.
    """
    model = get_model(**kwargs)
    params = getattr(model, "_ix_params", {})

    response = model.chat(
        messages=[{"role": "user", "content": prompt}],
        params=params,
    )

    # Extract the assistant message content from the chat response
    try:
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    except (KeyError, IndexError, TypeError):
        # Fallback: return the raw response as string
        return str(response).strip()
