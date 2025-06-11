import os

def collect_header_files(root_dir):
    header_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".h") or f.endswith(".hpp"):
                header_files.append(os.path.join(dirpath, f))
    return header_files
