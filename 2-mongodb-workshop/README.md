# Lecture 25 · MongoDB Hands-On: VCF, `bcftools` and MongoDB

> **Start here:** open [`workbook.ipynb`](workbook.ipynb) in JupyterLab. It contains the full explanations, code and exercises.
> Prerequisites: the Docker databases are running and the Python environment is ready ([`../SETUP.md`](../SETUP.md)).

## Learning objectives

At the end of this session, the students will be able to:
- **Explain** the RBAC model of MongoDB
- **Understand** MongoDB CRUD operations: Create · Read · Update · Delete
- **Explore** the provided dataset schema with Python
- **Perform** queries on the provided dataset with Python
- **Explain** how indexes and aggregation work

## Session flow at a glance (2.5-3 h)

| # | Part of the workbook | Time |
|---|---|---|
| 0 | Setup, connection string, the MongoDB data model | 10-15 min |
| 1-2 | Admin step (fill `public`), **RBAC**: what may the `student` account do? | 15 min |
| 3 | Exercise 1: explore `public`, infer the schema with `$sample` | 15 min |
| 4 | Exercise 2: parse a VCF with `vcfpy`, insert, `_id`, **indexes and `explain()`**, embed vs reference | 40 min |
| 5 | Exercise 3: queries (filters, arrays, `$elemMatch`, projections, sort) | 20 min |
| 6-7 | Exercises 4-5: updates (operators, pipeline updates, `arrayFilters`) and guarded deletes | 25 min |
| 8 | Exercise 6: **aggregation** ≈ `bcftools stats` (`$group`, `$unwind`, `$bucket`, `$lookup`, `$out`) | 35 min |
| 9 | Wrap-up and the **assignment** (`assignment.vcf`) | 10 min |

## Why MongoDB for VCF-like data?

- Flexible schema for INFO/FORMAT fields, multi-ALT alleles and evolving annotations
- Arrays and nested documents map naturally onto a VCF record (one document per line)
- Rich aggregation framework for cohort-level summaries
- Secondary indexes for the common access patterns (chromosome/position, FILTER, QUAL, AF); horizontal scaling when needed

## Files

| file | purpose |
|---|---|
| `workbook.ipynb` | the workshop (executed once, so the expected outputs are visible) |
| `seed_public_db.py` | the "administrator" step: loads the shared `public` database from [`../data/mongodb/`](../data/mongodb/) (called from the notebook; can also be run as `python seed_public_db.py`) |
| [`../docker/mongo-init/01-create-users.js`](../docker/mongo-init/01-create-users.js) | creates the restricted `student` account (RBAC) when the container starts for the first time |
| [`../data/README.md`](../data/README.md) | description of the (synthetic) variant data |

## Notes for the instructor

- The classroom's managed Atlas cluster is **not needed any more**: each student has their own MongoDB in Docker. The same *roles* are reproduced locally (`read` on `public`, `readWrite` + `dbAdmin` on `student_db`), so the RBAC demo works as before.
- A student who already runs a MongoDB on port 27017 should start the container on another port (`MONGO_PORT=27018`, see `SETUP.md`) and start Jupyter with the same variable.
- To reset a student's whole environment: `cd docker && docker compose down -v && docker compose up -d`.

## References

- PyMongo docs: <https://pymongo.readthedocs.io/> · MongoDB manual: <https://www.mongodb.com/docs/manual/>
- vcfpy: <https://vcfpy.readthedocs.io/> · VCF specification: <https://samtools.github.io/hts-specs/VCFv4.2.pdf>
- bcftools manual: <http://samtools.github.io/bcftools/bcftools.html>
