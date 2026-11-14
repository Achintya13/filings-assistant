# Interview prep — stories to tell

Private notes. Not for GitHub.

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