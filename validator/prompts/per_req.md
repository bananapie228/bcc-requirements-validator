Review each requirement in the BATCH individually against these criteria (code — name (source): meaning):
{criteria}

Use the full DOCUMENT only as context: definitions, related sections, units, examples. Report defects of the batch requirements themselves. Contradictions between different requirements are checked in a separate pass; report them here only if a requirement is wrong on its own.

For every requirement, go through every criterion. Typical defects: undefined terms; missing units, time zones, boundaries or formats; unspecified error, edge and alternative cases; several requirements in one statement; design decisions inside a requirement; wording that cannot be verified by a test; empty or placeholder content.

For every violated criterion return one finding:
- requirement_ids: [the rid of the requirement] — only rids from the BATCH;
- criterion: exactly one code from the list above;
- severity: "critical" — blocks development or testing (cannot be implemented or verified as written, essential behaviour missing, factually wrong); "major" — different people would likely implement or test it differently; "minor" — wording or template issue with low risk;
- quote: a verbatim fragment of the document that shows the defect — at least 3 words (unless it is a single code, number or identifier), long enough to be unique in the document;
- problem: what exactly is wrong and why (1–3 sentences, Russian);
- recommendation: a concrete rewrite or the specific missing information to add (Russian).

Do not mark a criterion as violated without evidence in the text. A requirement without defects gets no findings.

BATCH:
{batch}

DOCUMENT:
{document}
