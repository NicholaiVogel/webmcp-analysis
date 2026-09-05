# webmcp-analysis

Independent analysis of the ~2,500 submissions to the **WebMCP Challenge**.

The goal is to compare projects as fairly as possible using the challenge's actual judging criteria, while looking beyond submission descriptions at things like demos, live products, repositories, screenshots, and WebMCP behavior.

## Judging

Projects are scored on the four official criteria:

* **WebMCP Leverage**
* **Execution**
* **Potential Impact**
* **Creativity & Ambition**

All four are weighted equally.

The analysis is category-neutral: games, creative tools, business software, experiments, developer tools, and weird little hackathon projects are judged based on how well they accomplish what they are trying to do.

## Method

Every project receives multiple blind reviews using sanitized evidence packets.

Prior rankings and scores from the source dataset are quarantined so they cannot influence reviewers.

Stronger or uncertain projects receive progressively deeper review, including:

* demo video inspection
* live product testing
* repository inspection
* WebMCP verification where possible
* comparison against existing concepts

The earlier [HanClinto WebMCP analysis](https://gist.github.com/HanClinto/496ae203b5422a3c6a94cef2fc7b6244) is used later as a comparison point, not as ground truth.

See [`PROTOCOL.md`](./PROTOCOL.md) for the full methodology.

## The compute

This analysis was produced by 1,035 AI agents: three orchestrator sessions directing 1,032 independent reviewer agents, each spawned fresh with zero shared context, across 10,193 API calls.

* 59,287,332 non-cached tokens consumed; 526,261,568 additional cache-read tokens (585,548,900 total token movement)
* 8,734 individual judgments in the final ranking: 5,233 blind Stage-1 reviews (two full passes over all 2,500 projects), 716 live product observations, 1,432 blind Stage-2 rescores (716 projects x 2 independent scorers), and 1,353 Stage-1 re-scores after a video-evidence defect was found and fixed
* 80.2 hours of agent review time compressed into 3.9 hours of delegation windows, about 20 reviews in flight on average
* 2,500 of 2,500 projects scored and ranked, every judgment auditable

Every number is exact and comes from the run ledger: see [`VOLUME.md`](./VOLUME.md).

## Disclaimer

This is an independent experiment, not an official ranking or prediction of the WebMCP Challenge results.

Mostly I'm just trying to look at all of them without bullshitting myself.


## Top 50 Results

| Rank | Project | Leverage | Execution | Impact | Creativity | Total | Evidence |
|-----:|---------|-----:|-----:|-----:|-----:|-----:|----------|
| 1 | [Physical AI WebMCP Command Center](https://devpost.com/software/physical-ai-webmcp-command-center) | 10 | 10 | 9 | 9 | 38 | unverified |
| 2 | [Handrail](https://devpost.com/software/handrail-8v6gls) | 10 | 9 | 10 | 9 | 38 | unverified |
| 3 | [Alza](https://devpost.com/software/alza) | 10.0 | 9.0 | 9.0 | 10.0 | 38 | runtime ✓ |
| 4 | [Incident Command](https://devpost.com/software/incident-command) | 10 | 9 | 9 | 10 | 38 | unverified |
| 5 | [PaperVeil](https://devpost.com/software/paperveil) | 10 | 9 | 9 | 10 | 38 | unverified |
| 6 | [Grenz: a policy layer for WebMCP](https://devpost.com/software/grenz-a-policy-layer-for-webmcp) | 10.0 | 8.5 | 9.5 | 10.0 | 38 | claims only |
| 7 | [Mace](https://devpost.com/software/mace) | 10.0 | 9.0 | 8.5 | 10.0 | 37.5 | video |
| 8 | [Pillbox](https://devpost.com/software/pillbox-ktnp5v) | 10.0 | 8.5 | 10.0 | 9.0 | 37.5 | runtime ✓ |
| 9 | [Substrate](https://devpost.com/software/substrate-ys7ta2) | 10.0 | 7.5 | 10.0 | 10.0 | 37.5 | runtime ✓ |
| 10 | [AGENT CONTROL PLANE](https://devpost.com/software/agent-control-plane-cwqo5j) | 10 | 9 | 9 | 9 | 37 | unverified |
| 11 | [CareBridge: humans in control of multi-page agent workflows](https://devpost.com/software/careloop-webmcp-for-a-toddler-s-first-allergy) | 10 | 9 | 9 | 9 | 37 | unverified |
| 12 | [FlightSweeper](https://devpost.com/software/flightsweeper) | 10 | 9 | 9 | 9 | 37 | unverified |
| 13 | [Floortris](https://devpost.com/software/floortris) | 10 | 9 | 9 | 9 | 37 | unverified |
| 14 | [Ingram Sheets](https://devpost.com/software/ingram-sheets) | 10 | 9 | 9 | 9 | 37 | unverified |
| 15 | [Ops Co-pilot](https://devpost.com/software/ops-co-pilot) | 10 | 9 | 9 | 9 | 37 | unverified |
| 16 | [Overhead](https://devpost.com/software/overhead) | 10 | 9 | 9 | 9 | 37 | unverified |
| 17 | [Paris ICC](https://devpost.com/software/proofsheet) | 10 | 9 | 9 | 9 | 37 | unverified |
| 18 | [REWIND](https://devpost.com/software/rewind-siqgzb) | 10 | 9 | 9 | 9 | 37 | unverified |
| 19 | [RoomCraft](https://devpost.com/software/roomcraft-3wlqf5) | 10 | 9 | 9 | 9 | 37 | unverified |
| 20 | [ROUGH//CUT](https://devpost.com/software/rough-cut) | 10 | 9 | 9 | 9 | 37 | unverified |
| 21 | [Sightline](https://devpost.com/software/sightline-mndf14) | 10 | 9 | 9 | 9 | 37 | unverified |
| 22 | [Sigmora Live Relay](https://devpost.com/software/sigmora-live-relay) | 10 | 9 | 9 | 9 | 37 | unverified |
| 23 | [Verified Mission Control](https://devpost.com/software/verified-mission-control) | 10 | 9 | 9 | 9 | 37 | unverified |
| 24 | [LAST DOOR](https://devpost.com/software/last-door) | 10 | 9 | 8 | 10 | 37 | unverified |
| 25 | [Onionskin](https://devpost.com/software/onionskin) | 10 | 9 | 8 | 10 | 37 | unverified |
| 26 | [PARALLAX SPATIAL MCP](https://devpost.com/software/parallax-spatial-mcp) | 10 | 9 | 8 | 10 | 37 | unverified |
| 27 | [Paper Trail](https://devpost.com/software/paper-trail-9b2q4x) | 10 | 8 | 10 | 9 | 37 | unverified |
| 28 | [Gridfall](https://devpost.com/software/gridfall) | 10 | 8 | 9 | 10 | 37 | unverified |
| 29 | [Roadway Design Compiler](https://devpost.com/software/safety-critical-roadway-design-engine) | 9.5 | 9.0 | 9.5 | 9.0 | 37 | runtime ✓ |
| 30 | [TRACE](https://devpost.com/software/trace-ta9wup) | 9.5 | 9.0 | 8.5 | 10.0 | 37 | runtime ✓ |
| 31 | [KnownGate](https://devpost.com/software/knowngate) | 9 | 9 | 10 | 9 | 37 | unverified |
| 32 | [OVERTURN](https://devpost.com/software/overturn-hbk9dq) | 9 | 9 | 10 | 9 | 37 | unverified |
| 33 | [Deputy](https://devpost.com/software/deputy) | 10.0 | 6.5 | 10.0 | 10.0 | 36.5 | claims only |
| 34 | [OpenHardware](https://devpost.com/software/openhardware) | 9.5 | 9.0 | 9.0 | 9.0 | 36.5 | runtime ✓ |
| 35 | [Traces](https://devpost.com/software/traces-3snwtz) | 9.5 | 9.0 | 8.5 | 9.5 | 36.5 | video |
| 36 | [Spatialize](https://devpost.com/software/spatialize) | 9.5 | 8.0 | 9.5 | 9.5 | 36.5 | runtime ✓ |
| 37 | [Peira](https://devpost.com/software/peira) | 9.0 | 9.0 | 9.5 | 9.0 | 36.5 | runtime ✓ |
| 38 | [E-ternal × WebMCP](https://devpost.com/software/e-ternal-x-webmcp) | 10 | 9 | 9 | 8 | 36 | unverified |
| 39 | [Edgewright](https://devpost.com/software/edgewright) | 10 | 9 | 9 | 8 | 36 | unverified |
| 40 | [ExceptionOSMCP](https://devpost.com/software/exceptionosmcp) | 10 | 9 | 9 | 8 | 36 | unverified |
| 41 | [Recall Response Workbench — Recall the Right Items](https://devpost.com/software/recall-response-workbench-recall-the-right-items) | 10 | 9 | 9 | 8 | 36 | unverified |
| 42 | [Bridge Studio](https://devpost.com/software/bridge-studio) | 10 | 9 | 8 | 9 | 36 | unverified |
| 43 | [Crom’s Research Desk: WebMCP-Powered Agentic Publishing](https://devpost.com/software/crom-s-research-desk-webmcp-powered-agentic-publishing) | 10 | 9 | 8 | 9 | 36 | unverified |
| 44 | [DungeonQ](https://devpost.com/software/dungeonq) | 10 | 9 | 8 | 9 | 36 | unverified |
| 45 | [EvidenceBound WebMCP Authority Compiler](https://devpost.com/software/evidencebound-webmcp-authority-compiler) | 10 | 9 | 8 | 9 | 36 | unverified |
| 46 | [FableCut](https://devpost.com/software/fablecut) | 10 | 9 | 8 | 9 | 36 | unverified |
| 47 | [FORGE — Human-Agent World Laboratory](https://devpost.com/software/project-forge-3zyvef) | 10 | 9 | 8 | 9 | 36 | unverified |
| 48 | [Semantic City — Shared-World WebMCP Simulator](https://devpost.com/software/semantic-city-a-webmcp-city-simulator) | 10 | 9 | 8 | 9 | 36 | unverified |
| 49 | [AgentReady.js: Instant WebMCP for Every Website](https://devpost.com/software/agentready-js-instant-webmcp-for-every-website) | 10 | 8 | 9 | 9 | 36 | unverified |
| 50 | [CanvasOps](https://devpost.com/software/canvasops) | 10 | 8 | 9 | 9 | 36 | unverified |

Scores are the mean of two independent blind reviewers (S2 rows also had their live product exercised by an automated tester). Full ranking: [`analysis/FINAL_RANKING.csv`](./analysis/FINAL_RANKING.csv) · all 2,500 projects.
