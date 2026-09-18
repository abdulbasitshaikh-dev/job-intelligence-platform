from app.core.security import is_safe_webhook_url


def test_ssrf_blocked_urls():
    blocked = [
        "http://localhost/webhook",
        "http://127.0.0.1:8000/hook",
        "http://169.254.169.254/latest/meta-data",
        "http://10.0.0.1/notify",
        "http://172.16.0.1/notify",
        "http://192.168.1.100/notify",
        "ftp://example.com/hook",
        "javascript:alert(1)",
        "file:///etc/passwd",
        "",
        "not_a_url",
    ]
    for url in blocked:
        assert is_safe_webhook_url(url) is False, f"URL {url} should have been blocked"


def test_ssrf_allowed_public_urls():
    allowed = [
        "https://hooks.slack.com/services/T00/B00/X00",
        "https://discord.com/api/webhooks/123/abc",
        "https://api.example.com/webhooks/incoming",
        "http://example.com/webhook",
    ]
    for url in allowed:
        assert is_safe_webhook_url(url) is True, f"Public URL {url} should be permitted"
