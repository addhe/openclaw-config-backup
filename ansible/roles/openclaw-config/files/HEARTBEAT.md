# Heartbeat Tasks

Periodic checks to run on heartbeat polls.

## Checks (rotate 2-4 times per day)

- [ ] Email - check for urgent unread messages
- [ ] Calendar - upcoming events in next 24-48h
- [ ] Weather - relevant for outdoor plans

## State

Track in `memory/heartbeat-state.json`:
- lastChecks: timestamps for each check type
- lastHeartbeat: last heartbeat time

## When to reach out

- Important email arrived
- Calendar event coming up (<2h)
- Something interesting found
- Been >8h since last message

## When to stay quiet (HEARTBEAT_OK)

- Late night (23:00-08:00 UTC) unless urgent
- Nothing new since last check
- Just checked <30 minutes ago