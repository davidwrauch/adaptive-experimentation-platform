import React from "react";
import ResearchPopover from "./ResearchPopover";

export default function AboutPanel() {
  return (
    <section className="panel about-panel">
      <div className="section-heading">
        <h2>About this platform</h2>
        <ResearchPopover referenceKey="overview" />
      </div>

      <div className="about-grid">
        <article>
          <h3>Project purpose</h3>
          <p>
            This is a production-style adaptive experimentation and causal decisioning platform for
            Northstar, a fictional lifecycle messaging product balancing engagement, retention,
            fatigue, unsubscribe risk, incrementality, and rollout safety.
          </p>
        </article>
        <article>
          <h3>Why it is intentionally holistic</h3>
          <p>
            Real adaptive experimentation systems are not just A/B tests or ML models. They require
            experimentation science, causal inference, adaptive policies, long-term reward thinking,
            guardrail monitoring, rollout controls, decision logging, human review, and operational UX.
          </p>
        </article>
        <article>
          <h3>Creator / motivation</h3>
          <p>
            I built this to understand what a modern adaptive experimentation platform would need if
            it were designed not just to maximize clicks, but to support safe, accountable product
            decisions.
          </p>
        </article>
        <article>
          <h3>Philosophy</h3>
          <p>
            The system is intentionally broad because modern experimentation platforms are broad.
            The goal is not maximalism for its own sake, but to show how the pieces connect: what
            happened, why it happened, whether we can trust it, whether it is causal, whether it is
            safe, whether we should expand, and whether a human can explain the decision.
          </p>
        </article>
      </div>

      <div className="about-two-column">
        <article>
          <h3>What this is</h3>
          <ul className="plain-list">
            <li>a deployed prototype</li>
            <li>a simulation of adaptive lifecycle messaging</li>
            <li>an experimentation operating console</li>
            <li>a synthesis of production experimentation concepts</li>
          </ul>
        </article>
        <article>
          <h3>What this is not</h3>
          <ul className="plain-list">
            <li>a fully scaled enterprise experimentation platform</li>
            <li>a replacement for production infra at Netflix, Amazon, Airbnb, Uber, or Udemy</li>
            <li>a claim that simulated results are real business outcomes</li>
          </ul>
        </article>
      </div>

      <article className="about-stack">
        <h3>Technical stack summary</h3>
        <div className="capability-strip">
          {[
            "FastAPI",
            "React/Vite",
            "Postgres/Neon",
            "Render/Vercel",
            "contextual bandits",
            "OPE",
            "Bayesian experimentation",
            "uplift modeling",
            "governance",
            "live replay",
            "constrained AI messaging",
          ].map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
        <p>
          Inspired by public engineering and research writing from Netflix, Airbnb, Amazon, Uber,
          Udemy, Statsig, Optimizely, Eppo, and contextual bandit literature.
        </p>
      </article>
    </section>
  );
}
