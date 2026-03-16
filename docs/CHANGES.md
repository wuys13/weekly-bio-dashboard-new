# Configuration Changes Made

## Summary
Updated `config.py` to customize the dashboard for spatial transcriptomics, AI/ML, and tumor microenvironment research.

## Specific Changes

### 1. Added New Keyword Categories (5 new categories)

#### `spatial_transcriptomics` (TECH)
Keywords: spatial transcriptomics, visium, merfish, seqfish, osmfish, in situ sequencing, spatial rna, slide-seq, stereo-seq, imaging-based transcriptomics, tissue map, spatial resolution, spatial gene expression

#### `ai_ml` (TECH)
Keywords: machine learning, deep learning, neural network, artificial intelligence, transformer, foundation model, large language model, llm, attention mechanism, prediction, classification, representation learning, self-supervised, contrastive learning, generative model

#### `tumor_microenvironment` (BIO)
Keywords: tumor microenvironment, tme, immune infiltration, immune cell, t cell, macrophage, fibroblast, cancer-associated fibroblast, cab, immune checkpoint, immunosuppression, exhaustion, infiltrating lymphocyte, stromal, immune evasion

#### `single_cell` (TECH)
Keywords: single-cell, single cell, scRNA-seq, scrna, single-cell transcriptome, cell-level resolution, cell type, state transition, pseudotime, trajectory, cell state, cell annotation

### 2. Updated Tech/Bio Classification (lines 97-98)

**Before:**
```python
TECH_KEYS = ["genomics", "sequencing", "imaging", "proteomics", "computational"]
BIO_KEYS  = ["cell_biology", "development", "neuroscience", "cancer", "therapeutics"]
```

**After:**
```python
TECH_KEYS = ["genomics", "sequencing", "imaging", "proteomics", "computational", "spatial_transcriptomics", "ai_ml", "single_cell"]
BIO_KEYS  = ["cell_biology", "development", "neuroscience", "cancer", "therapeutics", "tumor_microenvironment"]
```

### 3. Replaced Focus Area 1 (lines 274-298)

**Before:** Gene regulation & epigenetics  
**After:** Spatial Transcriptomics in Tumor Microenvironment

Keywords now include:
- Spatial transcriptomics technologies (visium, merfish, seqfish, stereo-seq, slide-seq)
- Tumor microenvironment markers
- Immune cell types (t cells, macrophages, fibroblasts)
- Tumor biology

### 4. Replaced Focus Area 2 (lines 304-327)

**Before:** Stem cells & regenerative medicine  
**After:** AI/ML for Transcriptomics

Keywords now include:
- ML techniques (deep learning, neural networks, transformers, foundation models)
- Single-cell & transcriptomics analysis
- Cell annotation, clustering, trajectory inference
- Representation learning approaches

### 5. Enhanced Trend Detection (lines 390-441)

**Added/Updated trends:**
- "Spatial Transcriptomics" - new dedicated trend
- "Tumor Microenvironment & Immunology" - new dedicated trend
- "Single-cell & spatial omics" - expanded with more keywords
- "AI/ML in bio data analysis" - expanded with trajectory inference, cell type annotation

## Dashboard Impact

### Papers Now Tagged With
- Spatial transcriptomics papers: `spatial_transcriptomics` tag
- ML papers: `ai_ml` tag
- Single-cell papers: `single_cell` tag
- Tumor immune papers: `tumor_microenvironment` tag

### Must-Read Lists Will Now Include
- **Tech section**: Prioritizes spatial transcriptomics, AI/ML, and single-cell methods
- **Bio section**: Prioritizes tumor microenvironment and immune-related papers

### Focus Sections Show
- **Focus 1**: Papers at the intersection of spatial transcriptomics and tumor immunity
- **Focus 2**: Papers on AI/ML applications in transcriptomics and cell analysis

### Trends Tracked
- Emerging trends in spatial transcriptomics
- New immunology/tumor microenvironment discoveries
- AI/ML breakthroughs in biological data analysis

## Files Modified
- `config.py` - Core configuration file

## Files Not Modified (for email setup later)
- `.env.digest` - Not created (email digest skipped for now)
- `com.huiliw.weekly-bio-digest.plist` - Not modified (automation skipped for now)

## Testing the Configuration

Run the dashboard to see the changes:
```bash
cd /Users/stephen/Documents/GitHub/weekly-bio-dashboard-new
./run.sh
```

Check the configuration loaded correctly:
```bash
python -c "from config import TECH_KEYS, BIO_KEYS; print('Tech:', TECH_KEYS); print('Bio:', BIO_KEYS)"
```

Output should show:
```
Tech: ['genomics', 'sequencing', 'imaging', 'proteomics', 'computational', 'spatial_transcriptomics', 'ai_ml', 'single_cell']
Bio: ['cell_biology', 'development', 'neuroscience', 'cancer', 'therapeutics', 'tumor_microenvironment']
```
