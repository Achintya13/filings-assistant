# Filings assistant — decisions and observations

As of 25 October 2026

## The project

A retrieval-augmented question-answering system over five public Lloyds Banking Group results announcements, built to cover the technical ground named in an AI Engineer job specification: Python, RAG, prompt design for Anthropic models, evaluation, and later MCP, A2A and AWS.

The domain was chosen so that every component has a genuine reason to exist rather than being bolted on for the CV. Answers must be grounded in filings because a confident wrong number is unacceptable in finance; a second agent reviewing for compliance is a real second agent, not a function call; evaluation matters because the failure mode is a plausible answer rather than an error.

All source documents are public. No employer data, no synthetic client records.

## Where it stands

| Run | Pass | Partial | Fail | Change |
| --- | --- | --- | --- | --- |
| Baseline (17 Oct) | 6 | 3 | 0 | — |
| Period filtering (25 Oct) | 7 | 2 | 0 | Q4 fixed |

Zero hallucinations in both runs, including on the deliberately unanswerable question.

## Decisions

Each choice below was made deliberately and carries a cost. The cost is stated so it can be defended rather than glossed over.

| Decision | Reasoning | Trade-off accepted |
| --- | --- | --- |
| Chunk page by page | Page numbers stay exact, so every citation is verifiable | A paragraph spanning a page break is cut in two and neither half is complete |
| 900 characters, 150 overlap | Large enough to hold one complete idea, small enough that the embedding is not a blur of several | Tables split from their headers at the boundary |
| Drop chunks under 100 characters | Cover pages and running headers are never the right answer but still occupy a retrieval slot | A genuinely short but meaningful line would be lost |
| Voyage API for embeddings, not local | PyTorch, ChromaDB and LanceDB have all dropped Intel macOS wheels; the laptop cannot run them | Rate-limited to 3 requests per minute on the free tier; a dependency on a second provider |
| NumPy cosine similarity, not a vector database | 985 vectors is one matrix multiplication, about a millisecond; writing it by hand means understanding what a vector store does | No approximate nearest-neighbour indexing and no persistence layer |
| Prompt instructs refusal | In finance, a figure for the wrong period is worse than no figure | Occasionally refuses when a partial answer would have been useful |
| Retrieval and generation in separate modules | Each can be tested and swapped independently; a wrong answer can be traced to one or the other | Slightly more plumbing than a single script |
| Period extracted by a model, not a regex | Handles phrasings not anticipated in advance, and degrades to no filter rather than a wrong one | One extra API call per query, and the extraction itself can be wrong |
| Period is a score boost, not a hard filter | A question about Q2 has no Q2 document to find, so the half-year report must stay reachable | A strongly matching chunk from the wrong period can still surface |
| Year is a hard filter, period is not | A 2026 document cannot answer a question about 2025, so there is no softness to be had | Caused a regression on guidance questions — see below |

## Period filtering: what it bought and what it cost

The baseline showed every partial was a retrieval failure, and that embeddings were losing period qualifiers. Filenames already encoded the reporting period, so the fix was to use metadata that already existed.

**What was built.** Year and period parsed from each filename into chunk metadata, with a `covers` list recording which quarters each document can answer about — a full-year report covers all four. A Haiku call reads the period out of the question and returns structured JSON, validated against an allowed set before use. Chunks from an exactly matching document get +0.10; chunks from a document that merely covers the period get +0.05. The wrong year is excluded outright.

**First attempt failed.** Filtering strictly on the `covers` list changed nothing, because the full-year report covers Q1 and has 321 chunks against the Q1 statement's 70. It passed the filter and still dominated on volume. Boosting instead of filtering fixed it: the Q1 statement took the top three positions.

**The win.** Q4 went from partial to pass. Pages 8 and 10 of the Q1 statement — which had never been retrieved in any run — moved to positions 2 and 3, and the answer gained every figure in the expected answer except one.

**The regression.** Q8 asks how 2026 guidance changed through the year. The hard year filter read "2026" and excluded the 2025 full-year report, which is where the original guidance was issued. The year in the question named the subject, not the document.

**The fix.** Three lines added to the extraction prompt, teaching it that a question tracking change across several reports should return no filter. The discrimination is subtle and the model handled it: a question comparing end-2025 with end-Q1-2026 still filters to Q1 2026, because one document carries both figures, while a question about guidance changing through the year does not.

Q8 remained partial anyway. Removing the filter made the 2025 chunk reachable but it still did not rank, which identifies the real cause: not period filtering but score clustering. The chunk needed is one of many passages about net interest income, and nothing lexical distinguishes it.

