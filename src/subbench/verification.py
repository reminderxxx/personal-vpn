"""Spaced HTTPS probes through each node's dedicated local proxy listener."""
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlsplit

import requests


def probe(port: int) -> str | None:
    proxy = f'http://127.0.0.1:{port}'
    checks = [
        ('https://www.google.com/generate_204', 204, ''),
        ('https://www.cloudflare.com/cdn-cgi/trace', 200, 'ip='),
        ('https://chatgpt.com/', 200, 'chatgpt'),
    ]
    try:
        with requests.Session() as session:
            session.trust_env = False
            session.proxies = {'http': proxy, 'https': proxy}
            for url, status, marker in checks:
                with session.get(url, timeout=(4, 8), stream=True) as response:
                    if response.status_code != status:
                        return f'{urlsplit(url).hostname}: HTTP {response.status_code}'
                    if urlsplit(response.url).hostname != urlsplit(url).hostname:
                        return f'{urlsplit(url).hostname}: unexpected redirect'
                    body = bytearray()
                    started = time.monotonic()
                    for chunk in response.iter_content(8192):
                        body.extend(chunk)
                        if len(body) >= 262144 or time.monotonic() - started > 10:
                            break
                    if marker and marker.encode() not in bytes(body).lower():
                        return f'{urlsplit(url).hostname}: unexpected content'
                    if urlsplit(url).hostname == 'chatgpt.com' and any(
                        text in bytes(body).lower() for text in
                        (b'just a moment', b'cf-chl-', b'unsupported country', b'access denied')
                    ):
                        return 'chatgpt.com: challenge or restriction'
        return None
    except requests.RequestException as exc:
        return type(exc).__name__


def verify(nodes, ports, rounds=3, interval=20, workers=12):
    active = list(nodes)
    for index in range(rounds):
        if index and active:
            time.sleep(interval)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda node: probe(ports[node.name]), active))
        failures = Counter(error for error in results if error)
        active = [node for node, error in zip(active, results) if error is None]
        print(f'Strict HTTPS round {index+1}/{rounds}: {len(active)} passed; failures={dict(failures)}', flush=True)
        if not active:
            break
    for node in active:
        node.metadata['https_verification'] = {
            'rounds': rounds, 'interval_seconds': interval,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'chatgpt_homepage': True,
            'chatgpt_signed_in_conversation': 'not_tested',
        }
    return active
