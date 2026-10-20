#!/usr/bin/env python3
"""
make_mongodb_data.py  --  INSTRUCTOR-ONLY data preparation script
==================================================================

Students do NOT need to run this file: its output is already committed in
``data/mongodb/``.  Re-run it only if you want to change the teaching data:

    python data/prepare/make_mongodb_data.py

Only the Python standard library is needed, and no internet access.

What does it build?
-------------------
    sample.vcf                 ~250 variants, 3 samples  -> used live in the workshop
    assignment.vcf             ~800 variants, 3 samples  -> used for the assignment
    variant_catalog.jsonl.gz   50,000 pre-parsed variants -> used for the index / explain() demo
    samples.jsonl              metadata of the 6 samples  -> used for the $lookup ("join") demo

Why synthetic (made-up) data?
-----------------------------
* It is small and fast, so every cell in the workbook runs in seconds on a laptop.
* We control the "story": variants of several types (SNV, insertion, deletion,
  multi-allelic), a realistic transition/transversion ratio (~2), a mix of
  PASS / LowQual / LowDP records, so that every exercise gives a meaningful answer.
* There is NO patient data. Positions are random points on the human GRCh38
  chromosomes and the REF/ALT alleles are random bases: do not use it for biology!

The generator is deterministic (fixed random seed) -> same files every run.
"""
import gzip
import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "mongodb"
OUT.mkdir(parents=True, exist_ok=True)

# GRCh38 chromosome lengths (bp). Positions are drawn inside these ranges.
CONTIG_LENGTH = {
    "1": 248_956_422, "2": 242_193_529, "3": 198_295_559, "4": 190_214_555,
    "5": 181_538_259, "6": 170_805_979, "7": 159_345_973, "8": 145_138_636,
    "9": 138_394_717, "10": 133_797_422, "11": 135_086_622, "12": 133_275_309,
    "13": 114_364_328, "14": 107_043_718, "15": 101_991_189, "16": 90_338_345,
    "17": 83_257_441, "18": 80_373_285, "19": 58_617_616, "20": 64_444_167,
    "21": 46_709_983, "22": 50_818_468, "X": 156_040_895, "Y": 57_227_415,
}
BASES = "ACGT"
TRANSITION = {"A": "G", "G": "A", "C": "T", "T": "C"}   # purine<->purine, pyrimidine<->pyrimidine


# --------------------------------------------------------------------------- #
# 1. One random variant
# --------------------------------------------------------------------------- #
def random_alleles(rng: random.Random):
    """Return (REF, [ALT, ...]) for a random variant of a random type."""
    kind = rng.random()
    ref = rng.choice(BASES)
    if kind < 0.87:                                    # SNV (single nucleotide variant)
        if rng.random() < 0.67:                        # transitions are ~2x more common than
            return ref, [TRANSITION[ref]]              # transversions in real data (Ts/Tv ~ 2)
        return ref, [rng.choice([b for b in BASES if b not in (ref, TRANSITION[ref])])]
    if kind < 0.92:                                    # insertion: REF is 1 base, ALT is longer
        return ref, [ref + "".join(rng.choices(BASES, k=rng.randint(1, 3)))]
    if kind < 0.98:                                    # deletion: REF is longer, ALT is 1 base
        return ref + "".join(rng.choices(BASES, k=rng.randint(1, 3))), [ref]
    others = [b for b in BASES if b != ref]            # multi-allelic SNV: two ALT alleles
    return ref, rng.sample(others, 2)


def random_quality(rng: random.Random) -> float:
    """80% of calls look like true variants (high QUAL), 20% like noise (low QUAL)."""
    if rng.random() < 0.80:
        return round(min(rng.gammavariate(8, 8), 500), 1)    # mean ~64
    return round(rng.uniform(3, 35), 1)


def random_variant(rng: random.Random, contigs: list, samples: list) -> dict:
    chrom = rng.choice(contigs)
    ref, alts = random_alleles(rng)
    qual = random_quality(rng)
    dp = max(2, int(rng.gauss(32, 12)))                       # total depth
    # population allele frequency per ALT allele: mostly rare, some common
    afs = [round(min(rng.betavariate(0.3, 3), 0.99) + 0.0005, 4) for _ in alts]
    # genotypes of every sample: 0 = REF, 1.. = ALT index
    calls = {}
    ac = [0] * len(alts)
    an = 0
    for s in samples:
        if rng.random() < 0.03:                               # 3% missing genotype
            calls[s] = {"GT": "./.", "DP": 0, "GQ": 0}
            continue
        alleles = []
        for _ in range(2):                                    # diploid: draw 2 alleles
            r = rng.random()
            allele = 0
            for i, af in enumerate(afs, start=1):
                if r < af * 2.5:                              # x2.5: cohort is enriched for variants
                    allele = i
                    break
                r -= af * 2.5
            alleles.append(allele)
        for a in alleles:
            if a:
                ac[a - 1] += 1
        an += 2
        sep = "|" if rng.random() < 0.3 else "/"
        calls[s] = {
            "GT": sep.join(map(str, sorted(alleles))),
            "DP": max(1, int(rng.gauss(dp / len(samples), 5))),
            "GQ": min(99, max(3, int(rng.gauss(70, 25)))),
        }
    if qual < 30:
        flt = "LowQual"
    elif dp < 10:
        flt = "LowDP"
    else:
        flt = "PASS"
    return {
        "chrom": chrom, "ref": ref, "alt": alts, "qual": qual, "filter": flt,
        "info": {"DP": dp, "AF": afs, "AC": ac, "AN": an, "MQ": round(rng.gauss(58, 4), 1)},
        "calls": calls,
    }


