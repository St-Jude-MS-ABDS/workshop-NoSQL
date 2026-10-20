#!/usr/bin/env python3
"""
check_setup.py  --  "Is my laptop ready for the workshop?"
=========================================================

Run it from the repository root, with your virtual environment activated:

    python scripts/check_setup.py

It checks, in order, and tells you how to fix anything that is wrong:

  1. Python version and the packages from requirements.txt
  2. the data files in data/
  3. MongoDB  (container running? admin and student accounts working?)
  4. Neo4j    (container running? password correct?)

It only READS; nothing is changed in the databases.
"""
import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILED = []


def ok(msg):
    print(f"  ✅ {msg}")


def bad(msg, fix):
    print(f"  ❌ {msg}\n     → {fix}")
    FAILED.append(msg)


# --------------------------------------------------------------------------------------------- 1. Python
print("1) Python and packages")
if sys.version_info >= (3, 10):
    ok(f"Python {sys.version.split()[0]}")
else:
    bad(f"Python {sys.version.split()[0]} is too old", "install Python 3.10 or newer")

PACKAGES = {  # import name -> pip name
    "jupyterlab": "jupyterlab", "pandas": "pandas", "matplotlib": "matplotlib", "scipy": "scipy",
    "networkx": "networkx", "pymongo": "pymongo", "vcfpy": "vcfpy", "neo4j": "neo4j", "neo4j_viz": "neo4j_viz",
}
missing = []
for module, pip_name in PACKAGES.items():
    try:
        importlib.import_module(module)
    except ImportError:
        missing.append(pip_name)
if missing:
    bad("missing packages: " + ", ".join(missing), "activate your virtual environment, then: pip install -r requirements.txt")
else:
    ok(f"all {len(PACKAGES)} required packages are installed")

# --------------------------------------------------------------------------------------------- 2. data
print("2) Data files")
expected = {
    "data/mongodb": ["sample.vcf", "assignment.vcf", "variant_catalog.jsonl.gz", "samples.jsonl"],
    "data/neo4j": ["genomes.csv", "kos.csv", "genome_ko.csv", "taxa.csv", "taxon_tree.csv", "pathways.csv", "ko_pathway.csv"],
}
absent = [f"{folder}/{name}" for folder, names in expected.items() for name in names if not (ROOT / folder / name).exists()]
if absent:
    bad("missing data files: " + ", ".join(absent), "run `git pull` (the files are part of the repository)")
else:
    ok("all data files are present")

# --------------------------------------------------------------------------------------------- 3. MongoDB
print("3) MongoDB")
host, port = os.getenv("MONGO_HOST", "localhost"), os.getenv("MONGO_PORT", "27017")
try:
    from pymongo import MongoClient

    for who, uri in [("admin", f"mongodb://admin:workshop_admin@{host}:{port}/?authSource=admin"),
                     ("student", f"mongodb://student:student_password@{host}:{port}/?authSource=admin")]:
        client = MongoClient(os.getenv("MONGO_URI", uri) if who == "student" else uri, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        roles = client.admin.command("connectionStatus")["authInfo"]["authenticatedUserRoles"]
        ok(f"connected as '{who}' (roles: {', '.join(r['role'] + '@' + r['db'] for r in roles)})")
        client.close()
except Exception as err:  # noqa: BLE001 - we want to show ANY problem in friendly words
    bad(f"cannot use MongoDB on {host}:{port}  ({type(err).__name__})",
        "start it with `cd docker && docker compose up -d` and wait until `docker compose ps` says healthy. "
        "If another MongoDB already uses port 27017, use MONGO_PORT=27018 (see SETUP.md)")

# --------------------------------------------------------------------------------------------- 4. Neo4j
print("4) Neo4j")
uri = os.getenv("NEO4J_URI", f"bolt://localhost:{os.getenv('NEO4J_BOLT_PORT', '7687')}")
try:
    from neo4j import GraphDatabase

    with GraphDatabase.driver(uri, auth=(os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop_neo4j"))) as driver:
        driver.verify_connectivity()
        ok(f"connected to {driver.get_server_info().agent} at {uri}")
except Exception as err:  # noqa: BLE001
    bad(f"cannot use Neo4j at {uri}  ({type(err).__name__})",
        "start it with `cd docker && docker compose up -d`; the first start takes ~30 s. Browser UI: http://localhost:7474")

# --------------------------------------------------------------------------------------------- summary
print()
if FAILED:
    print(f"{len(FAILED)} problem(s) found. Fix the ❌ lines above (the → arrow says how), then run this script again.")
    sys.exit(1)
print("🎉 Everything is ready. Start JupyterLab with:  jupyter lab")
