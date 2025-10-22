erDiagram
    SOURCE_SYSTEM ||--o{ CHECK : provides
    CHECK ||--o{ CHECK_RESULT : produces
    ALERT ||--o{ ALERT_CHECK : "depends on"
    CHECK ||--o{ ALERT_CHECK : "feeds"
    ALERT ||--o{ ALERT_EVENT : "has events"
    USER ||--o{ ALERT_EVENT : "performed by (when actor_type=USER)"
    ALERT ||--|| ALERT_SNAPSHOT : "current denormalized view"

    SOURCE_SYSTEM {
      uuid id PK
      text name
      text kind        // e.g. "batch", "mlink-probe", "fix-probe", "infra"
      jsonb metadata   // optional
      timestamptz created_at
    }

    CHECK {
      uuid id PK
      text name
      text key UNIQUE       // natural key from source (e.g. "batch:daily_nav")
      uuid source_system_id FK
      text severity         // INFO|WARN|CRIT (or numeric 1..3)
      text component        // e.g. service/host/cluster
      jsonb config          // thresholds, dimensions
      timestamptz created_at
      timestamptz retired_at
    }

    CHECK_RESULT {
      uuid id PK
      uuid check_id FK
      timestamptz observed_at
      text status           // PASS|FAIL|WARN|UNKNOWN
      numeric value         // optional measured value
      text unit             // "ms","%","bool","count",...
      jsonb details         // payload from probe
      -- index(check_id, observed_at DESC)
    }

    ALERT {
      uuid id PK
      text name
      text pkey UNIQUE      // stable external identifier (for UI/links)
      text severity         // INFO|WARN|CRIT (default/worst-of checks)
      text state            // OK|FAIL|ACK (sticky; no auto-back-to-OK)
      uuid current_owner_id FK NULL  -- USER who ACKed
      timestamptz created_at
      timestamptz updated_at
      text runbook_url NULL
      jsonb metadata NULL
    }

    ALERT_CHECK {
      uuid id PK
      uuid alert_id FK
      uuid check_id FK
      text logic            // "ANY_FAIL" (v1), future: "ALL", "THRESHOLD", weight, etc.
      unique (alert_id, check_id)
    }

    ALERT_EVENT {
      uuid id PK
      uuid alert_id FK
      timestamptz occurred_at
      text event_type       // AUTO_FAIL, ACK, RESOLVE_OK, UNACK, ESCALATE, COMMENT, REOPEN_FAIL
      text prev_state       // OK|FAIL|ACK
      text new_state        // OK|FAIL|ACK
      text actor_type       // SYSTEM|USER
      uuid actor_user_id FK NULL
      text reason NULL      // free text (why)
      jsonb context NULL    // e.g. triggering check_ids, values
      -- index(alert_id, occurred_at DESC)
    }

    USER {
      uuid id PK
      text username UNIQUE
      text display_name
      text email
      timestamptz created_at
      boolean active
    }

    ALERT_SNAPSHOT {
      uuid alert_id PK FK
      text state                // OK|FAIL|ACK
      text severity             // computed worst-of checks or configured
      uuid current_owner_id NULL
      timestamptz last_event_at
      text last_event_type
      timestamptz first_failed_at NULL
      timestamptz acked_at NULL
      timestamptz last_changed_at
      int fail_count_24h        // rollups for UI sorting
      jsonb checks_summary      // [{check_id,name,status,value,...}]
      text pkey
      text name
      text runbook_url NULL
      -- indices for dashboard sorting/filters:
      -- index(state), index(severity, state), index(last_event_at DESC)
    }
