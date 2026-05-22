with performance as (
    select * from {{ ref('mart_policy_performance') }}
),
health as (
    select * from {{ ref('mart_experiment_health') }}
)

select
    performance.policy,
    performance.event_count,
    performance.average_immediate_reward,
    performance.average_long_term_reward,
    health.low_propensity_overlap_rate,
    health.high_unsubscribe_risk_rate,
    case
        when health.high_unsubscribe_risk_rate >= 0.20 then 'pause'
        when health.low_propensity_overlap_rate >= 0.15 then 'human_review'
        when performance.average_long_term_reward >= performance.average_immediate_reward then 'deploy'
        else 'canary'
    end as governance_status,
    case
        when health.high_unsubscribe_risk_rate >= 0.20 then 'high unsubscribe-risk exposure'
        when health.low_propensity_overlap_rate >= 0.15 then 'low propensity overlap'
        when performance.average_long_term_reward >= performance.average_immediate_reward then 'long-term reward supports rollout'
        else 'short-term reward needs more long-term validation'
    end as governance_reason
from performance
join health using (policy)
