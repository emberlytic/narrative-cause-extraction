# Case Study: Hartwell Claims Group

> Client names and identifying details are fictional.
> The problem structure, workflow logic, and solution approach are based on real-world patterns from actual engagements.

## Client

Hartwell Claims Group is a third-party claims management firm that handles investigation and adjudication for several regional insurers. Their operations team processes hundreds of investigation reports per month across personal lines, commercial property, and liability files.

## The Challenge

Hartwell's operations team received a request to identify all historical claims where a specific cause type was either confirmed or identified as the most probable cause -- across a backlog of several hundred investigation reports.

Each report was a free-text document written by an independent adjuster or investigator. Reports varied in length (2-10 pages), used hedged language ("probable cause", "consistent with", "cannot be definitively determined"), and embedded the key finding across different sections -- sometimes in Conclusion, sometimes in Findings, sometimes scattered through the narrative.

Manual review was estimated at 10-15 minutes per report. At 400 reports, that was 60-100 hours of analyst time. The deadline was days, not weeks.

A further complication: investigators used different phrasing for the same concept. "Electrical arcing", "electrical fault", and "failure of electrical distribution equipment" all referred to the same cause type. A keyword search would miss variants.

## What We Built

A Python pipeline that reads scrubbed report text from a CSV, sends each report to an LLM API with a structured extraction prompt, and returns three fields per report: the confirmed cause (if explicitly stated as such), the probable cause (if the report hedges or the confirmed cause is absent), and a confidence flag (confirmed, probable, or not_determinable).

The prompt instructs the LLM to reason across the full report text rather than pattern-match on keywords, so it handles varied phrasing and hedged language correctly. All results write to a CSV for downstream analysis and filtering.

Reports were pre-scrubbed (addresses, names, and identifying details removed) before being sent to the API -- a step that can be automated or done manually depending on data sensitivity requirements.

Key decisions:

- Extracting three distinct fields (confirmed cause, probable cause, confidence) rather than a single classification made the output useful for both strict and exploratory analysis.
- The prompt explicitly defines what "confirmed" versus "probable" means in this context, so the LLM applies consistent criteria across reports with varying language.
- No fine-tuning or custom model -- prompt engineering on a general-purpose LLM was sufficient.

## Results

| Metric | Result |
|---|---|
| Reports processed | 400 |
| Processing time | Under 2 hours, processed sequentially one report at a time (vs. 60-100 hours manual) |
| Cause classifications returned | Confirmed: 187, Probable: 134, Not determinable: 79 |
| Manual spot-check accuracy | Reviewed 40 randomly selected outputs (10% sample, standard for this type of validation); all classifications agreed with analyst review |

> Results are representative of the specific engagement. Accuracy will vary based on report quality and prompt tuning for your domain.

## Stack

- Python 3.10+
- Anthropic Claude API (original run) -- also compatible with OpenAI API
- python-dotenv

## Lessons

The biggest prompt engineering challenge was distinguishing "probable cause" from "contributing factor". Early versions over-classified contributing factors as probable causes. Adding explicit definitions and examples to the prompt resolved this.

For very long reports (8-10 pages), sending the full text hurt both cost and consistency. The pipeline now condenses reports over ~12,000 characters to their cause-relevant sections (Conclusion, Findings, Probable Cause) with a preliminary LLM call before running the main extraction -- this triggers automatically based on report length, no manual flagging needed.
