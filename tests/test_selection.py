import unittest
from subbench.models import Node
from subbench.selection import diverse_nodes


def node(name, source, server=None):
    return Node('trojan://'+name, 'trojan', name, {'server': server or name}, source)


class SelectionTests(unittest.TestCase):
    def test_large_source_cannot_exclude_smaller_source(self):
        nodes = [node(str(i), 'large') for i in range(100)] + [node('small', 'small')]
        selected = diverse_nodes(nodes, 4)
        self.assertIn('small', [n.name for n in selected])
        self.assertEqual(len(selected), 4)

    def test_shared_server_cannot_fill_subscription(self):
        nodes = [node(str(i), str(i), 'same.example') for i in range(10)]
        nodes += [node('other', 'other')]
        self.assertEqual(len(diverse_nodes(nodes, 20, per_server=2)), 3)