# --------------------------------------------------------------------------- #
# 2. Writing a VCF file
# --------------------------------------------------------------------------- #
VCF_HEADER = """##fileformat=VCFv4.2
##source=workshop-NoSQL synthetic generator (data/prepare/make_mongodb_data.py)
##reference=GRCh38 (coordinates only; alleles are synthetic)
{contigs}##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count in called genotypes, one value per ALT allele">
##INFO=<ID=AF,Number=A,Type=Float,Description="Population allele frequency, one value per ALT allele">
##INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles in called genotypes">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Combined read depth over all samples">
##INFO=<ID=MQ,Number=1,Type=Float,Description="RMS mapping quality">
##FILTER=<ID=LowQual,Description="QUAL below 30">
##FILTER=<ID=LowDP,Description="Combined depth below 10">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype (0 = REF, 1 = first ALT, 2 = second ALT)">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read depth of this sample">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype quality">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{samples}
"""


def write_vcf(path: Path, n: int, contigs: list, samples: list, seed: int) -> list:
    rng = random.Random(seed)
    variants = {}
    while len(variants) < n:                                  # unique (chrom, pos) pairs
        v = random_variant(rng, contigs, samples)
        if sum(v["info"]["AC"]) == 0:                         # a real call-set only lists sites where
            continue                                          # at least one sample carries the ALT allele
        v["pos"] = rng.randint(10_000, CONTIG_LENGTH[v["chrom"]] - 10_000)
        variants[(v["chrom"], v["pos"])] = v
    order = {c: i for i, c in enumerate(CONTIG_LENGTH)}
    rows = sorted(variants.values(), key=lambda v: (order[v["chrom"]], v["pos"]))

    contig_lines = "".join(
        f"##contig=<ID={c},length={CONTIG_LENGTH[c]},assembly=GRCh38>\n" for c in contigs
    )
    lines = [VCF_HEADER.format(contigs=contig_lines, samples="\t".join(samples)).rstrip("\n")]
    for v in rows:
        info = (
            f"AC={','.join(map(str, v['info']['AC']))};AF={','.join(map(str, v['info']['AF']))};"
            f"AN={v['info']['AN']};DP={v['info']['DP']};MQ={v['info']['MQ']}"
        )
        sample_cols = [
            f"{v['calls'][s]['GT']}:{v['calls'][s]['DP']}:{v['calls'][s]['GQ']}" for s in samples
        ]
        lines.append("\t".join([
            v["chrom"], str(v["pos"]), ".", v["ref"], ",".join(v["alt"]), str(v["qual"]),
            v["filter"], info, "GT:DP:GQ", *sample_cols,
        ]))
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path.name}: {len(rows)} variants on {len(contigs)} contigs")
    return rows


# --------------------------------------------------------------------------- #
# 3. The big catalogue (for the index demo) and the sample metadata
# --------------------------------------------------------------------------- #
def write_catalog(path: Path, n: int, seed: int) -> None:
    """Pre-parsed documents with exactly the same shape the notebook builds from a VCF."""
    rng = random.Random(seed)
    contigs = list(CONTIG_LENGTH)
    weights = [CONTIG_LENGTH[c] for c in contigs]            # longer chromosome -> more variants
    seen = set()
    with gzip.open(path, "wt", compresslevel=9) as fh:
        while len(seen) < n:
            chrom = rng.choices(contigs, weights)[0]
            pos = rng.randint(10_000, CONTIG_LENGTH[chrom] - 10_000)
            if (chrom, pos) in seen:
                continue
            seen.add((chrom, pos))
            v = random_variant(rng, [chrom], [])
            fh.write(json.dumps({
                "chrom": chrom, "pos": pos, "ref": v["ref"], "alt": v["alt"],
                "qual": v["qual"], "filter": v["filter"],
                "info": {"DP": v["info"]["DP"], "AF": v["info"]["AF"], "MQ": v["info"]["MQ"]},
            }, separators=(",", ":")) + "\n")
    print(f"wrote {path.name}: {n:,} documents")


def write_samples(path: Path) -> None:
    rows = [
        # _id is the sample name used in the VCF header -> it is the natural primary key
        ("SAMPLE_A", "F", "EUR", 34.2, "sample.vcf"), ("SAMPLE_B", "M", "AFR", 29.8, "sample.vcf"),
        ("SAMPLE_C", "F", "EAS", 31.5, "sample.vcf"), ("SAMPLE_D", "M", "EUR", 38.0, "assignment.vcf"),
        ("SAMPLE_E", "F", "AMR", 27.4, "assignment.vcf"), ("SAMPLE_F", "M", "SAS", 33.1, "assignment.vcf"),
    ]
    with open(path, "w") as fh:
        for sid, sex, pop, cov, vcf in rows:
            fh.write(json.dumps({
                "_id": sid, "sex": sex, "population": pop, "mean_coverage_x": cov,
                "platform": "Illumina NovaSeq 6000", "vcf_file": vcf, "synthetic": True,
            }) + "\n")
    print(f"wrote {path.name}: {len(rows)} samples")


if __name__ == "__main__":
    write_vcf(OUT / "sample.vcf", 250, ["1", "2", "17", "X"], ["SAMPLE_A", "SAMPLE_B", "SAMPLE_C"], seed=2025)
    write_vcf(OUT / "assignment.vcf", 800, ["7", "12", "19", "22"], ["SAMPLE_D", "SAMPLE_E", "SAMPLE_F"], seed=2026)
    write_catalog(OUT / "variant_catalog.jsonl.gz", 50_000, seed=7)
    write_samples(OUT / "samples.jsonl")
