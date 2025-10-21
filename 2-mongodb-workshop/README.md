# MongoDB Hands-On: VCF, bcftools, and MongoDB

## Learning Objectives

At the end of this session, the students will be able to:
- **Explain** RBAC model on MongoDB
- **Understand** MongoDB CRUD operations
  - Create
  - Read
  - Update
  - Delete
- **Explore** the profvided dataset schema with python
- **Perform** queries to the provided dataset with python
- **Explain** how aggregation works

## Session flow at a glance (2.5–3h)

1) Onboarding and connection (10–15m)
2) Explore public dataset (Read-only) (25–30m)
3) VCF parsing and ingestion into personal DB (40–50m)
4) Update and Delete with guardrails (20–25m)
5) Aggregations ≈ bcftools stats/query (35–40m)
6) Wrap-up and stretch goals (10m)

## Why MongoDB for VCF-like data (1 slide)

- Flexible schema for INFO/FORMAT fields, multi-ALT alleles, evolving annotations
- Rich aggregation framework for cohort-level summaries
- Horizontal scaling and secondary indexes for common query patterns (chrom/pos, FILTER, QUAL, AF)

## Pre-lab setup (5–10m)

- Install Python 3.10+ and dependencies for this course:
  - See `course_material/requirements.txt` and install into a virtualenv
- Ensure you can run Jupyter or Python scripts in your environment
- No local MongoDB needed. You will receive a managed Atlas connection string (mongodb+srv://)

## Exercise 0 — Get your connection string (mongo_uri)

- Go to the onboarding portal: abds.hpcs.stjude.org (SSO)
- After login, copy your personal `mongo_uri` for MongoDB Atlas
  - You will have `databaseAdmin` on your own database (e.g., `user_<id>`)
  - You will have `read` on the shared `public` database
- Verify connectivity quickly in Python:

```python
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "<paste-from-portal>")
client = MongoClient(MONGO_URI)
print(client.list_database_names())  # You should see 'public' and your personal DB
```

## Exercise 1 — Explore the `public` dataset (read-only)

Goal: learn to discover collections, sample documents, and indexes.

```python
db_public = client["public"]
print(db_public.list_collection_names())

coll = db_public["<pick_one_from_above>"]

print("One document:", coll.find_one())
print("Number of documents:", coll.estimated_document_count())
print("Indexes:", list(coll.list_indexes()))

# Basic finds
print(list(coll.find().limit(3)))
# Distinct values (e.g., FILTER status)
print(coll.distinct("filter"))
```

RBAC demo (intentional failure): try to delete one record in `public` and observe the authorization error, then explain why.

```python
try:
    coll.delete_one({})
except Exception as e:
    print("Expected RBAC error:", e)
```

Discuss: document shapes, key fields, potential indexes for common lookups.

## Exercise 2 — Parse VCF and ingest into your personal DB

We will ingest a VCF as documents with this minimal model:
{ chrom, pos, id, ref, alt: [str], qual: float, filter: str, info: dict }

Notes
- Use `vcfpy` (pure Python) for parsing
- If a record has multiple ALT alleles, store them as an array: `alt: ["A","T"]`
- Store INFO as a dict; keep numeric types numeric where possible

```python
import vcfpy
from pymongo import MongoClient, ASCENDING
import os

MONGO_URI = os.getenv("MONGO_URI", "<paste-from-portal>")
client = MongoClient(MONGO_URI)

db = client["<your_personal_db>"]  # e.g., user_<id>
variants = db["variants"]

reader = vcfpy.Reader.from_path("sample.vcf")  # or another path provided in class

docs = []
for rec in reader:
    alts = [str(a.value) for a in rec.ALT]
    info = {}
    for k, v in rec.INFO.items():
        # vcfpy returns scalars or lists; convert NumPy types if present
        info[k] = v
    doc = {
        "chrom": rec.CHROM,
        "pos": rec.POS,
        "id": rec.ID,
        "ref": rec.REF,
        "alt": alts,
        "qual": float(rec.QUAL) if rec.QUAL is not None else None,
        "filter": "PASS" if rec.FILTER is None or len(rec.FILTER) == 0 else ";".join(rec.FILTER),
        "info": info,
    }
    docs.append(doc)

if docs:
    variants.insert_many(docs, ordered=False)
    # Useful compound index for genomic lookups
    variants.create_index([("chrom", ASCENDING), ("pos", ASCENDING)])
    variants.create_index([("filter", ASCENDING)])
    variants.create_index([("qual", ASCENDING)])
print("Inserted", variants.estimated_document_count(), "documents")
```

Alternative source: the `public` database may also contain raw VCF text for you to parse. If provided, fetch a document that has fields like `{ name, text }` and pass a `StringIO` handle to `vcfpy.Reader.from_stream`.

## Exercise 3 — Update operations (on your DB)

Design two safe updates that add value without destroying data:
1) Add a quality flag: `is_high_quality = (qual >= 30 and filter == "PASS")`
2) Compute a simple AF bin from INFO.AF when available

