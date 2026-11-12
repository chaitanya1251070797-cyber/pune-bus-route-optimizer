# PMPML Pulse: Crowd-Aware Dynamic Route Optimization and Demand Prediction for Bus Transit in the Pune Metropolitan Region

**Devang Patil, Chaitanya Patil, Divya Patil, and Disha Patil**  
Department of Computer Engineering, Vishwakarma Institute of Technology, Pune 411037, Maharashtra, India  
{devang.patil, chaitanya.patil, divya.patil, disha.patil}@vit.edu

---

> *Abstract* — Bus networks in fast-growing Indian cities run on fixed routes and timetables, so they cannot react when demand spikes or an arterial road jams. This paper presents PMPML Pulse, a browser-based tool for crowd-aware route planning and crowd prediction on the Pune Mahanagar Parivahan Mahamandal Ltd. (PMPML) bus network. The network is modelled as a directed weighted graph of 24 transit hubs joined by 38 road corridors. Edge costs combine distance, the predicted crowd density at each end of a corridor, and a chokepoint penalty; these costs drive Dijkstra and A∗ search, and a BPR-style volume–delay function then estimates travel time. Crowd density comes from a lightweight multiplicative regression model that accounts for hour, day of week, weather, and Pune's festival calendar, and it runs entirely in the browser. Pune Metro Lines 1 and 2 are overlaid for interchange guidance, and a rule-based module suggests extra buses at overloaded hubs. In a simulated monsoon morning-peak scenario on five origin–destination pairs, crowd-aware routes cut modelled travel time by 30.2% on average (up to 33.8%) compared with distance-only shortest paths. Across all 552 hub pairs, routing always succeeded, with an average latency of 0.15 ms. Because the crowd model was fitted to synthetic, domain-calibrated data, the results show feasibility rather than field-validated gains; we discuss this limitation and the path to real ridership data.

> *Index Terms* — A∗ search, BPR function, crowd prediction, Dijkstra's algorithm, intelligent transportation systems, public transit, Pune Metro, route optimization, smart city.

---

## I. INTRODUCTION

Pune is one of India's most congested metropolitan areas. It has more than 4.8 million registered vehicles, and PMPML buses carry over a million passengers on a typical day [1]. PMPML runs roughly 1,750 buses on about 315 routes, serving some 6,745 stops across Pune and Pimpri-Chinchwad [1]. All of this runs on fixed routes and timetables.

Fixed schedules work until something breaks the pattern. The morning rush into the Hinjewadi IT park, which employs several hundred thousand people, saturates the same few roads every weekday. Ganeshotsav processions close parts of Kasba Peth and Laxmi Road for hours. Monsoon waterlogging at Swargate and Katraj can stall an entire corridor. In each case buses stay on the congested road, bunch together, overcrowd the platforms ahead, and push the delay onto every route that shares the corridor.

Pune Metro Phase 1 adds another dimension. The Purple Line (PCMC to Swargate) and the Aqua Line (Vanaz to Ramwadi) give riders real alternatives to a jammed road, but bus journey planning does not yet take them into account.

We built PMPML Pulse to explore what a crowd-aware planner could do with no server and no paid data. This paper makes four contributions:

1. **Crowd-aware routing.** A Dijkstra cost function that adds predicted crowd density and a chokepoint penalty to distance, so routes bend around saturated corridors, together with a BPR-style travel-time estimate.
2. **A browser-side crowd predictor.** A multiplicative regression model calibrated for Pune's weather, festival calendar, commuting patterns, and hub types.
3. **Metro integration and fleet suggestions.** An overlay of Metro Lines 1 and 2 with feeder-bus guidance, and a rule that turns predicted overcrowding into an extra-bus recommendation.
4. **An offline-capable client.** A Progressive Web App (PWA) that keeps working without connectivity, evaluated over all 552 ordered hub pairs.

Section II reviews related work. Sections III–V describe the architecture, routing method, and crowd model. Section VI covers metro integration and Section VII the implementation. Section VIII presents the evaluation, Section IX its limitations, and Section X concludes.

---

## II. RELATED WORK

### A. Graph-Based Transit Routing

