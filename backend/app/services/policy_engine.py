import math
import random
from dataclasses import dataclass, field


DEFAULT_ACTIONS = ["control", "variant_a", "variant_b"]


@dataclass
class PolicyEngine:
    epsilon: float = 0.1
    rng: random.Random = field(default_factory=random.Random)
    counts: dict[str, dict[str, int]] = field(default_factory=dict)
    rewards: dict[str, dict[str, float]] = field(default_factory=dict)
    thompson_successes: dict[str, float] = field(default_factory=dict)
    thompson_failures: dict[str, float] = field(default_factory=dict)
    linucb_counts: dict[str, int] = field(default_factory=dict)
    linucb_rewards: dict[str, float] = field(default_factory=dict)

    def choose(self, policy: str, context: dict | None = None, actions: list[str] | None = None) -> tuple[str, float]:
        actions = actions or DEFAULT_ACTIONS
        context = context or {}

        if policy in {"static", "ab_test"}:
            return self._static_ab(actions)
        if policy == "epsilon_greedy":
            return self._epsilon_greedy(actions)
        if policy == "thompson_sampling":
            return self._thompson_sampling(actions)
        if policy == "linucb":
            return self._linucb(context, actions)
        raise ValueError(f"Unknown policy: {policy}")

    def update(self, policy: str, action: str, reward: float) -> None:
        self.counts.setdefault(policy, {})
        self.rewards.setdefault(policy, {})
        self.counts[policy][action] = self.counts[policy].get(action, 0) + 1
        self.rewards[policy][action] = self.rewards[policy].get(action, 0.0) + reward

        self.thompson_successes[action] = self.thompson_successes.get(action, 1.0) + reward
        self.thompson_failures[action] = self.thompson_failures.get(action, 1.0) + (1.0 - reward)
        self.linucb_counts[action] = self.linucb_counts.get(action, 0) + 1
        self.linucb_rewards[action] = self.linucb_rewards.get(action, 0.0) + reward

    def _static_ab(self, actions: list[str]) -> tuple[str, float]:
        action = self.rng.choice(actions)
        return action, 1.0 / len(actions)

    def _epsilon_greedy(self, actions: list[str]) -> tuple[str, float]:
        if self.rng.random() < self.epsilon:
            return self.rng.choice(actions), self.epsilon / len(actions)

        action = max(actions, key=self._mean_reward)
        return action, 1.0 - self.epsilon + (self.epsilon / len(actions))

    def _thompson_sampling(self, actions: list[str]) -> tuple[str, float]:
        samples = {
            action: self.rng.betavariate(
                self.thompson_successes.get(action, 1.0),
                self.thompson_failures.get(action, 1.0),
            )
            for action in actions
        }
        return max(samples, key=samples.get), 1.0 / len(actions)

    def _linucb(self, context: dict, actions: list[str]) -> tuple[str, float]:
        engagement = float(context.get("engagement", 0.5))
        scores = {}
        for action in actions:
            count = self.linucb_counts.get(action, 0)
            mean_reward = self._mean_reward(action)
            confidence = math.sqrt(2.0 * math.log(sum(self.linucb_counts.values()) + 2) / (count + 1))
            scores[action] = mean_reward + (0.2 * engagement) + confidence
        return max(scores, key=scores.get), 1.0 / len(actions)

    def _mean_reward(self, action: str) -> float:
        reward_total = sum(policy_rewards.get(action, 0.0) for policy_rewards in self.rewards.values())
        count_total = sum(policy_counts.get(action, 0) for policy_counts in self.counts.values())
        return reward_total / count_total if count_total else 0.0


policy_engine = PolicyEngine()

