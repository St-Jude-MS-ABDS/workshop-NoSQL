#!/usr/bin/env python3
"""
build_genome_graph_data.py  --  INSTRUCTOR-ONLY data preparation script
=======================================================================

Students do NOT need to run this file. The CSV files it produces are already
committed in ``data/neo4j/`` so that the Neo4j workshop runs completely offline
(only the local Docker containers are needed).

Run it only if you want to rebuild or extend the dataset (e.g. add genomes):

    python data/prepare/build_genome_graph_data.py

It needs internet access and only the Python standard library.

What does it build?
-------------------
A small "genomes x KEGG Orthology (KO)" dataset that is later modelled as a graph:

    genomes.csv      one row per genome (a bacterial / archaeal reference genome)
    kos.csv          one row per KO (KEGG Orthology group = a gene "function family")
    genome_ko.csv    one row per (genome, KO) pair  -> becomes a relationship
    taxa.csv         one row per taxonomic group     (phylum, class, order ...)
    taxon_tree.csv   one row per (child taxon, parent taxon) -> the "phylogenetic" tree
    pathways.csv     one row per KEGG pathway map
    ko_pathway.csv   one row per (KO, pathway) pair

Where does the data come from?
------------------------------
* KEGG REST API (https://rest.kegg.jp)
    - which KOs does each genome carry   : /link/ko/<org>
    - genome statistics and NCBI taxid   : /get/gn:<T number>
    - KO names                           : /list/ko
    - KO -> pathway membership           : /link/pathway/ko , /list/pathway
  KEGG is free for academic use; see https://www.kegg.jp/kegg/legal.html before
  re-distributing the derived files outside of the course.
* NCBI Taxonomy (E-utilities, public domain)
    - the lineage (domain > phylum > class > order > family > genus > species)
      of every genome. We use this lineage as a stand-in for the "phylogenetic
      structure" (a tree of evolutionary relationships).

Design decisions (the "why" behind the code)
--------------------------------------------
1. ~65 genomes: large enough to see real evolutionary patterns (genome
   reduction in endosymbionts, patchy nitrogen fixation ...), small enough to
   load into Neo4j in seconds on a student laptop.
2. We keep only seven canonical ranks (see ``KEPT_RANKS``). NCBI also has many
   "no rank"/"clade" levels that would only add noise for beginners.
3. Everything is sorted before writing so that re-running the script produces
   byte-identical files (clean git diffs).
"""
import csv
import hashlib
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "neo4j"
CACHE_DIR = HERE / ".cache"          # raw downloads; git-ignored, makes re-runs fast
CACHE_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# 1. Which genomes?  (KEGG organism code -> comment about why it is interesting)
# --------------------------------------------------------------------------- #
# We want broad coverage of the bacterial tree plus a few archaea, and a few
# "teaching moments":
#   * several close relatives     -> similarity search has an obvious right answer
#   * reduced genomes (mge, mpn, buc, rpr, mle, bbu, ctr) -> gene loss
#   * nitrogen fixers scattered over the tree (sme, bja, ana, cac, gsu, mja...)
#       -> a KO (nifH) with a *patchy* distribution
#   * cyanobacteria -> photosynthesis KOs restricted to one clade
GENOMES = {
    # --- Gammaproteobacteria
    "eco": "E. coli K-12, the model bacterium",
    "ecs": "E. coli O157:H7, a second E. coli strain (nearest neighbour of eco?)",
    "sfl": "Shigella, hidden inside E. coli",
    "stm": "Salmonella Typhimurium",
    "kpn": "Klebsiella",
    "ype": "Yersinia pestis (plague)",
    "vch": "Vibrio cholerae",
    "hin": "Haemophilus influenzae",
    "pae": "Pseudomonas aeruginosa",
    "ppu": "Pseudomonas putida",
    "buc": "Buchnera, aphid endosymbiont (tiny genome)",
    "lpn": "Legionella",
    # --- Beta / Alpha / Delta / Epsilon proteobacteria
    "nme": "Neisseria meningitidis",
    "bpe": "Bordetella pertussis",
    "ccr": "Caulobacter",
    "sme": "Sinorhizobium meliloti (nitrogen fixer)",
    "bja": "Bradyrhizobium (nitrogen fixer)",
    "atu": "Agrobacterium",
    "rpr": "Rickettsia, obligate intracellular (reduced)",
    "wol": "Wolbachia, insect endosymbiont (reduced)",
    "mxa": "Myxococcus",
    "gsu": "Geobacter",
    "dvu": "Desulfovibrio",
    "hpy": "Helicobacter pylori",
    "cje": "Campylobacter jejuni",
    # --- Bacillota (Firmicutes)
    "bsu": "Bacillus subtilis (sporulation model)",
    "ban": "Bacillus anthracis",
    "sau": "Staphylococcus aureus",
    "lmo": "Listeria",
    "spn": "Streptococcus pneumoniae",
    "spy": "Streptococcus pyogenes",
    "lpl": "Lactiplantibacillus plantarum",
    "cdf": "Clostridioides difficile",
    "cac": "Clostridium acetobutylicum (nitrogen fixer)",
    "efa": "Enterococcus faecalis",
    # --- Mycoplasmatota (Mollicutes): minimal genomes
    "mpn": "Mycoplasma pneumoniae (minimal genome)",
    "mge": "Mycoplasma genitalium (minimal genome)",
    # --- Actinomycetota
    "mtu": "Mycobacterium tuberculosis",
    "mle": "Mycobacterium leprae (genome decay vs. M. tuberculosis)",
    "sco": "Streptomyces coelicolor (large genome)",
    "cgl": "Corynebacterium glutamicum",
    "bll": "Bifidobacterium longum",
    # --- Bacteroidota
    "bth": "Bacteroides thetaiotaomicron (gut)",
    "pgi": "Porphyromonas gingivalis",
    # --- Cyanobacteriota
    "syn": "Synechocystis (photosynthesis)",
    "pma": "Prochlorococcus (smallest photosynthetic cell)",
    "ana": "Nostoc / Anabaena (photosynthesis + nitrogen fixation)",
    "syf": "Synechococcus elongatus",
    # --- Spirochaetota, Chlamydiota and other bacterial phyla
    "bbu": "Borrelia (Lyme disease)",
    "tpa": "Treponema pallidum (syphilis)",
    "lil": "Leptospira",
    "ctr": "Chlamydia trachomatis",
    "dra": "Deinococcus radiodurans",
    "tth": "Thermus thermophilus",
    "tma": "Thermotoga maritima",
    "aae": "Aquifex aeolicus",
    "amu": "Akkermansia muciniphila",
    "fnu": "Fusobacterium nucleatum",
    # --- Archaea
    "mja": "Methanocaldococcus jannaschii (methanogen)",
    "hal": "Halobacterium salinarum",
    "sai": "Sulfolobus acidocaldarius",
    "pfu": "Pyrococcus furiosus",
    "tac": "Thermoplasma acidophilum",
    "mac": "Methanosarcina acetivorans (methanogen)",
    "nmr": "Nitrosopumilus maritimus",
}