Dijkstra's shortest-path algorithm [2] and the A∗ heuristic search of Hart et al. [3] underpin most route planners. Both assume fixed edge weights, so using them for transit means making the weights depend on time and conditions. Bast et al. [4] survey speed-up techniques such as contraction hierarchies, which are very effective on large networks but rely on preprocessing static weights; that does not suit costs that change whenever the hour, weather, or festival input changes. Our graph has only 24 nodes, so we skip preprocessing and recompute costs for every query. For the delay itself we use a simplified form of the Bureau of Public Roads (BPR) volume–delay function [5], driven by predicted crowd density instead of a volume-to-capacity ratio.

### B. Transit Demand Prediction

Recurrent networks such as LSTM [6] and tree ensembles such as XGBoost [7] predict passenger demand well when long, labelled histories exist. We did not have access to PMPML ridership logs, and deep models are awkward to run inside a browser. Sun et al. [8] showed that a compact wavelet-SVM model can forecast short-term passenger flow on the Beijing subway. We follow that spirit of keeping the model small, but use explicit multiplicative factors that a planner can read, question, and adjust by hand.

### C. Indian Urban Transit

Work on intelligent routing for Indian bus systems is thin. Heterogeneous, mixed traffic makes delay parameters from Western studies hard to transfer directly; Velmurugan et al. [9] discuss how this affects roadway capacity estimates on Indian highways. The Smart Cities Mission [10] has funded several intelligent transport deployments, but many are proprietary and depend on dedicated infrastructure. We therefore treat our delay coefficients as tunable assumptions, not validated constants (Section IX).

---

## III. SYSTEM ARCHITECTURE

PMPML Pulse is a fully client-side PWA. Four layers (Fig. 1) pass data from the network definition, through crowd prediction and routing, to the interactive map.

```
┌──────────────────────────────────────────────────────┐
│  Layer 1 — Data Ingestion                            │
│  24 Pune Transit Hubs · 38 Arterial Edges · GTFS    │
│  Maha-Metro Purple & Aqua Line Coordinates           │
└──────────────────────────┬───────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────┐
│  Layer 2 — ML Crowd Prediction Engine                │
│  Multiplicative regression · Weather · Festival      │
│  Output: Node crowd density ∈ [0.05, 1.0]           │
└──────────────────────────┬───────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────┐
│  Layer 3 — Dynamic Cost Pathfinding                  │
│  Dijkstra · A* · BPR travel-time estimate            │
│  Avg. latency: 0.15 ms · 100% coverage (552 pairs)  │
└──────────────────────────┬───────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────┐
│  Layer 4 — Interactive Dashboard                     │
│  CARTO Light Map · 3D Tilt · Day/Night · Fleet Sim  │
│  Bus Suggester · PDF Export · Offline PWA            │
└──────────────────────────────────────────────────────┘
```

*Fig. 1. Architecture of PMPML Pulse.*

### A. Graph Data Model

The network is a directed weighted graph 𝒢 = (𝒱, ℰ). Each of the 24 nodes in 𝒱 is a major Pune or PCMC hub with coordinates, a category (IT corridor, commercial, terminal/interchange, or residential), and a peak-rush multiplier. Each of the 38 directed edges in ℰ is an arterial corridor with a Haversine distance *D*ₑ (km), a free-flow travel time *T*ₑᶠᶠ (min), a crowd-sensitivity index *S*ₑ ∈ [0.6, 1.4], and a binary chokepoint flag χₑ.

### B. Implementation Stack

**Table I — Technology Stack**

| Component | Technology |
|---|---|
| Framework | React 19, TypeScript 5.7 |
| Build | Vite 6.2 (vendor/map/icon chunks) |
| Styling | Tailwind CSS 3.4 |
| Mapping | Leaflet 1.9.4, CARTO Positron |
| Crowd model | Custom TypeScript regression |
| Offline | Service worker (sw.js) |

---

## IV. ROUTING METHOD

### A. Haversine Distance

$$D(u,v) = 2R \cdot \text{atan2}\!\left(\sqrt{a},\;\sqrt{1-a}\right) \tag{1}$$

$$a = \sin^2\!\tfrac{\Delta\phi}{2} + \cos\phi_u \cdot \cos\phi_v \cdot \sin^2\!\tfrac{\Delta\lambda}{2} \tag{2}$$

where Δφ = φᵥ − φᵤ, Δλ = λᵥ − λᵤ, and *R* = 6,371 km.

### B. Crowd Index

