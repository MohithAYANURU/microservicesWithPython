# Module 6 — Reflection

**Team name**: MohithAYANURU
**Branch**: `module-06/<team-name>`
**Submitted**: before Module 7 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The gateway now validates every JWT before forwarding a request. Individual services no longer need to check identity themselves.

**What does centralising authentication at the gateway buy you?** What would the alternative look like — if every service validated tokens on its own?

Think about what happens when you need to rotate the secret key, or add a new service to the system.

Centralising authentication at the gateway means every request is checked before it reaches the internal services. The services do not all need to repeat the same basic token validation logic, and adding a new service becomes simpler because the gateway already handles the front door.

If every service validated tokens by itself, we would have to copy the same JWT code and config everywhere. Rotating the secret key would also be harder because every service would need to be updated correctly. The gateway gives us one consistent place to reject missing, expired, or fake tokens.

---

## 2. Your choice

When activity-service calls user-service internally, it uses a Machine-to-Machine (M2M) token — not a user's token.

**Why can't it just reuse the user's token that arrived in the original request?**

What would break, or what door would you accidentally leave open, if services passed user tokens between themselves?

The user's token represents what that user is allowed to do. An internal call from activity-service to user-service is different: the service is doing backend validation as part of its own workflow, not asking to borrow the user's identity.

If services passed user tokens around, the user's authority could accidentally spread further than intended. A downstream service might treat the call as a direct user action even though it came from another service. Using an M2M token makes the caller clear: this request is from activity-service, with service-level permissions, not from a normal gamer or admin.

---

## 3. The tradeoff

The gateway and the auth-service share the same `SECRET_KEY` to verify tokens without making a network call on every request.

**What is the security risk of sharing this key?** What happens if it leaks?

And what would the alternative look like — verifying tokens by calling auth-service on every request instead? What does that cost you?

The risk is that the shared `SECRET_KEY` becomes a very powerful secret. If it leaks, someone could create fake JWTs and make the gateway or services believe they are a real user, an admin, or even a trusted service. That would break the whole trust model.

The alternative is for the gateway to call auth-service on every request to verify the token. That avoids sharing the signing secret with more services, but it makes auth-service a dependency for every request. If auth-service is slow or down, the whole platform becomes slow or locked out. Local verification is faster and more resilient, but it means key management has to be taken seriously.

---

*Keep this file. You will refer back to it during the oral presentation.*