# Only these NCBI ranks become Taxon nodes. "root" is added by us (see below).
KEPT_RANKS = ["domain", "phylum", "class", "order", "family", "genus", "species"]
ROOT = {"taxid": "131567", "name": "cellular organisms", "rank": "root"}

# KEGG "overview / global" maps (map011xx - map012xx) contain almost every KO.
# Keeping them would connect everything to everything, so we drop them.
GLOBAL_MAP = re.compile(r"^map01[12]\d\d$")

KEGG = "https://rest.kegg.jp"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


# --------------------------------------------------------------------------- #
# 2. Tiny helper: polite HTTP GET with an on-disk cache
# --------------------------------------------------------------------------- #
def fetch(url: str, pause: float = 0.4) -> str:
    """Download ``url`` (cached on disk). KEGG/NCBI allow ~3 requests/second.

    Python's own certificate store sometimes rejects networks that inspect TLS
    traffic (hospital / university proxies). ``curl`` uses the operating system's
    store, so we fall back to it when Python reports a certificate error.
    """
    key = hashlib.sha1(url.encode()).hexdigest()
    cache_file = CACHE_DIR / key
    if cache_file.exists():
        return cache_file.read_text()
    for attempt in range(4):
        try:
            try:
                with urllib.request.urlopen(url, timeout=120) as resp:
                    text = resp.read().decode("utf-8")
            except (ssl.SSLError, urllib.error.URLError) as exc:
                if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
                    raise
                text = subprocess.run(
                    ["curl", "-fsSL", "--max-time", "120", url],
                    check=True, capture_output=True, text=True,
                ).stdout
            cache_file.write_text(text)
            time.sleep(pause)
            return text
        except Exception as exc:  # network hiccup -> back off and retry
            print(f"  ! {exc} (retry {attempt + 1}/4) {url}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"could not download {url}")


def write_csv(name: str, header: list, rows: list) -> None:
    path = OUT_DIR / name
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  wrote {path.relative_to(HERE.parent.parent)}  ({len(rows):,} rows)")


# --------------------------------------------------------------------------- #
# 3. KEGG genome metadata
# --------------------------------------------------------------------------- #
def kegg_genome_table() -> dict:
    """org code -> KEGG T-number, from /list/genome ("T00007<TAB>eco; Escherichia coli ...")"""
    table = {}
    for line in fetch(f"{KEGG}/list/genome").splitlines():
        tnum, rest = line.split("\t", 1)
        codes, name = rest.split("; ", 1)
        table[codes.split(",")[0].strip()] = (tnum, name.strip())
    return table


def kegg_genome_info(tnum: str) -> dict:
    """Parse the flat-file record of one genome (taxid, assembly, #protein genes)."""
    text = fetch(f"{KEGG}/get/gn:{tnum}")
    info = {}
    m = re.search(r"TAXONOMY\s+TAX:(\d+)", text)
    info["taxid"] = m.group(1) if m else ""
    m = re.search(r"Assembly:\s*(GC[AF]_\d+\.\d+)", text)
    info["assembly"] = m.group(1) if m else ""
    m = re.search(r"Number of protein genes:\s+(\d+)", text)
    info["n_protein_genes"] = int(m.group(1)) if m else 0
    return info


def kegg_genome_kos(org: str) -> Counter:
    """KO -> number of genes of this genome annotated with that KO (copy number)."""
    counts = Counter()
    for line in fetch(f"{KEGG}/link/ko/{org}").splitlines():
        if not line.strip():
            continue
        _gene, ko = line.split("\t")
        counts[ko.replace("ko:", "")] += 1
    return counts


# --------------------------------------------------------------------------- #
# 4. NCBI taxonomy lineages
# --------------------------------------------------------------------------- #
def ncbi_lineages(taxids: list) -> dict:
    """taxid -> list of (taxid, name, rank) from the root down to (and including) the taxon."""
    xml_text = fetch(
        f"{EUTILS}/efetch.fcgi?db=taxonomy&retmode=xml&id={','.join(sorted(set(taxids)))}"
    )
    root = ET.fromstring(xml_text)
    lineages = {}
    for tax in root.findall("Taxon"):
        own = (tax.findtext("TaxId"), tax.findtext("ScientificName"), tax.findtext("Rank"))
        chain = [
            (t.findtext("TaxId"), t.findtext("ScientificName"), t.findtext("Rank"))
            for t in tax.findall("LineageEx/Taxon")
        ]
        lineages[own[0]] = chain + [own]
    return lineages


# --------------------------------------------------------------------------- #
# 5. Main: download -> reshape -> write CSV
# --------------------------------------------------------------------------- #
def main() -> None:
    print("1) genome metadata (KEGG)")
    table = kegg_genome_table()
    genomes = {}
    for org in sorted(GENOMES):
        tnum, name = table[org]
        genomes[org] = {"genome_id": org, "name": name, "kegg_id": tnum, **kegg_genome_info(tnum)}

    print("2) genome -> KO annotations (KEGG)")
    genome_kos = {org: kegg_genome_kos(org) for org in genomes}
    all_kos = sorted({ko for counts in genome_kos.values() for ko in counts})
    print(f"  {len(genomes)} genomes, {len(all_kos):,} distinct KOs")

    print("3) lineages (NCBI taxonomy)")
    lineages = ncbi_lineages([g["taxid"] for g in genomes.values()])
    taxa = {ROOT["taxid"]: (ROOT["name"], ROOT["rank"])}
    parent_of = {}                      # child taxid -> parent taxid
    species_of = {}                     # genome -> taxid of its species (or lowest kept rank)
    for org, g in genomes.items():
        chain = [t for t in lineages[g["taxid"]] if t[2] in KEPT_RANKS]
        previous = ROOT["taxid"]
        for taxid, name, rank in chain:
            taxa[taxid] = (name, rank)
            if taxid != previous:
                parent_of.setdefault(taxid, previous)
            previous = taxid
        species_of[org] = previous      # deepest kept taxon = species (normally)

    print("4) KO names and pathways (KEGG)")
    ko_set = set(all_kos)               # a set makes the "is this KO in our data?" test O(1)
    ko_names = {}
    for line in fetch(f"{KEGG}/list/ko").splitlines():
        ko, text = line.split("\t", 1)
        ko = ko.replace("ko:", "")
        if ko in ko_set:
            symbol, _, definition = text.partition("; ")
            if not definition:                       # a few KOs have no gene symbol
                symbol, definition = "", text
            ko_names[ko] = (symbol.strip(), definition.strip())
    pathway_names = {}
    for line in fetch(f"{KEGG}/list/pathway").splitlines():
        pid, name = line.split("\t", 1)
        pathway_names[pid.replace("path:", "")] = name
    ko_pathways = defaultdict(set)
    for line in fetch(f"{KEGG}/link/pathway/ko").splitlines():
        ko, pid = line.split("\t")
        ko, pid = ko.replace("ko:", ""), pid.replace("path:", "")
        # KEGG lists every pathway twice (mapNNNNN = reference, koNNNNN = KO-specific): keep "map"
        if pid.startswith("map") and ko in ko_set and not GLOBAL_MAP.match(pid):
            ko_pathways[ko].add(pid)
    used_pathways = sorted({p for ps in ko_pathways.values() for p in ps})

    print("5) writing CSV files")
    write_csv(
        "genomes.csv",
        ["genome_id", "name", "kegg_id", "taxid", "species_taxid", "assembly",
         "n_protein_genes", "n_kos"],
        [[o, g["name"], g["kegg_id"], g["taxid"], species_of[o], g["assembly"],
          g["n_protein_genes"], len(genome_kos[o])] for o, g in sorted(genomes.items())],
    )
    write_csv(
        "kos.csv",
        ["ko_id", "symbol", "definition"],
        [[ko, *ko_names.get(ko, ("", ""))] for ko in all_kos],
    )
    write_csv(
        "genome_ko.csv",
        ["genome_id", "ko_id", "copies"],
        [[org, ko, n] for org in sorted(genomes) for ko, n in sorted(genome_kos[org].items())],
    )
    rank_order = {"root": 0, **{r: i + 1 for i, r in enumerate(KEPT_RANKS)}}
    # rank_level: 0 = root, 1 = domain ... 7 = species. A number is easier to compare in
    # Cypher than the rank name ("which of two clades is deeper in the tree?").
    write_csv(
        "taxa.csv",
        ["taxid", "name", "rank", "rank_level"],
        [[tid, n, r, rank_order[r]]
         for tid, (n, r) in sorted(taxa.items(), key=lambda kv: (rank_order[kv[1][1]], kv[1][0]))],
    )
    write_csv(
        "taxon_tree.csv",
        ["child_taxid", "parent_taxid"],
        [[c, p] for c, p in sorted(parent_of.items(), key=lambda kv: (rank_order[taxa[kv[0]][1]], taxa[kv[0]][0]))],
    )
    write_csv(
        "pathways.csv",
        ["pathway_id", "name"],
        [[p, pathway_names[p]] for p in used_pathways],
    )
    write_csv(
        "ko_pathway.csv",
        ["ko_id", "pathway_id"],
        [[ko, p] for ko in all_kos for p in sorted(ko_pathways.get(ko, []))],
    )
    print("done.")


if __name__ == "__main__":
    main()
