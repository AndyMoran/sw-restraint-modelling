# Constraint Event Modelling — GB System vs South West

## Executive Summary

This project analyses constraint events in the GB electricity system, comparing system-level behaviour with a regional deep dive in the South West (SW).

At a system level, constraint risk increases significantly with wind generation (from ~3% to ~11%, a ~3× increase). However, this relationship does not hold in the South West. Rather than indicating that wind is unimportant, this suggests that GB-wide wind generation is not the dominant physical driver of South West constraints, highlighting the importance of modelling regional systems using locally relevant generation characteristics.

Non-linear modelling suggests some structural variation in risk across combinations of wind and demand, but empirical validation shows that these effects are modest and constraint events remain rare (~3%) across all conditions.

The key finding is that constraint dynamics are region-specific and cannot be inferred from system-wide relationships alone.

---

## Hypothesis

Based on system-level behaviour, we expected high GB wind generation to increase South West constraint probability.

However, given the regional nature of the South West, we also consider the possibility that constraint behaviour may differ due to local demand conditions and network flows.

---

## Data Sources

* **Wind generation**: GB wind generation time series aligned to settlement periods
* **Demand**: South West Grid Supply Point (GSP) demand proxy
* **Balancing Mechanism (BOALF)**: Accepted *Bid/Offer Acceptance Limitations and Factors* volumes by *Balancing Mechanism Unit (BMU), aggregated using volume-weighted measures to reflect the scale of accepted actions.*

All data is aligned to **settlement period (SP)** granularity (1–48 per day).

---

## Methodology

### 1. Settlement Period Alignment

A consistent key is constructed:

```
sp_key = settlement_date + "_" + settlement_period
```

The demand dataset defines the complete timeline (**17,520 SPs in 2022**), onto which all other data is mapped.

---

### 2. Wind Data Construction

Wind generation is constructed as a continuous time series aligned to settlement periods.

Earlier iterations using intraday forecast vintages exhibited significant sparsity (~80% missing), requiring interpolation. These approaches were not retained due to the risk of smoothing short-term dynamics.

In the final dataset, a more complete wind series is used, preserving realistic short-term variability and avoiding the need for heavy interpolation. This ensures that ramping behaviour and system conditions are more accurately represented.

---

### 3. Constraint Event Definition

#### System (baseline)

* Large BOALF actions defined via volume threshold
* Constraint event = ≥2 large actions per SP
---

#### South West (final model)

* Total accepted BM volume per SP calculated
* Active SPs (non-zero activity) isolated
* Threshold = **75th percentile of active SPs**

For 2022:

* Threshold ≈ 34 MW
* Active SPs ≈ 12.9%
* Constraint events ≈ **3.1% of all SPs**

**Rationale:**
Regional BM actions are smaller than system-level actions, making absolute thresholds unsuitable. A percentile-based approach captures **relative abnormal activity**.

---

### 4. Modelling Approach

#### Logistic Regression (Baseline)

```
constraint_event ~ wind_mw + sw_demand_mw + interaction
```

The interaction term (wind × demand) was included to capture combined effects. This term showed limited statistical significance, suggesting that interactions exist but are not strongly expressed in a linear framework.

---

#### Random Forest (Non-linear Analysis)

Used to:

* detect non-linear relationships
* identify interaction effects (via Partial Dependence Plots)
* explore regime-based behaviour

Model configured with:

* shallow trees (max_depth=5)
* class_weight='balanced' to address the ~3% event rate

---

### 5. Evaluation

Due to strong class imbalance:

* **Precision–Recall AUC** and **F1-score** used
* Raw accuracy avoided

Model performance is modest, reflecting:

* low event frequency
* limited feature set

The objective is **interpretation rather than prediction**.

---

## Key Findings

### 1. System-Level Behaviour

* Constraint events are rare (~3%)
* Probability increases with wind generation
* At high wind levels, risk increases significantly **(from ~3% to ~11%, a ~3× increase)**

---

### 2. South West Behaviour

The South West shows a **different relationship**:

* Weak or slightly negative relationship between wind and constraint events
* Contrasts with system-level behaviour

This suggests that GB-wide wind generation is not an appropriate proxy for the dominant physical drivers of South West constraints. Unlike northern Scotland, where transmission constraints are heavily influenced by large onshore wind fleets, the South West has a markedly different generation mix. Constraint behaviour is therefore likely to be governed by local network conditions, embedded solar generation, demand patterns and reverse power flows.

---

### 3. Non-Linear Structure

Random Forest analysis indicates:

* Constraint risk is not monotonic
* Risk depends on combinations of wind and demand
* Structure exists, but effects are modest

---

### 4. Empirical Validation

A binned heatmap of observed constraint probabilities shows:

* Constraint events remain **rare across all conditions (~3%)**
* No region exhibits dramatically elevated risk
* Variation is continuous and subtle

---

### 5. Key Insight

> Non-linear models suggest structure, but empirical data shows the effect size is small.

Constraint risk in the South West is:

* **structurally non-linear**, but
* **low in magnitude across all operating conditions**

---

## Model-Driven Implications & Further Analysis

These are logical extensions of the modelling results, translating statistical findings into operational questions:

| Question                                    | What this would look like                                       |
| ------------------------------------------- | --------------------------------------------------------------- |
| When do these rare constraint events occur? | Time-of-day and month-of-year breakdown of events               |
| How much volume is involved?                | Distribution of BM volumes conditional on events                |
| Which BMUs are driving it?                  | Top BMUs by accepted volume during events                       |
| What is the false alarm cost?               | Rate of incorrect model alerts (false positives)                |
| Is there a simple rule of thumb?            | Identify regions of wind–demand space with zero observed events |

---

### Rule of Thumb Results

The system can be broadly segmented into three regimes based on wind generation and South West demand:

- **Low-risk (Safe zone):**  
  Demand < 1400 MW and wind < 5000 MW  
  → **0 observed constraint events** (no-event zone)  
  → Covers **~26% of settlement periods**

- **Elevated-risk (Watch zone):**  
  Demand > 1800 MW and wind > 4000 MW  
  → **~4.8% event rate** (vs ~3.1% baseline) across **1,447 settlement periods**  
  → Covers **~8% of settlement periods**

- **Neutral:**  
  All other conditions  
  → Baseline constraint probability (~3.1%)

**Interpretation:**  
Constraint risk is a function of system state rather than a random process. A significant portion of the year (~26%) sits in a no-risk regime, while elevated-risk conditions are relatively rare (~8%) but associated with a meaningful increase in constraint probability. This provides a simple operational filter: exclude risk in the safe zone and focus attention when the system enters elevated-risk conditions.
Elevated-risk conditions occur predominantly during winter months (December–February) and peak demand hours (late afternoon to evening), consistent with system stress driven by high demand.

## So What?

* **System-level insights do not generalise regionally**
* Constraint risk is driven by **local system conditions**, not national trends
* GB wide wind generation alone is not a reliable predictor of regional constraints
* Non-linear structure exists, but effects are **subtle rather than dominant**
* Empirical validation is essential to avoid over-interpreting model outputs

Constraint behaviour is best understood as a function of **system state**, not individual variables.

---

## Limitations

* Limited feature set (no explicit network topology or flows)
* Demand proxy used for regional load
* Constraint events inferred from BM activity
* Rare-event modelling inherently noisy
* GB-wide wind generation is used as a system-level explanatory variable and does not represent the local generation mix of the South West, which is characterised by relatively low wind capacity and significant embedded solar generation.

---

## Next Steps

* Incorporate network flow and constraint location data
* Extend analysis to other regions
* Explore time-series models for persistence effects
* Incorporate regional solar generation and embedded generation as local explanatory variables
* Compare GB system variables against regional physical drivers
* Incorporate network flow and constraint location data
---

## Summary

This project demonstrates that:

* Clean data construction enables meaningful analysis
* Regional modelling reveals behaviour hidden at system level
* Non-linear models help identify structure
* Empirical validation ensures conclusions remain grounded

Non-linear models suggest where to look; empirical data determines what is real.

## Project Reflection

The initial scope assumed a strong relationship between wind generation and constraint events, based on system-level behaviour. However, this relationship did not hold in the South West region, prompting a shift toward region-specific analysis.

Several data and modelling decisions materially shaped the final results:

- **Wind data sparsity:**  
  Early iterations using intraday forecast vintages exhibited significant sparsity (~80% missing), requiring interpolation. This approach was rejected in favour of a more complete wind series to preserve realistic variability and avoid smoothing system dynamics.

- **Aggregation methodology:**  
  Simple averaging of Balancing Mechanism volumes was found to under-represent the scale of system actions. Volume-weighted aggregation was adopted to better reflect the relative impact of accepted volumes.

- **System vs regional behaviour:**  
  System-level patterns did not generalise to the South West, highlighting the importance of local demand conditions and network flows in driving constraint events.

- **Physical interpretation:**  
  The statistical result that GB wind had little explanatory power initially appeared surprising. However, this reflected an important physical reality: the South West is a low-wind, high-solar region. The model therefore highlighted not that wind is unimportant, but that regional constraint models must be built using variables that reflect the local generation mix and network physics.

The project evolved through iterative validation and an adversarial approach to modelling assumptions. This helped prevent over-interpretation of weak signals and ensured that conclusions remained grounded in observed data.

A key takeaway is that constraint dynamics are highly context-dependent, and robust analysis requires both careful data construction and empirical validation.

## Next Project: From Risk to Value. Basis Implications

The current analysis establishes that regional constraint behaviour differs from system-level behaviour and identifies interpretable risk regimes. The next logical step is to determine whether those regimes translate into economically meaningful price dislocations.

A natural extension is to translate constraint probability into **basis risk**:

- Define the spread between **System Price** and the **average bid price of curtailed units** during constraint events  
- Evaluate how this spread behaves across the identified risk regimes  

This reframes the model from:

- “What is the probability of a constraint?”  

to:

- “What is the expected economic impact of a constraint?”

For example:

In elevated-risk regimes, constraint events may be associated with widening basis spreads (e.g. £X/MWh), creating potential opportunities to position against local generation or regional price indices.

This extension would allow the model to move from **risk classification** to **tradable signal generation**, linking system conditions directly to financial outcomes.
