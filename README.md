# PestTrail — US Invasive Pest Intelligence Platform

A strategic intelligence platform tracking invasive agricultural and forest pests introduced into the United States since 1995 — their origin, mode of entry, pathway, host, spread, and economic impact.

PestTrail is designed for biosurveillance analysts, plant health policymakers, agricultural researchers, and anyone who needs to understand not just *what* invasive pests are in the US, but *how they got here*, *where they came from*, and *what that pattern tells us about what arrives next*.

---

## The Problem

The United States has robust border inspection infrastructure — USDA APHIS, CBP, and the CAPS surveillance network collectively intercept thousands of potential invasive pests annually. Yet new pests continue to establish at an alarming rate, often causing billions of dollars in damage before detection triggers a coordinated response.

Three surveillance failures define the current landscape:

**1. The Detection Lag Problem**
The Emerald Ash Borer (EAB) is estimated to have arrived in the United States around 1992. It was not officially detected until 2002 — a 10-year window during which it spread silently across the Great Lakes region. By the time management began, eradication was impossible. The economic toll: over $10 billion in ash tree losses, with ripple effects across forestry, urban infrastructure, and ecosystem services.

This is not an isolated case. The Brown Marmorated Stink Bug likely arrived in the mid-1990s but was not detected until 1998 in Allentown, Pennsylvania. The Spotted Lanternfly arrived around 2012 and went undetected for two years. Detection lag — the gap between arrival and confirmed detection — is a systemic feature of current surveillance, not an anomaly.

**2. The Pathway Blindness Problem**
Current US surveillance systems track *where* invasive pests are found. They rarely systematically track *how they got there*. Yet pathway data is arguably more actionable than distribution data. If wooden packing materials from East Asia account for a disproportionate share of beetle introductions, that pattern — if tracked and analyzed — should drive inspection prioritization and import policy. That analysis does not exist in any publicly accessible, queryable form.

**3. The Fragmentation Problem**
Relevant data exists across at least 7 different systems: CAPS, EDDMapS, iMapInvasives, US-RIIS, EPPO Global Database, USDA Forest Service AFPE, and individual state databases. None of these systems share a common schema. Cross-referencing pathway, origin, host, and economic impact data requires manual research across multiple platforms. No unified analytical interface exists.

---

## What PestTrail Does

### 1. Unified Historical Database (1995–Present)

A structured, queryable database of invasive pests introduced to the US since 1995, integrating data from US-RIIS, USDA APHIS, EDDMapS, EPPO, and peer-reviewed literature into a single schema.

**Key fields captured for each pest:**
- Common and scientific name (standardized taxonomy)
- Year of first US detection vs. estimated year of actual arrival
- Detection lag (years between arrival and detection)
- Country and region of origin
- Mode of entry (cargo; passenger baggage; mail/parcels; nursery stock; wind dispersal; natural spread; unknown)
- Commodity pathway (wooden packaging; fresh produce; ornamental plants; etc.)
- US port of entry or first detection location
- Host plant or animal
- States currently affected
- Spread rate (km/year where documented)
- Economic impact estimate
- Affected agricultural or forestry sector
- Current quarantine and regulatory status

### 2. Pathway Hotspot Analysis

The central analytical innovation of PestTrail. Rather than asking "what pests are where," Pathway Hotspot Analysis asks:

- **Which origin countries** have contributed the most established invasive pests to the US?
- **Which commodity types** consistently serve as introduction pathways?
- **Which US ports of entry** have the highest rates of pest establishment following interception?
- **Which agricultural sectors** are most exposed based on pathway patterns?

This analysis is designed to inform inspection resource allocation and trade policy — directing surveillance effort toward the pathways that historical data shows are highest risk.

### 3. Temporal Trend Dashboard

- How has the rate of new invasions changed from 1995 to present?
- Did the post-9/11 tightening of cargo inspection affect introduction rates?
- Did COVID-era supply chain disruptions shift origin patterns?
- Are introductions accelerating or decelerating over time?
- What seasonal patterns exist in detections (shipping season, growing season)?

### 4. Detection Lag Analysis

For each pest: how long between estimated arrival and confirmed detection?

Aggregated across all pests: what is the average detection lag? Which pest types (insects vs. fungi vs. bacteria) have the longest lags? Which pathways have the worst detection rates?

This analysis directly quantifies where surveillance investment is most needed.

### 5. Host-Pathway Network Map

An interactive network visualization showing the structural relationships between:

```
Origin Country → Mode of Entry → Commodity Pathway → Pest → Host Plant/Animal → Affected Sector
```

For example: **China → Cargo → Wooden Packaging → Emerald Ash Borer → Ash Trees → Forestry**

This network reveals which combinations appear repeatedly — the structural patterns of US invasion biology — and which nodes in the network represent the highest leverage points for intervention.

### 6. Risk Scoring for Current Threats

Based on historical pathway patterns, which pest-commodity combinations currently monitored at borders most closely resemble the conditions that preceded past major invasions?

