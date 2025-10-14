# 🗒️ Transcript Analysis

This project aims to **standardize, tag, and analyze interview transcripts** written in Polish.  
It provides tools for text preprocessing, annotation, and generating structured outputs suitable for qualitative or quantitative linguistic analysis.

## ⚙️ Requirements

Before running the scripts, make sure you have **Python 3.9+** installed.  
Install the necessary dependencies using `pip`:

```bash
pip install num2words reportlab spacy
```

Then download one of the available spaCy Polish language models:

```bash
python -m spacy download pl_core_news_lg
```

Alternatively, you can install a smaller or medium-sized model if system resources are limited:
* pl_core_news_sm – small model, faster but less accurate
* pl_core_news_md – medium model, balance between speed and accuracy

## 🌐 Resources
This project uses free, publicly available fonts from:
* **Google fonts**: https://fonts.google.com/
* **Dejavu sans**: https://dejavu-fonts.github.io/