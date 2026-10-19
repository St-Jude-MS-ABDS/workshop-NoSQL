# Lecture 27 · Build a Genome Graph with Neo4j

> **Start here:** open [`workbook.ipynb`](workbook.ipynb) in JupyterLab.
> Prerequisites: the Docker databases are running and the Python environment is ready ([`../SETUP.md`](../SETUP.md)); Lecture 26 (graph basics).

## Learning objectives

At the end of this session, you will be able to:

- **Model** genomic data as a graph
- **Build** a genomic graph database with Neo4j
- Obtain **biological insights** via graph querying:
  - **Identify similar genomes** based on shared KO annotations
  - **Infer evolutionary patterns of KOs** across a phylogenetic structure

## The story

65 reference genomes, each described by the set of **KEGG Orthology (KO)** gene functions it carries, and the **taxonomic tree** they live in. Two questions:

1. *Which genomes have similar functional repertoires?* → a two-hop pattern `Genome → KO ← Genome` + the Jaccard index
2. *How are KOs distributed over the tree of life?* → variable-length paths up the tree; lowest common ancestor ("origin clade"); clade-specific vs patchy KOs; genome reduction and gene loss

```
(:Genome)-[:CONTAINS_KO {copies}]->(:KO)-[:IN_PATHWAY]->(:Pathway)
(:Genome)-[:CLASSIFIED_AS]->(:Taxon)-[:CHILD_OF]->(:Taxon)-[:CHILD_OF]->...   (the tree)
```

## Session flow (≈ 3 h)

| Step | Section of the workbook | Time |
|---|---|---|
| Model | 1 biology and data · 2 **graph modelling recipe** and design decisions · 3 warm-up with a 4-genome toy graph | 35 min |
| Import | 4 constraints, batch `UNWIND … MERGE` import, verification against the CSV row counts, optional `LOAD CSV` | 30 min |
| Explore | 5 counts, one genome, drawings, distributions (genome size, KO prevalence: the pan-genome "U") | 20 min |
| Query 1 | 6 **similar genomes**: shared KOs, Jaccard, all-pairs heat map, dendrogram, kNN graph | 40 min |
| Query 2 | 7 **KO evolution**: lineage paths, clade prevalence, origin clade, patterns, signature KOs, core shrinkage, gene loss | 45 min |
| Wrap-up | 8 limits, next steps · appendices: Cypher cheat sheet, practice quizzes, troubleshooting | 10 min |

## Files

| file | purpose |
|---|---|
| `workbook.ipynb` | the workshop (executed once, so the expected outputs are visible; interactive graph widgets appear when you run the cells) |
| [`../data/neo4j/`](../data/neo4j/) | the CSV files that are imported, described in [`../data/README.md`](../data/README.md) |
| [`../data/prepare/build_genome_graph_data.py`](../data/prepare/build_genome_graph_data.py) | how the CSV files were built from KEGG and NCBI Taxonomy (instructors only) |

## Notes for the instructor

- Runtime of the complete notebook: ~15 s (import ~6 s). Everything is local: no Aura / Hetionet account is required.
- The workbook is **re-runnable**: Section 4 starts by emptying the database, and all derived data (`n_genomes`, `SIMILAR_TO`, `ORIGIN_CLADE`) is rebuilt by the cells that create it.
- Good discussion points: (i) *Buchnera*'s nearest neighbours by raw count vs by Jaccard (convergent genome reduction); (ii) why `Enterobacterales` has a smaller core than `Enterobacteriaceae`; (iii) *nifH* as a patchy KO vs *psbA* as a clean clade innovation; (iv) taxonomy ≠ phylogeny.
- In the Neo4j Browser (<http://localhost:7474>) students can run the same Cypher by hand, for example `MATCH p=(:Genome {genome_id:'eco'})-[:CLASSIFIED_AS]->()-[:CHILD_OF*]->() RETURN p`.
