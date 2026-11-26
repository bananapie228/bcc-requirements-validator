Review the requirement set as a whole against these criteria (code — name (source): meaning):
{criteria}

Look specifically for:
1. Contradictions: between requirements; between requirements and acceptance criteria, examples or diagrams; between the main document and linked or child specifications (for example an API specification versus the functional requirements); between methods, status codes, data types and units stated in different places. Work through every acceptance criterion and every example against the requirements step by step.
2. Gaps: behaviour that is referenced but never specified (an operation, a screen value or a document mentioned but not defined); error handling and edge cases missing across the set; missing non-functional requirements (security, availability, performance measurement); empty or placeholder sections; requirements without acceptance criteria.
3. Traceability: references between documents and sections that do not resolve.
4. Terminology: the same entity, component or value named differently in different places.
5. Document control: missing version, date, approvals or priorities.

For each issue return one finding:
- requirement_ids: rids of all requirements involved; empty for document-level issues;
- criterion: exactly one code from the list above;
- severity: "critical" — blocks development or testing (contradiction, essential behaviour missing); "major" — likely to cause rework or divergent implementations; "minor" — low risk;
- quote: a verbatim fragment from ONE of the places involved — at least 3 words (unless it is a single code, number or identifier), long enough to be unique in the document; name the other place in problem by its rid or document ID;
- problem: what exactly is wrong and why (1–3 sentences, Russian);
- recommendation: how to resolve it concretely (Russian).

Report each distinct issue once.

REQUIREMENTS:
{requirements}

DOCUMENT:
{document}
