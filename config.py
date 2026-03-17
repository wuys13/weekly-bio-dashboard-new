# ============================================================================
#  Weekly Bio Dashboard — Configuration
# ============================================================================
#
#  HOW TO CUSTOMIZE FOR YOUR RESEARCH
#  -----------------------------------
#  This file is the ONLY file you need to edit to tailor the dashboard to
#  your own research interests. Everything else (app.py, scoring.py, etc.)
#  reads from here automatically.
#
#  Step 1: Edit JOURNALS / JOURNAL_ISSN — pick the journals you follow.
#  Step 2: Edit CORE_KEYWORDS — define keyword categories that matter to you.
#          Each category becomes a "tag" on matched papers and feeds into scoring.
#  Step 3: Edit TECH_KEYS / BIO_KEYS — assign your categories to Tech vs Bio
#          buckets so the Must-read list can split them.
#  Step 4: Edit the two FOCUS_*_KEYS lists — these power the dedicated Focus
#          sections in the dashboard. Replace them with your own niche terms.
#  Step 5: Edit TREND_LEXICON — groups of keywords for trend detection.
#
#  The examples below use "gene regulation / epigenetics" and
#  "stem cells / regenerative medicine" as sample focus areas. Replace them
#  with whatever fits your lab.
# ============================================================================


# ========================
# Journal whitelist
# ========================
# Add or remove journals here. Each entry must match the journal name as it
# appears in Crossref. Use JOURNAL_ISSN below to map ambiguous names to ISSNs.
JOURNALS = [
    "Cell",
    "Nature",
    "Science",
    "Cancer Cell",
    "Nature Biotechnology",
    "Nature Methods",
    "Immunity",
    "Nature Immunology",
    "Science Advances",
    "Science Immunology",
    "Science Translational Medicine",
    "Nature Cancer",
    "Nature Genetics",
    "Nature Medicine",
    "Nature Biomedical Engineering",
    "Cell Systems",
    "Cell Reports Methods",
    "PNAS",
    "Nature Chemical Biology",
    "Nature Communications",
    "eLife",
]
INCLUDE_BIORXIV_DEFAULT = True
INCLUDE_MEDRXIV_DEFAULT = False

# ISSN look-up speeds up Crossref queries and avoids false matches.
# Find ISSNs at https://portal.issn.org
JOURNAL_ISSN = {
    "Cell": ['0092-8674', '1097-4172'],
    "Nature": ['0028-0836', '1476-4687'],
    "Science": ['0036-8075', '1095-9203'],
    "Cancer Cell": ['1535-6108', '1878-3686'],
    "Nature Biotechnology": ['1087-0156', '1546-1696'],
    "Nature Methods": ['1548-7091', '1548-7105'],
    "Immunity": ['1074-7613', '1097-4180'],
    "Nature Immunology": ['1529-2908', '1529-2916'],
    "Science Advances": ['2375-2548'],
    "Science Immunology": ['2470-9468'],
    "Science Translational Medicine": ['1946-6234'],
    "Nature Cancer": ['2662-1347'],
    "Nature Genetics": ['1061-4036', '1546-1718'],
    "Nature Medicine": ['1078-8956', '1546-170X'],
    "Nature Biomedical Engineering": ['2157-846X'],
    "Cell Systems": ['2405-4712'],
    "Cell Reports Methods": ['2667-2375'],
    "PNAS": ['0027-8424', '1091-6490'],
    "Nature Chemical Biology": ['1552-4450', '1552-4469'],
    "Nature Communications": ['2041-1723'],
    "eLife": ['2050-084X'],
}

# Must-read list size
MUST_READ_N = 20

# Cap how many papers from the same journal can appear in each Must-read list
MAX_PER_JOURNAL_MUST_READ = 3


# ========================
# Tech vs Bio tag buckets
# ========================
# These must match keys in CORE_KEYWORDS below.
# Papers tagged with a TECH key go into the "Must-read Tech" list;
# papers tagged with a BIO key go into "Must-read Bio".
# A paper can appear in both if it hits keywords from both sides.
TECH_KEYS = ["genomics", "sequencing", "imaging", "proteomics", "computational", "spatial_transcriptomics", "ai_ml", "single_cell"]
BIO_KEYS  = ["cell_biology", "development", "neuroscience", "cancer", "therapeutics", "tumor_microenvironment"]


# ========================
# Core keyword lexicon
# ========================
# Each key becomes a tag. The list of strings are search terms (case-insensitive
# substring match in title + abstract). Longer phrases are matched first to
# avoid double-counting (e.g. "spatial transcriptomics" won't also count
# "spatial"). Short acronyms (<=3 chars) use word-boundary matching.
#
# >>> CUSTOMIZE THESE to match your research interests <<<
CORE_KEYWORDS = {
    # --- Technology categories ---
    "genomics": [
        "genomics",
        "genome-wide",
        "genome wide",
        "whole genome",
        "exome",
        "gwas",
        "genome sequencing",
        "chromatin",
        "epigenome",
        "methylome",
        "chip-seq",
        "cut&run",
        "cut&tag",
    ],
    "sequencing": [
        "sequencing",
        "single-cell",
        "single cell",
        "scrna",
        "rna-seq",
        "atac-seq",
        "multiome",
        "cite-seq",
        "perturb-seq",
        "crispr screen",
        "guide rna",
        "long-read",
        "nanopore",
    ],
    "imaging": [
        "imaging",
        "microscopy",
        "fluorescence",
        "confocal",
        "light-sheet",
        "super-resolution",
        "live imaging",
        "spatial transcriptomics",
        "spatial proteomics",
        "merfish",
        "seqfish",
        "visium",
        "codex",
        "expansion microscopy",
    ],
    "proteomics": [
        "proteomics",
        "mass spectrometry",
        "mass-spec",
        "lc-ms",
        "lc-ms/ms",
        "phosphoproteomics",
        "protein profiling",
        "olink",
        "somalogic",
        "cytof",
    ],
    "computational": [
        "deep learning",
        "machine learning",
        "artificial intelligence",
        "neural network",
        "foundation model",
        "large language model",
        "transformer",
        "graph neural network",
        "cell segmentation",
        "image analysis",
        "computational",
        "bioinformatics",
        "algorithm",
        "dimensionality reduction",
        "clustering",
        "trajectory inference",
        "batch correction",
        "data integration",
    ],

    # --- Biology / application categories ---
    "cell_biology": [
        "cell cycle",
        "cell division",
        "mitosis",
        "apoptosis",
        "autophagy",
        "cell migration",
        "cell adhesion",
        "cytoskeleton",
        "organelle",
        "membrane trafficking",
        "endocytosis",
        "exocytosis",
        "signal transduction",
        "cell polarity",
    ],
    "development": [
        "development",
        "embryo",
        "embryonic",
        "morphogenesis",
        "organogenesis",
        "differentiation",
        "stem cell",
        "progenitor",
        "lineage",
        "fate decision",
        "gastrulation",
        "patterning",
        "regeneration",
    ],
    "neuroscience": [
        "neuron",
        "neural",
        "brain",
        "cortex",
        "hippocampus",
        "synapse",
        "synaptic",
        "neurotransmitter",
        "glia",
        "astrocyte",
        "microglia",
        "axon",
        "dendrite",
        "neural circuit",
        "electrophysiology",
    ],
    "cancer": [
        "cancer",
        "tumor",
        "tumour",
        "oncology",
        "neoplasm",
        "malignant",
        "metastasis",
        "oncogene",
        "tumor suppressor",
        "tumor microenvironment",
    ],
    "therapeutics": [
        "drug",
        "therapy",
        "therapeutic",
        "treatment",
        "inhibitor",
        "small molecule",
        "antibody",
        "immunotherapy",
        "clinical trial",
        "pharmacology",
        "drug resistance",
        "combination therapy",
    ],

    # --- Custom additions for spatial transcriptomics focus ---
    "spatial_transcriptomics": [
        "spatial transcriptomics",
        "spatial transcriptomic",
        "visium",
        "merfish",
        "seqfish",
        "osmfish",
        "in situ sequencing",
        "spatial rna",
        "slide-seq",
        "stereo-seq",
        "imaging-based transcriptomics",
        "tissue map",
        "spatial resolution",
        "spatial gene expression",
    ],

    # --- Custom additions for AI/ML ---
    "ai_ml": [
        "machine learning",
        "deep learning",
        "neural network",
        "artificial intelligence",
        "transformer",
        "foundation model",
        "large language model",
        "llm",
        "attention mechanism",
        "prediction",
        "classification",
        "representation learning",
        "self-supervised",
        "contrastive learning",
        "generative model",
    ],

    # --- Custom additions for tumor microenvironment ---
    "tumor_microenvironment": [
        "tumor microenvironment",
        "tme",
        "immune infiltration",
        "immune cell",
        "t cell",
        "macrophage",
        "fibroblast",
        "cancer-associated fibroblast",
        "cab",
        "immune checkpoint",
        "immunosuppression",
        "exhaustion",
        "infiltrating lymphocyte",
        "stromal",
        "immune evasion",
    ],

    # --- Custom additions for single-cell analysis ---
    "single_cell": [
        "single-cell",
        "single cell",
        "scRNA-seq",
        "scrna",
        "single-cell transcriptome",
        "cell-level resolution",
        "cell type",
        "state transition",
        "pseudotime",
        "trajectory",
        "cell state",
        "cell annotation",
    ],
}


