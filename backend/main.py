from __future__ import annotations

import json
import os
import re
import time
import base64
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
DEFAULT_MOCK_PATH = ROOT / "mock-data" / "test_data.md"


def load_env_file() -> None:
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


load_env_file()

MOONSHOT_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
MOONSHOT_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
MOONSHOT_FALLBACK_MODELS = [
    item.strip()
    for item in os.getenv(
        "KIMI_FALLBACK_MODELS",
        "moonshot-v1-8k,kimi-k2.5,kimi-k2.6",
    ).split(",")
    if item.strip()
]
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "kimi").strip().lower()
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_MODEL = os.getenv("ARK_MODEL", "doubao-seed-1-6-flash-250828")
ARK_FALLBACK_MODELS = [
    item.strip()
    for item in os.getenv(
        "ARK_FALLBACK_MODELS",
        "doubao-seed-1-6-flash-250828",
    ).split(",")
    if item.strip()
]
ZHIHU_SEARCH_URL = os.getenv(
    "ZHIHU_SEARCH_URL",
    "https://developer.zhihu.com/api/v1/content/zhihu_search",
)
ZHIHU_OAUTH_BASE_URL = os.getenv("ZHIHU_OAUTH_BASE_URL", "https://openapi.zhihu.com")
ZHIHU_OAUTH_APP_ID = os.getenv("ZHIHU_OAUTH_APP_ID", "")
ZHIHU_OAUTH_APP_KEY = os.getenv("ZHIHU_OAUTH_APP_KEY", "")
ZHIHU_OAUTH_REDIRECT_URI = os.getenv("ZHIHU_OAUTH_REDIRECT_URI", "")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5173")
OAUTH_FRONTEND_COOKIE = "what_if_frontend_base"
MOONSHOT_FALLBACK_BASE_URLS = [
    item.strip().rstrip("/")
    for item in os.getenv(
        "KIMI_FALLBACK_BASE_URLS",
        "https://api.moonshot.cn/v1,https://api.moonshot.ai/v1",
    ).split(",")
    if item.strip()
]


class AnalyzeRequest(BaseModel):
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    mock_file: str | None = Field(default=None, description="Optional absolute/relative markdown file path")


class TrajectoryObservation(BaseModel):
    theme: str = ""
    key_metrics: list[str] = Field(default_factory=list)
    overview: str
    high_frequency_browsing: list[str]
    late_night_searches: list[str]
    likes_tendency: list[str]
    interest_shift: str
    reflective_question: str


class AnalyzeResponse(BaseModel):
    time_range: str
    observation: TrajectoryObservation
    stardust_tag_suggestions: list[str]
    raw_excerpt_links: list[str]


class GenerateRequest(BaseModel):
    start_date: str
    end_date: str
    story_title: str = ""
    story_text: str
    mock_file: str | None = None


class KeyNode(BaseModel):
    id: str
    title: str
    description: str
    emotion: str
    reading_links: list[str] = Field(default_factory=list, description="1-2 Zhihu links for node 1/2")


class GenerateResponse(BaseModel):
    title: str
    time_range: str
    tags: list[str]
    nodes: list[KeyNode]
    summary: str
    liu_kanshan_state: str


class WhatIfRequest(BaseModel):
    card_title: str
    time_range: str
    tags: list[str]
    summary: str
    liu_kanshan_state: str
    original_nodes: list[KeyNode]
    rewritten_opening: str = Field(..., description="A short rewritten version of the first node description")


class ZhihuSearchResult(BaseModel):
    title: str
    url: str
    content_type: str = ""
    content_text: str = ""
    author_name: str = ""
    vote_up_count: int = 0


class NodeZhihuSearchResult(BaseModel):
    node_id: str
    query: str
    results: list[ZhihuSearchResult] = Field(default_factory=list)


class WhatIfResponse(BaseModel):
    rewritten_title: str = ""
    rewritten_opening: str
    divergence_note: str
    rewritten_nodes: list[KeyNode]
    rewritten_tags: list[str]
    rewritten_summary: str
    rewritten_state: str
    rewritten_liu_kanshan_state: str
    zhihu_search_queries: list[str] = Field(default_factory=list)
    zhihu_search_results: list[ZhihuSearchResult] = Field(default_factory=list)
    node_search_results: list[NodeZhihuSearchResult] = Field(default_factory=list)


