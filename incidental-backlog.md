# Incidental Backlog (small later jobs)

## Purpose
Track small, non-blocking improvements noticed during feature work so they don’t get lost. Each item should be completable in ≤1 day and not expand the scope of a current feature.

## Ground rules
- No schema changes or major UI reworks here
- Prefer isolated edits; add tests where practical
- Keep acceptance criteria explicit (“done when …”)

## Current items
- [ ] Dashboard: make stacked cards a uniform size to prevent overlap/stacking artifacts
  - Done when: all cards within a stack render to identical height/width, the stack animation looks consistent regardless of content length, and no larger cards visually protrude behind smaller ones. Document any CSS variables used and ensure responsiveness.
