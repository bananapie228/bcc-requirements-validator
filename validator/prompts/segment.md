Below is a requirements document. Each line is prefixed with its line number ("N: ").

Task: extract every individual requirement statement so that each can be reviewed on its own.

What counts as a requirement — any statement that obliges or constrains the system, its data, interfaces or behaviour:
- numbered functional requirements: keep each numbered item whole even if it has several sentences (do not split it; atomicity is reviewed later);
- non-functional, data, integration and UI requirements;
- architecture, process and sequence descriptions that prescribe how systems interact: one requirement per described flow;
- each row of an acceptance-criteria table: one row = one requirement;
- in API / interface specifications: method, URL and authorisation; each processing-logic step; each special rule; each request parameter row; each response field row; each status-code rule.

What is NOT a requirement: document metadata tables, goals and background, review checklists, approval or signature blocks, headings, empty template placeholders. Their defects are checked in another pass.

For each requirement return:
- doc_id: the identifier exactly as written in the document (a number, a code like "FR-1", a parameter name); null if it has none;
- section: the path of the nearest headings as "<heading> / <subheading>", copied in the document's own language;
- text: a VERBATIM quote of the requirement. Copy characters exactly. Omit line-number prefixes and markdown symbols (*, |, #, `). For a table row, quote the cell texts in order separated by single spaces. Never merge text from different places.

Keep the document order. Do not skip anything that matches the definition above.

DOCUMENT:
{document}
