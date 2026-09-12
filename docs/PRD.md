# AURA Product Requirements Document

## Core user journey
1. Agent/customer submits case.
2. Intake classifies intent, sentiment and priority.
3. Customer agent gathers profile/history.
4. Investigation agent gathers order/shipment/ticket evidence.
5. Policy agent retrieves applicable policy.
6. Root-cause agent creates evidence-backed diagnosis.
7. Resolution agent proposes customer/internal action.
8. Risk gate evaluates confidence, policy and financial threshold.
9. Low-risk actions execute; high-risk actions wait for human approval.
10. Audit event is recorded.
11. Aggregated patterns appear in the executive control tower.

## MVP acceptance criteria
- End-to-end case resolution works from API and UI.
- High-value delayed order scenario produces a grounded root cause.
- Compensation threshold is enforced.
- Approval and rejection flows work.
- Audit trail is visible.
- KPI and ROI endpoints return valid data.
- Test suite passes.
