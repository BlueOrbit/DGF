import json
import subprocess
from types import SimpleNamespace

from dgf_feedback.branch_coverage_collector import (
    BranchCoverageCollector,
    _extract_branch_count,
    _iter_exported_functions,
)


def test_extract_branch_count_supports_dict_and_tuple():
    assert _extract_branch_count({"count": 3}) == 3
    assert _extract_branch_count([1, 2, 3, 4, 5]) == 5
    assert _extract_branch_count([1, 2]) == 0


def test_iter_exported_functions_supports_files_and_data_level_functions():
    output = {
        "data": [
            {"files": [{"functions": [{"name": "f1"}]}]},
            {"functions": [{"name": "f2"}]},
        ]
    }
    names = [func["name"] for func in _iter_exported_functions(output)]
    assert names == ["f1", "f2"]


def test_collect_branch_coverage_handles_mixed_schema(monkeypatch, tmp_path):
    work_dir = tmp_path / "cov"
    work_dir.mkdir()
    profraw = work_dir / "default.profraw"
    profraw.write_text("dummy")

    output = {
        "data": [
            {
                "files": [
                    {
                        "functions": [
                            {
                                "name": "foo",
                                "branches": [{"count": 1}, {"count": 0}],
                            },
                            {
                                "name": "bar",
                                "branches": [[1, 2, 3, 4, 2], [1, 2, 3, 4, 0]],
                            },
                        ]
                    }
                ]
            }
        ]
    }

    def fake_run(cmd, check, stdout, stderr, text):
        if "export" in cmd:
            return SimpleNamespace(returncode=0, stdout=json.dumps(output), stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    collector = BranchCoverageCollector()
    func_cov, overall = collector.collect_branch_coverage("dummy-bin", str(work_dir))

    assert func_cov["foo"] == 0.5
    assert func_cov["bar"] == 0.5
    assert overall == 0.5


def test_collect_branch_coverage_handles_invalid_json(monkeypatch, tmp_path):
    work_dir = tmp_path / "cov"
    work_dir.mkdir()
    (work_dir / "default.profraw").write_text("dummy")

    def fake_run(cmd, check, stdout, stderr, text):
        if "export" in cmd:
            return SimpleNamespace(returncode=0, stdout="not-json", stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    collector = BranchCoverageCollector()
    func_cov, overall = collector.collect_branch_coverage("dummy-bin", str(work_dir))

    assert func_cov == {}
    assert overall == 0.0


def test_collect_branch_coverage_handles_missing_tool(monkeypatch, tmp_path):
    work_dir = tmp_path / "cov"
    work_dir.mkdir()
    (work_dir / "default.profraw").write_text("dummy")

    def fake_run(cmd, check, stdout, stderr, text):
        raise FileNotFoundError("tool missing")

    monkeypatch.setattr(subprocess, "run", fake_run)
    collector = BranchCoverageCollector()
    func_cov, overall = collector.collect_branch_coverage("dummy-bin", str(work_dir))
    assert func_cov == {}
    assert overall == 0.0
