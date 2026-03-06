import subprocess
from types import SimpleNamespace

import pytest

import dgf_header_parser.ast_parser as ast_parser_module
import dgf_header_parser.extractor as extractor_module
from dgf_feedback.branch_coverage_collector import BranchCoverageCollector
from dgf_header_parser.ast_parser import ASTParser
from dgf_validator.fuzzer_runner import FuzzerRunner
from dgf_validator.validator import Validator


def test_branch_coverage_collector_handles_missing_profdata_binary(monkeypatch, tmp_path):
    work_dir = tmp_path
    (work_dir / "default.profraw").write_text("profile")
    collector = BranchCoverageCollector(profdata_path="missing-profdata", cov_path="llvm-cov")

    def fake_run(cmd, **kwargs):
        _ = kwargs
        if cmd[0] == "missing-profdata":
            raise FileNotFoundError("not found")
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    func_cov, overall = collector.collect_branch_coverage("fake-bin", str(work_dir))
    assert func_cov == {}
    assert overall == 0.0


def test_validator_returns_false_when_compiler_not_found(monkeypatch, tmp_path):
    src_file = tmp_path / "driver.c"
    src_file.write_text("int LLVMFuzzerTestOneInput(const unsigned char*d, unsigned long s){return 0;}")

    def fake_run(*args, **kwargs):
        _ = args, kwargs
        raise FileNotFoundError("clang not found")

    monkeypatch.setattr(subprocess, "run", fake_run)
    validator = Validator(clang_path="missing-clang", work_dir=str(tmp_path / "validated"))
    assert validator.validate_source(str(src_file)) == (False, None)


def test_fuzzer_runner_handles_missing_binary(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        _ = args, kwargs
        raise FileNotFoundError("missing binary")

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = FuzzerRunner(timeout_sec=1)
    assert runner.run_libfuzzer(str(tmp_path / "nope"), str(tmp_path)) is False


def test_ast_parser_extract_only_keeps_nodes_from_target_header(tmp_path):
    header = tmp_path / "a.h"
    other = tmp_path / "b.h"
    header.write_text("int a(void);")
    other.write_text("int b(void);")

    parser = ASTParser()
    def fake_extract_function(node):
        return {"name": node.spelling}

    parser.extract_function = fake_extract_function  # type: ignore[method-assign]

    function_decl_kind = ast_parser_module.cindex.CursorKind.FUNCTION_DECL

    class FakeNode:
        def __init__(self, spelling, file_path):
            self.kind = function_decl_kind
            self.spelling = spelling
            self.location = SimpleNamespace(file=SimpleNamespace(name=str(file_path)))

    tu = SimpleNamespace(
        spelling=str(header),
        cursor=SimpleNamespace(
            get_children=lambda: [
                FakeNode("in_header", header),
                FakeNode("from_other_file", other),
            ]
        ),
    )

    result = parser.extract(tu, source_file=str(header))
    assert [func["name"] for func in result["functions"]] == ["in_header"]


def test_extract_all_api_raises_when_every_header_fails(monkeypatch):
    class BrokenParser:
        def __init__(self, include_dirs=None):
            _ = include_dirs

        def parse(self, header_file):
            _ = header_file
            raise RuntimeError("parse failure")

    monkeypatch.setattr(extractor_module, "collect_header_files", lambda _: ["a.h", "b.h"])
    monkeypatch.setattr(extractor_module, "ASTParser", BrokenParser)

    with pytest.raises(RuntimeError, match="Failed to parse any header file"):
        extractor_module.extract_all_api("/tmp/headers", [])
