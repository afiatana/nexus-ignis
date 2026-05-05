"""Abuse protection helpers for public submission endpoints."""

from __future__ import annotations

import ipaddress
import os
import socket
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse


DEFAULT_RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30"))
MAX_URL_LENGTH = int(os.environ.get("MAX_SUBMITTED_URL_LENGTH", "2048"))
RATE_WINDOW_SECONDS = 60


@dataclass(frozen=True)
class URLValidationResult:
    is_valid: bool
    normalized_url: str | None = None
    error: str | None = None


class InMemoryRateLimiter:
    """Simple fixed-window limiter for MVP deployments.

    This protects single-process deployments. For multi-worker or multi-instance
    production, replace this with Redis-backed limits.
    """

    def __init__(self, limit: int = DEFAULT_RATE_LIMIT, window_seconds: int = RATE_WINDOW_SECONDS):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True


def _is_blocked_ip(ip_text: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_text)
    except ValueError:
        return True

    return any([
        ip.is_private,
        ip.is_loopback,
        ip.is_link_local,
        ip.is_multicast,
        ip.is_reserved,
        ip.is_unspecified,
    ])


def _resolve_host_ips(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return []
    ips: list[str] = []
    for info in infos:
        sockaddr = info[4]
        if sockaddr:
            ips.append(sockaddr[0])
    return list(set(ips))


def validate_public_url(raw_url: str) -> URLValidationResult:
    """Validate that a submitted URL is a public HTTP(S) URL.

    Blocks localhost/private/link-local/reserved IP targets to reduce SSRF risk.
    """

    url = (raw_url or "").strip()
    if not url:
        return URLValidationResult(False, error="URL is required")

    if len(url) > MAX_URL_LENGTH:
        return URLValidationResult(False, error="URL is too long")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return URLValidationResult(False, error="Only http and https URLs are allowed")

    if not parsed.hostname:
        return URLValidationResult(False, error="URL hostname is required")

    hostname = parsed.hostname.strip().lower().rstrip(".")
    if hostname in {"localhost", "localhost.localdomain"}:
        return URLValidationResult(False, error="Localhost URLs are not allowed")

    try:
        if _is_blocked_ip(hostname):
            return URLValidationResult(False, error="Private or reserved IP URLs are not allowed")
    except Exception:
        pass

    resolved_ips = _resolve_host_ips(hostname)
    if not resolved_ips:
        return URLValidationResult(False, error="URL hostname cannot be resolved")

    if any(_is_blocked_ip(ip) for ip in resolved_ips):
        return URLValidationResult(False, error="URL resolves to a private or reserved IP")

    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path or "/",
        "",
        parsed.query,
        "",
    ))
    return URLValidationResult(True, normalized_url=normalized)


def get_rate_limit_key(remote_addr: str | None, forwarded_for: str | None = None) -> str:
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return remote_addr or "unknown"
