from types import SimpleNamespace

from dgf_header_parser.ast_parser import _is_node_from_target_header


def test_is_node_from_target_header_matches_path(tmp_path):
    header = tmp_path / "x.h"
    header.write_text("int x;")

    node = SimpleNamespace(location=SimpleNamespace(file=str(header)))
    assert _is_node_from_target_header(node, str(header)) is True


def test_is_node_from_target_header_handles_missing_location():
    node = SimpleNamespace(location=SimpleNamespace(file=None))
    assert _is_node_from_target_header(node, "/tmp/a.h") is False
