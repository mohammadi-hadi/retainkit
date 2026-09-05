# Context policies on LoCoMo

10 conversations, 1527 probes, 23056 tokens of conversation on average (`char4` estimator).

- **dataset**: LoCoMo (Maharana et al., ACL 2024), 10 conversations
- **questions**: 1527 scored, 13 dropped for unresolvable evidence, adversarial category excluded
- **sessions per conversation**: 19–32

## Recall against budget

| Budget | Policy | Sees question | Recall | 95% CI | Whole turns | Partial | Tokens |
| ---: | --- | :---: | ---: | --- | ---: | ---: | ---: |
| 512 | `oracle` | yes | 99.5% | 99.2%–99.8% | 99.5% | 99.9% | 83 |
| 512 | `fact_memory` | yes | 47.8% | 45.3%–50.2% | 1.9% | 52.5% | 511 |
| 512 | `retrieval` | yes | 45.8% | 43.4%–48.3% | 45.8% | 50.0% | 510 |
| 512 | `session_summary` | no | 10.7% | 9.2%–12.4% | 0.3% | 14.1% | 504 |
| 512 | `head_tail` | no | 1.5% | 0.9%–2.1% | 1.5% | 2.1% | 510 |
| 512 | `recency` | no | 1.3% | 0.8%–1.9% | 1.3% | 1.4% | 510 |
| 1024 | `oracle` | yes | 99.9% | 99.8%–100.0% | 99.9% | 100.0% | 84 |
| 1024 | `fact_memory` | yes | 54.4% | 51.9%–56.8% | 2.6% | 59.6% | 1023 |
| 1024 | `retrieval` | yes | 52.8% | 50.3%–55.3% | 52.8% | 58.1% | 1022 |
| 1024 | `session_summary` | no | 12.2% | 10.6%–13.9% | 0.9% | 15.8% | 1018 |
| 1024 | `head_tail` | no | 3.5% | 2.6%–4.4% | 3.5% | 4.5% | 1021 |
| 1024 | `recency` | no | 3.3% | 2.4%–4.1% | 3.3% | 3.8% | 1022 |
| 2048 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 84 |
| 2048 | `fact_memory` | yes | 62.7% | 60.2%–65.1% | 3.9% | 69.4% | 2047 |
| 2048 | `retrieval` | yes | 59.5% | 56.8%–62.0% | 59.5% | 65.3% | 2046 |
| 2048 | `session_summary` | no | 13.4% | 11.7%–15.2% | 2.0% | 17.3% | 1836 |
| 2048 | `head_tail` | no | 8.2% | 6.9%–9.6% | 8.2% | 10.3% | 2045 |
| 2048 | `recency` | no | 7.7% | 6.4%–9.0% | 7.7% | 8.9% | 2047 |
| 4096 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 84 |
| 4096 | `fact_memory` | yes | 72.0% | 69.7%–74.1% | 4.5% | 79.0% | 4095 |
| 4096 | `retrieval` | yes | 65.0% | 62.5%–67.3% | 65.0% | 71.4% | 4094 |
| 4096 | `head_tail` | no | 17.0% | 15.2%–18.9% | 17.0% | 20.5% | 4095 |
| 4096 | `recency` | no | 15.5% | 13.6%–17.2% | 15.5% | 17.7% | 4093 |
| 4096 | `session_summary` | no | 13.8% | 12.0%–15.5% | 2.4% | 17.6% | 1922 |
| 8192 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 84 |
| 8192 | `fact_memory` | yes | 81.5% | 79.4%–83.4% | 5.0% | 87.6% | 8191 |
| 8192 | `retrieval` | yes | 71.4% | 69.0%–73.7% | 71.4% | 78.7% | 8190 |
| 8192 | `head_tail` | no | 33.1% | 30.8%–35.3% | 33.1% | 38.9% | 8189 |
| 8192 | `recency` | no | 30.3% | 28.2%–32.5% | 30.3% | 34.8% | 8190 |
| 8192 | `session_summary` | no | 13.8% | 12.0%–15.5% | 2.4% | 17.6% | 1922 |
| 16384 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 84 |
| 16384 | `fact_memory` | yes | 91.6% | 90.0%–92.9% | 5.8% | 94.9% | 16383 |
| 16384 | `retrieval` | yes | 87.0% | 85.2%–88.6% | 87.0% | 91.6% | 16249 |
| 16384 | `head_tail` | no | 65.5% | 63.1%–67.8% | 65.5% | 71.6% | 16246 |
| 16384 | `recency` | no | 64.4% | 62.1%–66.7% | 64.4% | 69.6% | 16248 |
| 16384 | `session_summary` | no | 13.8% | 12.0%–15.5% | 2.4% | 17.6% | 1922 |
| 32768 | `head_tail` | no | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 23528 |
| 32768 | `oracle` | yes | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 84 |
| 32768 | `recency` | no | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 23528 |
| 32768 | `retrieval` | yes | 100.0% | 100.0%–100.0% | 100.0% | 100.0% | 23528 |
| 32768 | `fact_memory` | yes | 99.7% | 99.5%–99.9% | 6.2% | 99.8% | 28317 |
| 32768 | `session_summary` | no | 13.8% | 12.0%–15.5% | 2.4% | 17.6% | 1922 |

## Recall by how old the evidence is, at 2048 tokens

| Policy | same session | 1-2 back | 3-5 back | 6-10 back | 11+ back |
| --- | ---: | ---: | ---: | ---: | ---: |
| `oracle` | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `fact_memory` | 86.1% | 76.9% | 74.3% | 74.3% | 55.7% |
| `retrieval` | 61.1% | 73.1% | 72.1% | 72.2% | 52.9% |
| `session_summary` | 86.1% | 15.4% | 15.0% | 14.3% | 10.1% |
| `head_tail` | 100.0% | 30.8% | 0.0% | 0.0% | 4.9% |
| `recency` | 100.0% | 62.3% | 0.0% | 0.0% | 0.0% |
| _probes_ | 36 | 130 | 140 | 230 | 991 |

## Cheapest budget that reaches a recall target

| Policy | 50% recall | 80% recall | 90% recall |
| --- | ---: | ---: | ---: |
| `fact_memory` | 1024 | 8192 | 16384 |
| `head_tail` | 16384 | 32768 | 32768 |
| `oracle` | 512 | 512 | 512 |
| `recency` | 16384 | 32768 | 32768 |
| `retrieval` | 1024 | 16384 | 32768 |
| `session_summary` | not reached | not reached | not reached |

## Recall by question type, at 2048 tokens

| Policy | multi-hop | open-domain | single-hop | temporal |
| --- | ---: | ---: | ---: | ---: |
| `oracle` | 100.0% | 100.0% | 100.0% | 100.0% |
| `fact_memory` | 16.2% | 33.7% | 76.8% | 74.4% |
| `retrieval` | 14.0% | 27.0% | 73.6% | 70.9% |
| `session_summary` | 2.9% | 11.2% | 9.9% | 32.5% |
| `head_tail` | 1.4% | 7.9% | 9.9% | 9.7% |
| `recency` | 0.7% | 6.7% | 10.2% | 7.2% |
