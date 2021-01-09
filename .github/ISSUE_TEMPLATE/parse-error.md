---
name: Parse Error
about: Report commit parse errors with this template.
title: "[PARSE ERROR]"
labels: bug
assignees: jeremyagray

---

### Instructions

The following list corresponds to the the current data used for testing the parser.  Complete as much as possible, but at least the "raw" field and add your configuration options.  Several options have pre-filled choices; please select one.  All options are either strings or integers, except `body["paragraphs"]` (an array of strings, one per body paragraph) and `footers` (an array of `footer` objects).

Commit parsing errors will be resolved by integrating submitted data into the parser unit testing and fixing any resulting issues.

### Commit Parsing Data

- raw: ""
- parsed: ""
- header:
  - type: ""
  - scope: ""
  - description: ""
  - length: 0
- body:
  - paragraphs
    - ""
  - longest: 0
- breaking:
  - flag: true or false
  - token: "BREAKING CHANGE" or "BREAKING-CHANGE" or " #"
  - separator: ": " or " #"
  - value: ""
- footers:
  - footer:
    - token: ""
    - separator: ": " or " #"
    - value: ""

### Configuration Data

Add your`[tool.pccc]` section of `pyproject.toml` and/or your CLI arguments used to produce the parsing error.
