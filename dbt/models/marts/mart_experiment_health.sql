select
    logged_policy as policy,
    count(*) as event_count,
    avg(case when propensity < 0.05 then 1 else 0 end) as low_propensity_overlap_rate,
    avg(case when unsubscribe_risk >= 0.35 then 1 else 0 end) as high_unsubscribe_risk_rate,
    avg(prior_touch_count) as average_prior_touch_count,
    avg(immediate_reward - long_term_reward) as delayed_reward_gap
from {{ ref('stg_events') }}
group by 1
