select
    logged_policy as policy,
    count(*) as event_count,
    avg(immediate_reward) as average_immediate_reward,
    avg(long_term_reward) as average_long_term_reward,
    sum(immediate_reward) as cumulative_immediate_reward,
    sum(long_term_reward) as cumulative_long_term_reward,
    avg(propensity) as average_propensity
from {{ ref('stg_events') }}
group by 1
