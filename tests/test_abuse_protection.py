from web.abuse_protection import InMemoryRateLimiter, validate_public_url


def test_validate_public_url_accepts_https_domain(monkeypatch):
    monkeypatch.setattr('web.abuse_protection._resolve_host_ips', lambda hostname: ['93.184.216.34'])

    result = validate_public_url('HTTPS://Example.COM/path?q=1#frag')

    assert result.is_valid is True
    assert result.normalized_url == 'https://example.com/path?q=1'


def test_validate_public_url_rejects_localhost():
    result = validate_public_url('http://localhost:5000/admin')

    assert result.is_valid is False


def test_validate_public_url_rejects_private_ip():
    result = validate_public_url('http://192.168.1.1/router')

    assert result.is_valid is False


def test_validate_public_url_rejects_private_dns_resolution(monkeypatch):
    monkeypatch.setattr('web.abuse_protection._resolve_host_ips', lambda hostname: ['10.0.0.5'])

    result = validate_public_url('https://internal.example.com')

    assert result.is_valid is False


def test_validate_public_url_rejects_unsupported_scheme():
    result = validate_public_url('file:///etc/passwd')

    assert result.is_valid is False


def test_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60)

    assert limiter.is_allowed('client') is True
    assert limiter.is_allowed('client') is True
    assert limiter.is_allowed('client') is False
