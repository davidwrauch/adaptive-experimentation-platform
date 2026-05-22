# Lifecycle Messaging Scenario

## Fictional Company

Northstar is a fictional subscription-based platform with marketplace-style content and creator recommendations. Its lifecycle team uses messaging to help users finish onboarding, discover relevant recommendations, return after inactivity, renew subscriptions, and avoid churn.

## Business Problem

The team wants to improve short-term response without damaging long-term customer value. A reminder that earns clicks today can become harmful if it over-contacts fatigued users, increases unsubscribe risk, or trains the system to optimize urgency over retention.

## Intervention Types

Northstar experiments with approved message interventions:

- short reminder
- personalized recommendation summary
- weekly digest
- win-back message
- urgency reminder
- educational onboarding tip
- contextual recommendation

Each intervention has metadata such as message length, personalization depth, frequency category, fatigue score, estimated unsubscribe risk, and tone/style.

## Adaptive Policy Behavior

- Static Control provides a baseline comparison for causal lift.
- Epsilon Greedy explores aggressively and can over-expose high-frequency reminders while learning.
- Thompson Sampling balances uncertainty and observed reward.
- LinUCB adapts to user context, often preferring personalized summaries for mature or high-value users.

## Governance Tradeoffs

The system can hold expansion even when a policy appears statistically promising. Guardrails watch traffic quality, low overlap, saturation, fatigue, unsubscribe-risk exposure, and long-term reward. Hold Expansion means the experiment is not a failure; it means the policy should not receive broader traffic until the risk picture improves.

## Short-Term vs Long-Term Optimization

Immediate reward approximates response or click behavior. Long-term reward incorporates retention, fatigue, delayed value, and unsubscribe risk. This lets the dashboard explain why Epsilon Greedy may win short-term response while LinUCB is stronger for retention.

## Constrained AI Messaging

The AI-assisted messaging layer is review-only. It creates candidate variants from approved templates, retrieval-grounded examples, tone and length constraints, and governance context. It does not autonomously deploy messages or generate unrestricted copy.
