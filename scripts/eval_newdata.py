import json
import os
import argparse
import datetime

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("sem_file")
ARGS = arg_parser.parse_args()
JSEM_DIR = "jsem_plain"
RESULT_DIR = "results"
OUTPUT_FILE = "new_results.html"

with open("jsem_templates/jsem.json", "r") as f:
    data = json.load(f)

for d in data:
    id = d["id"]
    with open(f"cache/{id}.txt", "w") as f:
        for premise in d["premises"]:
            f.write(premise + "\n")
        f.write(d["hypothesis"] + "\n")
    cmd = f"scripts/rte.sh cache/{id}.txt {ARGS.sem_file}"
    os.system(cmd)
    os.remove(f"cache/{id}.txt")
