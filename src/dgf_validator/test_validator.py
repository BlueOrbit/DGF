import os
import subprocess
from types import SimpleNamespace

from dgf_validator.validator import Validator


def test_validate_source_uses_include_and_lib_flags(monkeypatch, tmp_path):
    src_file = tmp_path / "driver.c"
    src_file.write_text("int LLVMFuzzerTestOneInput(const unsigned char*d, unsigned long s){return 0;}")

    captured = {}

    def fake_run(cmd, check, stdout, stderr, text):
        captured["cmd"] = cmd
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    validator = Validator(
        clang_path="clang",
        work_dir=str(tmp_path / "validated"),
        lib_dir="/tmp/libs",
        libs=["cjson", "-lfoo"],
    )
    success, binary = validator.validate_source(str(src_file), include_dirs=["/tmp/include"])

    assert success is True
    assert os.path.basename(binary) == "driver"
    assert "-I" in captured["cmd"]
    assert "/tmp/include" in captured["cmd"]
    assert "-L/tmp/libs" in captured["cmd"]
    assert "-Wl,-rpath,/tmp/libs" in captured["cmd"]
    assert "-lcjson" in captured["cmd"]
    assert "-lfoo" in captured["cmd"]
