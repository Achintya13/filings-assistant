# Filings assistant — decisions and observations

As of 17 October 2026

## The project

A retrieval-augmented question-answering system over five public Lloyds Banking Group results announcements, built to cover the technical ground named in an AI Engineer job specification: Python, RAG, prompt design for Anthropic models, evaluation, and later MCP, A2A and AWS.

The domain was chosen so that every component has a genuine reason to exist rather than being bolted on for the CV. Answers must be grounded in filings because a confident wrong number is unacceptable in finance; a second agent reviewing for compliance is a real second agent, not a function call; evaluation matters because the failure mode is a plausible answer rather than an error.

All source documents are public. No employer data, no synthetic client records.

## Decisions

Each choice below was made deliberately and carries a cost. The cost is stated so it can be defended rather than glossed over.

| Decision | Reasoning | Trade-off accepted |
| --- | --- | --- |
| Chunk page by page | Page numbers stay exact, so every citation is verifiable | A paragraph spanning a page break is cut in two and neither half is complete |
| 900 characters, 150 overlap | Large enough to hold one complete idea, small enough that the embedding is not a blur of several | Tables split from their headers at the boundary |
| Drop chunks under 100 characters | Cover pages and running headers are never the right answer but still occupy a retrieval slot | A genuinely short but meaningful line would be lost |
| Voyage API for embeddings, not local | PyTorch, ChromaDB and LanceDB have all dropped Intel macOS wheels; the laptop cannot run them | Rate-limited to 3 requests per minute on the free tier; a dependency on a second provider |
| NumPy cosine similarity, not a vector database | 985 vectors is one matrix multiplication, about a millisecond; writing it by hand means understanding what a vector store does | No approximate nearest-neighbour indexing, no persistence layer, no metadata filtering yet |
| Prompt instructs refusal | In finance, a figure for the wrong period is worse than no figure | Occasionally refuses when a partial answer would have been useful |
| Retrieval and generation in separate modules | Each can be tested and swapped independently; a wrong answer can be traced to one or the other | Slightly more plumbing than a single script |

The embedding decision is the one worth explaining at length. Three libraries failed to install for the same reason — the machine is x86 macOS and the ML ecosystem has moved to Apple Silicon and Linux. Rather than buying hardware, the fix was architectural: push the heavy compute to APIs and keep the laptop for orchestration. That is what production systems do anyway, and it brings the design closer to the AWS target than a local-everything version would have been.

## Baseline results

Six passes, three partials, zero failures and zero hallucinations across nine questions. Run on 17 October 2026 against claude-sonnet-4-6, voyage-3.5 embeddings, top_k of 5, over 985 chunks from five documents. Total cost 12,648 input tokens and 1,800 output tokens, roughly 6.5p.

The nine questions were written before the system was run, with expected answers and page references taken from the filings by hand. Writing them first matters: it removes the temptation to pick questions the system happens to pass.

| ID | Question type | Grade | Note |
| --- | --- | --- | --- |
| Q1 | Single fact, prose | Pass | 14.0%, cited correctly |
| Q2 | Single fact, prose | Pass | Up 6% to GBP 13,635m; added an unrequested divisional breakdown |
| Q3 | Single fact, prose | Pass | GBP 1,950m total provision |
| Q4 | Reasoning across a passage | Partial | Right figure, missing the mechanics on page 8 |
| Q5 | Reasoning across a passage | Pass | Dividend and buyback both correct |
| Q6 | Table lookup | Partial | Right answer, reached by inference rather than from the table |
| Q7 | Multi-document comparison | Pass | Separated reported from pro forma unprompted |
| Q8 | Multi-document comparison | Partial | Two of three guidance points; flagged the gap itself |
| Q9 | Unanswerable | Pass | Refused, and named which periods the documents cover |

The grading is deliberately strict. Q4, Q6 and Q8 all produced answers a reader would accept; they are marked partial because they omitted detail the expected answer contains, or arrived at the right conclusion without the evidence that should have supported it.

## Observations

