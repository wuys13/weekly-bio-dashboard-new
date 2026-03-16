# ✅ Weekly Bio Dashboard - Setup Complete

## Configuration Summary

Your dashboard is now configured for your research interests:

### 📊 Dashboard Statistics
- **Journals monitored**: 21 top-tier journals (Cell, Nature, Science, etc.)
- **Keyword categories**: 14 specialized areas
- **Preprint sources**: bioRxiv + medRxiv

### 🔬 Your Research Focus Areas

#### Tech Categories (8)
✓ Genomics  
✓ Sequencing  
✓ Imaging  
✓ Proteomics  
✓ Computational  
✓ **Spatial Transcriptomics** (NEW)  
✓ **AI/ML** (NEW)  
✓ **Single-cell Analysis** (NEW)  

#### Biology Categories (6)
✓ Cell Biology  
✓ Development  
✓ Neuroscience  
✓ Cancer  
✓ Therapeutics  
✓ **Tumor Microenvironment** (NEW)  

### 🎯 Focus Areas

**Focus Area 1**: Spatial Transcriptomics in Tumor Microenvironment
- Keywords: spatial transcriptomics, visium, merfish, seqfish, tumor immune infiltration, macrophage, fibroblast, immune cells, etc.

**Focus Area 2**: AI/ML for Transcriptomics
- Keywords: machine learning, deep learning, neural networks, transformers, cell annotation, trajectory inference, single-cell analysis, etc.

**Focus Area 3**: AI/ML in Bio Data Analysis (Already configured)

### 📈 Trend Detection

The dashboard tracks 6 major research trends:
- Spatial Transcriptomics
- Single-cell & spatial omics  
- Tumor Microenvironment & Immunology
- Cancer biology & therapy
- Neuroscience & circuits
- AI/ML in bio data analysis

---

## 🚀 How to Run the Dashboard

### Quick Start
```bash
cd /Users/stephen/Documents/GitHub/weekly-bio-dashboard-new
source .venv/bin/activate
streamlit run app.py
```

Or use the convenience script:
```bash
cd /Users/stephen/Documents/GitHub/weekly-bio-dashboard-new
./run.sh
```

The dashboard will open at: **http://localhost:8501**

### What You'll See
1. **Must-Read — Tech**: Top papers matching your tech keywords
2. **Must-Read — Bio**: Top papers matching your biology keywords
3. **Must-Read — Preprints**: Latest preprints from bioRxiv/medRxiv
4. **Focus 1**: Spatial Transcriptomics in Tumor Microenvironment papers
5. **Focus 2**: AI/ML for Transcriptomics papers
6. **Focus 3**: AI/ML in Bio Data Analysis papers
7. **Trends**: Hot research areas this week

---

## 📧 Email Digest (Optional - Skip for Now)

When you're ready to set up the weekly email digest, you'll need to:

1. Create `.env.digest` file with Feishu SMTP credentials:
   ```
   SMTP_HOST=smtp.feishu.cn
   SMTP_PORT=587
   SMTP_USER=<your-feishu-email>
   SMTP_PASSWORD=<your-feishu-password>
   EMAIL_TO=<recipient-email>
   ```

2. Test the email:
   ```bash
   source .venv/bin/activate
   python send_digest.py --dry-run  # Preview in HTML
   python send_digest.py            # Send actual email
   ```

3. Set up weekly automation (macOS):
   ```bash
   cp com.huiliw.weekly-bio-digest.plist ~/Library/LaunchAgents/
   # Edit the .plist file to update paths to your project directory
   launchctl load ~/Library/LaunchAgents/com.huiliw.weekly-bio-digest.plist
   ```

---

## 📝 Customization Guide

### To modify journals (config.py:31-55)
Edit the `JOURNALS` list to add/remove journals

### To modify keywords (config.py:110-266)
Edit the `CORE_KEYWORDS` dictionary:
- Each category becomes a "tag" on papers
- Papers matching multiple categories get higher scores
- Short acronyms (≤3 chars) use word-boundary matching

### To modify focus areas (config.py:270+)
Edit `FOCUS_AREA_1_KEYS` and `FOCUS_AREA_2_KEYS` for different research niches

### To modify trends (config.py:390+)
Edit `TREND_LEXICON` to track different emerging topics

---

## 📂 File Structure

```
/Users/stephen/Documents/GitHub/weekly-bio-dashboard-new/
├── config.py                          ← Your customization file
├── .env.digest                        ← Email config (optional)
├── .venv/                             ← Virtual environment
├── app.py                             ← Streamlit dashboard
├── send_digest.py                     ← Email digest script
├── run.sh                             ← Convenience launcher
├── requirements.txt                   ← Python dependencies
└── README.md                          ← Full documentation
```

---

## ✨ Next Steps

1. **Run the dashboard now**:
   ```bash
   cd /Users/stephen/Documents/GitHub/weekly-bio-dashboard-new
   ./run.sh
   ```

2. **Check the results**: Browse papers in your research areas

3. **Adjust keywords** if needed based on what you see

4. **Set up email digest** when ready (optional)

5. **Customize further** by editing config.py

---

Enjoy exploring the latest papers in spatial transcriptomics, AI/ML, and tumor immunology! 🧬🤖
