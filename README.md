# Constraint Event Modelling — GB System vs South West

## Executive Summary

This project analyses constraint events in the GB electricity system, comparing system-level behaviour with a regional deep dive in the South West (SW).

At a GB system level, constraint risk increases significantly with wind generation, rising from approximately **3% to 11%** at high wind levels — around a **3× increase**.

However, this relationship does **not** generalise to the South West. Regional constraint events remain rare, occurring in approximately **3% of settlement periods**, and show a weak or slightly negative relationship with GB-wide wind generation.

The key finding is not simply that “wind does not matter”. It is that **GB-wide wind generation is the wrong physical proxy for South West constraint behaviour**.

The South West has a different local asset mix and network structure from the constraint-heavy Scottish export regions that dominate the national wind–constraint relationship. South West constraint dynamics are more likely to be shaped by local demand, embedded generation, reverse-flow conditions, Grid Supply Point (GSP) limits, and distribution-network behaviour — many of which are only partially visible in national Balancing Mechanism data.

The project therefore demonstrates a broader modelling lesson:

> System-level relationships cannot be assumed to hold regionally unless the causal mechanism and data layer are aligned.

---

## Hypothesis

Based on system-level behaviour, the initial hypothesis was:

> High GB wind generation should increase South West constraint probability.

This was motivated by the strong relationship between national wind output and GB system constraint activity.

However, the regional analysis tested whether that system-level relationship was physically meaningful in the South West, rather than assuming it would generalise automatically.

---

## Data Sources

The analysis uses settlement-period-level data for 2022.

* **GB wind generation**
  System-wide wind generation aligned to settlement periods.

* **South West demand proxy**
  Regional Grid Supply Point (GSP) demand used as a proxy for South West load.

* **Balancing Mechanism activity (BOALF)**
  Accepted Bid/Offer Acceptance Level and Factor data by Balancing Mechanism Unit (BMU), aggregated to settlement-period level using volume-weighted measures to reflect the scale of accepted actions.

All datasets are aligned to **settlement period (SP)** granularity, with 48 settlement periods per day.

---

## Data-Layer Caveat

A key lesson from the project is that the **data layer matters as much as the model**.

BOALF captures Balancing Mechanism actions from BM-visible assets. It does not fully represent all embedded generation or distribution-network actions, particularly smaller embedded solar assets that may be managed through distribution-level mechanisms rather than appearing directly in national BM data.

This means the South West model should not be interpreted as a complete model of all local physical constraint drivers. It is better understood as a model of **BM-visible regional constraint activity** using the available system-level and regional demand variables.

This distinction is central to the interpretation of the results.

---

## Methodology

### 1. Settlement Period Alignment

A consistent settlement-period key is constructed:

```python
sp_key = settlement_date + "_" + settlement_period
```

The demand dataset defines the complete 2022 timeline, covering:

```text
17,520 settlement periods
```

Wind generation, demand and Balancing Mechanism activity are mapped onto this common settlement-period structure.

---

### 2. Wind Data Construction

Wind generation is constructed as a continuous time series aligned to settlement periods.

Earlier iterations using intraday forecast vintages exhibited significant sparsity, requiring interpolation. These approaches were not retained due to the risk of smoothing short-term dynamics.

The final dataset uses a more complete wind series, preserving realistic short-term variability and avoiding heavy interpolation.

Important interpretation:

> GB wind is included as a system-level explanatory variable, not as a local South West generation proxy.

---

### 3. Constraint Event Definition

#### System-level baseline

At system level:

* Large BOALF actions are identified using a volume threshold
* A constraint event is defined where multiple large actions occur in the same settlement period

This provides a GB-wide reference point for comparing system behaviour with regional behaviour.

#### South West regional model

For the South West:

* Total accepted BM volume is calculated per settlement period
* Active settlement periods with non-zero BM activity are isolated
* The regional event threshold is set at the **75th percentile of active settlement periods**

For 2022:

```text
Threshold: approximately 34 MW
Active settlement periods: approximately 12.9%
Constraint events: approximately 3.1% of all settlement periods
```

### Rationale

