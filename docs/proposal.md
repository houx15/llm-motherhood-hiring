# The Invisible Gatekeeper: Auditing LLMs for Motherhood Penalties in Hiring

Oct 14, 2026 · @Evie Hou

## Summary

This study audits whether widely used large language models (LLMs) reproduce the motherhood penalty and fatherhood bonus when they screen job applicants and when they advise job seekers. Employers increasingly use LLMs to score and rank résumés, and job seekers increasingly ask them for career advice. Neither side can see the counterfactual: what the model would have said had the same résumé carried a different gender or family status.

We run a series of controlled correspondence experiments on otherwise identical résumés, varying applicant gender, marital and parental status, occupation, and job-description wording. We measure model outputs on both sides of the market: as gatekeeper (scores, pairwise choices, rankings, recommended salary) and as advisor (career recommendations, résumé edits, salary targets).

The design links the audit to sociological theory. Occupations are sampled by female share, wage, and time demands, so we can test whether penalties concentrate in Goldin's "greedy jobs." Job-description manipulations then make greediness and family-friendly policy experimental. A replication arm of Correll, Benard & Paik (2007) provides a human benchmark for whether LLMs mirror, reduce, or amplify human bias.

The full program (about 65,000 calls per model) costs roughly $21–$33 on DeepSeek V4.1 Flash and $204 on GPT-5.4 Mini before pilots and reruns.

## Motivation

LLMs are becoming an invisible actor in the labor market, entering from both ends at once. Recruiters paste résumés into chatbots or use LLM-based screening tools to score and shortlist candidates. Job seekers ask the same models which jobs to apply for, how to rewrite their résumés, and what salary to request.

The object of study is the model itself, not the model as a proxy for human recruiters. The question is what preferences these deployed systems carry, and in which situations they impose them on real people. Three features make this consequential:

- **Invisibility.** A mother told to "consider roles with more flexibility" experiences this as considerate personalization. She never sees that the same résumé under a man's name would have received different advice. Bias that is invisible at the individual level can only be revealed by systematic audit.
- **Scale and monoculture.** One biased recruiter affects one firm. One model used by thousands of firms produces correlated decisions across the market.
- **Legitimacy.** Model output looks neutral, which makes discriminatory patterns harder to contest.

The human benchmark therefore plays a different role here than in most LLM-bias studies. It is not a validity check for generalizing to humans; it is the counterfactual status quo. It lets us ask whether introducing LLMs into hiring and career guidance makes outcomes for mothers better or worse than before.

## Theoretical framework

The study draws on five strands of theory. Together they predict *where* an LLM's family-status bias should be strongest and *what form* it should take.

