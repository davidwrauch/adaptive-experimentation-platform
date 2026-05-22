import React from "react";
import { HelpLabel } from "./InfoTooltip";
import { formatPolicyLabel, launchRecommendation, statisticalPosture } from "../interpretations";

const policyDescriptions = {
  static: "Traditional equal-split experiment used as a baseline comparison.",
  epsilon_greedy: "Aggressively explores new messaging strategies to maximize short-term engagement.",
  thompson_sampling: "Balances exploration and uncertainty using probabilistic reward estimates.",
  linucb: "Personalizes messaging decisions using user context and long-term behavioral patterns.",
};

const policyOrder = ["static", "epsilon_greedy", "thompson_sampling", "linucb"];

export default function ExperimentComparisonPanel({ metrics, uplift }) {
  const baseline = (metrics.policies ?? []).find((policy) => policy.policy === "static") ?? metrics.policies?.[0];
  const bayesianByPolicy = Object.fromEntries(
    (metrics.bayesian?.policies ?? []).map((policy) => [policy.policy, policy]),
  );
  const recommendation = launchRecommendation(metrics, uplift);
  const policies = policyOrder
    .map((name) => (metrics.policies ?? []).find((policy) => policy.policy === name))
    .filter(Boolean);

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="This comparison explains the experiment without requiring bandit or statistics knowledge: what is being tested, how each adaptive policy behaves, and which outcomes matter.">
            Experiment Comparison
          </HelpLabel>
        </h2>
        <span className={`launch-badge launch-${slug(recommendation.state)}`}>{recommendation.state}</span>
      </div>
      <p className="panel-copy">
        Northstar is testing lifecycle messaging strategies across message timing, frequency,
        length, personalization depth, urgency level, and recommendation style.
      </p>
      <div className="experiment-grounding-grid">
        {policies.map((policy) => {
          const posture = statisticalPosture(policy, baseline, bayesianByPolicy[policy.policy]);
          return (
            <article className="experiment-comparison-card" key={policy.policy}>
              <div>
                <strong className="policy-label">{displayName(policy.policy)}</strong>
                <p>{policyDescriptions[policy.policy]}</p>
              </div>
              <dl>
                <dt>Click/engagement outcome</dt>
                <dd>{policy.average_reward.toFixed(3)} avg reward</dd>
                <dt>Long-term retention outcome</dt>
                <dd>{(policy.behavioral?.average_long_term_reward ?? policy.average_reward).toFixed(3)}</dd>
                <dt>Unsubscribe/fatigue risk</dt>
                <dd>{riskLabel(policy)}</dd>
                <dt>Confidence</dt>
                <dd>{posture.posture}</dd>
                <dt>Rollout posture</dt>
                <dd>{policy.governance?.status ?? "canary"}</dd>
                <dt>Recommendation</dt>
                <dd>{posture.operationalRecommendation}</dd>
              </dl>
            </article>
          );
        })}
      </div>
      <div className="ab-adaptive-comparison">
        <div>
          <strong>Traditional A/B</strong>
          <ul className="plain-list">
            <li>fixed traffic split</li>
            <li>static experiment</li>
            <li>slower adaptation</li>
          </ul>
        </div>
        <div>
          <strong>Adaptive Optimization</strong>
          <ul className="plain-list">
            <li>learn continuously</li>
            <li>personalize by context</li>
            <li>optimize over time</li>
            <li>dynamically adjust exploration</li>
          </ul>
        </div>
      </div>
    </section>
  );
}

function displayName(policy) {
  if (policy === "static") return "Static A/B Control";
  return formatPolicyLabel(policy);
}

function riskLabel(policy) {
  const risk = policy.behavioral?.average_unsubscribe_risk ?? 0;
  const fatigue = policy.behavioral?.average_fatigue_delta ?? 0;
  if (risk >= 0.3 || fatigue >= 0.08) return "Elevated";
  if (risk >= 0.18 || fatigue >= 0.04) return "Moderate";
  return "Low";
}

function slug(value) {
  return String(value).toLowerCase().replaceAll(" ", "-");
}
