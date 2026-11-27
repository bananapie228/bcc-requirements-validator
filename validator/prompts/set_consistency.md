Check the requirement set for CONTRADICTIONS and inconsistencies, against these criteria (code — name (source): meaning):
{criteria}

Work through these steps one by one and do not skip any:
1. For every acceptance criterion, test case or worked example in the document: take its preconditions and action, apply the requirements literally to derive the expected result, and compare it with the stated expected result. Any mismatch is a critical contradiction.
2. Compare goals and purpose statements with what the requirements actually specify (timing, scope, guarantees).
3. Compare the main specification with linked or child specifications: operations that exist, HTTP methods, status codes and their meaning, field names, types, units and formats.
4. Compare units, currencies, data types and formats used for the same quantity in different sections.
5. Check that the same component, entity or value is named the same way everywhere.
(Conflicts between requirements that govern the same behaviour are checked in a separate pass.)

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