**1. The motherhood penalty as status-based discrimination.** Mothers earn less than childless women, and survey controls for productivity explain only part of the gap. [Correll, Benard & Paik (2007)](https://swap.stanford.edu/was/20140911222256mp_/http://gender.stanford.edu/sites/default/files/motherhoodpenalty.pdf) showed experimentally that evaluators rate equally qualified mothers as less competent and less committed, recommend lower salaries, and are less likely to hire them. Fathers are not penalized and sometimes benefit. An audit with real employers found the same pattern. Their explanation: cultural schemas of the devoted mother conflict with schemas of the ideal worker, while fatherhood does not.

**2. Statistical versus normative discrimination.** Statistical discrimination uses group membership as a proxy for unobserved productivity, so it should disappear once direct evidence of commitment is provided. Benard & Correll (2010) found that highly committed mothers were still penalized, now for being less warm and likable. This is normative discrimination: the penalty enforces a prescriptive norm about how mothers should behave. Our design includes a high-commitment condition to distinguish the two in LLM behavior.

**3. The ideal worker norm.** Acker (1990) and Williams (2000) describe organizations as built around an unencumbered worker with no caregiving obligations. Penalties should therefore depend on how strongly a job or organization signals this norm, not on gender alone.

**4. Greedy jobs.** Goldin (2014; 2021) argues that the remaining gender pay gap is concentrated in occupations that disproportionately reward long, inflexible, always-available hours. Parents, overwhelmingly mothers, sort out of these roles or are penalized within them. This yields a testable moderation hypothesis: family-status penalties should be largest in high-time-demand, low-flexibility occupations and in job descriptions that signal greediness.

**5. Algorithmic monoculture and automation bias.** Kleinberg & Raghavan (2021) show that when many decision-makers rely on the same algorithm, errors become correlated and welfare can fall even if each decision-maker's accuracy rises. Applied here, a single model's family-status bias becomes a market-wide pattern rather than idiosyncratic noise.

**Integrating claim.** We expect LLMs to show *surface fairness, deep bias*. Alignment may suppress overt penalties in direct decisions such as scoring. The same schemas may persist in advice and reasoning: steering mothers toward flexible, lower-paid roles, or penalizing caregiving signals such as leave gaps. If so, LLMs shift gender inequality from overt discrimination to personalized steering, which is harder to see and contest.

## Previous studies on LLMs and résumés

Name-swap résumé scoring is a saturated design; family status, occupational moderation, job-description context, and the advisor role remain thin. Most studies adapt the Bertrand & Mullainathan (2004) correspondence design to LLMs, and their findings on gender point in opposite directions depending on the task.

| Study | Role of LLM | Design | Gender finding | Family status |
| --- | --- | --- | --- | --- |
| [Born, Curhan & Bowles (2026)](https://arxiv.org/abs/2610.14036) | Advisor | Negotiation advice, 4 models, female vs male personas | Lower salary targets for women; agendas steer women to flexibility and caregiving, men to pay and advancement | Not varied |
| [Rozado (2025)](https://arxiv.org/abs/2505.17049v2) | Gatekeeper, pairwise | 22 models, 70 professions, gender-swapped CV pairs | All models favored female-named candidates; strong first-position bias | Not varied |
| [An et al. (2025), PNAS Nexus](https://pmc.ncbi.nlm.nih.gov/articles/PMC11937954/) | Gatekeeper, scoring | \~361,000 randomized résumés, 5 models | Higher scores for women; lower for Black men | Not varied |
| [Chaturvedi & Chaturvedi (2025)](https://arxiv.org/abs/2504.21400) | Gatekeeper, callback | 332,044 real Indian job ads, open models | Most models favor men, especially in higher-wage jobs; reproduce occupational segregation | Not varied |
| [Bloomberg (Yin et al. 2024)](https://prod.cm.bloomberg.com/graphics/2024-openai-gpt-hiring-racial-discrimination/) | Gatekeeper, ranking | 8 résumés ranked 1,000 times, 4 jobs | Direction varies by job; women favored for HR roles | Not varied |
| [Armstrong et al. (2024)](https://arxiv.org/abs/2405.04412v3) | Gatekeeper and generator | 32 names, 10 occupations; GPT also writes résumés | Modest score gaps; generated résumés give women less experience | Not varied |
| [Wilson & Caliskan (2024)](https://arxiv.org/html/2407.20371v1) | Retrieval ranking | 500+ real résumés and job descriptions, embedding models | Male and White names favored; results sensitive to résumé length and name frequency | Not varied |
| [Veldanda et al. (2023)](https://arxiv.org/abs/2310.05135) | Gatekeeper, classification | 334 résumés, 3 job categories, 4 models | Little gender or race bias | Pregnancy and parental-leave gaps penalized |
| Frermann et al. (2023), Univ. of Melbourne | Gatekeeper, ranking | ChatGPT, gender × parental-leave gap | No gender difference | Parents with leave gaps ranked lower regardless of gender |
| [Iso et al. (2025)](https://aclanthology.org/2025.naacl-industry.55/) | Gatekeeper, matching | Gender, race, education | Explicit-attribute bias reduced in newer models | Not varied; education bias persists |
| [Sorokovikova et al. (2025)](https://arxiv.org/html/2506.10491v1) | Advisor | Salary negotiation, 5 models | Lower salary advice for female personas | Not varied |
| [Geiger et al. (2024)](https://arxiv.org/abs/2409.15567v3) | Advisor | 98,800 prompts per model, 4 ChatGPT versions | Significant but smaller gender gaps than university or major | Not varied |

**Gaps this study addresses.**

1. **Family status is the least studied attribute.** Only two audits vary it, with one crude cue each (a pregnancy sentence or a leave gap). Their results conflict: one finds a parenthood penalty for both genders, the other a mother-specific penalty. No study compares cue types or tests a fatherhood bonus.
2. **No occupational moderation.** Studies cover many occupations but treat them as fixed effects, not as a theoretically meaningful moderator such as female share or time demands.
3. **Context is ignored.** No study manipulates job-description wording or organizational policy, though Correll herself proposed a family-friendly-employer condition.
4. **Gatekeeper and advisor are studied separately.** The opposite gender findings (pro-female scoring, anti-female salary advice) have never been tested within one design on the same résumés.
5. **Ranking rarely varies anything but names.** Pool-composition effects, such as one mother among childless candidates, are untested.
6. **No human benchmark.** Few studies compare model penalties with established human estimates.

**Methodological lessons carried forward.** Use validated names and multiple names per cell (Wilson & Caliskan show name frequency can flip results). Counterbalance position in every comparative task (Rozado). Record model versions and dates, because bias direction changes across versions (Geiger et al.).

## Research questions and hypotheses

**RQ1.** Do LLMs acting as gatekeepers penalize mothers and reward fathers relative to childless applicants with identical qualifications?

**RQ2.** Does the penalty vary across occupations, and is the variation explained by occupational female share, wages, or time demands?

**RQ3.** Does job-description wording, such as signaling long hours or a family-friendly policy, change or reverse the penalty?

**RQ4.** When the same résumés are presented by job seekers asking for advice, do LLMs steer mothers and fathers differently?

**RQ5.** How do LLM penalties compare with human evaluators in the Correll et al. (2007) benchmark: do models mirror, reduce, or amplify them?

| Hypothesis | Prediction | Tested in |
| --- | --- | --- |
| H1 Motherhood penalty | Mothers receive lower scores, salary, and commitment ratings than childless women | E1, E2 |
| H2 Fatherhood bonus | Fathers receive equal or higher evaluations than childless men | E1, E2 |
| H3 Greedy-job moderation | The motherhood penalty grows with occupational time demands, net of female share | E1, E4 |
| H4 Gender-typing moderation | The penalty is larger in male-dominated occupations; in female-dominated ones, men or fathers may be penalized | E1 |
| H5 Caregiving cue | A parental-leave gap is penalized more than a parent cue alone, and for fathers as well as mothers | E1, E2 |
| H6 Normative discrimination | Penalties persist for highly committed mothers, with rationales shifting from commitment to warmth or fit | E2 |
| H7 Organizational context | A substantive family-friendly policy reduces the penalty; boilerplate EEO language does not; greedy wording increases it | E4 |
| H8 Surface fairness, deep bias | Penalties are smaller in direct scoring than in advice, where mothers are steered toward lower-paid, more flexible, more female-typed roles | E1 vs E5 |

## Data

All inputs are public or constructed; no human-subjects data is collected in the core study.

**Occupations (20).** Sampled on a 3 × 2 grid of gender composition (male-dominated, mixed, female-dominated) × wage (low, high), with 3–4 occupations per cell. Each carries continuous moderators:

| Moderator | Source |
| --- | --- |
| Female share of employment | BLS Current Population Survey, employed persons by detailed occupation and sex |
| Median annual wage | BLS Occupational Employment and Wage Statistics |
| Time demands and flexibility | O\*NET Work Context: duration of typical work week, work schedules, time pressure, travel |
| Task content for résumé grounding | O\*NET tasks and skills by SOC code |

Illustrative cells: software engineer and financial analyst (male, high wage); truck driver and warehouse supervisor (male, low wage); lawyer and marketing manager (mixed, high); retail manager (mixed, low); registered nurse and HR manager (female, high); administrative assistant and preschool teacher (female, low).

**Base résumés (80).** Four per occupation. Sources: anonymized real résumés from the public Kaggle résumé dataset used by Veldanda et al. (2023), supplemented by O\*NET-grounded synthetic résumés where coverage is thin. All personal details are stripped. Within each occupation, résumés are pretested for equal quality by having three models score anonymized versions; résumés outside one standard deviation are replaced.

**Names.** Three first names per gender, drawn from validated name-perception data (e.g., Gaddis 2017) or the [Bloomberg name lists](https://github.com/BloombergGraphics/2024-openai-gpt-hiring-racial-discrimination), chosen to be strongly gendered but racially ambiguous or White-coded and matched on frequency. Race is held constant in the core design; a race extension is optional.

**Family-status cues.** Following Correll et al. (2007), the parent cue is a résumé line (e.g., "PTA Coordinator, Lincoln Elementary") plus, in a cover note, "married with two children." Leave gaps use a dated résumé entry ("Parental leave, 2024"). Wording is identical across genders.

**Job descriptions.** One base job description per occupation, assembled from O\*NET tasks and real postings, plus experimental variants (see E4).

**Real-usage prompts.** We sample hiring and career-advice conversations from public chat logs (WildChat, LMSYS-Chat-1M) to model the wording of recruiter and job-seeker prompts. This step also yields a descriptive estimate of how often users disclose family status unprompted.

**Human benchmark.** Effect sizes from Correll et al. (2007) for competence, commitment, recommended salary, and hiring. We will request the original materials from the authors; if unavailable, we reconstruct them from the published methods.

## Experimental design

Five experiments share one résumé pool and one set of manipulations. E1–E4 put the model in the recruiter's seat; E5 puts it in the job seeker's. Each base résumé is rotated through every condition, so résumé quality is absorbed by fixed effects.

**Core factors**

| Factor | Levels |
| --- | --- |
| Gender | Female, male (signaled by first name; pronoun and explicit-field cues as robustness checks) |
| Family status | (1) not mentioned; (2) married, no children; (3) married with children (PTA cue); (4) children + parental-leave gap; (5) children + high-commitment signals (top-performer award, led overtime project); (6) pregnancy disclosure, women only |
| Occupation | 20, varying in female share, wage, and time demands |
| Job description | Base; greedy; family-friendly policy; greedy + family-friendly; EEO boilerplate only |
| Model | See Models and cost |

**The five experiments**

| Experiment | LLM role | Task | Design | Calls per model |
| --- | --- | --- | --- | --- |
| E1 Independent scoring | Gatekeeper | Score one résumé against a job description | 20 occupations × 4 résumés × 11 gender–family cells × 3 names × 5 samples | 13,200 |
| E2 Paired comparison (Correll replication) | Gatekeeper | Choose between two same-gender candidates; rate both | 20 occupations × 2 résumé pairs × 2 role assignments × 2 positions × 2 genders × 3 contrasts (childless vs parent, vs parent + leave gap, vs high-commitment parent) × 3 name pairs × 5 samples | 14,400 |
| E3 Ranking pools | Gatekeeper | Rank a pool of six résumés | 20 occupations × 4 pool compositions × 4 résumé draws × 6 position rotations × 3 samples | 5,760 |
| E4 Job-description context | Gatekeeper | E1 scoring under JD variants | 8 occupations × 4 résumés × 2 genders × 3 family states × 3 names × 5 JD variants × 5 samples | 14,400 |
| E5 Career advice | Advisor | First-person request for career plan, résumé edits, or salary target | 20 occupations × 4 résumés × 2 genders × 4 family states × 3 names × 3 request types × 3 samples | 17,280 |
| **Total** |  |  |  | **65,040** |

**E1 – Independent scoring.** The baseline audit. The model receives a job description and one résumé and returns structured ratings. This estimates the main motherhood and fatherhood effects and their variation across occupations (H1–H5).

**E2 – Paired comparison.** A direct replication of the Correll et al. (2007) laboratory design: two equally qualified, same-gender candidates differing only in parental status. Résumé roles and screen position are fully counterbalanced. The high-commitment contrast separates statistical from normative discrimination (H6).

**E3 – Ranking pools.** Mirrors how recruiters shortlist. Compositions: one mother among five childless candidates; one father among five childless; three parents and three childless, mixed gender; and an all-parent pool. Outcomes are top-1 and top-3 selection rates. This tests token and pool-composition effects that single-résumé scoring cannot detect.

**E4 – Job-description context.** Holding the job constant, we vary only the organizational signal. *Greedy* adds "fast-paced, frequent after-hours availability and travel." *Family-friendly* adds "16 weeks paid parental leave, flexible hours, remote options." *EEO boilerplate* adds only the standard equal-opportunity sentence. The eight occupations are those with the highest and lowest time demands. This makes greediness experimental rather than inferred across occupations (H3, H7).

**E5 – Career advice.** The same résumés, now pasted by the job seeker with one of three requests: "What roles should I target next?", "How should I improve this résumé?", or "What salary should I ask for?" Family status is disclosed by the user in the message ("I have two young kids"), mirroring how people actually write. Comparing E5 with E1 on identical résumés tests H8.

**Prompting protocol.** Default temperature and system prompt, to match consumer use. Each prompt template has three paraphrases derived from real-usage logs. Gatekeeper tasks request JSON output with a short rationale. All calls log model slug, provider, date, and full response. The protocol is preregistered on OSF before data collection.

## Measures and analysis plan

**Outcome measures**

| Level | Measure | Experiments |
| --- | --- | --- |
| Decision | Overall fit (1–10), interview yes/no, recommended starting salary (USD) | E1, E2, E4 |
| Mechanism | Perceived competence, commitment, promotability, likability (1–7, as in Correll et al.) | E1, E2, E4 |
| Selection | Chosen candidate (E2); rank, top-1 and top-3 inclusion (E3) | E2, E3 |
| Advice: jobs | Recommended occupations, coded to SOC, then linked to female share and median wage | E5 |
| Advice: salary | Recommended salary target (USD) | E5 |
| Advice: content | Suggests flexible or part-time work; suggests hiding or explaining family status; suggests lowering seniority | E5 |
| Language | Agentic vs communal wording (LIWC and embedding-based scores) in rationales and advice | All |

Open-text outcomes are coded by an LLM coder (a different model from the one evaluated) using a fixed codebook. Two human coders label a stratified 5% sample; we report Cohen's κ and recode categories below 0.7.

**Core model.** For outcome Y of résumé r, name n, occupation o, model m:

```latex
Y_{rnom} = \beta_1 F + \beta_2 P + \beta_3 (F \times P) + \beta_4 (P \times Z_o) + \beta_5 (F \times P \times Z_o) + \alpha_r + \gamma_n + \delta_m + \varepsilon_{rnom}
```

Here F indicates a female applicant, P a family-status condition, and Z the occupation's female share, wage, or time demands (standardized). β2 is the fatherhood effect and β2 + β3 the motherhood effect. β5 tests whether the gender gap in the parent effect varies with occupational characteristics (H3, H4). Standard errors are clustered by base résumé. Models are estimated pooled and separately per LLM.

**Experiment-specific analyses.**

- **E2:** conditional logit for candidate choice; paired differences for ratings and salary, directly comparable with Correll et al.
- **E3:** rank-ordered logit; selection rate ratios against the four-fifths rule used in US adverse-impact analysis.
- **E4:** JD variant × gender × family status interactions within occupation, with occupation fixed effects.
- **E5:** gender × family differences in the female share and median wage of recommended occupations; logit models for advice categories.
- **H8:** standardized penalties compared across E1 and E5 on the same résumés.

**Benchmarks.** Per-occupation LLM penalties are correlated with occupational female share and with published occupation-level motherhood wage penalties. Pooled E2 effects are compared with Correll et al. (2007) using standardized effect sizes, classifying each model as mirroring, reducing, or amplifying the human pattern.

**Power.** With 20 occupations × 4 résumés × 3 names × 5 samples per cell, E1 yields 1,200 observations per gender–family cell per model. Ignoring clustering, this detects a 0.15 SD difference between two cells at α = 0.05 with power of about 0.95 (0.1 SD at about 0.7). Pooling family-status levels or models raises power for the main effects; occupation-level interactions rely on the 20-occupation gradient. A pilot (two occupations, all conditions, two models) will estimate within-cell variance before the full run.

## Models and estimated cost

Running all five experiments costs about $21–$33 per model on DeepSeek V4.1 Flash and about $204 on GPT-5.4 Mini, the current GPT mini tier. Prices are OpenRouter list prices per million tokens as of 14 Oct 2026; DeepSeek's price is its off-peak first-party rate (peak hours double it).

**Token assumptions per call** (input / output): E1 1,300 / 300 · E2 2,100 / 350 · E3 4,850 / 200 · E4 1,350 / 300 · E5 1,000 / 700. Inputs include the job description, one to six résumés, and instructions; outputs include JSON ratings with a short rationale, or free-text advice in E5. Totals: 65,040 calls, 112 M input and 27 M output tokens per model.

| Model (OpenRouter slug) | Price in / out ($ per 1M) | E1 | E2 | E3 | E4 | E5 | Total | Total + 20% pilot and reruns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash) (deepseek/deepseek-v4.1-flash) | 0.15 / 0.60 | $4.95 | $7.56 | $4.88 | $5.51 | $9.85 | **$32.75** | $39.30 |
| [DeepSeek V4.1 Flash, batch](https://openrouter.ai/deepseek/deepseek-v4.1-flash:batch) | 0.112 / 0.336 | $3.25 | $5.08 | $3.52 | $3.63 | $6.00 | **$21.48** | $25.77 |
| [GPT-5.4 Mini](https://openrouter.ai/openai/gpt-5.4-mini) (openai/gpt-5.4-mini) | 0.75 / 4.50 | $30.69 | $45.36 | $26.14 | $34.02 | $67.39 | **$203.60** | $244.32 |
| [GPT-5 Mini](https://openrouter.ai/openai/gpt-5-mini) (openai/gpt-5-mini) | 0.25 / 2.00 | $12.21 | $17.64 | $9.29 | $13.50 | $28.51 | **$81.15** | $97.38 |
| [Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) (google/gemini-3.8-flash) | 0.75 / 3.75 | $27.72 | $41.58 | $25.27 | $30.78 | $58.32 | **$183.67** | $220.41 |
| [Gemini 3.8 Flash, batch](https://openrouter.ai/google/gemini-3.8-flash:batch) | 0.375 / 1.875 | $13.86 | $20.79 | $12.64 | $15.39 | $29.16 | **$91.84** | $110.20 |
| [Claude Haiku 5.5](https://openrouter.ai/anthropic/claude-haiku-5.5) (anthropic/claude-haiku-5.5) | 0.10 / 0.50 | $3.70 | $5.54 | $3.37 | $4.10 | $7.78 | **$24.49** | $29.39 |
| [Qwen3.8 Flash](https://openrouter.ai/qwen/qwen3.8-flash) (qwen/qwen3.8-flash) | 0.15 / 0.47 | $4.44 | $6.90 | $4.73 | $4.95 | $8.28 | **$29.30** | $35.15 |

**Recommended model set.** DeepSeek V4.1 Flash and GPT-5.4 Mini as the two core models (one Chinese open-weight, one US proprietary), plus Claude Haiku 5.5, Gemini 3.8 Flash, and Qwen3.8 Flash for breadth. All five cost about $474 at list price, or about $570 with the 20% buffer. Using batch endpoints for DeepSeek, Gemini, and Claude Haiku (half price, about $12 for Haiku) cuts the list total to roughly $360.

**Additional costs and caveats.**

- **Reasoning tokens.** If a model's hidden reasoning is left on, each call adds output tokens. At 1,000 reasoning tokens per call, costs roughly double: DeepSeek V4.1 Flash rises to about $72 and GPT-5.4 Mini to about $496. We will fix reasoning effort to the lowest setting that matches consumer defaults and log reasoning-token counts.
- **Coding open-text outputs.** Coding E5 responses with GPT-5.4 Mini as the coder costs about $27 per evaluated model (1,200 input / 150 output tokens per response).
- **Price volatility.** Several listed prices changed within the past quarter, and OpenRouter adds a fee on credit purchases. We will re-quote prices at launch and record the price paid per call.
- **Alias drift.** Slugs such as gpt-mini-latest silently redirect to newer models. We will call dated, pinned slugs only.

## Timeline, risks, and contributions

**Timeline.** The study takes about six months from materials to draft.

&#91;embedded content: study timeline · 5 phases, 1 gate\]

The pilot fixes prompts and variance estimates; the protocol is preregistered before any main-run data are collected.

**Risks and mitigations**

| Risk | Mitigation |
| --- | --- |
| Names carry race, class, or age signals | Frequency-matched validated names; three per gender; name fixed effects; pronoun-only robustness check |
| Results are prompt-specific | Three paraphrases per template, drawn from real-usage logs; report variance across paraphrases |
| Models update or are retired mid-study | Pinned dated slugs; complete each model's run within one week; log dates |
| Models refuse or flag sensitive attributes | Record refusals as an outcome; analyze refusal rates by condition |
| Résumés differ in quality | Pretest equalization; résumé fixed effects; role rotation in E2 |
| LLM coder introduces bias in E5 | Coder differs from evaluated model; 5% human double-coding; codebook preregistered |
| Reviewers question external validity | Frame the model as the object of study; anchor prompts in real usage; report the human benchmark as status quo |

**Expected contributions**

1. **Empirical.** The first systematic audit of motherhood penalties and fatherhood bonuses in LLMs across occupations, caregiving cues, and both sides of the labor market, on identical résumés.
2. **Theoretical.** A test of greedy-jobs and ideal-worker theory using an experimental subject that allows manipulations infeasible with human evaluators. A test of whether LLMs shift gender inequality from overt discrimination toward personalized steering.
3. **Policy.** Evidence on whether a single sentence of organizational policy in a job description changes model behavior, and on how fragile audit conclusions are to context. Directly relevant to bias-audit rules for automated employment decision tools, such as New York City Local Law 144.
4. **Methodological.** An open résumé corpus, manipulation library, and audit pipeline that others can rerun on new models.

**Target venues.** ACM FAccT or AIES (computational audience); PNAS Nexus, Sociological Science, or Socius (sociological audience).

**Possible extension.** A human-subjects follow-up in which participants receive model advice from E5 and report salary expectations and job preferences. This would test whether LLM steering changes behavior, not only output.

## References

- Acker, J. (1990). Hierarchies, jobs, bodies: A theory of gendered organizations. *Gender & Society*, 4(2), 139–158.
- An, J., Huang, D., Lin, C., & Tai, M. (2025). [Measuring gender and racial biases in large language models: Intersectional evidence from automated resume evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11937954/). *PNAS Nexus*, 4(3), pgaf089.
- Armstrong, L., Liu, A., MacNeil, S., & Metaxa, D. (2024). [The Silicon Ceiling: Auditing GPT's race and gender biases in hiring](https://arxiv.org/abs/2405.04412v3). arXiv:2405.04412.
- Benard, S., & Correll, S. J. (2010). Normative discrimination and the motherhood penalty. *Gender & Society*, 24(5), 616–646.
- Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg more employable than Lakisha and Jamal? *American Economic Review*, 94(4), 991–1013.
- Born, N., Curhan, J. R., & Bowles, H. R. (2026). [AI advice reinforces traditional gender roles](https://arxiv.org/abs/2610.14036). arXiv:2610.14036.
- Chaturvedi, S., & Chaturvedi, R. (2025). [Who gets the callback? Generative AI and gender bias](https://arxiv.org/abs/2504.21400). arXiv:2504.21400.
- Correll, S. J., Benard, S., & Paik, I. (2007). [Getting a job: Is there a motherhood penalty?](https://swap.stanford.edu/was/20140911222256mp_/http://gender.stanford.edu/sites/default/files/motherhoodpenalty.pdf) *American Journal of Sociology*, 112(5), 1297–1338.
- Frermann, L., Njoto, S., Cheong, M., & Ruppanner, L. (2023). Gender bias and parental-leave gaps in ChatGPT résumé ranking. University of Melbourne ([coverage](https://hrmasia.com/applying-for-a-job-ai-might-not-like-the-fact-that-you-have-kids/)).
- Gaddis, S. M. (2017). How black are Lakisha and Jamal? Racial perceptions from names used in correspondence audit studies. *Sociological Science*, 4, 469–489.
- Geiger, R. S., et al. (2024). [Asking an AI for salary negotiation advice is a matter of concern](https://arxiv.org/abs/2409.15567v3). arXiv:2409.15567.
- Goldin, C. (2014). A grand gender convergence: Its last chapter. *American Economic Review*, 104(4), 1091–1119.
- Goldin, C. (2021). *Career and Family: Women's Century-Long Journey toward Equity*. Princeton University Press.
- Iso, H., Pezeshkpour, P., et al. (2025). [Evaluating bias in LLMs for job-resume matching: Gender, race, and education](https://aclanthology.org/2025.naacl-industry.55/). NAACL Industry Track.
- Kleinberg, J., & Raghavan, M. (2021). Algorithmic monoculture and social welfare. *PNAS*, 118(22), e2018340118.
- Rozado, D. (2025). [Gender and positional biases in LLM-based hiring decisions](https://arxiv.org/abs/2505.17049v2). arXiv:2505.17049.
- Sorokovikova, A., Chizhov, P., et al. (2025). [Surface fairness, deep bias: A comparative study of bias in language models](https://arxiv.org/html/2506.10491v1). GeBNLP Workshop.
- Veldanda, A. K., et al. (2023). [Investigating algorithmic hiring bias in the era of ChatGPT](https://arxiv.org/abs/2310.05135). arXiv:2310.05135.
- Williams, J. C. (2000). *Unbending Gender: Why Family and Work Conflict and What to Do About It*. Oxford University Press.
- Wilson, K., & Caliskan, A. (2024). [Gender, race, and intersectional bias in resume screening via language model retrieval](https://arxiv.org/html/2407.20371v1). AIES.
- Yin, L., Alba, D., & Nicoletti, L. (2024). [OpenAI's GPT is a recruiter's dream tool. Tests show there's racial bias](https://prod.cm.bloomberg.com/graphics/2024-openai-gpt-hiring-racial-discrimination/). *Bloomberg*.

Model prices: OpenRouter model pages linked in the cost table, accessed 14 Oct 2026; DeepSeek off-peak rates per [DeepSeek V4.1 Flash router guide](https://www.orcarouter.ai/blog/deepseek-v4-1-flash-openrouter).

