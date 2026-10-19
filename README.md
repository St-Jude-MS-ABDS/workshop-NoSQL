# ABDS 8131 Unit 5 - Bioinformatic Applications with NoSQL


## Fact Sets
| Key | Value |
| ------- | ----- |
| Course | NoSQL |
| Date | 10/22/2025 – 10/23/2025 |
| Lecture num. | 24 ~ 27 |


## Learning Objectives

- **Lecture 24: NoSQL Introduction**, students will be able to:
  - Explain how & why NoSQL databases emerged to address modern data challenges
  - Compare major NoSQL data models
    - Document (e.g. MongoDB)
    - Key-Value (e.g. Redis)
    - Wide-column (e.g. Cassandra)
    - Graph (e.g. Neo4j)
  - Acknowledge the use case of NoSQL data models in bioscience
  
- **Lecture 25: Mongodb Hands-on**, students will be able to:
  - Explain RBAC model on MongoDB
  - Understand MongoDB CRUD operations:
    - Create
    - Read
    - Update
    - Delete
  - Explore the provided dataset schema with python
  - Perform queries to the provided dataset with python
  - Explain how aggregation works

- **Lecture 26: Graph Database Basics**, students will be able to:
  - Understand the fundamental data model
    - Nodes
    - Relationships
    - Properties
  - Understand graph traversal techniques
  - Understand genomic data as a graph

- **Lecture 27: Neo4j Hands-on (genome graph)**, students will be able to:
  - Model genomic data as a graph
  - Build a genomic graph database with Neo4j
  - Perform biological insights via graph querying
    - Identify similar genomes based on shared KO annotations
    - Infer evolutionary patterns of KOs across a phylogenetic structure


## Quick start (on your own laptop)

Everything runs locally: **MongoDB** and **Neo4j** in Docker containers, the workbooks in JupyterLab. No cloud account, no internet needed after the first install.

```bash
git clone https://github.com/St-Jude-MS-ABDS/workshop-NoSQL.git && cd workshop-NoSQL
(cd docker && docker compose up -d)                    # 1. start MongoDB + Neo4j
python3 -m venv .venv && source .venv/bin/activate     # 2. Python environment (Windows: see SETUP.md)
pip install -r requirements.txt
python scripts/check_setup.py                          # 3. is everything ready?
jupyter lab                                            # 4. open the workbooks
```

👉 **Step-by-step instructions (Windows / macOS / Linux) and troubleshooting: [`SETUP.md`](SETUP.md).**

## What is where

| Folder | Lecture | Content |
|---|---|---|
| [`1-nosql-concept/`](1-nosql-concept/) | 24 · NoSQL basics | history of databases, the live poll web app (FastAPI + MongoDB) |
| [`2-mongodb-workshop/`](2-mongodb-workshop/) | 25 · MongoDB hands-on | `workbook.ipynb`: RBAC, CRUD, indexes, aggregation on VCF data |
| [`3-graphdb-concept/`](3-graphdb-concept/) | 26 · Graph basics | `workbook.ipynb`: nodes, relationships, properties, Cypher |
| [`4-neo4j-workshop/`](4-neo4j-workshop/) | 27 · Neo4j hands-on | `workbook.ipynb`: **genome graph**: similar genomes and KO evolution over a phylogenetic tree |
| [`data/`](data/README.md) | | all data files + the scripts that generated them |
| [`docker/`](docker/) | | `docker-compose.yml` (MongoDB + Neo4j) |
| [`slides/`](slides/) | | the lecture slides (PowerPoint), consistent with the workbooks |
| [`scripts/`](scripts/) · [`tools/`](tools/) | | `check_setup.py` for students; notebook clean-up tool for maintainers |

### Pre-requisites
- Basic Python Skills
  - Understand python data structures (list, dict, set, tuple)
  - Can write simple functions to manipulate data
  - Familiar with Python syntax and control flow (if, for, while)
- Basic SQL Skills
  - Understand SQL database concepts (tables, rows, columns)
  - Can write simple SQL queries to manipulate data

### Course Description

This two-day intensive course offers a specialized exploration of NoSQL databases, emphasizing their role in bioinformatics and data science. Participants will investigate key architectures and use cases of NoSQL systems—including document stores (MongoDB/JSON) and graph databases—to manage and analyze complex biological datasets, such as genomic sequences, pangenomic structures, and molecular interaction networks.


## Alternative: run with GitHub Codespaces

> Prefer the local setup above (it is what the workbooks are tested with). In a Codespace, open a terminal and follow Steps 3 and 5 of [`SETUP.md`](SETUP.md): the default Codespaces image includes Docker. The ports of MongoDB (27017) and Neo4j (7474, 7687) are forwarded automatically.

Github Codespaces provides a cloud-based environment that is consistent, reproducible, and easy to use for audiences. 

Setting up the codespace from scratch might be slow, we have prebuilt available when a change on `.devcontainer/devcontainer.json` is made on `main` branch.
[codespace example for Jupyter Notebooks](https://github.com/github/codespaces-jupyter)