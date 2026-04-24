# PestTrail — US Invasive Pest Intelligence Platform

**Built by [Mary Akinyuwa](https://www.linkedin.com/in/mary-akinyuwa-700268165/)** | Published Plant Pathologist · Food Systems & AI Strategist · Incoming MBA, Tepper School of Business at Carnegie Mellon University

---

> *The Emerald Ash Borer arrived in the United States around 1992. It was not detected until 2002. By the time a coordinated response began, eradication was permanently foreclosed — not because the pest was unstoppable, but because the 10-year detection lag had already allowed it to spread across five states and reach a threshold beyond which eradication is biologically impossible. The cumulative urban tree loss now exceeds $10.7 billion. The pathway that introduced it — wooden crating and packing materials from East Asia — was already known to be high-risk. What did not exist was a tool that made that pattern visible, queryable, and actionable before the window closed.*

---

## The Problem Is Architectural, Not Logistical

There is a common misconception about why invasive pest surveillance fails in the United States. The dominant narrative blames under-resourcing: not enough inspectors, not enough sentinel sites, not enough funding. That narrative is incomplete and, in important ways, misleading.

The United States has substantial biosurveillance infrastructure. USDA APHIS intercepts tens of thousands of potential introductions annually at ports of entry. The Cooperative Agricultural Pest Survey (CAPS) deploys sentinel plots and survey grids across all 50 states. EDDMapS has aggregated over 8.6 million field observations of invasive species distribution. The federal investment is real.

Yet the Emerald Ash Borer went undetected for 10 years. The Spotted Lanternfly for 2. The Asian Citrus Psyllid — vector of the bacterium that has since eliminated 74% of Florida's orange production — arrived in 1998 and was not connected to a disease outbreak until 2005. These are not failures of effort. They are failures of architecture.

**Current US biosurveillance systems are built to detect what they are programmed to find.** They are reactive, not predictive. A pest that does not match a known detection template — a specific PCR primer, a morphological key, a trap design calibrated to a known pheromone — is effectively invisible to these systems. The Emerald Ash Borer had no detection protocol when it arrived. It had no search image. It was not in anyone's inspection checklist. It spread silently for a decade not because it was cryptic by nature, but because the surveillance architecture had no mechanism for identifying threats outside its existing knowledge base.

This is the problem PestTrail is designed to address.

---

## The Five Analytical Gaps This Platform Closes

### Gap 1 — Pathway Intelligence Is Not Publicly Queryable

USDA APHIS interception records represent the most valuable predictive dataset in US invasive species management. Every year, inspectors at ports of entry record thousands of encounters with potential invasive organisms — what they were, where they came from, what commodity they were found on. This data exists. It is not publicly accessible in a form that supports pathway pattern analysis.

The single most actionable question in US biosurveillance — *"Of all wood-boring beetle interceptions in solid wood packing material from East Asia, what percentage have subsequently established in the United States within 10 years?"* — cannot be answered by any existing public tool. That question, answered systematically across all pathway-commodity-origin combinations, would transform inspection resource allocation.

PestTrail's **Pathway Hotspot Analysis** is the first public step toward answering it. Using 30 validated high-impact case studies spanning 1995–2025, it identifies which origin countries, commodity types, and entry modes have historically produced the highest rates of establishment and damage. This is not data aggregation — it is a pattern analysis that does not exist anywhere else in this form.

### Gap 2 — Detection Lag Has Never Been Operationalized as a Policy Metric

Federal surveillance programs are evaluated on detections per unit time: how many new pests were found, how many survey plots were visited, how quickly a response was mounted after confirmation. What they are never evaluated on is: *how long before we found it?*

Detection lag — the interval between estimated arrival and confirmed detection — is the most direct measure of surveillance system performance. A program that detects pests with a mean lag of 8 years is functionally failing, regardless of how many detections it records annually. Yet this metric does not appear in any USDA program evaluation framework I am aware of. It is not tracked. It is not reported. It is not used to allocate resources.

PestTrail makes detection lag a first-class analytical variable. For every pest in the database, the platform captures estimated arrival year alongside confirmed detection year, calculates the lag, and enables comparison across pest types, entry pathways, and origin regions. The aggregate pattern — which pest categories consistently evade detection longest, and via which routes — is the information needed to redesign surveillance architecture toward the threats most likely to be already present but unconfirmed.

### Gap 3 — The Eradication Window Is Not Being Tracked

Invasion biology has a well-established dose-response relationship between time-since-establishment and eradication probability. Below a certain population density and geographic extent — generally within the first 2–5 years of establishment — eradication is biologically feasible and cost-effective. Beyond that threshold, eradication becomes increasingly impractical, and the management strategy necessarily shifts from elimination to containment. Beyond 10 years of established spread, true eradication is, with rare exceptions, no longer achievable.

This principle is well understood in the academic literature. It is not operationalized in any public tool.

The Asian Longhorned Beetle eradication program has been active in parts of the northeastern US since 1996 — nearly 30 years. The Coconut Rhinoceros Beetle was confirmed on Oahu in December 2013 — over a decade ago. For each of these, the question of whether the pest remains within the biological window for eradication should be driving program scope and resource commitment decisions. That question has no public, queryable home.

PestTrail's **Eradication Scorecard** tracks every pest record against its eradication status — not established / eradication ongoing / established / eradicated — alongside the years elapsed since first detection. This is the framework needed to evaluate whether eradication investment is being directed at pests that can still be eliminated, or whether resources are being committed to containment programs that have no realistic path to pest-free status.

### Gap 4 — Economic Damage Cannot Be Attributed to Pathway Failures

The US absorbs an estimated $40 billion annually in invasive species damage across agriculture, forestry, urban infrastructure, and ecosystem services. This figure is cited frequently. It is almost never attributed to specific pathway failures — because the pathway data that would enable that attribution does not exist in a public, analyzable form.

Attribution matters because it is the precondition for cost-benefit analysis of prevention investment. The argument for significantly increasing inspection intensity of solid wood packing materials from East Asia — beyond the $75 million annual federal allocation for all plant pest prevention programs — requires demonstrating that this pathway is responsible for a calculable share of identifiable damage. That calculation requires pathway-attributable damage data.

PestTrail builds the analytical foundation for this attribution. When the platform shows that wooden packaging from East Asia accounts for the Emerald Ash Borer ($10.7B), Asian Longhorned Beetle ($669B potential), and Sirex Woodwasp ($1.5B/yr potential) — all from a single pathway-origin combination — it is making the cost-benefit argument that prevention investment in this pathway would yield returns many orders of magnitude beyond its cost.

### Gap 5 — The Threat Horizon Has No Public Dashboard

Two high-consequence pathogens currently under USDA APHIS active surveillance have not yet established in the continental United States. Both have pathway profiles that closely match conditions that preceded past major invasions. Neither has a public dashboard tracking their approach.

**Wheat Stem Rust Race Ug99 (Puccinia graminis f. sp. tritici, race TTKSK)** — first identified in Uganda in 1999, now established across East Africa, the Horn of Africa, and extending into South Asia and the Middle East. FAO estimates 90% of global wheat varieties are susceptible. US wheat is no exception. The Great Plains — the most productive wheat belt in the world — sits downwind of the long-range atmospheric dispersal corridor through which Ug99 is advancing. $10 billion+ in US wheat production is at risk.

**Wheat Blast (Magnaporthe oryzae Triticum pathotype)** — first described in Brazil in 1985, now endemic across South America and detected in Bangladesh in 2016, confirming intercontinental spread. Causes 80%+ yield losses in epidemic years. US imports wheat from South America. Seed-surface contamination is a confirmed introduction pathway. The US has no existing resistance or treatment options for Wheat Blast in commercial wheat production.

PestTrail's **Threat Horizon** section tracks these and future at-risk pathogens against the pathway profiles of past major introductions — making the case for preemptive surveillance investment before detection lags begin accumulating.

---

## The Scale of the Problem

| Metric | Figure | Source |
|---|---|---|
| Annual US economic damage, invasive species | **$40 billion/year** | USDA |
| Annual federal investment in plant pest prevention | **$75 million/year** | USDA APHIS FY2025, PPA §7721 |
| Cumulative US losses (1960–2020) | **$1.22 trillion** | Diagne et al., *Science of the Total Environment*, 2022 |
| Global annual cost | **$423 billion/year** | UN Environment Programme, 2023 |
| EAB — urban tree loss | **$10.7 billion** | Kovacs et al., USFS, 2010 |
| Citrus Greening (HLB) — FL citrus losses | **$4.5+ billion** | UF/IFAS FE903; FDACS |
| Citrus Greening — FL orange production decline | **74%+ since 2005; 90%+ by 2025** | FDACS; USDA ERS |
| Citrus Canker eradication program cost | **$1.4 billion+** | USDA APHIS; Federal Register 2006 |
| ALB — potential urban forest loss | **$669 billion** | Nowak et al., 2001 |

**The spending-damage gap:** The federal government spends $75 million per year on plant pest prevention while absorbing $40 billion per year in damage. That is a 533:1 loss ratio. No private sector risk management framework would accept that ratio without a fundamental re-examination of the prevention architecture. The academic and policy case for rebalancing this ratio is unambiguous. The analytical infrastructure to make that case has not existed. PestTrail is part of building it.

---

## What PestTrail Does

### Unified Historical Intelligence Database (1995–Present)

A structured, cross-validated database of invasive pests and pathogens introduced to the US since 1995, integrating records from US-RIIS, USDA APHIS, EDDMapS, EPPO Global Database, and peer-reviewed literature into a single schema. Each record captures:

- Standardized common and scientific name (with taxonomic authority)
- **Year of first confirmed US detection** (verified against primary USDA or peer-reviewed source)
- **Estimated year of actual arrival** (where determinable from tree-ring data, genetic analysis, or epidemiological back-calculation)
- **Detection lag** in years — the operationalized surveillance performance metric
- Country and region of origin (with confirmation method noted)
- Mode of entry (cargo; nursery stock; mail and parcels; passenger baggage; wind dispersal; natural spread)
- Commodity pathway (solid wood packing material; fresh produce; ornamental stock; etc.)
- US port of entry or first detection location
- Host plant or animal (with specificity)
- US states currently affected
- Spread rate (km/year, where documented in peer-reviewed literature)
- Economic impact estimate with source publication and year of estimate
- Affected agricultural or forestry sector
- Inoculum type and transmission biology (for pathogens)
- Current quarantine and regulatory status
- **Eradication status**: Not Yet Arrived / Eradication Ongoing / Established / Eradicated

### Pathway Hotspot Analysis

The central analytical innovation of PestTrail. Rather than asking *where are invasive pests distributed*, Pathway Hotspot Analysis asks:

- Which **origin countries** have produced the highest number of established, high-impact introductions?
- Which **commodity pathways** appear repeatedly in the establishment records of the most damaging pests?
- Which **US ports of entry** are associated with the highest establishment rates?
- Which **agricultural sectors** are most exposed, based on pathway pattern history?

The pattern that emerges from 30 validated case studies is stark: **East Asian origin combined with solid wood packing material accounts for a disproportionate share of the highest-impact pest introductions in US history.** The EAB, ALB, Spotted Lanternfly, Brown Marmorated Stink Bug, and Sirex Woodwasp all share this pathway profile. This is not coincidence — it is a systemic vulnerability in the inspection framework for wooden packaging from this trade corridor.

### Detection Lag Analysis

For each pest in the database: how many years elapsed between estimated arrival and confirmed detection?

Aggregated across all records: what is the mean detection lag? Do insects have longer lags than fungal pathogens? Are wood-boring beetles harder to detect early than sap-feeding hemipterans? Which entry pathways are associated with the worst detection rates?

This analysis directly quantifies where surveillance redesign is most needed — and provides the evidentiary basis for that argument in policy settings.

### Eradication Scorecard

An honest accounting of what the US eradication record actually shows:

- **Successfully eradicated:** Plum Pox Virus (20-year program, declared complete October 2019; protected $6.3B stone fruit industry); Northern Giant Hornet (4 nests located and destroyed, declared eradicated December 2024)
- **Eradication ongoing:** Asian Longhorned Beetle (active since 1996); Coconut Rhinoceros Beetle, Oahu (active since 2013)
- **Established — eradication abandoned:** Emerald Ash Borer (quarantine lifted 2021); Citrus Canker (eradication program abandoned January 2006 after $1.4B spent)
- **Established — management only:** 20+ additional species

The pattern is unambiguous: **pests detected within 2 years of estimated arrival have been eradicated. Pests with detection lags exceeding 5 years have not.** This relationship is the core policy argument for early detection investment — and it is visible in the data.

### Temporal Trend Dashboard

How has the rate of new invasions changed from 1995 to present? Did the tightening of phytosanitary standards following the International Standards for Phytosanitary Measures No. 15 (ISPM-15) for wooden packaging affect introduction rates post-2002? Did COVID-era supply chain disruptions alter origin patterns? What seasonal patterns exist in first detections?

### Threat Horizon

Pests not yet established in the continental US, tracked against the pathway and origin profiles of past high-impact introductions. Currently monitoring: Wheat Stem Rust Ug99 (TTKSK) and Wheat Blast (*Magnaporthe oryzae* Triticum pathotype).

---

## Data Sources and Validation Standard

| Source | Records | Access |
|---|---|---|
| US Register of Introduced and Invasive Species (US-RIIS) | 15,264 taxa | Public — USGS |
| Early Detection & Distribution Mapping (EDDMapS) | 8.6M+ observations | Public — eddmaps.org |
| USDA APHIS CAPS | Federal surveillance | Public — USDA |
| EPPO Global Database | 98,700+ species | Public — gd.eppo.int |
| USDA Forest Service AFPE | Forest pest spatial data | Public — USFS |
| Peer-reviewed literature | Pathway and impact data | APS, USDA ERS, UF/IFAS |

**Validation standard:** Every economic figure in the database is cited to a primary source with year of estimate. Where a figure appeared only in secondary sources without traceable primary citation, it was removed. Where more recent authoritative estimates supersede older figures, the current estimate is used and the prior figure is noted. Figures that could not be verified against USDA official documents, federal register entries, or peer-reviewed publications are not included.

---

## Verified Case Studies

| Pest | Estimated Arrival | Confirmed Detection | Lag | Origin | Pathway | Verified Impact |
|---|---|---|---|---|---|---|
| Emerald Ash Borer | ~1992 | 2002 | **10 yr** | China | Solid wood packing | $10.7B — Kovacs et al., USFS 2010 |
| Spotted Lanternfly | ~2012 | 2014 | 2 yr | China/S. Korea | Stone shipment (egg masses) | $324.9M/yr potential statewide PA — Penn State 2019 |
| Brown Marmorated Stink Bug | ~1996 | 1998 | 2 yr | China | Shipping containers | $37M/yr agricultural — USDA ARS |
| Citrus Greening (HLB) | ~late 1990s | 2005 (disease FL) | 5–7 yr | South/SE Asia | Ornamental citrus nursery stock | $4.5B+ FL losses — UF/IFAS FE903 |
| Asian Longhorned Beetle | ~early 1990s | 1996 | ~4 yr | China | Wooden crating | $669B potential urban forest — Nowak et al. 2001 |
| Citrus Canker | 1994–1995 | 1995 | 0 yr | Asia | Nursery stock | $1.4B+ eradication cost — USDA APHIS |
| Spotted Wing Drosophila | 2008 | 2008 | 0 yr | East Asia | Produce/trade | $1.275B/yr national — USDA 2022 |
| Plum Pox Virus | 1999 | 1999 | 0 yr | Europe (Bulgaria) | Nursery budwood | $6.3B stone fruit industry protected — USDA APHIS |
| N. Giant Hornet | 2019 | 2019 | 0 yr | East Asia | Shipping cargo | Eradicated Dec 2024; $15B+ pollination services at risk |
| Asian Soybean Rust | 2004 | 2004 | 0 yr | Asia via S. America | Hurricane Ivan atmospheric dispersal | $240M–$2B/yr potential — USDA ERS |
| Wheat Stem Rust Ug99 | Not yet arrived | — | — | Uganda/E. Africa | Wind dispersal | $10B+ US wheat at risk — USDA ARS; 90% global varieties susceptible (FAO) |

---

## Tech Stack

### Current — Phase 2 Prototype
- **Streamlit** — Python-based interactive analytical dashboard
- **Pandas** — pathway analysis and detection lag calculations
- **Plotly** — interactive charts, trend visualizations
- **SQLite** — visitor session analytics
- **Anthropic Claude API** — automated data update and validation agent (`data_update_agent.py`)

The update agent runs in three modes: daily (new detection sweep from USDA APHIS, NPDN, EDDMapS), weekly (existing record validation), and monthly (policy intelligence refresh — federal budget figures, ERS damage estimates, eradication program status). All updates require primary source confirmation before records are modified.

### Roadmap — Phase 3 Full Platform
- React frontend + FastAPI backend
- PostgreSQL with full US-RIIS and EDDMapS integration
- Real-time APHIS PestLens API feed
- Predictive pathway risk scoring model
- Public API for USDA/APHIS, CGIAR, and academic access

---

## Running Locally

```bash
git clone https://github.com/Mary-Akinyuwa/pesttrail.git
cd pesttrail
pip install -r requirements.txt
streamlit run app.py
```

Requires Python 3.9+.

The data update agent requires an Anthropic API key set as an environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
python3 data_update_agent.py           # daily new detection sweep
python3 data_update_agent.py --validate   # weekly record validation
python3 data_update_agent.py --policy     # monthly policy intelligence refresh
```

---

## Project Structure

```
pesttrail/
├── app.py                             # Main Streamlit dashboard (1,089 lines)
├── data_update_agent.py               # Claude-powered automated validation agent
├── setup_daily_agent.sh               # Cron scheduling for automated updates
├── requirements.txt                   # Python dependencies
├── pages/
│   └── admin.py                       # Admin interface — session analytics
├── data/
│   ├── invasive_pests_1995_2025.csv   # Validated pest intelligence database (30 records)
│   ├── data_model.md                  # Field definitions and data dictionary
│   └── policy_intelligence.json      # Policy gap figures, sector vulnerability data
├── analytics/                         # Analytics modules
└── docs/                              # Supporting documentation
```

---

## Roadmap

- [x] Validated seed dataset — 30 high-impact pests and pathogens (1995–present), all figures primary-source verified
- [x] Streamlit prototype — pathway analysis, detection lag, temporal trends, pest search
- [x] Automated data update agent (Claude API) — daily, weekly, and monthly modes
- [ ] Eradication Scorecard page — visual timeline of eradication probability vs. years since establishment
- [ ] Sector Vulnerability Map — state-level exposure by commodity sector
- [ ] Threat Horizon page — at-risk pathogens not yet established, tracked against historical pathway profiles
- [ ] Economic Gap Dashboard — federal prevention spending vs. annual sector damage, interactive by pathway
- [ ] Expand dataset to 50+ pests with full primary source citations
- [ ] Integrate US-RIIS full dataset via USGS API
- [ ] Host-pathway network visualization (D3.js)
- [ ] Real-time APHIS PestLens feed integration
- [ ] Predictive pathway risk scoring model
- [ ] Public API for USDA/APHIS, CGIAR, and research access

---

## Why I Built This

I am a plant pathologist by training and practice. My doctoral and postdoctoral work focused on plant disease diagnostics, molecular characterization of fungal and bacterial pathogens, and field surveillance methodology. I have worked on disease detection programs in Nigeria, Europe, and the United States, including time at Corteva Agriscience applying molecular and strategic tools to crop protection at scale.

What I observed repeatedly, across multiple surveillance systems and institutional contexts, was the same pattern: the data needed to prevent a catastrophic introduction existed — somewhere, fragmented across incompatible databases, inaccessible to the analysts who needed it, and not synthesized in a form that supported decision-making. By the time a response was organized, the window for effective intervention had often already closed.

PestTrail is built around a specific conviction: **the most valuable contribution to US invasive species management is not more data collection — it is better synthesis of data that already exists, organized around the questions that drive prevention investment.** Which pathways produce the most damage? How long are we missing pests before we find them? Which active eradication programs still have a realistic path to success?

These questions have answers. They require analytical infrastructure to make those answers visible. That is what this platform builds.

The Emerald Ash Borer cost $10.7 billion in urban tree loss. It entered via a pathway that was already known to be high-risk. It was present for 10 years before it was found. A tool that made that pattern visible and queryable in 1998 would have been worth building.

---

## Data Integrity Statement

All economic figures in this platform are cited to primary sources with year of estimate. Where figures appeared only in secondary sources without a traceable primary citation, they were removed from the database. Where USDA official documents, federal register entries, or peer-reviewed publications provide more recent figures than earlier estimates, the current figure is used.

Specific corrections made during the April 2026 data validation audit:
- Brown Marmorated Stink Bug first detection corrected to 1998 (first collection, Allentown PA) from 2001 (formal species description)
- Citrus Greening FL production decline updated to 74%+ (74% confirmed by FDACS/USDA ERS; 90%+ by 2025)
- Citrus Canker eradication cost corrected to $1.4B+ (from $1B) per USDA APHIS and Federal Register records
- Hemlock Woolly Adelgid $29B figure removed — no USFS primary source located; replaced with accurate statement that full economic quantification is ongoing
- Wheat Stem Rust Ug99 susceptibility corrected to 90% of global wheat varieties (FAO) from uncited 80% figure
- Spotted Wing Drosophila economic impact updated to $1.275B/yr (2022 USDA national estimate) from earlier $500M figure
- Plum Pox Virus potential impact corrected to $6.3B stone fruit industry protected (USDA APHIS language) from unverified $4B figure

If you identify an error or have a more recent authoritative source for any figure, please open an issue.

---

## Related Work

- [PlantPath AI](https://github.com/Mary-Akinyuwa/plantpath-ai) — AI-powered plant disease diagnostic tool (Claude + ServiceNow)
- [LifeScience ServiceNow Workflows](https://github.com/Mary-Akinyuwa/lifescience-servicenow-workflows) — Reusable ServiceNow automation templates for life science organizations

---

## Author

**Mary Akinyuwa**

Published plant pathologist. Field experience across Nigeria, Europe, and the United States. Former research scientist at Corteva Agriscience, where my work contributed to $51M+ in documented cost savings across crop protection programs. Incoming MBA candidate, Tepper School of Business at Carnegie Mellon University (Class of 2028). Consortium Fellow. Forte Fellow.

My research background is in fungal and bacterial plant pathogen characterization, molecular diagnostics, and surveillance system design. My current work sits at the intersection of food systems strategy, AI-powered agricultural intelligence, and the policy frameworks that govern how the US protects its agricultural and forest resources from biological threat.

[LinkedIn](https://www.linkedin.com/in/mary-akinyuwa-700268165/) | [GitHub](https://github.com/Mary-Akinyuwa)

---

*Data sources: USDA APHIS · USGS US-RIIS · USFS NRS · EDDMapS (UGA) · EPPO Global Database · NISIC · APS Plant Disease · USDA ERS · UF/IFAS · Penn State Extension · Peer-reviewed literature*