*"If the Emerald Ash Borer, Spotted Lanternfly, and Asian Longhorned Beetle all entered via wooden packaging from East Asia and had detection lags of 5-10 years — what does current border interception data tell us about what is already here but not yet detected?"*

---

## Data Sources

| Source | Records | Type | Access |
|---|---|---|---|
| US Register of Introduced and Invasive Species (US-RIIS) | 15,264 | National registry | Public — USGS |
| Early Detection and Distribution Mapping (EDDMapS) | 8.6M+ observations | Field observations | Public — eddmaps.org |
| USDA APHIS CAPS | Federal surveillance | Regulatory | Public — USDA website |
| EPPO Global Database | 98,700+ species | International regulatory | Public — gd.eppo.int |
| USDA Forest Service AFPE | Forest pest spatial data | Geospatial | Public — USFS portal |
| iMapInvasives | Multi-state observations | Geospatial | Public — imapinvasives.org |
| Peer-reviewed literature | Pathway and impact data | Academic | PubMed / Google Scholar |

The seed dataset in this repository (`data/invasive_pests_1995_2025.csv`) covers 15 high-impact case studies. The full platform would integrate all publicly available records from the sources above.

---

## Case Studies: What the Data Reveals

| Pest | Arrival | Detected | Lag | Origin | Pathway | Impact |
|---|---|---|---|---|---|---|
| Emerald Ash Borer | ~1992 | 2002 | **10 years** | China | Wooden packaging | $10B+ |
| Spotted Lanternfly | ~2012 | 2014 | 2 years | China/S. Korea | Stone shipment | $324M/yr (PA) |
| Brown Marmorated Stink Bug | ~1996 | 1998 | 2 years | China/Japan/Korea | Cargo (unknown) | $37M/yr |
| Citrus Greening (vector) | ~1998 | 1998/2005 | 0-7 years | Asia | Ornamental citrus? | $4.7B (FL) |
| Asian Longhorned Beetle | ~1992 | 1996 | 4 years | China | Wooden crates | $669B potential |
| Sudden Oak Death | ~early 1990s | 1995 | Unknown | Asia | Nursery stock | $16.3B potential |
| Spotted Wing Drosophila | 2008 | 2008 | 0 years | East Asia | Fresh fruit/trade | $500M+/yr |

**Pattern:** East Asian origin + wooden packaging or nursery stock = disproportionate share of high-impact introductions.

---

## Tech Stack (Roadmap)

### Phase 1 — Current (Concept + Seed Data)
- Structured CSV database with 15 case studies
- Detailed README and data model documentation
- GitHub repository for open collaboration

### Phase 2 — Prototype
- **Streamlit** (Python) dashboard for rapid interactive visualization
- Leaflet.js map showing introduction points and spread
- Pandas-based pathway hotspot analysis
- D3.js network diagram for host-pathway relationships

### Phase 3 — Full Platform
- React frontend + FastAPI backend
- PostgreSQL database with full US-RIIS and EDDMapS integration
- Real-time APHIS PestLens API feed
- Predictive risk scoring model
- Public API for USDA/APHIS, CGIAR, and academic use

---

## Why This Matters

Plant diseases and invasive pests cause an estimated **$40 billion in annual losses** to US agriculture and forestry. The federal investment in border inspection and post-border surveillance is substantial — but its effectiveness is limited by the absence of unified, analytically sophisticated intelligence tools.

PestTrail is designed as the analytical layer that existing surveillance systems lack: not more data collection, but better synthesis of data that already exists into actionable intelligence about pathway risk, detection gaps, and emerging threats.

The Emerald Ash Borer cost $10 billion. It entered via a pathway that was already known to be high-risk. A tool that made that pattern visible and queryable in 1998 would have been worth building.

---

## Roadmap

- [ ] Expand seed dataset to 50+ pests (1995–present)
- [ ] Integrate US-RIIS full dataset via USGS API
- [ ] Build Streamlit prototype with interactive map and pathway analysis
- [ ] Add EDDMapS observation data integration
- [ ] Develop detection lag analysis module
- [ ] Build host-pathway network visualization
- [ ] Add real-time APHIS PestLens feed integration
- [ ] Develop predictive risk scoring algorithm

---

## Related Projects

- [PlantPath AI](https://github.com/Mary-Akinyuwa/plantpath-ai) — AI-powered plant disease diagnostic chatbot (Claude + ServiceNow)
- [LifeScience ServiceNow Workflows](https://github.com/Mary-Akinyuwa/lifescience-servicenow-workflows) — Reusable ServiceNow automation templates for life science organizations

---

## Author

Built by [Mary Akinyuwa](https://www.linkedin.com/in/mary-akinyuwa-700268165/) | Life Scientist | Food Systems & AI Strategy

Published plant pathologist with field experience in Nigeria, Europe, and the US. Former research scientist at Corteva Agriscience. Incoming MBA candidate.

[LinkedIn](https://www.linkedin.com/in/mary-akinyuwa-700268165/) | [GitHub](https://github.com/Mary-Akinyuwa)
