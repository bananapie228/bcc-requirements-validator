Check the requirement set for GAPS, against these criteria (code — name (source): meaning):
{criteria}

Work through these steps one by one and do not skip any:
1. Sections that are empty, contain a placeholder or "to be filled" text, or templates and checklists left unanswered.
2. Requirements that have no acceptance criterion; missing acceptance criteria for boundary values, error cases and alternative flows.
3. Things referenced but never specified: operations, screen values, documents, data fields, error messages.
4. Missing non-functional requirements: security, availability, performance with a measurement point, logging and audit.
5. Missing rollback, disabling or migration strategy; missing error handling across the set.
6. Document control: version, date, approvals, priority or stability of requirements.
7. Traceability: references between documents and sections that do not resolve; requirements that cannot be traced to a goal.

For each issue return one finding:
- requirement_ids: rids of all requirements involved; empty for document-level issues;
- criterion: exactly one code from the list above;
- severity: "critical" — blocks development or testing; "major" — likely to cause rework or divergent implementations; "minor" — low risk;
- quote: a verbatim fragment of the DOCUMENT text (never of the requirement headers) from ONE of the places involved — at least 3 words unless it is a single code, number or identifier, long enough to be unique; name the other place in problem by its rid or document ID;
- problem: what exactly is wrong and why (1–3 sentences, Russian), naming both places for a contradiction;
- recommendation: how to resolve it concretely (Russian).

Report each distinct issue once. Do not repeat wording defects of single requirements — they are reviewed separately.

REQUIREMENTS (header lines are metadata; only "text:" lines are document text):
{requirements}

DOCUMENT:
{document}
