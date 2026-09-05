# retainkit fixture

8 conversations, 120 probes, 6613 tokens of conversation on average (`char4` estimator).

- **source**: synthetic fixture, seed 7

## Recall against budget

| Budget | Policy | Sees question | Evidence recall | 95% CI | Partial | Tokens |
| ---: | --- | :---: | ---: | --- | ---: | ---: |
| 256 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 22 |
| 256 | `retrieval` | yes | 95.8% | 91.7%–99.2% | 95.8% | 252 |
| 256 | `fact_memory` | yes | 82.5% | 75.8%–89.2% | 82.5% | 251 |
| 256 | `head_tail` | no | 0.0% | 0.0%–0.0% | 0.0% | 251 |
| 256 | `recency` | no | 0.0% | 0.0%–0.0% | 0.0% | 252 |
| 256 | `session_summary` | no | 0.0% | 0.0%–0.0% | 0.0% | 246 |
| 512 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 22 |
| 512 | `retrieval` | yes | 100.0% | 100.0%–100.0% | 100.0% | 508 |
| 512 | `fact_memory` | yes | 99.2% | 97.5%–100.0% | 99.2% | 508 |
| 512 | `head_tail` | no | 6.7% | 2.5%–11.7% | 6.7% | 510 |
| 512 | `recency` | no | 0.0% | 0.0%–0.0% | 0.0% | 509 |
| 512 | `session_summary` | no | 0.0% | 0.0%–0.0% | 0.0% | 507 |
| 1024 | `fact_memory` | yes | 100.0% | 100.0%–100.0% | 100.0% | 1019 |
| 1024 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 22 |
| 1024 | `retrieval` | yes | 100.0% | 100.0%–100.0% | 100.0% | 1019 |
| 1024 | `recency` | no | 13.3% | 7.5%–20.0% | 13.3% | 1021 |
| 1024 | `head_tail` | no | 6.7% | 2.5%–11.7% | 6.7% | 1018 |
| 1024 | `session_summary` | no | 6.7% | 2.5%–11.7% | 6.7% | 1018 |
| 2048 | `fact_memory` | yes | 100.0% | 100.0%–100.0% | 100.0% | 2044 |
| 2048 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 22 |
| 2048 | `retrieval` | yes | 100.0% | 100.0%–100.0% | 100.0% | 2043 |
| 2048 | `head_tail` | no | 33.3% | 24.2%–42.5% | 33.3% | 2042 |
| 2048 | `recency` | no | 26.7% | 19.2%–35.0% | 26.7% | 2043 |
| 2048 | `session_summary` | no | 13.3% | 7.5%–19.2% | 13.3% | 1185 |
| 4096 | `fact_memory` | yes | 100.0% | 100.0%–100.0% | 100.0% | 4091 |
| 4096 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 22 |
| 4096 | `retrieval` | yes | 100.0% | 100.0%–100.0% | 100.0% | 4091 |
| 4096 | `recency` | no | 60.0% | 50.8%–68.3% | 60.0% | 4091 |
| 4096 | `head_tail` | no | 58.3% | 49.2%–66.7% | 58.3% | 4095 |
| 4096 | `session_summary` | no | 13.3% | 7.5%–19.2% | 13.3% | 1185 |
| 8192 | `fact_memory` | yes | 100.0% | 100.0%–100.0% | 100.0% | 6613 |
| 8192 | `head_tail` | no | 100.0% | 100.0%–100.0% | 100.0% | 6613 |
| 8192 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 22 |
| 8192 | `recency` | no | 100.0% | 100.0%–100.0% | 100.0% | 6613 |
| 8192 | `retrieval` | yes | 100.0% | 100.0%–100.0% | 100.0% | 6613 |
| 8192 | `session_summary` | no | 13.3% | 7.5%–19.2% | 13.3% | 1185 |

## Recall by how old the evidence is, at 1024 tokens

| Policy | 1-2 back | 3-5 back | 6-10 back | 11+ back |
| --- | ---: | ---: | ---: | ---: |
| `fact_memory` | 100.0% | 100.0% | 100.0% | 100.0% |
| `oracle` | 100.0% | 100.0% | 100.0% | 100.0% |
| `retrieval` | 100.0% | 100.0% | 100.0% | 100.0% |
| `recency` | 100.0% | 0.0% | 0.0% | 0.0% |
| `head_tail` | 0.0% | 0.0% | 0.0% | 20.0% |
| `session_summary` | 0.0% | 0.0% | 0.0% | 20.0% |
| _probes_ | 16 | 24 | 40 | 40 |

## Cheapest budget that reaches a recall target

| Policy | 50% recall | 80% recall | 90% recall |
| --- | ---: | ---: | ---: |
| `fact_memory` | 256 | 256 | 512 |
| `head_tail` | 4096 | 8192 | 8192 |
| `oracle` | 256 | 256 | 256 |
| `recency` | 4096 | 8192 | 8192 |
| `retrieval` | 256 | 256 | 256 |
| `session_summary` | not reached | not reached | not reached |

