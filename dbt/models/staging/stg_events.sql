with source_events as (
    select
        id as event_id,
        user_id,
        policy as logged_policy,
        action,
        reward as immediate_reward,
        propensity,
        context,
        created_at as event_timestamp
    from {{ source('app', 'events') }}
)

select
    event_id,
    user_id,
    logged_policy,
    action,
    immediate_reward,
    propensity,
    cast(context -> 'outcome' ->> 'long_term_reward' as numeric) as long_term_reward,
    cast(context ->> 'fatigue_score' as numeric) as fatigue_score,
    cast(context ->> 'unsubscribe_risk' as numeric) as unsubscribe_risk,
    cast(context ->> 'prior_touch_count' as integer) as prior_touch_count,
    event_timestamp
from source_events