```python
from pymongo import UpdateOne

# 1) Quality flag
variants.update_many(
    {"qual": {"$ne": None}},
    [{
        "$set": {
            "is_high_quality": {
                "$and": [
                    {"$gte": ["$qual", 30]},
                    {"$eq": ["$filter", "PASS"]}
                ]
            }
        }
    }]
)

# 2) AF bin when INFO.AF exists
variants.update_many(
    {"info.AF": {"$exists": True}},
    [{
        "$set": {
            "af_bin": {
                "$switch": {
                    "branches": [
                        {"case": {"$lt": [{"$first": "$info.AF"}, 0.01]}, "then": "<1%"},
                        {"case": {"$lt": [{"$first": "$info.AF"}, 0.05]}, "then": "1-5%"},
                        {"case": {"$lt": [{"$first": "$info.AF"}, 0.5]},  "then": "5-50%"}
                    ],
                    "default": ">=50%"
                }
            }
        }
    }]
)
```

## Exercise 4 — Delete operations (on your DB)

Task: remove obviously low-quality sites, e.g., `qual < 10` or `filter != "PASS"`.

1) Count how many would be deleted using a find query
2) Perform `delete_many` with that predicate
3) Confirm the new count

```python
pred = {"$or": [{"qual": {"$lt": 10}}, {"filter": {"$ne": "PASS"}}]}
to_remove = variants.count_documents(pred)
print("Would remove:", to_remove)
res = variants.delete_many(pred)
print("Deleted:", res.deleted_count)
```

## Exercise 5 — Aggregations equivalent to bcftools

We will emulate a few common bcftools queries/stats.

1) Count by chromosome (≈ `bcftools query -f '%CHROM\n' | sort | uniq -c`)
```python
list(variants.aggregate([
  {"$group": {"_id": "$chrom", "n": {"$sum": 1}}},
  {"$sort": {"n": -1}}
]))
```

2) PASS vs non-PASS counts (≈ `bcftools view -f PASS`)
```python
list(variants.aggregate([
  {"$group": {"_id": "$filter", "n": {"$sum": 1}}},
  {"$sort": {"n": -1}}
]))
```

3) Transition/Transversion (Ts/Tv) for SNPs
```python
pipeline = [
  {"$match": {"$expr": {"$and": [
      {"$eq": [{"$strLenCP": "$ref"}, 1]},
      {"$in": [1, {"$map": {"input": "$alt", "as": "a", "in": {"$strLenCP": "$$a"}}}]}
  ]}}},
  {"$unwind": "$alt"},
  {"$project": {
      "class": {
        "$switch": {
          "branches": [
            {"case": {"$in": [["$ref", "$alt"], [["A","G"],["G","A"],["C","T"],["T","C"]]]}, "then": "transition"}
          ],
          "default": "transversion"
        }
      }
  }},
  {"$group": {"_id": "$class", "n": {"$sum": 1}}}
]
print(list(variants.aggregate(pipeline)))
```

4) QUAL histogram (≈ `bcftools query -f '%QUAL\n' | hist`)
```python
bins = [0,10,20,30,40,50,60,1000]
pipeline = [
  {"$match": {"qual": {"$ne": None}}},
  {"$bucket": {
    "groupBy": "$qual",
    "boundaries": bins,
    "default": ">=1000",
    "output": {"count": {"$sum": 1}}
  }}
]
print(list(variants.aggregate(pipeline)))
```

Optionally, write aggregation outputs into a new collection:

```python
db["variant_stats"].insert_many(list(variants.aggregate(pipeline)))
```

## Indexing recommendations

- Always index by genomic location: `{"chrom": 1, "pos": 1}`
- Add selective indexes used by your queries: `filter`, `qual`, and commonly used `info` keys
- Consider compound indexes for frequent filters, e.g., `{ filter: 1, chrom: 1 }`

## bcftools ↔ MongoDB quick mapping

- bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\n' → `find({}, {chrom:1,pos:1,ref:1,alt:1,qual:1})`
- bcftools view -f PASS → `find({filter: 'PASS'})`
- bcftools stats (counts by type) → `$group` pipelines and projections

## Permissions and safety

- Read-only on `public` prevents accidental modification; demonstrate the error and its meaning
- Full control only in your personal database; encourage defensive deletes using a pre-check `count_documents`

## Stretch goals

- Model multi-allelic records as one doc vs. one doc per alt allele; compare trade-offs
- Store genotypes (FORMAT/GT) for a subset and compute per-sample stats
- Add a text index to search INFO annotations by keyword

## References

- PyMongo docs: https://pymongo.readthedocs.io/
- vcfpy: https://vcfpy.readthedocs.io/
- bcftools manual: http://samtools.github.io/bcftools/bcftools.html