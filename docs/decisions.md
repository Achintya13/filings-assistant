# Filings assistant — decisions and observations

As of 14 November 2026

## The project

A question-answering system over five public Lloyds Banking Group results announcements. You ask a question in plain English and it answers from the filings, with the document and page it used.

It was built to cover the ground named in an AI Engineer job specification: Python, RAG, prompt design for Anthropic models, evaluation, and later MCP, A2A and AWS.

The domain was chosen so that every part has a real reason to exist. Answers must come from the filings because a confident wrong number is unacceptable in finance. Evaluation matters because the usual failure is a believable answer, not an error message.

All source documents are public. No employer data, no synthetic client records.

Much of the code was written with an AI coding assistant (Claude). The answer key, the automated checks and the decisions recorded here are how that work is checked and owned.

## Where it stands

| Run | Marked by | Questions | Pass | Partial | Fail | What changed |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline (17 Oct) | Hand | 9 | 6 | 3 | 0 | First run |
| Period filtering (25 Oct) | Hand | 9 | 7 | 2 | 0 | Q4 improved |
| Automated run 1 (14 Nov) | Script | 10 | 6 | 3 | 1 | First run of the automated marker; Q10 added |
| Automated run 2 (14 Nov) | Script | 10 | 6 | 3 | 1 | Answer key trimmed; page and citation checks added |

The hand-marked and script-marked rows are not directly comparable. The script is stricter than the hand marking was, and it marks ten questions where the earlier runs had nine.

In the latest run, three questions fall short because the search did not find the right page (Q6, Q8, Q10). One falls short because the answer gave a reason the document does not state (Q4).

The system has refused the deliberately unanswerable question in every run, and no run has produced an invented figure. The automated checks did find two smaller slips, described below: an unsupported reason, and in one run a citation to a file name that does not exist.

## How retrieval works

Five documents are cut into 985 chunks of about 900 characters. Each chunk is sent to Voyage's `voyage-3.5` model, which returns 1,024 numbers that stand for its meaning. Those numbers are stored in `data/vectors.npy`. The text stays in `data/chunks.json`.

When a question arrives, it is turned into numbers the same way and compared with all 985 chunks. The five closest chunks have their text sent to Claude. The numbers never reach Claude. They only decide which five chunks to send.

### The search method

The search is exhaustive cosine similarity: every stored chunk is compared with the question, and nothing is skipped. All vectors are scaled to length 1 when loaded, so the comparison is a single line:

```python
scores = vectors @ query_vector
```

This takes about a millisecond for 985 chunks. The call to Voyage that comes before it takes about 200 milliseconds, so making the search faster would gain nothing.

| Consideration | At this size |
| --- | --- |
| Speed | About 1 ms |
| Accuracy | Exact: it cannot miss the closest chunk |
| Complexity | Four lines of NumPy, no index to build |
| Visibility | The raw scores are easy to inspect, which is how the score clustering problem was found |

The work grows in step with the number of chunks. At around a hundred thousand chunks it would be too slow, and an approximate index such as HNSW would replace it.

### Why not a vector database

A vector database solves problems this project does not yet have: speed at large scale, adding documents one at a time, and keeping the text and its numbers in one record.

That last point is a real weakness here. A chunk and its vector are linked only by position: row 47 of the array belongs to entry 47 of the JSON file. Re-cutting the documents without re-embedding them would return the wrong text with no error. A vector database prevents that. OpenSearch is the likely choice later, because it runs inside AWS and also does keyword search.

## Decisions

Each choice was made on purpose and has a cost. The cost is written down so it can be defended.

