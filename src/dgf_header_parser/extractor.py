import argparse
import json
import logging

from tqdm import tqdm

from dgf_header_parser.ast_parser import ASTParser
from dgf_header_parser.header_scanner import collect_header_files

LOGGER = logging.getLogger(__name__)

def extract_all_api(header_dir, include_dirs):
    headers = collect_header_files(header_dir)
    parser = ASTParser(include_dirs)

    all_results = []
    for h in tqdm(headers, desc="Parsing Headers"):
        try:
            tu = parser.parse(h)
            result = parser.extract(tu)
            all_results.append({
                "file": h,
                "result": result
            })
        except Exception as e:
            LOGGER.warning("Error parsing %s: %s", h, e)

    return all_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--header_dir", required=True, help="Path to library header files")
    parser.add_argument("--include_dirs", nargs='*', default=[], help="Additional include directories")
    parser.add_argument("--output", default="output.json", help="Output file to save results")
    args = parser.parse_args()

    results = extract_all_api(args.header_dir, args.include_dirs)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    LOGGER.info("Extraction completed, output saved to %s", args.output)
