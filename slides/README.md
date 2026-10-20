# Lecture slides

| Deck | Lecture | Matching workbook | What changed in this revision |
|---|---|---|---|
| `24 NoSQL Basics …pptx` | 24 · NoSQL foundations | (concept lecture, poll app in `1-nosql-concept/`) | typo fix; **new:** roadmap of the hands-on sessions and a "get your laptop ready" checklist (Docker, `SETUP.md`) |
| `25 MongoDB workshop …pptx` | 25 · MongoDB hands-on | [`2-mongodb-workshop/workbook.ipynb`](../2-mongodb-workshop/workbook.ipynb) | Atlas / Codespaces slides replaced by the **Docker** lab; new slides follow the workbook: data model, **RBAC**, schema exploration, VCF → document, `_id`, **indexes + `explain()`**, embed vs reference, CRUD, aggregation ≈ `bcftools`, cheat sheet, assignment |
| `26 - GraphDB Basics …pptx` | 26 · Graph basics | [`3-graphdb-concept/workbook.ipynb`](../3-graphdb-concept/workbook.ipynb) | the remote Hetionet exploration is replaced by local **hands-on** slides (Cypher, `CREATE` vs `MERGE`, course graph, exercise, traversal, update/delete) and a **bridge to genomes**; invalid curly-quote Cypher fixed |
| `27 Neo4j workshop …pptx` | 27 · Neo4j genome workshop | [`4-neo4j-workshop/workbook.ipynb`](../4-neo4j-workshop/workbook.ipynb) | **fully redesigned**: the Aura import tutorial and Northwind (products / categories) examples are replaced by the genome graph: model → import → explore → *similar genomes* → *KO evolution on the tree* |

* The title and "Learning objectives" slides of every deck keep the original branding and wording.
* Every new slide has **speaker notes** that explain the slide in full sentences (useful for self-study: open *View ▸ Notes*).
* Numbers on the slides (counts, similarity scores, Ts/Tv, …) come from the executed workbooks.