## Observations

**Every partial was a retrieval failure. None was a generation failure.** Claude read the context it was given correctly in every case across both runs, and flagged its own gaps unprompted where the evidence was incomplete. The prompt works; the search is the constraint.

**Similarity scores barely separate.** The baseline CET1 query returned 0.602, 0.602, 0.601, 0.601, 0.601 — a spread of 0.001 across five chunks. Five quarterly reports from one issuer share vocabulary and structure, so the vectors crowd into a narrow region and similarity stops discriminating. This is why a +0.10 boost was decisive: it is nine times larger than the natural spread between chunks.

**Embeddings lose period qualifiers.** A question about Q1 2025 impairment returned full-year figures. Dates, quarters and precise numbers are what embeddings handle worst, and in financial filings they are exactly what distinguishes otherwise-identical passages.

**Retrieval has no empty state.** The unanswerable question returned five chunks at 0.547 to 0.567 — the same range as answerable ones. No score threshold separates found from not-found, so refusal has to come from the prompt.

**Tables extract as unlabelled number streams.** Page 3 of the Q1 statement produced headers split across five lines, then rows like `Underlying net interest income 3,294 3,184 3 3,276 1`. Q6 is the consequence: the system reached the right quarter by reasoning from nine-month figures rather than reading the quarterly table. Right answer, wrong evidence — and nothing would have distinguished that from a wrong answer.

**Low scores are themselves a signal.** A later question — which quarter was most profitable — retrieved at 0.364 to 0.371, far below the 0.50 to 0.78 of every other question. The phrasing shares almost no vocabulary with the documents, which never say "most profitable quarter". That gap between question language and document language is visible in the score before the answer is read.

## What to build next

Both remaining partials now have a diagnosis, and neither is a period problem.

1. **Hybrid search.** BM25 keyword scoring combined with cosine similarity. A keyword match on a specific figure would pull the guidance chunk straight to the top where semantic similarity cannot. This targets Q8 directly and addresses the score-clustering problem generally.
2. **Table handling.** Extracting tables separately and converting them to markdown before embedding, so headers stay attached to their numbers. This is what Q6 needs.
3. **Contextual retrieval.** Prepending a generated sentence of context to each chunk before embedding, so a chunk explains what it is.
4. **Automated grading.** Parsing the question set, scoring retrieval and answers automatically, running in CI so a change that drops the score fails the build.

Each change is a separate commit with a re-run of the evaluation, so the effect of each is attributable.

After retrieval, the planned phases are an MCP server exposing search and calculation as tools, an A2A compliance agent reviewing answers before they return, and deployment to AWS using Bedrock, Lambda and API Gateway.

## Talking points

The strongest material is the measurement, not the build. Almost every candidate can describe what RAG is; far fewer can say what their own system gets wrong and why.

**On evaluation.** "I wrote the questions with expected answers before running the system, graded by hand, and logged which chunks were retrieved alongside each answer. Six of nine passed at baseline, seven after the first improvement. Every failure traced to retrieval rather than generation."

**On measuring a change properly.** "Period filtering took me from six to seven. It also caused a regression I would not have found without the full set re-run: a question about 2026 guidance excluded the 2025 document where that guidance was first issued, because the year in the question named the subject, not the source."

**On a first attempt that did not work.** "My first version filtered strictly on which periods a document covers. It changed nothing, because the annual report covers every quarter and has four times the chunks. Boosting the exact match instead of excluding the rest fixed it, and it degrades more gracefully when the period is guessed wrongly."

**On knowing the limits.** "My scores cluster within 0.001 of each other because five quarterly reports from one issuer share almost all their vocabulary. Semantic similarity stops discriminating on a homogeneous corpus. That is why hybrid search is next rather than a better prompt."

**On hallucination.** "I included an unanswerable question deliberately. Retrieval returned five chunks from the wrong year at perfectly normal scores, because semantic search has no empty state. The refusal has to come from the prompt, and it did in both runs."

**On a near-miss worth noticing.** "One question got the right answer from the wrong evidence — it inferred the weakest quarter from nine-month figures because the quarterly table was never retrieved. A correct answer is not proof the pipeline worked, which is why I log retrieved chunks alongside every answer."

**On the platform problem.** "Three embedding libraries wouldn't install because the ecosystem has dropped Intel macOS support. I moved embeddings to an API rather than buying hardware, which is closer to how it would run in production anyway."
