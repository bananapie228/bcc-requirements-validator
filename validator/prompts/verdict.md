The requirements document "{title}" ({n_requirements} requirements) has been reviewed. The findings are listed below as: ID [severity] criterion (requirements; line): problem.

Decide whether development and testing can start from this document as it is.
Hard rule: there are {n_critical} critical findings; if this number is above zero, both flags must be false and the summary must say that work cannot start yet.

Return:
- ready_for_development: false if any finding would block or seriously distort implementation;
- ready_for_testing: false if any finding makes expected results impossible to derive or verify;
- summary: 2–4 sentences in Russian — the overall state of the document and the main risk;
- top_fixes: up to 7 items in Russian, most important first. Each item starts with the finding IDs it resolves, e.g. "F-001, F-004: ...", and says concretely what to change in the document.

FINDINGS:
{findings}
