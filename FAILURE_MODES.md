# Failure modes and designed behavior

| Failure | Detection | System behavior | Evidence |
|---|---|---|---|
| Duplicate Pub/Sub delivery | Existing terminal `event_id` | Return prior result; no version/outbox change | `op_duplicate_delivery`, `film_duplicate_delivery` |
| Crash before commit | Transaction never writes | Retry from persisted `received` state | Three crash-injection tests |
| Lost ACK after commit | Terminal event already exists | Replay is a no-op business effect | `test_duplicate_delivery_has_exactly_once_effects` |
| Two simultaneous incidents | Firestore transaction retry / local lock | Each sees a coherent version; obsolete incident becomes no-impact | Concurrent fixtures in both domains |
| Stale manual plan | `base_version != version` | Reject before mutation | 100% stale rejection in evaluation |
| No qualified cover | Unresolved activities | `human_required`; no commit/outbox | Both-domain no-cover fixtures |
| Participant unavailable | Availability gate | Human escalation | Evaluation fixtures |
| Person conflict | Conflict proof | Move to nearest valid slot or escalate | Engine and evaluation tests |
| Resource conflict | Conflict proof | Move safely or escalate if impossible | Both-domain fixtures |
| Unknown person/resource | Strict lookup / verification | Reject or human escalation | Evaluation fixtures |
| Malformed incident | Pydantic validation | HTTP 422; no ledger entry | Schema fixtures |
| Prompt injection in reason | Reason treated as data | Policy unchanged; zero messages sent | Adversarial fixtures |
| Gemini fails to invoke workflow | Non-terminal ledger after ADK run | Worker returns error; Pub/Sub retries | `/api/pubsub/push` terminal-state check |
| Vertex AI unavailable | ADK request fails | Non-2xx push; bounded Pub/Sub retry | Deployment architecture |
| Firestore contention | Transaction retry | Re-evaluate against current version | Firestore repository |
| Pub/Sub publish failure | Publish exception after durable receive | API reports persisted-but-not-published; event remains auditable | API error path |
| No safe recovery | `safe_to_commit=false` | Professional `human_required` state | Workflow policy |
| External delivery attempt | No send tool exists | Messages stay `prepared_not_sent` | Tool allowlist and evaluation |

The demo makes a deliberate distinction between *workflow completion* and
*communication delivery*. A completed recovery can prepare an outbox, but a
human or a separately governed downstream system must authorize any external
message.