**Every partial was a retrieval failure. None was a generation failure.** In Q4, Q6 and Q8 the chunk containing the answer never entered the top five. Claude read the context it was given correctly in all nine cases, and in Q4 and Q8 flagged its own gaps without being asked to. This is the single most useful finding: the prompt is working and the search is not.

**Similarity scores barely separate.** The CET1 query returned scores of 0.602, 0.602, 0.601, 0.601 and 0.601 — a spread of 0.001 across five chunks. Five quarterly reports from one issuer share vocabulary and structure, so all 985 vectors crowd into a narrow region of the space and semantic similarity stops discriminating. The chunk holding the correct figure ranked fourth.

**Embeddings lose period qualifiers.** A question about Q1 2025 impairment returned full-year 2025 figures. The embedding captured the topic and discarded the date. Dates, quarters and precise numbers are what embeddings handle worst, and in financial filings they are exactly what distinguishes one otherwise-identical passage from another.

**Retrieval has no empty state.** Q9 asked about results that do not exist in the corpus. Five chunks came back at 0.547 to 0.567 — the same range as answerable questions, four of them from Q3 2025. There is no score threshold that separates found from not-found, so refusal cannot be handled in retrieval. It has to come from the prompt.

**Tables extract as unlabelled number streams.** Page 3 of the Q1 statement produced column headers split across five lines, then rows like `Underlying net interest income 3,294 3,184 3 3,276 1`. The spatial grid that made it readable is gone. Q6 is the consequence: the system reached the right quarter by reasoning from nine-month figures rather than reading the quarterly table, which was never retrieved. Right answer, wrong evidence — and no signal would have distinguished that from a wrong answer.

## What to build next

The evidence points at retrieval, so that is what changes. Each item below addresses a specific observation above, and each is measured against the same nine questions.

1. **Metadata filtering by period.** Filenames already encode the quarter. Filtering to the relevant document before ranking would fix most of Q4 and Q8, where the right topic was found in the wrong period.
2. **Hybrid search.** Combining semantic similarity with keyword matching. Keywords nail "CET1" and "2025" precisely where embeddings blur them, and would separate the cluster of near-identical scores.
3. **Contextual retrieval.** Prepending a generated sentence of context to each chunk before embedding, so a chunk explains what it is. Addresses chunk isolation and helps with orphaned table rows.
4. **Table handling.** Extracting tables separately and converting to markdown before embedding, so headers stay attached to their numbers.

The order matters. Metadata filtering is cheapest and addresses the most failures; table handling is the most work for the narrowest gain. Each change is a separate commit with a re-run of the evaluation, so the effect of each is attributable.

After retrieval improves, the phases already planned are: automated grading in CI, an MCP server exposing search and calculation as tools, an A2A compliance agent reviewing answers before they return, and deployment to AWS using Bedrock, Lambda and API Gateway.

## Talking points

The strongest material is the measurement, not the build. Almost every candidate can describe what RAG is; far fewer can say what their own system gets wrong and why.

**On evaluation.** "I wrote nine questions with expected answers before running the system, graded the output by hand, and recorded which chunks were retrieved alongside each answer. Six passed, three were partial. Every partial traced to retrieval rather than generation — the model read what it was given correctly in all nine cases."

**On knowing the limits.** "My scores cluster between 0.60 and 0.61 because five quarterly reports from one issuer share almost all their vocabulary. Semantic similarity stops discriminating on a homogeneous corpus. That is why hybrid search is my next change rather than a better prompt."

**On hallucination.** "I included an unanswerable question deliberately. Retrieval returned five chunks from the wrong year at perfectly normal scores, because semantic search has no empty state. The refusal has to come from the prompt, and it did."

**On a near-miss worth noticing.** "One question got the right answer from the wrong evidence — it inferred the weakest quarter from nine-month figures because the quarterly table was never retrieved. That taught me that a correct answer is not proof the pipeline worked, which is why I log retrieved chunks alongside every answer."

**On the platform problem.** "Three embedding libraries wouldn't install because the ecosystem has dropped Intel macOS support. I moved embeddings to an API rather than buying hardware, which is closer to how it would run in production anyway."
