"""
seed_public_db.py  --  the "database administrator" step of the MongoDB workshop
===============================================================================

In the classroom version of this workshop an administrator has already filled a
shared database called ``public`` which every student may *read* but not change.
On your own laptop YOU are the administrator, so this script does that job once:

    python seed_public_db.py            # or call seed_public() from the notebook

It uses the **admin** account (root) of the Docker MongoDB, because the restricted
``student`` account is not allowed to write to ``public``  -- that is exactly the
RBAC (role-based access control) idea you will explore in the notebook.

What it loads (all files live in ``../data/mongodb/``)
-----------------------------------------------------
public.example          2 documents  {_id: "sample.vcf", content: "<the whole VCF text>"}, ...
public.variant_catalog  50,000 documents, one per variant (used for the index demo)
public.samples          6 documents, one per sample (used for the $lookup "join" demo)

It is safe to run again: every collection is dropped and re-created, so you always
end up with exactly the same starting state.
"""
import gzip
import json
import os
import sys
from pathlib import Path

from pymongo import MongoClient

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "mongodb"

# Same variable names as docker-compose.yml, so one setting works for both.
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
DEFAULT_ADMIN_URI = f"mongodb://admin:workshop_admin@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"


def _read_jsonl(path: Path):
    """Yield one dict per line of a .jsonl (JSON Lines) file; .gz files are decompressed on the fly."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def _insert_in_batches(collection, documents, batch_size=10_000):
    """insert_many() in chunks: faster than one insert per document, and light on memory."""
    batch, total = [], 0
    for doc in documents:
        batch.append(doc)
        if len(batch) == batch_size:
            collection.insert_many(batch, ordered=False)
            total += len(batch)
            batch = []
    if batch:
        collection.insert_many(batch, ordered=False)
        total += len(batch)
    return total


def seed_public(admin_uri: str = None, verbose: bool = True) -> dict:
    """(Re)create the shared ``public`` database. Returns {collection: n_documents}."""
    client = MongoClient(admin_uri or os.getenv("MONGO_ADMIN_URI", DEFAULT_ADMIN_URI),
                         serverSelectionTimeoutMS=5000)
    client.admin.command("ping")          # fail fast, with a clear error, if the container is down
    public = client["public"]
    counts = {}

    # 1) VCF files stored as *text documents*: the whole file in a single field.
    public.drop_collection("example")
    docs = []
    for name, note in [("sample.vcf", "Used live during the workshop"),
                       ("assignment.vcf", "Used for the assignment")]:
        text = (DATA_DIR / name).read_text()
        docs.append({
            "_id": name,                    # the file name is a natural, unique primary key
            "format": "VCFv4.2",
            "description": note,
            "size_bytes": len(text.encode()),
            "content": text,
        })
    public["example"].insert_many(docs)
    counts["example"] = len(docs)

    # 2) A large collection of pre-parsed variants (no index on purpose -> see the explain() demo).
    public.drop_collection("variant_catalog")
    counts["variant_catalog"] = _insert_in_batches(
        public["variant_catalog"], _read_jsonl(DATA_DIR / "variant_catalog.jsonl.gz"))

    # 3) Sample metadata, referenced by name from the genotypes of each variant.
    public.drop_collection("samples")
    counts["samples"] = _insert_in_batches(public["samples"], _read_jsonl(DATA_DIR / "samples.jsonl"))

    if verbose:
        for name, n in counts.items():
            print(f"public.{name:<16} {n:>7,} documents")
    return counts


if __name__ == "__main__":
    seed_public(sys.argv[1] if len(sys.argv) > 1 else None)
