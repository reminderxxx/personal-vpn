import importlib.util
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from subbench.models import Node
from subbench.output import write_outputs

spec = importlib.util.spec_from_file_location('publish', Path(__file__).parents[1] / 'scripts/publish.py')
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)

class PublishTests(unittest.TestCase):
    def test_empty_output_preserves_existing_files(self):
        with TemporaryDirectory() as root:
            staging, output = Path(root)/'stage', Path(root)/'public'
            output.mkdir()
            (output/'clash.yaml').write_text('previous-success')
            write_outputs(staging, [], [])
            with self.assertRaises(ValueError):
                publish.prepare(staging, output, 'mihomo')
            self.assertEqual((output/'clash.yaml').read_text(), 'previous-success')

    def test_unverified_node_is_rejected(self):
        with TemporaryDirectory() as root:
            staging = Path(root)/'stage'
            node = Node('trojan://secret@example.com:443', 'trojan', 'test', {'name':'test','type':'trojan','server':'example.com','port':443,'password':'secret'}, 'source')
            write_outputs(staging, [node], [])
            with self.assertRaises(ValueError):
                publish.prepare(staging, Path(root)/'public', 'mihomo')

    @patch.object(publish.subprocess, 'run')
    def test_success_exports_both_formats_and_redacts_status(self, run):
        with TemporaryDirectory() as root:
            staging, output = Path(root)/'stage', Path(root)/'public'
            node = Node('trojan://secret@example.com:443', 'trojan', '<unsafe>', {'name':'test','type':'trojan','server':'example.com','port':443,'password':'secret'}, 'private-source', latency_ms=100)
            write_outputs(staging, [node], [])
            publish.prepare(staging, output, 'mihomo')
            self.assertEqual((output/'shadowrocket.txt').read_bytes(), (staging/'v2ray.txt').read_bytes())
            status = (output/'status.json').read_text()
            self.assertNotIn('private-source', status)
            self.assertNotIn('secret', status)
            self.assertEqual(json.loads(status)['node_count'], 1)
            run.assert_called_once()
