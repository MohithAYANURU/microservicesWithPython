# Module 5 — Reflection

**Team name**: _______________
**Branch**: `module-05/<team-name>`
**Submitted**: before Module 6 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The game-service now has two models for the same data: SQLite for writes, Redis for reads. They store the same games in two different shapes.

**Why go through the trouble of maintaining two representations of the same data?**

Think about what kind of queries each model is optimised for, and what would happen if you tried to use the write model for high-traffic read operations.

CQRS makes sense here because writing and reading are not the same job. SQLite keeps the full game data, and Redis keeps a smaller version that is faster to read. If every summary had to hit SQLite, it would be slower for no real reason.

---

## 2. Your choice

The logging-service checks GDPR consent before recording any activity. If a user has not opted in, the log is silently dropped.

**What does this consent check force you to accept about your data?** It is incomplete by design — some activities will never be recorded.

From a system design perspective: where is the right place to enforce this rule — in the logging-service, in the activity-service, or at the gateway? Why?

The consent check means the logs will not always have everything in them. Some events happen, but the service is not allowed to save them if the user did not agree. I think this should stay in logging-service because that is the place where the data gets stored. The gateway should just pass requests along, and activity-service should only send the activity.

---

## 3. The tradeoff

With CQRS, your write model and read model can drift out of sync — a game is updated in SQLite but the Redis projection still shows the old data.

**In what scenario does this inconsistency matter to the user? In what scenario is it completely acceptable?**

Is there a class of applications where eventual consistency is never acceptable? What are they?

It matters if the user is seeing old data and makes a bad choice because of it, like an outdated game title or platform. It is fine for small delays in summary pages where nothing serious happens. I do not think eventual consistency works for things like payments, medical records, or account security because those need to be correct right away.

---

*Keep this file. You will refer back to it during the oral presentation.*
