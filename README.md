# Real Estate Beyond RGB — UniAI Makeathon 2026

Using hyperspectral satellite imagery to decide which of 4 Greek land plots is the best €1M investment.

## The Challenge

4 land plots (~250,000 m² each, ~€1M each). Which one do you buy?

Instead of relying on traditional data, we analyze **EnMap hyperspectral satellite data** — light beyond what the human eye can see (NIR/SWIR, 700–2500 nm) — to assess soil quality, moisture, and vegetation health.

| Plot | Longitude | Latitude |
|------|-----------|----------|
| Arkadia | 22.366139 | 37.651492 |
| Magnisia | 22.766325 | 39.174176 |
| Arkadia 2 | 22.143828 | 37.324456 |
| Veroia | 22.120677 | 40.398697 |

## Approach

- Download hyperspectral data via the [EnMap downloader](https://huggingface.co/spaces/DionysosKM/enmap-demo)
- Analyze spectral bands for soil quality, moisture, and vegetation health
- Cross-reference with open data (elevation, land use, accessibility)
- Deliver a data-backed investment recommendation

## Structure

```
├── data/          # Raw EnMap hyperspectral images
├── notebooks/     # Jupyter notebooks for analysis
├── src/           # Processing scripts
└── report/        # Final report and presentation
```

## Setup

```bash
git clone https://github.com/akakarantzas/makeathlon-real-estate-beyond-rgb.git
cd makeathlon-real-estate-beyond-rgb
pip install -r requirements.txt
```

## Resources

- [EnMap Downloader Tool](https://huggingface.co/spaces/DionysosKM/enmap-demo)
- [EGSA87 → WGS84 Converter](https://mykaek.gr/egsa-to-wgs/)
- [Challenge Data (Google Drive)](https://drive.google.com/file/d/1j9zbdI81vJ6F9L8xy5ZcoZcs5WQ-ht2W/view?usp=sharing)
