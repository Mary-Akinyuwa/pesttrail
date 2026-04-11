# PestTrail Data Model

## Core Table: `invasive_pests`

| Field | Type | Description | Source |
|---|---|---|---|
| `pest_common_name` | String | Common name(s) used in field and policy contexts | USDA APHIS |
| `pest_scientific_name` | String | Binomial nomenclature (standardized taxonomy) | ITIS / EPPO |
| `pest_type` | Enum | Insect; Fungal Pathogen; Bacterial Pathogen; Viral Pathogen; Nematode; Oomycete; Weed; Other | Taxonomy |
| `year_first_detected_us` | Integer | Year of confirmed first US detection (official record) | USDA APHIS / State Records |
| `estimated_year_arrival` | Integer | Estimated actual year of US arrival (often precedes detection) | Academic literature |
| `detection_lag_years` | Computed | `year_first_detected_us - estimated_year_arrival` | Computed |
| `origin_country` | String | Primary country of origin | USDA / Academic literature |
| `origin_region` | String | Broader geographic region (East Asia; South Asia; Europe; etc.) | USDA / EPPO |
| `mode_of_entry` | Enum | Cargo; Passengers/Baggage; Mail/Parcels; Nursery Stock; Natural Spread; Wind Dispersal; Unknown | USDA APHIS pathway analysis |
| `commodity_pathway` | String | Specific commodity type that served as pathway (wooden crates; fresh fruit; ornamental plants; etc.) | USDA APHIS |
| `port_of_entry` | String | US port where pest likely entered or was first detected | USDA CBP / APHIS |
| `host_plant_animal` | String | Primary host(s) in the US | USDA / EPPO |
| `us_states_affected` | String | States with confirmed presence (comma-separated) | USDA APHIS / EDDMapS |
| `spread_rate_km_per_year` | String | Estimated annual spread rate (range if variable) | Academic literature |
| `economic_impact_usd` | String | Estimated annual or cumulative economic impact | USDA / Academic literature |
| `impact_sector` | String | Primary affected sector (Forestry; Agriculture - Citrus; Horticulture; etc.) | USDA |
| `quarantine_status` | String | Current federal/state quarantine and regulatory status | USDA APHIS |
| `data_sources` | String | Primary sources for this record | Various |

---

## Data Sources

| Source | Coverage | Access |
|---|---|---|
| US-RIIS (USGS) | 15,264 introduced species records | Public — USGS data portal |
| EDDMapS (UGA) | 8.6M+ observation records | Public — eddmaps.org |
| USDA APHIS CAPS | Federal surveillance data | Public — USDA website |
| EPPO Global Database | 98,700+ species; regulatory pests | Public — gd.eppo.int |
| USDA Forest Service AFPE | Forest pest spatial data | Public — USFS data portal |
| iMapInvasives | Multi-state observation data | Public — imapinvasives.org |
| Academic Literature | Pathway and impact estimates | PubMed; Google Scholar |

---

## Key Computed Fields (for dashboard analytics)

| Computed Field | Formula | Purpose |
|---|---|---|
| `detection_lag_years` | `year_first_detected_us - estimated_year_arrival` | Shows surveillance gap |
| `introduction_decade` | Decade of estimated arrival | Temporal trend analysis |
| `origin_region_group` | Grouped region | Hotspot analysis by origin |
| `pathway_category` | Grouped pathway type | Entry mode analysis |
| `economic_impact_tier` | Low (<$1M) / Medium ($1M-$100M) / High ($100M-$1B) / Critical (>$1B) | Risk tier visualization |

---

## Future Data Fields (Phase 2)

- `first_interception_date` — date pest was first intercepted at US border (if applicable)
- `number_of_border_interceptions` — how many times intercepted before establishment
- `control_methods_deployed` — pesticide; biocontrol; eradication; containment
- `eradication_outcome` — successful; ongoing; abandoned
- `climate_risk_projection` — projected range expansion under climate scenarios
- `trade_partner_flag` — whether origin country is major US trade partner