Regional BM actions are much smaller than system-level actions. A fixed national threshold would miss most regional activity. A percentile-based threshold captures **relative abnormal regional BM activity**.

---

## Modelling Approach

### Logistic Regression

A baseline logistic regression model is estimated:

```text
constraint_event ~ wind_mw + sw_demand_mw + wind_mw × sw_demand_mw
```

The interaction term tests whether wind and demand jointly explain South West constraint probability.

The linear model finds limited evidence of a strong monotonic relationship between GB wind and South West constraint events.

---

### Random Forest

A Random Forest model is used to explore non-linear structure.

The model is configured with:

```text
max_depth = 5
class_weight = 'balanced'
```

This helps address the low event rate while keeping the model interpretable.

The Random Forest is used for:

* detecting non-linear relationships
* identifying interaction effects
* exploring regime-based behaviour
* generating partial dependence plots

However, model outputs are not treated as sufficient evidence on their own. They are checked against empirical event rates.

---

## Evaluation

Due to strong class imbalance, raw accuracy is not used as the primary metric.

Instead, the project focuses on:

* Precision–Recall AUC
* F1-score
* observed event rates
* empirical binned heatmaps

The objective is **interpretation rather than prediction**.

Model performance is modest, reflecting:

* low event frequency
* limited feature set
* incomplete visibility of distribution-level drivers
* the use of GB-wide wind as a system proxy rather than a local physical variable

---

## Key Findings

## 1. System-Level Behaviour

At GB system level:

* Constraint events are rare
* Constraint probability increases strongly with wind generation
* At high wind levels, estimated risk rises from approximately **3% to 11%**
* This is around a **3× increase**

This confirms the expected national relationship between wind output and constraint activity.

---

## 2. South West Behaviour

The South West does not follow the GB system-level pattern.

Regional constraint events:

* remain rare at approximately **3%** of settlement periods
* show a weak or slightly negative relationship with GB-wide wind
* do not exhibit a strong monotonic wind-driven risk pattern

This result initially appeared counter-intuitive, but the physical interpretation is clearer once the data layer and network structure are considered.

GB-wide wind is a poor proxy for South West constraint behaviour because the South West is not dominated by the same large transmission-connected wind export mechanism that drives many Scottish and northern constraint events.

Instead, South West constraint dynamics are more likely to involve:

* embedded solar
* local demand
* reverse-flow conditions
* GSP limits
* distribution-network behaviour
* BMU visibility thresholds

---

## 3. Non-Linear Structure

Random Forest analysis detects some non-linear structure across combinations of wind and demand.

However, empirical validation shows that the effects are modest. No region of the observed wind–demand feature space produces dramatically elevated constraint risk.

The model is useful as a structure detector, but not as a standalone source of truth.

---

## 4. Empirical Validation

A binned heatmap of observed constraint probabilities shows:

* constraint events remain rare across almost all conditions
* variation is continuous and subtle
* modelled high-probability regions are not strongly supported by observed event rates

This prevents over-interpreting Random Forest artefacts as physical grid behaviour.

---

## 5. Main Insight

The main insight is methodological as much as regional:

> The model correctly showed that the system-level relationship broke down regionally. The deeper lesson is that the explanatory variable was not causally aligned with the local physical mechanism.

GB-wide wind explains part of the national transmission constraint story. It does not adequately explain South West local constraint behaviour.

---

## Rule of Thumb Results

Using the available wind–demand feature space, settlement periods can be segmented into three empirical regimes.

These regimes should be interpreted as **descriptive statistical filters**, not as causal physical drivers.

### Low-risk zone

```text
South West demand < 1400 MW
GB wind < 5000 MW
```

Observed result:

```text
0 observed constraint events
covers approximately 26% of settlement periods
```

### Elevated-risk zone

```text
South West demand > 1800 MW
GB wind > 4000 MW
```

Observed result:

```text
approximately 4.8% event rate
baseline approximately 3.1%
1,447 settlement periods
covers approximately 8% of settlement periods
```

### Neutral zone

All other conditions.

Observed result:

```text
approximately baseline event probability
```

### Interpretation

The rule of thumb shows that constraint risk is not purely random. Some combinations of available variables are associated with lower or higher observed event rates.