| Decision | Reasoning | Cost accepted |
| --- | --- | --- |
| Cut documents page by page | Page numbers stay exact, so every citation can be checked | A paragraph that crosses a page break is split in two |
| 900 characters, 150 overlap | Big enough for one complete idea, small enough to stay focused | Tables get split from their headers |
| Drop chunks under 100 characters | Cover pages and headers are never the answer | A short but useful line would be lost |
| Voyage API for embeddings | PyTorch, ChromaDB and LanceDB no longer install on Intel Macs | Limited to 3 requests a minute on the free tier |
| Exhaustive search, no index | One multiplication at this size, and exact | Would need replacing at around a hundred thousand chunks |
| NumPy arrays, not a vector database | Nothing to tune, and raw scores stay visible | Chunks and vectors are linked only by position |
| Text and vectors in separate files | Numbers stored as text would be a slow 20 MB file; the binary file is 4 MB | Two files to keep in step |
| Prompt tells the model to refuse | A figure for the wrong period is worse than no figure | Sometimes refuses when a partial answer would help |
| Search and answering in separate modules | Each can be tested alone, and a bad answer can be traced to one or the other | A little more wiring |
| A model reads the period from the question | Handles wording nobody planned for | One extra API call, and it can be wrong |
| Haiku for reading the period, Sonnet for answering and judging | The period is a short, simple task on every question; answering and judging need the stronger model | Two models to keep track of |
| Model output is checked before use | A model asked for JSON can return a bad value | A few lines of checking on every call |
| Period boosts the score; it does not exclude | A question about Q2 has no Q2 document, so the half-year report must stay reachable | A strong chunk from the wrong period can still appear |
| Wrong year is excluded outright | A 2026 document cannot answer a question about 2025 | Caused a regression on guidance questions, described below |
| Questions live in one markdown file | One copy to edit; the code reads it | The file must keep a fixed layout |
| Plain code checks beside the model judge | Whether the right page came back, and whether a cited file is real, are facts that need no judgement | Two more checks to maintain |
| Retrieval is checked by page, not just by document | A document-level check blamed the answer when the search had found the wrong page | Marks a miss when the answer was found on a page the key does not list |
| The judge marks strictly | In a bank, a confident wrong figure is the worst result, so a wrong period is a fail | Can mark down an answer a reader would accept |
| The run fails on any fail grade or invented citation | An automated build can then block a bad change | A single flaky grade can stop a run |

## Period filtering: what it bought and what it cost

The baseline showed the search losing track of time periods. File names already held the reporting period, so the fix used information that was already there.

**What was built.** The year and period are read from each file name and stored with every chunk, along with a list of the quarters that document can answer about. A Haiku call reads the period out of the question. Chunks from an exactly matching document get +0.10 on their score. Chunks from a document that covers the period get +0.05. The wrong year is excluded.

**The first attempt failed.** Filtering on the list of covered quarters changed nothing. The full-year report covers Q1 and has 321 chunks against the Q1 statement's 70, so it passed the filter and still won on volume. Boosting the exact match fixed it: the Q1 statement took the top three places.

**The win.** For Q4, pages 8 and 10 of the Q1 statement had never been retrieved in any run. They moved to places 2 and 3, and the answer gained the figures it had been missing.

**The regression.** Q8 asks how 2026 guidance changed through the year. The year filter read "2026" and excluded the 2025 full-year report, where that guidance was first given. The year in the question named the subject, not the document.

**The fix.** Three lines were added to the period-reading prompt: a question that tracks change across several reports gets no filter. Q8 stayed partial anyway. With the filter gone the 2025 chunk was reachable but still did not rank, which points to the real cause: too many passages look alike.

## Automated grading: what it is and what it found

Until November every run was marked by reading each answer. That took about twenty minutes a run and depended on the reader's care. The marking is now done by a script.

**How it works.** Four small files:

| File | Job |
| --- | --- |
| `eval_set.py` | Reads the questions, expected answers and source pages from `data/eval_questions.md` |
| `grade.py` | Sends the question, the expected answer and the system's answer to Claude, which returns pass, partial or fail with a reason |
| `checks.py` | Two plain checks with no AI: did the right document and page come back, and is every cited file one that was retrieved |
| `run_graded_evals.py` | Runs all ten questions, applies every check, writes a report, and compares with the previous run |