def resolve_mock_path(mock_file: str | None) -> Path:
    if not mock_file:
        return DEFAULT_MOCK_PATH
    path = Path(mock_file)
    if not path.is_absolute():
        path = ROOT / mock_file
    return path


def read_mock_data(mock_file: str | None) -> str:
    path = resolve_mock_path(mock_file)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Mock file not found: {path}")
    return path.read_text(encoding="utf-8")


def compact_mock_data(md_text: str) -> str:
    title_keywords = (
        "标题：",
        "回答标题：",
        "问题标题：",
        "文章标题：",
        "搜索内容：",
        "链接：",
        "页面链接：",
        "浏览时间：",
        "搜索时间：",
        "收藏时间：",
        "点赞时间：",
        "停留时间：",
        "发布时间：",
        "回答发布时间：",
    )
    lines: list[str] = []
    pending_label = ""
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line in title_keywords:
            pending_label = line
            continue
        if pending_label:
            lines.append(f"{pending_label}{line}")
            pending_label = ""
            continue
        if line.startswith(("https://www.zhihu.com/", "https://zhuanlan.zhihu.com/")):
            lines.append(f"链接：{line}")
    return "\n".join(lines[:90])


def require_kimi_api_key() -> str:
    key = os.getenv("KIMI_API_KEY")
    if not key:
        raise HTTPException(
            status_code=500,
            detail="KIMI_API_KEY is missing. Please set it before calling this API.",
        )
    return key


def require_ark_api_key() -> str:
    key = os.getenv("ARK_API_KEY")
    if not key:
        raise HTTPException(
            status_code=500,
            detail="ARK_API_KEY is missing. Please set it before calling this API.",
        )
    return key


