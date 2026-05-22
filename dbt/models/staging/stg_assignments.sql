select
    event_id,
    user_id,
    logged_policy,
    action as selected_intervention,
    propensity,
    event_timestamp,
    case
        when propensity < 0.05 then true
        else false
    end as low_overlap_flag
from {{ ref('stg_events') }}