When a question falls short, the report names the cause. If the right page was not retrieved, the cause is the search. If the page was there and the answer is still poor, the cause is the answer.

**What the first automated run showed.** The score looked worse than the hand marking, but the system had not changed. The problems were in the marking:

- **The answer key asked for too much.** Q1 asks for one number. The system gave it. The expected answer also listed two more figures, so the judge marked it partial.
- **The judge was inconsistent.** Q2 left out an extra figure in the same way and was passed.
- **The retrieval check was too coarse.** For Q6 the right documents came back but the wrong pages. The check only looked at documents, so it blamed the answer.
- **One answer cited a file that does not exist.** Q10 cited `2025-lbg-ims.pdf`. The real file is `2025-lbg-q1-ims.pdf`. The judge did not notice. It was found by reading.
- **Q10's answer changed between runs.** In October it named a quarter. In November it retrieved different chunks and said the data was insufficient.

**What was changed.** The expected answers for Q1 and Q2 were cut back to what each question asks. The retrieval check now compares pages as well as documents. A citation check was added: every file an answer cites must be one of the five retrieved.

**What the second run showed.**

- Q1 moved to pass.
- Q6 was correctly blamed on the search: the key wanted page 6 and the search returned page 16.
- No answer cited a file that was not retrieved.
- **Q4 moved from pass to partial, and the judge was right.** The answer had the right pages and the right figures. It also said the charge rose because of "deterioration across Retail and Commercial Banking". The document does not say that. The stated reason is that a one-off release in early 2024 did not happen again. The system had filled a gap with a guess that sounds sensible.

The same sentence was in the answer during the first automated run, and the judge passed it then, crediting the answer with a point it had not made. An earlier manual review had passed it too.

**Known limits.**

- The judge can give a different grade to the same answer on a different run.
- The page check is strict. Three questions pass while showing a miss, because the answer was found on a page the key does not list (Q2, Q3) or because one document held both figures (Q7).
- Q10's expected answer was drafted from an earlier system output and has not yet been checked against the filings.
- The token count in the report covers the answering call only, not the period-reading call or the judge.

## Observations

**Most shortfalls come from the search, but not all.** In the latest run three of four come from the search not finding the right page. The fourth is the answer adding a reason the document does not give. Earlier versions of this document said every shortfall was a search problem. The automated marker showed that was too generous.

**Similarity scores barely separate.** The baseline CET1 question returned scores of 0.602, 0.602, 0.601, 0.601 and 0.601. Five reports from one company share most of their words and layout, so the search can hardly tell passages apart. This is why a +0.10 boost was decisive.

**The search loses time periods.** A question about Q1 2025 returned full-year figures. Dates, quarters and exact numbers are what this kind of search handles worst, and in financial filings they are what separates one passage from another.

**The search always returns something.** The unanswerable question got five chunks back at ordinary scores. No score threshold separates found from not found, so the refusal has to come from the prompt.

**Tables come out as loose numbers.** Page 3 of the Q1 statement produced rows like `Underlying net interest income 3,294 3,184 3 3,276 1`, with the column headers gone. Q6 is the result: the system reached the right quarter by reasoning from nine-month figures because it never read the quarterly table.

**Low scores are a warning.** "Which quarter was the most profitable?" retrieved at 0.364 to 0.371, far below every other question. The wording shares almost nothing with the documents. The same question also got a different answer on a different day.

**The marker needs marking too.** The first automated run found faults in the answer key and in the checks before it found anything new in the system. A marker is only trusted after its grades have been compared with careful hand grades.

**A second reader finds what the first missed.** The unsupported reason in Q4 survived two manual reviews and one automated run before it was caught.

## What to build next

