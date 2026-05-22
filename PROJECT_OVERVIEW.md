# Project Overview

## Adaptive Experimentation & AI Decisioning Platform

This project is a production-style MVP for adaptive lifecycle messaging. It demonstrates how an experimentation platform can choose interventions while balancing immediate clicks, long-term retention, user fatigue, and unsubscribe risk.

The core demo scenario:

> A lifecycle messaging system is choosing interventions while balancing clicks, retention, fatigue, and unsubscribe risk.

## What It Includes

- FastAPI backend
- Postgres event store
- React/Vite dashboard
- Redpanda/Kafka streaming scaffold
- Synthetic lifecycle simulation
- Open Bandit Dataset replay support
- Contextual bandit policy engine
- OPE estimators: IPS, SNIPS, doubly robust
- Governance and rollout controls
- Experiment observability checks
- Exploration budget governance
- Bayesian sequential comparison
- Deterministic AI-assisted assignment and messaging scaffolds
- dbt-style warehouse metrics layer

## Demo Story

The seeded demo intentionally shows why short-term optimization can be misleading:

- `epsilon_greedy` wins immediate reward.
- `linucb` wins long-term reward.
- one policy receives governance review due to low traffic.
- observability flags saturation and unsubscribe-risk exposure.
- high-risk profiles route to abstain or review.

## Safety Position

The system does not autonomously deploy generated messages or policy changes. AI-assisted outputs are deterministic by default, require human review, and are generated only from approved templates and retrieved evidence.
