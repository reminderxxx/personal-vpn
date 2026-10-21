import unittest
from unittest.mock import patch, MagicMock
from subbench.verification import verify, probe
from subbench.models import Node


class VerificationTests(unittest.TestCase):
    @patch('subbench.verification.time.sleep')
    @patch('subbench.verification.probe')
    def test_any_failed_round_removes_node(self, check, sleep):
        nodes = [Node('a', 'trojan', 'a', {}, 's'), Node('b', 'trojan', 'b', {}, 's')]
        check.side_effect = [None, None, 'timeout', None, None]
        result = verify(nodes, {'a': 20000, 'b': 20001}, interval=20, workers=1)
        self.assertEqual([n.name for n in result], ['b'])
        self.assertEqual(result[0].metadata['https_verification']['rounds'], 3)
        self.assertEqual(sleep.call_count, 2)

    @patch('subbench.verification.requests.Session')
    def test_chatgpt_challenge_is_not_accepted(self, session_class):
        session = session_class.return_value.__enter__.return_value
        responses = []
        for url, status, body in [
            ('https://www.google.com/generate_204', 204, b''),
            ('https://www.cloudflare.com/cdn-cgi/trace', 200, b'ip=1.2.3.4'),
            ('https://chatgpt.com/', 200, b'ChatGPT Just a moment'),
        ]:
            response = MagicMock(status_code=status, url=url)
            response.iter_content.return_value = [body]
            context = MagicMock()
            context.__enter__.return_value = response
            responses.append(context)
        session.get.side_effect = responses
        self.assertEqual(probe(20000), 'chatgpt.com: challenge or restriction')
        self.assertFalse(session.trust_env)