async def kimi_json_call(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    return await llm_json_call(system_prompt, user_prompt)


async def llm_json_call(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    provider = current_provider()
    api_key = provider["api_key"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload_base = {
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    last_resp: httpx.Response | None = None
    async with httpx.AsyncClient(timeout=90.0) as client:
        for base_url in provider["base_urls"]:
            for model in provider["models"]:
                url = f"{base_url}/chat/completions"
                payload = {"model": model, **payload_base}
                resp = await client.post(url, headers=headers, json=payload)
                last_resp = resp
                if resp.status_code < 400:
                    print(f"LLM request succeeded with provider={provider['name']}, base_url={base_url}, model={model}")
                    break
                print(
                    f"LLM request failed with provider={provider['name']}, "
                    f"base_url={base_url}, model={model}: {resp.status_code} {resp.text[:300]}"
                )
            if last_resp and last_resp.status_code < 400:
                break
        else:
            resp = last_resp

    if last_resp is None:
        raise HTTPException(status_code=502, detail="Kimi API error: no response")

    resp = last_resp
    if resp.status_code >= 400:
        detail = f"{provider['name']} API error: {resp.status_code} {resp.text}"
        print(detail)
        raise HTTPException(status_code=502, detail=detail)

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        return parse_json_object(content)
    except Exception as exc:  # noqa: BLE001
        detail = f"Invalid Kimi response: {exc}; body={resp.text[:1000]}"
        print(detail)
        raise HTTPException(status_code=502, detail=detail) from exc


def parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def kimi_base_url_candidates() -> list[str]:
    candidates = [MOONSHOT_BASE_URL.rstrip("/")]
    for item in MOONSHOT_FALLBACK_BASE_URLS:
        if item not in candidates:
            candidates.append(item)
    return candidates


def kimi_model_candidates() -> list[str]:
    candidates = [MOONSHOT_MODEL]
    for item in MOONSHOT_FALLBACK_MODELS:
        if item not in candidates:
            candidates.append(item)
    return candidates


def ark_model_candidates() -> list[str]:
    candidates = [ARK_MODEL]
    for item in ARK_FALLBACK_MODELS:
        if item not in candidates:
            candidates.append(item)
    return candidates


def current_provider() -> dict[str, Any]:
    if LLM_PROVIDER == "ark":
        return {
            "name": "ark",
            "api_key": require_ark_api_key(),
            "base_urls": [ARK_BASE_URL.rstrip("/")],
            "models": ark_model_candidates(),
        }
    return {
        "name": "kimi",
        "api_key": require_kimi_api_key(),
        "base_urls": kimi_base_url_candidates(),
        "models": kimi_model_candidates(),
    }


def normalize_frontend_base(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if normalized.startswith("www.127.0.0.1"):
        normalized = f"http://{normalized.removeprefix('www.')}"
    if normalized.startswith("www.localhost"):
        normalized = f"http://{normalized.removeprefix('www.')}"
    if normalized.startswith("127.0.0.1") or normalized.startswith("localhost"):
        normalized = f"http://{normalized}"
    normalized = normalized.replace("://www.127.0.0.1", "://127.0.0.1")
    normalized = normalized.replace("://www.localhost", "://localhost")
    return normalized


def is_allowed_frontend_base(base_url: str) -> bool:
    base_url = normalize_frontend_base(base_url)
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    hostname = parsed.hostname or ""
    configured_host = urlparse(FRONTEND_BASE_URL).hostname or ""
    return (
        hostname in {"127.0.0.1", "localhost"}
        or hostname.endswith(".tcloudbaseapp.com")
        or bool(configured_host and hostname == configured_host)
    )


def frontend_base_from_request(request: Request) -> str:
    explicit_frontend = normalize_frontend_base(request.query_params.get("frontend", ""))
    if explicit_frontend and is_allowed_frontend_base(explicit_frontend):
        return explicit_frontend

    origin = request.headers.get("origin", "").strip()
    if origin and is_allowed_frontend_base(origin):
        return normalize_frontend_base(origin)

    referer = request.headers.get("referer", "").strip()
    if referer:
        parsed = urlparse(referer)
        referer_base = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else ""
        if referer_base and is_allowed_frontend_base(referer_base):
            return normalize_frontend_base(referer_base)

    return normalize_frontend_base(FRONTEND_BASE_URL)


def encode_oauth_state(frontend_base: str) -> str:
    encoded = base64.urlsafe_b64encode(frontend_base.encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def decode_oauth_state(state: str) -> str:
    if not state:
        return ""
    try:
        padded = state + "=" * (-len(state) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        return normalize_frontend_base(decoded)
    except Exception:  # noqa: BLE001
        parsed_state = parse_qs(state)
        return normalize_frontend_base((parsed_state.get("frontend") or [""])[0])


def frontend_base_from_state(state: str) -> str:
    if not state:
        return normalize_frontend_base(FRONTEND_BASE_URL)
    state_base = decode_oauth_state(state)
    if state_base and is_allowed_frontend_base(state_base):
        return state_base
    return normalize_frontend_base(FRONTEND_BASE_URL)


def frontend_base_from_callback(request: Request) -> str:
    cookie_base = normalize_frontend_base(request.cookies.get(OAUTH_FRONTEND_COOKIE, ""))
    if cookie_base and is_allowed_frontend_base(cookie_base):
        return cookie_base
    return frontend_base_from_state(request.query_params.get("state", ""))


def frontend_letter_url(params: dict[str, str] | None = None, base_url: str | None = None) -> str:
    base = normalize_frontend_base(base_url or FRONTEND_BASE_URL)
    query = urlencode(params or {})
    return f"{base}/#/letter?{query}" if query else f"{base}/#/letter"


def frontend_landing_url(params: dict[str, str] | None = None, base_url: str | None = None) -> str:
    base = normalize_frontend_base(base_url or FRONTEND_BASE_URL)
    query = urlencode(params or {})
    return f"{base}/#/?{query}" if query else f"{base}/#/"


def oauth_redirect_uri(request: Request | None = None) -> str:
    configured_uri = ZHIHU_OAUTH_REDIRECT_URI.strip()
    if configured_uri:
        return configured_uri
    if request:
        return str(request.url_for("zhihu_oauth_callback"))
    return ""


async def check_llm_auth() -> list[dict[str, Any]]:
    provider = current_provider()
    api_key = provider["api_key"]
    headers = {"Authorization": f"Bearer {api_key}"}
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for base_url in provider["base_urls"]:
            for model in provider["models"]:
                url = f"{base_url}/chat/completions"
                try:
                    resp = await client.post(
                        url,
                        headers={**headers, "Content-Type": "application/json"},
                        json={
                            "model": model,
                            "messages": [
                                {"role": "user", "content": "只返回 JSON：{\"ok\":true}"},
                            ],
                            "temperature": 0,
                        },
                    )
                    results.append(
                        {
                            "provider": provider["name"],
                            "base_url": base_url,
                            "model": model,
                            "status_code": resp.status_code,
                            "ok": resp.status_code < 400,
                            "body_preview": resp.text[:500],
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    results.append(
                        {
                            "provider": provider["name"],
                            "base_url": base_url,
                            "model": model,
                            "status_code": None,
                            "ok": False,
                            "body_preview": str(exc),
                        }
                    )
    return results


def extract_zhihu_links(md_text: str) -> list[str]:
    links: list[str] = []
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("https://www.zhihu.com/"):
            links.append(line)
    return links


def normalize_zhihu_search_item(item: dict[str, Any]) -> ZhihuSearchResult | None:
    title = str(item.get("Title") or item.get("title") or "").strip()
    url = str(item.get("Url") or item.get("url") or "").strip()
    content_text = str(item.get("ContentText") or item.get("content_text") or "").strip()
    if not title or not url:
        return None
    return ZhihuSearchResult(
        title=title,
        url=url,
        content_type=str(item.get("ContentType") or item.get("content_type") or ""),
        content_text=content_text,
        author_name=str(item.get("AuthorName") or item.get("author_name") or ""),
        vote_up_count=int(item.get("VoteUpCount") or item.get("vote_up_count") or 0),
    )


def zhihu_result_score(result: ZhihuSearchResult, query: str) -> int:
    haystack = f"{result.title} {result.content_text}".lower()
    terms = [term.strip().lower() for term in re.split(r"[\s，,、：:]+", query) if term.strip()]
    score = min(result.vote_up_count, 500) // 20
    for term in terms:
        if len(term) < 2:
            continue
        if term in result.title.lower():
            score += 8
        elif term in haystack:
            score += 3
    if result.content_text:
        score += 2
    if result.content_type in {"Answer", "Article", "Question"}:
        score += 1
    return score


async def search_zhihu_content(query: str, count: int = 3) -> list[ZhihuSearchResult]:
    access_secret = os.getenv("ZHIHU_ACCESS_SECRET", "").strip()
    if not access_secret or not query.strip():
        return []

    headers = {
        "Authorization": f"Bearer {access_secret}",
        "X-Request-Timestamp": str(int(time.time())),
        "Content-Type": "application/json",
    }
    params = {
        "Query": query.strip(),
        "Count": max(1, min(count, 10)),
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(ZHIHU_SEARCH_URL, params=params, headers=headers)
    except Exception as exc:  # noqa: BLE001
        print(f"Zhihu search request failed: {exc}")
        return []

    if resp.status_code >= 400:
        print(f"Zhihu search error: {resp.status_code} {resp.text[:300]}")
        return []

    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        print(f"Invalid Zhihu search response: {exc}; body={resp.text[:300]}")
        return []

    if isinstance(payload, dict) and payload.get("Code") not in (None, 0):
        print(f"Zhihu search business error: {payload}")
        return []

    data = payload.get("Data", {}) if isinstance(payload, dict) else {}
    items = data.get("Items", []) if isinstance(data, dict) else []
    results: list[ZhihuSearchResult] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized = normalize_zhihu_search_item(item)
        if normalized:
            results.append(normalized)
    return sorted(results, key=lambda item: zhihu_result_score(item, query), reverse=True)


async def search_zhihu_for_queries(queries: list[str], count_per_query: int = 2, limit: int = 5) -> list[ZhihuSearchResult]:
    seen_urls: set[str] = set()
    results: list[ZhihuSearchResult] = []
    for query in queries:
        for item in await search_zhihu_content(query, count=count_per_query):
            if item.url in seen_urls:
                continue
            seen_urls.add(item.url)
            results.append(item)
            if len(results) >= limit:
                return results
    return results


async def search_zhihu_for_nodes(nodes: list[dict[str, Any]], fallback_tags: list[str]) -> list[NodeZhihuSearchResult]:
    node_results: list[NodeZhihuSearchResult] = []
    shared_context = " ".join(fallback_tags[:2])
    for node in nodes[:5]:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "").strip()
        title = str(node.get("title") or "").strip()
        description = str(node.get("description") or "").strip()
        if not node_id or not title:
            continue
        compact_description = re.sub(r"[^\w\u4e00-\u9fff]+", " ", description).strip()[:18]
        query = " ".join(item for item in [title, compact_description, shared_context] if item).strip()
        if len(query) > 42:
            query = query[:42]
        results = await search_zhihu_content(query, count=5)
        if results:
            node_results.append(NodeZhihuSearchResult(node_id=node_id, query=query, results=results[:1]))
    return node_results


app = FastAPI(title="What If Universe Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        item.strip()
        for item in os.getenv("CORS_ALLOW_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
        if item.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, Any]:
    kimi_key = os.getenv("KIMI_API_KEY", "")
    ark_key = os.getenv("ARK_API_KEY", "")
    return {
        "status": "ok",
        "llm_provider": LLM_PROVIDER,
        "kimi_key_loaded": bool(kimi_key),
        "kimi_key_fingerprint": f"{kimi_key[:8]}...{kimi_key[-6:]}" if kimi_key else "",
        "kimi_model": MOONSHOT_MODEL,
        "kimi_fallback_models": MOONSHOT_FALLBACK_MODELS,
        "kimi_base_url": MOONSHOT_BASE_URL,
        "kimi_fallback_base_urls": MOONSHOT_FALLBACK_BASE_URLS,
        "ark_key_loaded": bool(ark_key),
        "ark_key_fingerprint": f"{ark_key[:8]}...{ark_key[-6:]}" if ark_key else "",
        "ark_base_url": ARK_BASE_URL,
        "ark_model": ARK_MODEL,
        "ark_fallback_models": ARK_FALLBACK_MODELS,
        "zhihu_search_configured": bool(os.getenv("ZHIHU_ACCESS_SECRET", "").strip()),
        "zhihu_search_url": ZHIHU_SEARCH_URL,
        "zhihu_oauth_configured": bool(ZHIHU_OAUTH_APP_ID and ZHIHU_OAUTH_APP_KEY and ZHIHU_OAUTH_REDIRECT_URI),
        "mock_data_exists": DEFAULT_MOCK_PATH.exists(),
    }


@app.get("/api/debug/kimi-auth")
async def debug_kimi_auth() -> dict[str, Any]:
    kimi_key = os.getenv("KIMI_API_KEY", "")
    if LLM_PROVIDER != "kimi":
        return {
            "message": "Current provider is not kimi. Use /api/debug/llm-auth for active provider checks.",
            "llm_provider": LLM_PROVIDER,
        }
    return {
        "kimi_key_loaded": bool(kimi_key),
        "kimi_key_fingerprint": f"{kimi_key[:8]}...{kimi_key[-6:]}" if kimi_key else "",
        "checks": await check_llm_auth(),
    }


@app.get("/api/debug/llm-auth")
async def debug_llm_auth() -> dict[str, Any]:
    provider = current_provider()
    api_key = provider["api_key"]
    return {
        "llm_provider": provider["name"],
        "key_loaded": bool(api_key),
        "key_fingerprint": f"{api_key[:8]}...{api_key[-6:]}" if api_key else "",
        "checks": await check_llm_auth(),
    }


@app.get("/api/auth/zhihu/login")
async def zhihu_oauth_login(request: Request) -> RedirectResponse:
    redirect_uri = oauth_redirect_uri(request)
    frontend_base = frontend_base_from_request(request)
    if not ZHIHU_OAUTH_APP_ID or not redirect_uri:
        return RedirectResponse(
            frontend_landing_url(
                {
                    "zhihu_login": "failed",
                    "reason": "oauth_not_configured",
                },
                base_url=frontend_base,
            )
        )

    query = urlencode({
        "redirect_uri": redirect_uri,
        "app_id": ZHIHU_OAUTH_APP_ID,
        "response_type": "code",
        "state": encode_oauth_state(frontend_base),
    })
    response = RedirectResponse(f"{ZHIHU_OAUTH_BASE_URL.rstrip('/')}/authorize?{query}")
    response.set_cookie(
        key=OAUTH_FRONTEND_COOKIE,
        value=frontend_base,
        max_age=600,
        httponly=True,
        samesite="lax",
    )
    return response


@app.get("/api/auth/zhihu/callback")
async def zhihu_oauth_callback(request: Request) -> RedirectResponse:
    redirect_uri = oauth_redirect_uri(request)
    query_params = request.query_params
    frontend_base = frontend_base_from_callback(request)
    oauth_code = (
        query_params.get("code")
        or query_params.get("authorization_code")
        or query_params.get("auth_code")
        or query_params.get("authorizationCode")
    )
    zhihu_error = query_params.get("error") or query_params.get("reason") or ""
    if not oauth_code:
        return RedirectResponse(
            frontend_landing_url(
                {
                    "zhihu_login": "failed",
                    "reason": zhihu_error or "missing_code",
                    "received": ",".join(query_params.keys()) or "none",
                },
                base_url=frontend_base,
            )
        )
    if not ZHIHU_OAUTH_APP_ID or not ZHIHU_OAUTH_APP_KEY or not redirect_uri:
        return RedirectResponse(
            frontend_landing_url(
                {
                    "zhihu_login": "failed",
                    "reason": "oauth_not_configured",
                },
                base_url=frontend_base,
            )
        )

    async with httpx.AsyncClient(timeout=30) as client:
        token_resp = await client.post(
            f"{ZHIHU_OAUTH_BASE_URL.rstrip('/')}/access_token",
            data={
                "app_id": ZHIHU_OAUTH_APP_ID,
                "app_key": ZHIHU_OAUTH_APP_KEY,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": oauth_code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code >= 400:
            return RedirectResponse(
                frontend_landing_url(
                    {
                        "zhihu_login": "failed",
                        "reason": "token_failed",
                        "status": str(token_resp.status_code),
                    },
                    base_url=frontend_base,
                )
            )

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return RedirectResponse(
                frontend_landing_url(
                    {"zhihu_login": "failed", "reason": "missing_token"},
                    base_url=frontend_base,
                )
            )

        user_resp = await client.get(
            f"{ZHIHU_OAUTH_BASE_URL.rstrip('/')}/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code >= 400:
            return RedirectResponse(
                frontend_landing_url(
                    {
                        "zhihu_login": "failed",
                        "reason": "user_failed",
                        "status": str(user_resp.status_code),
                    },
                    base_url=frontend_base,
                )
            )

        user_data = user_resp.json()

    nickname = (
        user_data.get("fullname")
        or user_data.get("name")
        or user_data.get("headline")
        or "知乎用户"
    )
    return RedirectResponse(
        frontend_letter_url(
            {
                "zhihu_login": "success",
                "zhihu_name": str(nickname),
            },
            base_url=frontend_base,
        )
    )


@app.post("/api/guest/analyze", response_model=AnalyzeResponse)
async def guest_analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    md_text = read_mock_data(payload.mock_file)
    compact_md = compact_mock_data(md_text)
    zhihu_links = extract_zhihu_links(md_text)

    system_prompt = (
        "你是“看山平行宇宙”的认知轨迹分析引擎。"
        "你必须基于给定 markdown 行为数据生成结构化 JSON，不要输出任何多余文本。"
        "输出风格要像年度报告中的个人洞察：主题明确、数据可感、短句分条、克制精炼。"
    )
    user_prompt = f"""
任务：
1) 用户为游客模式，时间范围为 {payload.start_date} 到 {payload.end_date}。
2) 请阅读行为数据并输出“认知轨迹观察”与“星尘标签建议”。
3) 必须保持知乎语境，强调“内容如何影响认知轨迹”。
4) 不要写成长文，不要写散文；必须像年度报告：有主题、有数据、有分条观察。
5) 每条观察尽量 18-32 字，最多 3 条；数字必须来自行为数据或基于行为数据保守概括。

输出 JSON 结构（严格）：
{{
  "time_range": "YYYY-MM-DD ~ YYYY-MM-DD",
  "observation": {{
    "theme": "8-14字主题，例如：深夜科幻与人生重启",
    "key_metrics": ["深夜浏览 6 次", "连续搜索 4 个关键词", "收藏长回答 3 篇"],
    "overview": "一句总述，35-55字",
    "high_frequency_browsing": ["18-32字观察1", "18-32字观察2"],
    "late_night_searches": ["18-32字观察1", "18-32字观察2"],
    "likes_tendency": ["18-32字观察1", "18-32字观察2"],
    "interest_shift": "一句变化总结，35-55字",
    "reflective_question": "一句引导式问题，20字以内"
  }},
  "stardust_tag_suggestions": ["2-6字标签1", "2-6字标签2", "2-6字标签3", "2-6字标签4", "2-6字标签5"],
  "raw_excerpt_links": ["https://www.zhihu.com/....", "...最多2个"]
}}

行为数据摘要：
{compact_md}
"""
    result = await kimi_json_call(system_prompt, user_prompt)
    if "raw_excerpt_links" not in result or not result["raw_excerpt_links"]:
        result["raw_excerpt_links"] = zhihu_links[:2]
    return AnalyzeResponse(**result)


@app.post("/api/guest/generate-stardust", response_model=GenerateResponse)
async def generate_stardust(payload: GenerateRequest) -> GenerateResponse:
    if not payload.story_text.strip():
        raise HTTPException(status_code=400, detail="story_text is required")

    md_text = read_mock_data(payload.mock_file)
    compact_md = compact_mock_data(md_text)
    zhihu_links = extract_zhihu_links(md_text)

    system_prompt = (
        "你是“看山平行宇宙”的星尘生成引擎。"
        "你需要把该阶段轨迹拆分为关键节点链，并返回严格 JSON。"
    )
    user_prompt = f"""
任务：
1) 用户点击了“生成人生星尘”，请根据时间范围、故事文本、行为数据输出星尘卡片。
2) 节点链 nodes 至少 3 个，最多 5 个。
3) 第 1 或第 2 个关键节点必须包含 1-2 篇知乎阅读链接 reading_links。
4) 输出风格需接近“主宇宙节点卡片”：节点链 + 阶段总结 + 看山状态。

输出 JSON 结构（严格）：
{{
  "title": "人生星尘标题",
  "time_range": "{payload.start_date} ~ {payload.end_date}",
  "tags": ["标签1", "标签2", "标签3", "标签4"],
  "nodes": [
    {{
      "id": "node-1",
      "title": "节点标题",
      "description": "节点描述",
      "emotion": "情绪词",
      "reading_links": ["https://www.zhihu.com/..."]
    }}
  ],
  "summary": "阶段总结，100-180字",
  "liu_kanshan_state": "一句阶段看山状态"
}}

如果用户标题为空，请自动生成一个简洁标题。

用户输入标题：{payload.story_title}
用户故事文本：
{payload.story_text}

行为数据摘要：
{compact_md}
"""
    result = await kimi_json_call(system_prompt, user_prompt)

    nodes = result.get("nodes", [])
    if nodes:
        first_two = nodes[:2]
        has_links = any(item.get("reading_links") for item in first_two if isinstance(item, dict))
        if not has_links:
            nodes[0]["reading_links"] = zhihu_links[:2]
            result["nodes"] = nodes

    return GenerateResponse(**result)


@app.post("/api/guest/what-if", response_model=WhatIfResponse)
async def generate_what_if(payload: WhatIfRequest) -> WhatIfResponse:
    if not payload.original_nodes:
        raise HTTPException(status_code=400, detail="original_nodes is required")

    rewritten_opening = payload.rewritten_opening.strip()
    if len(rewritten_opening) < 8:
        raise HTTPException(status_code=400, detail="rewritten_opening is too short")
    if len(rewritten_opening) > 90:
        raise HTTPException(status_code=400, detail="rewritten_opening is too long")

    original_nodes_text = json.dumps([node.model_dump() for node in payload.original_nodes], ensure_ascii=False)

    system_prompt = (
        "你是“看山平行宇宙”的 What If 分叉分析引擎。"
        "你要从原卡片中提炼这个人的性格气质、兴趣方向、表达方式和行动习惯。"
        "你只允许做轻微改写：保持原阶段主题、时间背景、兴趣方向基本不变，"
        "只根据用户对第一个节点的一小段改写，讲述一条新的平行故事。"
        "必须输出严格 JSON，不要输出任何多余文本。"
    )
    user_prompt = f"""
任务：
1) 原卡片标题是《{payload.card_title}》，时间范围是 {payload.time_range}。
2) 用户只改写了第一个节点的一小段描述，请把它视为“新的起点”。
3) 改写幅度必须小，不能改掉整个人生主题，不能突然引入完全无关的新行业、新城市、新身份。
4) 不要再把原世界线里已经发生过的行为数据当作新世界线的事实依据。
5) 你只能参考原卡片本身：原节点链、原总结、原标签、原看山状态，从中提炼“这个人原本会如何思考、犹豫、行动、表达”。
6) 请基于这个微小改动，重新续写 3-5 个节点，形成 What If 平行路径。
7) 第一个 rewritten node 必须保留原来的起点标题，但 description 使用用户改写后的版本。
8) 新标签需与原标签大体一致，最多新增 2 个更细的标签。
9) 不要给新节点编造知乎文章链接，reading_links 请返回空数组。
10) 请额外生成 2-3 个适合去知乎搜索的新世界线关键词 zhihu_search_queries。
11) 搜索词必须贴合新世界线的节点主题，避免过宽泛的词，例如“人生”“选择”“内容”。

输出 JSON 结构（严格）：
{{
  "rewritten_title": "为这条平行宇宙分支生成一个简短标题，8-14字，不要照抄原标题，不要出现“平行分支”四个字",
  "rewritten_opening": "用户改写后的起点描述",
  "divergence_note": "一句简短说明这次分叉改变了什么，30-50字",
  "rewritten_nodes": [
    {{
      "id": "whatif-node-1",
      "title": "节点标题",
      "description": "节点描述",
      "emotion": "情绪词",
      "reading_links": []
    }}
  ],
  "rewritten_tags": ["标签1", "标签2", "标签3", "标签4"],
  "rewritten_summary": "100-160字阶段总结",
  "rewritten_state": "一句状态变化总结",
  "rewritten_liu_kanshan_state": "一句新的看山状态",
  "zhihu_search_queries": ["搜索词1", "搜索词2", "搜索词3"]
}}

原标签：
{json.dumps(payload.tags, ensure_ascii=False)}

原总结：
{payload.summary}

原看山状态：
{payload.liu_kanshan_state}

原节点链：
{original_nodes_text}

用户改写后的第一个节点描述：
{rewritten_opening}
"""
    result = await kimi_json_call(system_prompt, user_prompt)
    if not result.get("rewritten_title"):
        result["rewritten_title"] = f"{payload.card_title}的另一种可能"

    nodes = result.get("rewritten_nodes", [])
    if nodes:
        for node in nodes:
            if isinstance(node, dict):
                node["reading_links"] = []
        result["rewritten_nodes"] = nodes

    queries = result.get("zhihu_search_queries", [])
    if not isinstance(queries, list) or not queries:
        queries = [payload.card_title, rewritten_opening]
    result["zhihu_search_queries"] = [str(query).strip() for query in queries if str(query).strip()][:3]
    result["zhihu_search_results"] = [
        item.model_dump()
        for item in await search_zhihu_for_queries(result["zhihu_search_queries"], count_per_query=2, limit=5)
    ]
    result["node_search_results"] = [
        item.model_dump()
        for item in await search_zhihu_for_nodes(nodes, result.get("rewritten_tags", payload.tags))
    ]

    return WhatIfResponse(**result)
