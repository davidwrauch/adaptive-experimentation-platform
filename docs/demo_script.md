# Demo Script

## 1. Open With The Scenario

"This is a lifecycle messaging decisioning platform. It chooses interventions while balancing clicks, retention, fatigue, and unsubscribe risk."

## 2. Show Summary Metrics

Point out the event count, immediate reward, and best immediate policy.

Key line: "The top click policy is not necessarily the best lifecycle policy."

## 3. Show Observability

Explain that adaptive systems can corrupt their own evaluation data through traffic imbalance, low overlap, reward drift, saturation, and high-risk exposure.

## 4. Show Assignment And Messaging

Run the sample assignment. Explain the route, confidence, evidence, and governance reason.

Run constrained messaging generation. Emphasize that all generated variants require human review.

## 5. Show OPE And Governance

Describe IPS, SNIPS, and doubly robust estimates as ways to evaluate policies from logged data. Show deploy/canary/review/pause labels.

## 6. Show Long-Term Tradeoff

Use the seeded demo story:

- `epsilon_greedy` wins immediate reward.
- `linucb` wins long-term reward.

## 7. Show Rollout And Bayesian Panels

Explain that rollout controls and Bayesian stopping recommendations are the operating layer between experimentation and production.

## 8. Close

"The project demonstrates not just policy learning, but the governance, observability, and evidence layers needed to operate adaptive systems responsibly."
