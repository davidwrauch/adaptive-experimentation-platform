select
    user_id,
    count(*) as event_count,
    avg(fatigue_score) as average_fatigue_score,
    avg(unsubscribe_risk) as average_unsubscribe_risk,
    max(prior_touch_count) as max_prior_touch_count,
    avg(long_term_reward) as average_long_term_reward
from {{ ref('stg_events') }}
group by 1
