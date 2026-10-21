"""Validate both exports before packaging a new Pages deployment."""
import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def prepare(staging: Path, output: Path, mihomo: str):
    report = json.loads((staging / 'report.json').read_text())
    config = yaml.safe_load((staging / 'clash.yaml').read_text())
    raw = base64.b64decode((staging / 'v2ray.txt').read_text().strip(), validate=True).decode()
    links = [line for line in raw.splitlines() if line.strip()]
    proxies = config.get('proxies', [])
    if not proxies or not links or len(proxies) != len(links):
        raise ValueError('Empty or mismatched subscriptions; previous deployment is preserved')
    if any(n.get('latency_ms') is None or n.get('error') for n in report['nodes']):
        raise ValueError('Unverified nodes; refusing deployment')
    subprocess.run([mihomo, '-t', '-d', str(staging.resolve()), '-f', str((staging / 'clash.yaml').resolve())], check=True, capture_output=True)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copy(staging / 'clash.yaml', output / 'clash.yaml')
    shutil.copy(staging / 'v2ray.txt', output / 'shadowrocket.txt')
    # Public status deliberately excludes credentials, upstream URLs and raw error text.
    status = {k: report[k] for k in ('generated_at', 'node_count')}
    status.update({'test_environment': 'GitHub Actions cloud runner', 'speed_tested': False,
                   'failed_sources': len(report.get('source_errors', [])),
                   'nodes': [{'name': n['name'], 'protocol': n.get('type', ''), 'latency_ms': n['latency_ms']} for n in report['nodes']]})
    (output / 'status.json').write_text(json.dumps(status, ensure_ascii=False), encoding='utf-8')
    shutil.copy('site/index.html', output / 'index.html')
    (output / '.nojekyll').touch()
    return status


if __name__ == '__main__':
    prepare(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
