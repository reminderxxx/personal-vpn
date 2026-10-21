"""Bounded round-robin selection across sources, protocols and countries."""
from collections import defaultdict, deque
from .models import Node


def diverse_nodes(nodes: list[Node], limit: int, per_server: int = 2) -> list[Node]:
    buckets = defaultdict(deque)
    for node in nodes:
        buckets[(node.source, node.scheme, node.metadata.get('country_code', 'UN'))].append(node)
    selected = []
    servers = defaultdict(int)
    while buckets and (limit <= 0 or len(selected) < limit):
        for key in list(buckets):
            bucket = buckets[key]
            node = bucket.popleft()
            server = str((node.clash or {}).get('server', node.uri)).lower()
            if servers[server] < per_server:
                selected.append(node)
                servers[server] += 1
            if not bucket:
                del buckets[key]
            if limit > 0 and len(selected) >= limit:
                break
    return selected
