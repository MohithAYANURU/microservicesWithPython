# Module 4 — Reflection

**Team name**: MohithAYANURU
**Branch**: `module-04/<team-name>`
**Submitted**: before Module 5 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

In Module 3, services called each other directly over HTTP. Now activity-service drops a message into a broker and moves on — it never waits for a reply.

**What does the activity-service gain by not waiting? And what does the notification-service gain by consuming at its own pace?**

Think about what happens under load, or when notification-service is temporarily down.

> *Your answer:*

Activity-service basically gets to say "I'm done!" and leave. It drops the message in the broker and immediately tells the user their action was saved. It doesn't sit around waiting for the notification service to actually send an email or SMS. When things get busy, the user still gets a fast response instead of waiting for the slowest service in the chain. And if notification-service goes down? Activity-service keeps working fine—the messages just pile up in the broker waiting to be delivered later.

For notification-service, it's like having your own schedule. Instead of getting bombarded with requests whenever activity-service fires, it can pull messages from the broker whenever it has capacity. Maybe it batches them, maybe it scales up workers to handle a spike, or maybe it runs at 3 AM when things are quiet. It's in control of its own pace instead of being pushed around by whoever's sending notifications.

---

## 2. Your choice

In Module 3 you already knew how to call another service directly over HTTP — you did it for user validation and game enrichment.

**Why not use the same approach for notifications? What does introducing a broker give you that a direct HTTP call doesn't?**

Think about what happens if notification-service is slow, or crashes mid-message.

> *Your answer:*

With direct HTTP calls, you're basically playing hot potato. If notification-service is being slow that day, activity-service either times out or has to keep retrying. If it crashes while handling a request, that message just... vanishes. And suddenly you've built this whole retry mechanism into activity-service just to handle a notification issue—that's coupling problems we didn't have before.

With a broker, messages are saved to disk. If notification-service is slow, messages just pile up in the queue. If it crashes, the broker keeps them safe and tries again when it comes back. The broker handles all that retry logic, dead letter queues for broken messages, and delivery guarantees automatically. Instead of activity-service worrying about whether notifications actually got sent, it just throws the message at the broker and moves on. The broker handles the hard stuff.

---

## 3. The tradeoff

With synchronous REST, you get an immediate answer: success or failure. With async messaging, the activity is saved and the message is sent — but you have no idea if the notification was ever delivered.

**How would a user know if their notification was never sent? How would you know as a developer?**

What visibility do you lose when you go async?

> *Your answer:*

Here's the problem: the user sees "Activity saved successfully!" and thinks they're good. But their notification might never arrive and they'd have no clue. For us as developers, it's worse—we get no immediate signal. With REST, you'd get a 500 error instantly. With async? Complete silence. Notifications just fail silently somewhere in the broker.

To fix this, you basically have to become a detective. Add logging to see what messages enter the broker. Set up monitoring to catch errors when messages are processed. Create alerts when messages get stuck in dead letter queues. You could even have notification-service send back a confirmation event saying "yep, email sent!" and track that. Without all this infrastructure, async messaging turns into a black hole where things quietly break and nobody notices until someone complains they never got their email.

---

*Keep this file. You will refer back to it during the oral presentation.*
