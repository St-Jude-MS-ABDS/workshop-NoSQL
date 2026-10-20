# Data used in the workshops

Everything the notebooks need is in this folder: **no internet connection and no downloads are required** during the workshops.

```
data/
├── mongodb/                  Lecture 25 (MongoDB)   → synthetic variant data
│   ├── sample.vcf              250 variants, 3 samples   (used live)
│   ├── assignment.vcf          800 variants, 3 samples   (assignment)
│   ├── variant_catalog.jsonl.gz  50,000 parsed variants  (index / explain() demo)
│   └── samples.jsonl           6 sample metadata records ($lookup demo)
├── neo4j/                    Lectures 26-27 (Neo4j) → real genome × KO annotations
│   ├── genomes.csv             65 genomes
│   ├── kos.csv                 8,994 KEGG Orthology groups
│   ├── genome_ko.csv           90,445 (genome, KO) pairs
│   ├── taxa.csv                270 taxonomic groups
│   ├── taxon_tree.csv          269 child → parent links
│   ├── pathways.csv            356 KEGG pathways
│   └── ko_pathway.csv          7,579 (KO, pathway) pairs
└── prepare/                  the scripts that generated the files above (instructors only)
    ├── make_mongodb_data.py
    └── build_genome_graph_data.py
```

---

## `data/mongodb/`: synthetic variant data

**These files are made up.** They are produced by [`prepare/make_mongodb_data.py`](prepare/make_mongodb_data.py) with a fixed random seed (re-running gives identical files). Positions are random points on the GRCh38 chromosomes and the REF/ALT alleles are random bases, so there is **no patient data and no biological meaning**. The data mimics the *statistics* of a real call set so that the exercises give sensible answers:

| property | value |
|---|---|
| variant types | ~88% SNV, ~6% insertions, ~7% deletions; ~5% of the sites are multi-allelic (two ALT alleles) |
| transition / transversion ratio | ≈ 2.1 (like real human data) |
| `FILTER` | `PASS` (≈ 76%), `LowQual` (QUAL < 30), `LowDP` (combined depth < 10) |
| QUAL | a mixture: mostly high-confidence calls (mean ≈ 64) plus a noise component below 35 |
| INFO fields | `AC`, `AF`, `AN`, `DP`, `MQ` |
| FORMAT fields | `GT` (phased `|` and unphased `/`, 3% missing `./.`), `DP`, `GQ` |

| file | what | where it is used |
|---|---|---|
| `sample.vcf` | VCFv4.2, 250 variants on chromosomes 1, 2, 17, X; samples `SAMPLE_A/B/C` | stored in MongoDB as text (`public.example`), parsed in the workbook |
| `assignment.vcf` | VCFv4.2, 800 variants on chromosomes 7, 12, 19, 22; samples `SAMPLE_D/E/F` | the assignment |
| `variant_catalog.jsonl.gz` | **JSON Lines**, gzip-compressed: one JSON document per line, e.g. `{"chrom":"5","pos":40503267,"ref":"A","alt":["C"],"qual":31.2,"filter":"PASS","info":{...}}` | `public.variant_catalog` (index and `explain()` demo) |
| `samples.jsonl` | one document per sample: `_id`, `sex`, `population`, `mean_coverage_x`, `platform`, `vcf_file`, `synthetic` | `public.samples` ( `$lookup` demo) |

The files are loaded into MongoDB by [`../2-mongodb-workshop/seed_public_db.py`](../2-mongodb-workshop/seed_public_db.py) (called from the workbook).

---

## `data/neo4j/`: genomes × KEGG Orthology (real data)

A small comparative-genomics data set: **65 reference genomes** (58 bacteria, 7 archaea) annotated with **KEGG Orthology (KO)** gene-function groups, plus the **NCBI taxonomy** lineage of each genome. It is modelled as a graph in Lecture 27.

| file | one row is... | columns |
|---|---|---|
| `genomes.csv` | a genome | `genome_id` (KEGG organism code, e.g. `eco`), `name`, `kegg_id` (T number), `taxid` (NCBI strain taxid), `species_taxid`, `assembly`, `n_protein_genes`, `n_kos` |
| `kos.csv` | a KO | `ko_id` (e.g. `K04077`), `symbol` (gene symbols), `definition` |
| `genome_ko.csv` | genome *carries* KO | `genome_id`, `ko_id`, `copies` (number of genes annotated with that KO) |
| `taxa.csv` | a taxonomic group | `taxid`, `name`, `rank` (`root`, `domain`, `phylum`, `class`, `order`, `family`, `genus`, `species`), `rank_level` (0-7) |
| `taxon_tree.csv` | taxon *is a child of* taxon | `child_taxid`, `parent_taxid` |
| `pathways.csv` | a KEGG pathway map | `pathway_id` (e.g. `map00010`), `name` |
| `ko_pathway.csv` | KO *takes part in* pathway | `ko_id`, `pathway_id` |

Design notes:

* Only the **seven main ranks** of the NCBI lineage are kept (domain › phylum › class › order › family › genus › species), plus an artificial `root`; NCBI's many "clade / no rank" levels are dropped. Each genome points to its **species**.
* KEGG's global/overview maps (`map011xx`, `map012xx`) are **excluded** from the pathways: they contain nearly every KO and would connect everything to everything.
* The taxonomy stands in for a phylogeny. It is not an inferred evolutionary tree; see the "Limits" section of the Lecture 27 workbook.

### Sources, licences and attribution

| data | source | terms |
|---|---|---|
| genome ↔ KO annotation, KO names, pathway membership, KEGG organism codes | **KEGG** (Kanehisa & Goto, *Nucleic Acids Res* 2000; <https://www.kegg.jp>), retrieved through the KEGG REST API in October 2026 | KEGG is free for **academic use**; redistribution and commercial use are restricted. See <https://www.kegg.jp/kegg/legal.html>. **If this repository is made public beyond the course, check that these terms are respected**, or replace `data/neo4j` by files rebuilt from an openly licensed source. |
| taxonomic lineages | **NCBI Taxonomy** (<https://www.ncbi.nlm.nih.gov/taxonomy>) through E-utilities | public domain |

### Re-creating or extending the files

Only needed by instructors; students never run this. It needs internet access and Python (standard library only):

```bash
python data/prepare/build_genome_graph_data.py     # ~6 min the first time (polite 0.4 s pause between requests), seconds afterwards (cache)
python data/prepare/make_mongodb_data.py           # instant, no internet
```

To **add genomes**, add their KEGG organism code (see <https://www.genome.jp/kegg/catalog/org_list.html>) to the `GENOMES` dictionary at the top of `build_genome_graph_data.py` and re-run it. Raw downloads are cached in `data/prepare/.cache/` (git-ignored).

After re-generating the Neo4j files, re-run the Lecture 27 workbook; if you commit it, run `python tools/clean_notebook_outputs.py <notebook>` first to keep the file small.