However, because GB wind is not a local South West physical proxy, these regimes should not be interpreted as the final physical explanation of South West constraints.

The rule of thumb is useful as a diagnostic result, but future work should rebuild the regime framework using local solar, local net demand and embedded-generation indicators.

---

## So What?

This project shows that:

* system-level electricity-market relationships do not necessarily generalise regionally
* GB-wide wind is not a reliable physical proxy for South West constraint behaviour
* regional modelling requires variables aligned to local asset mix and network topology
* BM-visible data may miss important distribution-level mechanisms
* non-linear models can detect structure, but empirical validation is essential
* weak regional results can reveal a framing problem rather than a modelling failure

The key practical lesson:

> Before modelling regional constraint behaviour, check whether the explanatory variables are physically connected to the local constraint mechanism.

---

## Limitations

This project has several important limitations:

* GB-wide wind is used as a system-level explanatory variable and does not represent the local South West generation mix
* Local embedded solar is not explicitly modelled
* Distribution-level actions may not be visible in BOALF data
* Demand is represented using a regional GSP demand proxy
* Constraint events are inferred from BM activity rather than directly observed network constraints
* The model does not include explicit network topology, constraint boundaries or power-flow data
* Rare-event modelling is inherently noisy
* Random Forest probabilities are not treated as calibrated event probabilities

These limitations are not incidental. They are central to the interpretation of the project.

---

## Next Steps

The most important next step is to replace GB-wide wind with locally relevant South West physical variables.

Future work should incorporate:

* regional solar generation
* embedded generation estimates
* local net demand
* reverse-flow indicators
* GSP-level constraints
* network topology and constraint-location data
* distribution-level flexibility and curtailment signals
* comparison between BM-visible and distribution-visible activity

A revised regional model would test whether South West constraint events are better explained by:

```text
embedded solar + low local demand + reverse-flow conditions
```

rather than by GB-wide wind.

---

## Project Reflection

The initial scope assumed that the strong system-level relationship between wind generation and constraint events might also appear in the South West.

It did not.

The model found a weak or slightly negative relationship between GB wind and South West constraint events. At first, this appeared counter-intuitive.

The deeper issue was not the grid. It was the framing.

The project used a national transmission-level explanatory variable to model a regional constraint process that may be driven by local distribution-level conditions.

Several lessons followed.

### 1. Data construction matters

A complete settlement-period dataset enabled consistent comparison across system and regional models.

### 2. Regional thresholds matter

A percentile-based threshold was more appropriate than applying system-level volume thresholds to regional BM activity.

### 3. Model validation matters

Non-linear models suggested structure, but empirical heatmaps showed that effect sizes were small.

### 4. The data layer matters

BOALF captures BM-visible activity. It does not fully represent all embedded or distribution-level actions.

### 5. Causal framing matters

Before modelling, the physical mechanism should be specified:

```text
What is the variable measuring?
What network layer does it represent?
How does it connect to the outcome?
What important mechanisms are invisible in the data?
```

This is the strongest lesson from the project.

---

## Summary

This project demonstrates that:

* clean data construction enables meaningful analysis
* system-level relationships can fail at regional scale
* regional electricity-market models require regional physical variables
* non-linear models are useful for exploration but must be empirically validated
* weak or null results can reveal important causal and data-layer mismatches

The final conclusion is:

> Non-linear models suggest where to look. Empirical data determines what is real. Causal structure explains why.

---

## Future Project Direction

This project motivates a follow-on analysis focused on local physical drivers of South West constraint risk.

Potential extensions include:

### 1. Local Solar and Net Demand

Test whether South West constraint events are better explained by:

```text
high embedded solar
low local demand
low or negative local net demand
reverse-flow risk
```

### 2. Distributed Flexibility and VPPs

Investigate whether distributed flexibility, BESS and virtual power plants could help manage local constraint regimes by absorbing excess embedded generation or shifting demand.

### 3. Basis Risk

Test whether identified regional risk regimes translate into economically meaningful price dislocations, such as spreads between System Price and accepted BM bid prices.

These extensions would move the work from:

regional constraint classification

toward:

physical mechanism modelling and flexibility value