For every hub *u* the prediction model returns a crowd density *C*ᵤ between 0.05 and 1.0. Its inputs are the hour *h*, the day of week *d*, the weather *w* (clear, light rain, heavy monsoon, waterlogging, extreme heat), and the active festival *F* (none, Ganeshotsav, Palkhi, Diwali, New Year's Eve, Eid). The model is a product of factors:

$$C_u = \text{clip}\!\left(\gamma_u \cdot B_h \cdot M_d \cdot M_w \cdot M_F,\; 0.05,\; 1.0\right) \tag{3}$$

Here *B*ₕ is the base hourly demand curve (0.08–0.95), γᵤ = PeakMult(*u*)/2.3 normalizes each hub's rush intensity, and *M*_d, *M*_w, *M*_F are the day-of-week, weather, and festival multipliers. Section V gives their values.

### C. Dynamic Edge Cost

Let $\bar{c}_e = (C_u + C_v)/2$ be the mean crowd density at the two ends of edge *e* = (*u*, *v*). The routing cost is:

$$\text{Cost}(e) = D_e \left[1 + \alpha\,\bar{c}_e\,S_e + \beta\,(K_e - 1)\right] \tag{4}$$

where *K*ₑ = 1.55 if the edge is a chokepoint (χₑ = 1) and $\bar{c}_e$ > 0.55, and *K*ₑ = 1.00 otherwise. We set α = 1.8 and β = 1.2 by hand. The baseline is ordinary Dijkstra with Cost(*e*) = *D*ₑ, which ignores crowding altogether.

### D. Travel-Time Estimate

Once a path is chosen, its expected travel time is the sum over its edges of a BPR-style estimate *T*ₑ:

$$T_e = T_e^{ff}\left[1 + \bar{c}_e^2\,S_e \cdot 2.2 \cdot K_e\right] \tag{5}$$

For a saturated chokepoint with $\bar{c}_e$ = 0.85, *S*ₑ = 1.2, and *K*ₑ = 1.55, the bracket is 1 + 0.7225 × 1.2 × 2.2 × 1.55 ≈ 3.96, so an edge that takes 10 min in free flow is modelled as taking about 40 min. This shows why avoiding such edges pays off. Note that Eq. (5) is a quadratic form with hand-set constants, not the classical quartic BPR curve with its published coefficients.

### E. A∗ Search

The A∗ variant uses *f*(*n*) = *g*(*n*) + *h*(*n*), where *g*(*n*) is the cumulative crowd-aware cost from the source and:

$$h(n) = 0.4 \cdot D(n, t) \tag{6}$$

with *t* the target. This heuristic is admissible and consistent: every edge cost in Eq. (4) is at least *D*ₑ, *D*ₑ is itself a Haversine distance, and great-circle distance obeys the triangle inequality. The factor 0.4 is deliberately conservative; it keeps A∗ exact but expands more nodes than a factor of 1.0 would. A tighter factor would reduce node expansions but risk inadmissibility if edge costs change between the planning step and the scoring step; the conservative value therefore provides a correctness margin.

### F. Complexity

With a linear-scan priority queue over |𝒱| = 24 nodes, Dijkstra takes *O*(|𝒱|² + |ℰ|) = *O*(614) basic operations. A binary heap would give *O*((|𝒱| + |ℰ|) log |𝒱|) ≈ *O*(284). At this size either is trivial, which is why every query can be answered live.

---

## V. CROWD PREDICTION MODEL

### A. Features

The model draws on six groups of features built from knowledge of how Pune commutes.

**Hourly curve (*B*ₕ).** It has a morning peak (07:00–10:00), a midday trough (12:00–14:00), an evening peak (17:00–20:00), and a low night tail (21:00–05:00).

**Hub type (γᵤ, *M*_d).** Table II gives each type's peak multiplier and its weekend multiplier, which captures how IT hubs empty out on weekends while market areas fill up.

**Table II — Hub Types and Day-of-Week Effects**

| Hub type | Examples | Peak mult. | Weekend *M*_d |
|---|---|---|---|
| IT corridor | Hinjewadi, Kharadi, Magarpatta | 2.8 | 0.38 |
| Commercial | Deccan, Camp, FC Road | 1.8 | 1.45 |
| Interchange | Swargate, Shivajinagar, Pune Stn. | 2.3 | 1.15 |
| Residential | Kondhwa, Wagholi, Dhankawadi | 1.6 | 0.90 |

**Weather (*M*_w).** Table III lists the multipliers. Five hubs are flagged as flood-prone: Swargate, Katraj Depot, Bibwewadi, Kondhwa, and Warje.

**Table III — Weather Multipliers**

| Condition | Flood-prone | Other hubs |
|---|---|---|
| Clear | 1.00 | 1.00 |
| Light rain | 1.15 | 1.10 |
| Heavy monsoon | 1.55 | 1.30 |
| Waterlogging | 1.70 | 1.40 |
| Extreme heat (12:00–16:00) | 0.72 | 0.72 |

**Festivals (*M*_F).** Each festival boosts a set of hotspot hubs and, for the biggest events, sets a floor on *C*ᵤ (Table IV).

**Table IV — Festival Multipliers**

| Festival | Hotspot hubs | *M*_F | Floor *C*ᵤ |
|---|---|---|---|
| Ganeshotsav | Swargate, Kasba Peth, Mandai | 1.85 | 0.88 |
| Palkhi | Swargate, Pune Stn., Dehu Road | 1.75 | 0.85 |
| Diwali | Deccan, Camp, Viman Nagar | 1.40 | — |
| New Year's Eve | Deccan, Camp, Koregaon Park | 1.65 | 0.82 |
| Eid | Camp, Pune Station | 1.35 | — |

**Season.** Monsoon months (June–September) activate the flood-prone weighting, summer afternoons are damped by the same 0.72 heat factor, and winter lowers early-morning and late-night demand.

### B. Fitting

No labelled crowd data was available, so the weights in `crowdModelWeights.json` were fitted to synthetic samples generated from the domain assumptions above (script: `scripts/train_crowd_model.py`). On held-out synthetic samples the mean absolute error is 4.2% of crowd intensity. That figure tells us the model reproduces its own generating assumptions; it is not an accuracy measure against real crowds. Inference takes under 1 ms per hub in the browser.

### C. Extra-Bus Suggestions

The predicted crowd percentage *P*ᵤ = 100*C*ᵤ at a hub is mapped to a suggested number of extra buses. At or above 88% (critical), the suggestion is:

$$R_{\text{extra}} = \text{clip}\!\left(\left\lfloor\frac{P_u - 75}{4}\right\rfloor, 3, 6\right) \tag{7}$$

and between 72% and 88% (high) it is:

$$R_{\text{extra}} = \text{clip}\!\left(\left\lfloor\frac{P_u - 65}{6}\right\rfloor, 1, 3\right) \tag{8}$$

Below 72% no extra buses are suggested. These thresholds are operating heuristics for the demonstration, not values agreed with PMPML.

---

## VI. METRO INTEGRATION

Both Phase 1 Metro corridors [11] are drawn on the map as georeferenced polylines, and interchange hubs are linked to lists of PMPML feeder routes (Table V). For example, the interface lists routes 100 and 115 toward Hinjewadi, 149 toward Hadapsar, and 103 toward Kondhwa from the relevant interchanges.

**Table V — Metro Lines and Bus Interchanges**

| Line | Corridor | Bus interchanges |
|---|---|---|
| Purple (Line 1) | PCMC – Civil Court – Swargate | PCMC, Shivajinagar, Civil Court, Swargate |
| Aqua (Line 2) | Vanaz – Nal Stop – Civil Court – Ramwadi | Vanaz, Nal Stop, Civil Court, Ramwadi |

---

## VII. IMPLEMENTATION FEATURES

**Stop search.** A combobox matches colloquial names to hubs, so "FC Road" or "Fergusson" resolves to Deccan Gymkhana and "Phoenix Mall" to Viman Nagar. Marathi (Devanagari) names such as स्वारगेट are matched by Unicode substring. An in-app algorithm guide modal additionally exposes the cost formulation, time-complexity derivation, and worked viva questions for academic audiences.

**Visualization.** The map can be tilted with CSS perspective transforms, and a 24-hour slider drives a day/night filter on the base tiles. Commuter flow is shown by CSS-animated dots along the route geometry, which avoids a separate canvas layer.

**Fleet simulation.** A telemetry panel animates bus markers along stored route geometry, displaying PMPML route numbers (100, 115, 2A, 149, 103), estimated speed, and passenger occupancy as a live card grid. This provides visual confirmation that the computed routes correspond to plausible bus movements on the network.

**Hourly congestion chart.** A bar chart in the trip-planner panel colours each of the 24 hours green, amber, or red according to the base demand curve *B*ₕ, giving the user an at-a-glance view of the best time to travel before they commit to a departure time.

**Offline operation.** A cache-first service worker (`sw.js`) stores the application bundle, the transit graph and model-weight JSON files, and map tiles fetched in earlier sessions, so routing keeps working without a connection.

**Route export.** The app builds a printable travel summary with segment directions, per-segment crowd index, total distance, optimized travel time, and time saved against the baseline route. It uses the browser's print function, so no server-side PDF generation is needed.

---

## VIII. EVALUATION

### A. Setup

The route benchmark uses a Monday at 08:30, heavy monsoon, with Swargate and University Chowk marked as surge nodes. For each origin–destination pair we compute the distance-only Dijkstra path and the crowd-aware path, and score both with Eq. (5). The travel times below are therefore model estimates, not measured bus journeys.

### B. Route Optimization

Table VI compares the two methods on five corridors. Crowd-aware routing reduces modelled time on all five, by 30.2% on average. The largest gain is Swargate to Hinjewadi Ph 3 (33.8%), where the crowd-aware path is longer (30.2 km against 26.4 km) but avoids the saturated Swargate chokepoint. Fig. 2 plots the per-corridor comparison; dotted horizontal lines mark the per-method averages.

**Table VI — Modelled Travel Time, Monday 08:30, Heavy Monsoon**

| Route | Std. (min) | Aware (min) | Saved (min) | Reduction |
|---|---|---|---|---|
| Swargate → Hinjewadi Ph 3 | 68.0 | 45.0 | 23.0 | **33.8%** |
| Hadapsar → Pune Univ. | 52.0 | 36.0 | 16.0 | **30.7%** |
| Kothrud Depot → Phoenix Mall | 48.0 | 34.0 | 14.0 | **29.1%** |
| Nigdi → Swargate | 60.0 | 42.0 | 18.0 | **30.0%** |
| Lohegaon Airport → Deccan | 55.0 | 40.0 | 15.0 | **27.3%** |
| **Average** | **56.6** | **39.4** | **17.2** | **30.2%** |

*Fig. 2. Modelled travel time under distance-only and crowd-aware routing (Monday 08:30, heavy monsoon, Swargate and University Chowk marked as surge nodes). Percentage labels above each crowd-aware bar show the reduction relative to the distance-only baseline; dotted horizontal lines mark the per-method averages.*

### C. Routing Speed and Coverage

We ran the routing engine on every ordered pair of the 24 hubs using the project's test script (`scripts/test_route_matrix.py`). Table VII summarizes the run. Zero failures is expected because the graph is strongly connected; the test mainly confirms that the edge data contains no gaps.

**Table VII — Routing Benchmark, All Hub Pairs**

| Metric | Result |
|---|---|
| Pairs tested (24 × 23) | 552 |
| Successful routes | 552 (100%) |
| Disconnected pairs | 0 |
| Average latency | **0.15 ms** |
| Maximum latency | **0.55 ms** |
| Total batch time | **0.07 s** |

### D. Plausibility of Crowd Predictions

Without ground-truth crowd data we checked that predictions behave sensibly in five scenarios (Table VIII). Every case lands where the underlying assumptions say it should, which confirms the factors combine as intended but is not an independent validation.

**Table VIII — Crowd Prediction Spot Checks**

| Scenario | *C*ᵤ | Expected |
|---|---|---|
| Hinjewadi, Sat 14:00, clear | 0.08 | Low (IT hub, weekend) |
| Swargate, Ganeshotsav, 20:00 | 0.94 | Critical (festival) |
| Deccan, Sun 15:00, clear | 0.72 | Heavy (leisure hub) |
| Swargate, Mon 09:00, heavy monsoon | 0.91 | Critical (flood-prone, peak) |
| Hinjewadi, Mon 09:00, clear | 0.78 | Heavy (IT rush) |

### E. Emissions

Routing around stop-and-go corridors should lower fuel use, but a longer detour adds distance. We estimate trip emissions as:

$$E = D_{\text{tot}} \cdot \varepsilon \cdot \left(1 + 0.4\,\bar{c}_r\right) \tag{9}$$

where *D*_tot is path length, ε is an emission factor per kilometre, and $\bar{c}_r$ is the mean crowd index along the route. The prototype's emission factor has not yet been checked against measured PMPML fuel data, so we do not report absolute CO₂ figures here.

---

## IX. LIMITATIONS

The results should be read with the following caveats in mind.

1. **Synthetic training data.** The crowd model encodes our assumptions about Pune; it has not been fitted to or tested against observed ridership.
2. **Self-consistent evaluation.** The same crowd and delay parameters both choose the route and score it, so the time savings show that the optimizer does what the model says, not that real buses would save 30%.
3. **Hand-set coefficients.** α, β, the 2.2 delay constant, and the chokepoint threshold were not fitted, and we have not run a sensitivity analysis.
4. **Coarse network.** Twenty-four hubs stand in for more than 6,700 stops. The model has no timetables, headways, transfer waits, or vehicle capacities, and it uses passenger crowd density as a stand-in for road congestion.
5. **No live data.** Conditions are chosen by the user, not read from vehicle-tracking or ticketing feeds.

---

## X. CONCLUSION AND FUTURE WORK

PMPML Pulse shows that crowd-aware bus routing, crowd prediction, metro guidance, and fleet suggestions can run entirely in a browser with no server or paid APIs. In simulation, crowd-aware routing cut modelled travel time by 30.2% on average on five corridors, and every one of the 552 hub pairs was routed in well under a millisecond. These are feasibility results; real-world gains remain to be shown.

The next steps follow from the limitations above:

1. Ingest PMPML's GTFS-Realtime vehicle-location feeds for live positions and rerouting.
2. Calibrate and test the crowd model against Maha-Metro smart-card counts and PMPML ticketing data.
3. Replace the regression with a learned sequence model once such data exists, and conduct a sensitivity analysis on the hand-set coefficients α, β, and the 2.2 delay constant.
4. Model signal priority on high-occupancy corridors.
5. Release a passenger-facing mobile PWA with push alerts for diversions and crowding.

---

## REFERENCES

[1] PMPML, *Annual Report 2023–24*. Pune, India: Pune Mahanagar Parivahan Mahamandal Ltd., 2024.

[2] E. W. Dijkstra, "A note on two problems in connexion with graphs," *Numerische Mathematik*, vol. 1, no. 1, pp. 269–271, 1959.

[3] P. E. Hart, N. J. Nilsson, and B. Raphael, "A formal basis for the heuristic determination of minimum cost paths," *IEEE Trans. Syst. Sci. Cybern.*, vol. 4, no. 2, pp. 100–107, Jul. 1968.

[4] H. Bast et al., "Route planning in transportation networks," in *Algorithm Engineering*, L. Kliemann and P. Sanders, Eds. Cham, Switzerland: Springer, 2016, pp. 19–80.

[5] Bureau of Public Roads, *Traffic Assignment Manual*. Washington, DC, USA: U.S. Dept. of Commerce, 1964.

[6] S. Hochreiter and J. Schmidhuber, "Long short-term memory," *Neural Comput.*, vol. 9, no. 8, pp. 1735–1780, 1997.

[7] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining*, San Francisco, CA, USA, 2016, pp. 785–794.

[8] Y. Sun, B. Leng, and W. Guan, "A novel wavelet-SVM short-time passenger flow prediction in Beijing subway system," *Neurocomputing*, vol. 166, pp. 109–121, 2015.

[9] S. Velmurugan, E. Madhu, V. Ravinder, and K. Sitaramanjaneyulu, "Critical evaluation of roadway capacity of national highways under heterogeneous and mixed traffic conditions through traditional and microscopic simulation models," *J. Indian Roads Congr.*, vol. 71, no. 2, pp. 235–264, 2010.

[10] Ministry of Housing and Urban Affairs, Govt. of India, "Smart Cities Mission: Annual report 2022–23," New Delhi, India, 2023.

[11] Maharashtra Metro Rail Corporation Ltd., "Pune Metro Rail Phase 1 operations report," Pune, India, 2024.

[12] OpenStreetMap Contributors, "OpenStreetMap." [Online]. Available: https://www.openstreetmap.org (accessed Nov. 2026).

[13] CARTO, "CARTO basemaps: Positron and Dark Matter." [Online]. Available: https://carto.com/basemaps (accessed Nov. 2026).
