Check whether requirements that govern the SAME behaviour can all be satisfied together, against these criteria (code — name (source): meaning):
{criteria}

Procedure — do not skip steps:
1. Group the requirements by the behaviour they govern: the same trigger or event, the same counter, limit or stored value, the same notification or response.
2. For every group with two or more requirements, build in your reasoning at least two concrete scenarios as a timeline of events. Cover: a setting changed in the middle of a period after something already happened; an event repeated or reversed (cancellation, refund, redelivery); a boundary value reached exactly; a period boundary crossed.
3. At every step of every scenario apply each requirement of the group literally and note what it demands. If two requirements demand different outcomes at the same step, or one forbids what another requires, that is a contradiction: report it as critical and describe the exact scenario and step in problem.
4. If the outcome at some step is simply not defined by any requirement, report it only if it blocks implementation; wording gaps of single requirements are reviewed elsewhere.

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