1. **Stop the answer giving unstated reasons.** One rule in the answering prompt: give a cause only if the excerpt states it. This targets Q4.
2. **Steady the judge.** Have it tick off each expected point one by one, so the same answer gets the same grade every time.
3. **Tidy the answer key.** Add the extra pages for Q2 and Q3, drop the unneeded document for Q7, and check Q10 against the filings.
4. **Run the marker automatically.** A GitHub Actions workflow that runs the checks on every change.
5. **MCP server.** Offer search and calculation as tools the model chooses to use, then measure what that costs in time and tokens against always searching first.
6. **Keyword search alongside meaning search.** A keyword match on a figure such as "14.9" would pull the right chunk to the top. This targets Q8.
7. **Table handling.** Extract tables separately and keep headers with their numbers. This targets Q6.

Each change is one commit followed by a run of the marker, so its effect can be seen.

After that: an A2A compliance agent that reviews answers before they are returned, and deployment to AWS with Bedrock, Lambda and API Gateway.

## Stories to tell

The strongest material is the measurement, not the build. Each story below is short enough to tell in under a minute.

**The marker that caught what two readers missed.**
"My system answered a question about why a charge had risen. It had the right pages and the right numbers, and two manual reviews passed it. Then my automated marker flagged it. The answer said the rise was due to 'deterioration' in two divisions, and the document never says that. The model had filled a gap with a sensible-sounding guess. In a bank that is the mistake that matters, and I only found it because I had automated the marking."

**The test that was unfair to the pupil.**
"The first time I ran my automated marker, the score dropped. Nothing in the system had changed. One question asked for a single number, the system gave it, and it was marked down, because my own answer key listed two extra figures. I learned to check the marker against hand grades before trusting it, and to make each expected answer match exactly what the question asks."

**Right book, wrong page.**
"One check asked whether the right document had been retrieved. For one question it said yes and blamed the answer. When I looked, the search had found the right document but page 16 where the answer was on page 6. I tightened the check to compare pages, and the blame moved to the search, where it belonged. A coarse check had been pointing me at the wrong fix."

**The file that did not exist.**
"In one run an answer cited a file name that was not in my documents at all. The model judge did not notice. I added a check in plain code: every file an answer cites must be one that was retrieved. That needs no model, costs nothing and cannot be talked round. It is my example of where ordinary code is the better tool."

**The filter that changed nothing.**
"My search kept returning full-year figures for questions about a single quarter. My first fix filtered to documents covering that quarter, and nothing changed, because the annual report covers every quarter and is four times bigger. I switched to adding a small bonus for the exact matching document. The right pages went from never retrieved to second and third place."

**The fix that broke something else.**
"After that change I re-ran every question and found one had got worse. It asked how 2026 guidance changed through the year, and my year filter had excluded the 2025 report where that guidance was first given. The year in the question named the subject, not the document. I would not have found it without re-running the full set."

**Right answer, wrong evidence.**
"One question asked which quarter had the lowest return. The system got it right, but it never read the table with the quarterly figures. It worked it out from nine-month numbers. A correct answer does not prove the system worked, which is why every answer is saved with the pages it was given."

**The question with no answer.**
"I included a question about results that had not been published. The search still returned five passages at normal scores, most from the same quarter a year earlier. This kind of search always returns something. The refusal had to come from the prompt, and it has in every run."

**Choosing the simple search.**
"I compare the question against all 985 chunks directly, with no vector database. At that size it takes a millisecond and it is exact. It also kept the raw scores in front of me, which is how I saw that my top five results were scoring within 0.001 of each other. I know what I gave up: my text and my vectors are linked only by position, and a database would remove that risk."

**The laptop that could not run the tools.**
"Three libraries would not install because they no longer support Intel Macs. I moved that work to an API. It is closer to how the system would run in production anyway."

**Working with an AI coding assistant.**
"I built this with an AI coding assistant, and I treat its output as something to check. The expected answers come from the filings, each change is followed by a run of the marker, and the marker has caught mistakes in the system, in my answer key and in earlier manual reviews. That checking is the part I own."