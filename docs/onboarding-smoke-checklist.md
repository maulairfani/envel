# Onboarding Smoke Test Checklist

## Purpose

Verify a first-time user can complete setup end-to-end and land in a usable post-onboarding state.

## Source of truth for completion

Onboarding completion is defined by `get_onboarding_status` in `apps/mcp-server/src/envel_mcp/tools/analytics.py`:
- Step 1: Add accounts (`has_accounts`)
- Step 2: Set envelope targets (`has_targets`)
- Step 3: Assign money to envelopes (`any_assigned`)
- Step 4: Ready to Assign reaches zero (`all_assigned`)

## Minimal smoke checklist

### 1) Verify account creation step
- Create a fresh user account in platform web signup flow.
- Confirm successful auth redirect lands on `/connect`.
- Add at least one account with positive balance from Accounts page.
- Verify onboarding status marks Step 1 "Add accounts" as done.

Pass criteria:
- User can create an account and sign in.
- At least one account exists.
- `steps[0].done === true`.

### 2) Verify envelope setup step
- Create at least one expense envelope.
- Set a target type and value on that envelope.
- Verify onboarding status marks Step 2 "Set envelope targets" as done.

Pass criteria:
- At least one expense envelope has `target_type` not null.
- `steps[1].done === true`.

### 3) Verify completion state and dashboard behavior
- Assign funds to envelopes for current period.
- Confirm at least one budget assignment record exists.
- Continue assigning until Ready to Assign is approximately zero.
- Verify onboarding status marks Step 3 and Step 4 as done and returns completion.
- Open dashboard/default authenticated route and verify app is usable (routes resolve, no onboarding blocker UI).

Pass criteria:
- `steps[2].done === true`.
- `steps[3].done === true`.
- `is_complete === true`.
- `ready_to_assign` is within ±1 of zero.
- Authenticated app routes to `/envelopes` by default and pages load.

## Verification evidence format (for issue comments)

Use this compact template for each smoke run:

- Date/time:
- Environment:
- User used for test:
- Result: PASS / FAIL
- Step 1 (account creation): PASS/FAIL + evidence
- Step 2 (envelope setup): PASS/FAIL + evidence
- Step 3 (completion + dashboard): PASS/FAIL + evidence
- Onboarding status payload excerpt:
- Notes / follow-ups:
