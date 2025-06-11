import argparse
import json
from header_scanner import collect_header_files
from ast_parser import ASTParser
from tqdm import tqdm

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
            print(f"Error parsing {h}: {e}")

    return all_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--header_dir", required=True, help="Path to library header files")
    parser.add_argument("--include_dirs", nargs='*', default=[], help="Additional include directories")
    parser.add_argument("--output", default="output.json", help="Output file to save results")
    args = parser.parse_args()

    results = extract_all_api(args.header_dir, args.include_dirs)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Extraction completed, output saved to {args.output}")