# ========================
# Focus 1: Spatial Transcriptomics in Tumor Microenvironment
# ========================
# Spatial analysis of tumor immune infiltration and stromal composition
FOCUS_AREA_1_KEYS = [
    "spatial transcriptomics",
    "visium",
    "merfish",
    "seqfish",
    "stereo-seq",
    "slide-seq",
    "in situ sequencing",
    "tumor microenvironment",
    "immune infiltration",
    "immune cell",
    "t cell",
    "macrophage",
    "fibroblast",
    "cancer-associated fibroblast",
    "stromal",
    "tumor",
    "cancer",
    "tissue",
    "spatial resolution",
    "immune landscape",
]


# ========================
# Focus 2: AI/ML for Transcriptomics
# ========================
# Machine learning applications in single-cell and spatial transcriptomics
FOCUS_AREA_2_KEYS = [
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "neural network",
    "transformer",
    "foundation model",
    "prediction",
    "classification",
    "single-cell",
    "scRNA-seq",
    "transcriptomics",
    "gene expression",
    "cell type",
    "cell annotation",
    "clustering",
    "dimensionality reduction",
    "trajectory inference",
    "pseudotime",
    "representation learning",
    "self-supervised",
]


# ========================
# Focus 3: AI/ML in biological data analysis  (broadly useful — keep or customize)
# ========================
FOCUS_AI_KEYS = [
    "deep learning",
    "machine learning",
    "artificial intelligence",
    "neural network",
    "convolutional neural network",
    "graph neural network",
    "transformer",
    "foundation model",
    "large language model",
    "generative model",
    "variational autoencoder",
    "diffusion model",
    "self-supervised",
    "self supervised",
    "contrastive learning",
    "transfer learning",
    "representation learning",
    "cell segmentation",
    "image segmentation",
    "image analysis",
    "computational pathology",
    "digital pathology",
    "spatial deconvolution",
    "cell type annotation",
    "cell type classification",
    "automated annotation",
    "multimodal integration",
    "imputation",
    "trajectory inference",
    "gene regulatory network",
    "cell-cell communication",
    "cell cell communication",
]


# ========================
# Big-deal hints (broad advances)
# ========================
BIG_DEAL_HINTS = [
    "first-in-class",
    "breakthrough",
    "paradigm",
    "unexpected",
    "previously unknown",
    "landmark",
    "fundamental",
]


# ========================
# Trend lexicon
# ========================
# Each key is a trend name shown in the UI; its value is a list of keywords.
# Papers matching many keywords in a group signal a "hot trend".
#
# >>> CUSTOMIZE THESE to reflect the trends you care about <<<
TREND_LEXICON = {
    "Spatial Transcriptomics": [
        "spatial transcriptomics",
        "visium",
        "merfish",
        "seqfish",
        "stereo-seq",
        "slide-seq",
        "in situ sequencing",
        "spatial resolution",
    ],
    "Single-cell & spatial omics": [
        "single-cell",
        "single cell",
        "scRNA-seq",
        "spatial transcriptomics",
        "spatial proteomics",
        "multiome",
        "cell atlas",
    ],
    "Tumor Microenvironment & Immunology": [
        "tumor microenvironment",
        "immune infiltration",
        "immune cell",
        "macrophage",
        "t cell",
        "immunotherapy",
        "immune checkpoint",
        "immune evasion",
    ],
    "Cancer biology & therapy": [
        "cancer",
        "tumor",
        "metastasis",
        "immunotherapy",
        "tumor microenvironment",
        "oncogene",
    ],
    "Neuroscience & circuits": [
        "neural circuit",
        "synapse",
        "brain",
        "cortex",
        "hippocampus",
        "neuron",
    ],
    "AI/ML in bio data analysis": [
        "deep learning",
        "machine learning",
        "neural network",
        "foundation model",
        "transformer",
        "cell segmentation",
        "computational pathology",
        "spatial deconvolution",
        "automated annotation",
        "cell type annotation",
        "trajectory inference",
    ],
}
