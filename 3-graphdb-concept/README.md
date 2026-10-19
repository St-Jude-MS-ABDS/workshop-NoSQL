# Lecture 26 · Graph Databases: the Basics

> **Start here:** open [`workbook.ipynb`](workbook.ipynb) in JupyterLab.
> Prerequisites: the Docker databases are running and the Python environment is ready ([`../SETUP.md`](../SETUP.md)).

## Learning objectives

- Understand the fundamental graph data model: **nodes**, **relationships**, **properties** (and labels, types, direction)
- Create, read, update and delete graph data with **Cypher**
- Understand **graph traversal**: answering questions by following relationships
- Recognise **genomic data as a graph** (bridge to Lecture 27)

## Session flow (≈ 1.5 h)

| # | Part of the workbook | Time |
|---|---|---|
| 0-1 | Connect; what is a graph? (Königsberg bridges) | 10 min |
| 2 | The property graph model, Cypher "ASCII art" | 10 min |
| 3 | `CREATE` vs `MERGE`: build the course graph (*MeetingRoom*, *Lecture*, *Lecturer*) | 15 min |
| 4 | `MATCH`/`WHERE`/`RETURN`, traversals, aggregation, drawing patterns | 20 min |
| 5 | **Exercise:** check in to the course (Student node + `ATTENDS` relationship) | 10 min |
| 6-7 | Update/delete; friends-of-friends = *shared-neighbour* pattern | 15 min |
| 8 | **Genomic data as a graph**: tiny Genome–KO graph; same pattern finds similar genomes | 10 min |

## Notes for the instructor

- The workbook uses the lecture example of the slides (course graph). The remote Hetionet / Aura instances are **no longer required**; Hetionet is mentioned as optional further reading.
- The workbook wipes the database at the start and at the end; Lecture 27 starts from an empty database.
