# Raw LaTeX floats inserted into the manuscript body (values from the claim-checked report).
FIG = r"""
\begin{figure}[%s]
\centering
\includegraphics[width=%s\textwidth]{figures/%s}
\caption{%s}
\label{fig:%s}
\end{figure}
"""
def fig(file, cap, label, w="1.0", pos="tbp"):
    return FIG % (pos, w, file, cap, label)

FIGS = {
 "fig1": fig("fig1_framework.pdf", "Framework: protection follows the label. Components of the motherhood signal are ordered by how directly they refer to a protected category, from named gender to correlated caregiving signals. Each column states the Study 1 test and what the label account expects; bands show where outcomes are measured, how remedies are tested, and the planned Study 2. Section numbers locate each test.", "framework", pos="t"),
 "fig2": fig("fig2_scores_vs_choices.pdf", "The caregiver penalty appears where selection happens. Hollow markers: probability that a mother is chosen over an equally qualified childless woman, predicted from the model's own scores; filled markers: observed.", "scores"),
 "fig3": fig("fig3_decomposition.pdf", "Decomposition of the parent-with-leave penalty: the interruption and family signals carry it; the caregiving label adds nothing.", "decomp"),
 "fig4": fig("fig5_invariance.pdf", "Removing all gender information leaves the penalty unchanged. (a) Probability the parent is chosen when gender is conveyed by name and when it is removed. (b) The difference with its 90\\% confidence interval; intervals inside the shaded band are statistically equivalent to zero. A null difference here is the finding.", "invariance"),
 "fig5": fig("fig6_direct_gender.pdf", "Named gender: direct woman-versus-man choices by how gender is conveyed.", "direct", w="0.9"),
 "fig7": fig("fig9_findings.pdf", "The framework revisited with Study 1's findings in place.", "findings"),
 "fig8": fig("fig8_disparate_impact.pdf", "Gender-neutral in form, gendered in effect: implied ratio of women's to men's shortlist rates as women's prevalence of caregiving signals rises (men fixed at 5\\%).", "di", w="0.9"),
 "figA1": fig("figA1_withholding.pdf", "Claude Haiku: salary offers withheld by model (a) and interview recommendations for Haiku's pregnant applicants by whether an offer was made (b).", "withhold"),
}

T1 = r"""
\begin{table}[tbp]
\centering\small
\caption{Unbundling the motherhood signal}\label{tab:cues}
\begin{tabularx}{\textwidth}{@{}l>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X@{}}
\toprule
Signal & What it adds to the same résumé & What the comparison isolates \\
\midrule
None & neutral cover note & baseline \\
Personal (placebo) & a length-matched hobby and volunteer line & disclosure as such \\
Travel gap (placebo) & 8-month ``Career break --- extended travel'' & the interruption (vs.\ equal treatment) \\
Parental leave only (placebo) & the same dates labeled ``Parental leave'' & the caregiving label (vs.\ travel gap) \\
Parent & ``married with two children''; parent-association line & parenthood without a gap (vs.\ personal) \\
Parent + leave & Parent plus the parental-leave entry & family signals on top of a leave (vs.\ leave only) \\
\addlinespace
Neutral gap labels & same dates as ``company closure'' or ``certification'' & whether travel is stigmatized \\
Parent + commitment & Parent plus objective commitment bullets & the normative account \\
Pregnant (women only) & ``currently pregnant'' & pregnancy, incl.\ withholding \\
\bottomrule
\end{tabularx}
\begin{minipage}{\textwidth}\footnotesize\vspace{3pt}
\emph{Note:} Signals render identically for women and men; every application includes a cover note. Gender information is varied separately (names; name or initial plus an explicit gender line; initials only).
\end{minipage}
\end{table}
"""

T2 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Probability that the applicant with the family signal is chosen in pairwise choice (main run)}\label{tab:choice}
\begin{tabular}{@{}lccc@{}}
\toprule
Signal --- applicant & DeepSeek & Luna & Qwen \\
\midrule
Parent --- mother & .357 & .297 & .387 \\
Parent --- father & .349 & .294 & .398 \\
Parent + commitment --- mother & .419 & .228 & .407 \\
Parent + leave --- mother & .310 & .186 & .230 \\
Parent + leave --- father & .308 & .184 & .256 \\
\midrule
\multicolumn{4}{@{}l}{\emph{Shortlisting: rate relative to the same résumé without the signal}} \\
Mothers & .71 & .78 & .75 \\
Fathers & .70 & .81 & .80 \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Pairwise choice against an equally qualified childless candidate of the same gender; .50 = equal treatment. 95\% confidence intervals clustered by résumé pair (40 pairs) are $\pm$.02--.07; none includes .50. Shortlisting ratios are résumé fixed-effect estimates from pools of six; .80 is the four-fifths threshold. Claude Haiku: Table A1.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

T3 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Placebo decomposition of the parent-with-leave penalty (percentage points)}\label{tab:decomp}
\begin{tabular}{@{}lccc@{}}
\toprule
Component (comparison) & DeepSeek & Luna & Qwen \\
\midrule
Interruption & $-10.5$ & $-26.0$ & $-22.1$ \\
\quad(travel gap vs.\ .50) & ($t=-8.0$) & ($t=-7.3$) & ($t=-8.8$) \\
Caregiving label & $+1.7$ & $+6.5$ & $+6.6$ \\
\quad(parental leave only $-$ travel gap) & [$+0.5$, $+2.9$] & [$+3.7$, $+9.2$] & [$+4.8$, $+8.4$] \\
Family signals on top of leave & $-10.7$ & $-11.5$ & $-12.3$ \\
\quad(parent + leave $-$ parental leave only) & [$-12.7$, $-8.6$] & [$-15.4$, $-7.5$] & [$-14.8$, $-9.8$] \\
Parenthood net of disclosure & $-10.4$ & $-12.1$ & $-8.0$ \\
\quad(parent $-$ personal placebo) & [$-12.8$, $-8.0$] & [$-16.3$, $-7.9$] & [$-11.1$, $-4.9$] \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Mothers; 20 main occupations; gender stated explicitly (levels L1 and L2 pooled); 40 résumé pairs. Brackets: 95\% confidence intervals clustered by résumé pair. The personal placebo itself costs 2.7--3.5 points.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

T4 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Mother--father differences (main run)}\label{tab:mf}
\begin{tabular}{@{}llccc@{}}
\toprule
Signal & Outcome & DeepSeek & Luna & Qwen \\
\midrule
Parent & Pairwise choice (points) & $+0.8$ & $-0.4$ & $-1.1$ \\
 & Paired salary (\$) & $+118$ & $-100$ & $-456$ \\
 & Commitment, single applicant & $\mathbf{-.09}$ & $+.03$ & $-.00$ \\
Parent + leave & Pairwise choice (points) & $+0.2$ & $+0.2$ & $-2.6$ \\
 & Paired salary (\$) & $+72$ & $-9$ & $-543$ \\
 & Commitment, single applicant & $\mathbf{-.12}$ & $+.01$ & $-.04$ \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Mother minus father on the same résumé pairs (choice, salary) or résumés (single-applicant ratings, 1--7 scale). Bold: significant after Holm correction within outcome. No choice difference is significant.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

T5 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Direct woman-versus-man choices: probability the woman is chosen}\label{tab:direct}
\begin{tabular}{@{}llccc@{}}
\toprule
Model & Pair & Names (L0) & Name + line (L1) & Initial + line (L2) \\
\midrule
DeepSeek & childless / parents & .514 / \textbf{.535} & \textbf{.540} / \textbf{.540} & \textbf{.538} / \textbf{.548} \\
Luna & childless / parents & \textbf{.522} / \textbf{.577} & \textbf{.587} / \textbf{.647} & \textbf{.575} / \textbf{.634} \\
Qwen & childless / parents & .505 / .504 & .494 / .515 & \textbf{.518} / .493 \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Both candidates share a family status; .50 = no preference; 56 résumé pairs. Bold: differs from .50 after Holm correction (six tests per model). Qwen is statistically equivalent to .50 within $\pm$5 points in every cell.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

T6 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Fairness instructions (remedies phase): probability that a mother is chosen, by system prompt}\label{tab:fair}
\begin{tabular}{@{}lccc@{}}
\toprule
Model & Parent & Parent + leave & Travel gap \\
\midrule
DeepSeek & .361 / .325 / .369 & .317 / .301 / .386 & .422 / .420 / .451 \\
Luna & .307 / .357 / .376 & .195 / .188 / .286 & .238 / .283 / .307 \\
Qwen & .381 / .333 / .351 & .234 / .181 / .279 & .274 / .286 / .339 \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Entries: no system prompt / generic equal-opportunity prompt / generic prompt plus ``do not penalize employment gaps taken for caregiving.'' Women; 20 main occupations; 40 résumé pairs; .50 = equal treatment. Hypotheses and tests were specified before the run. Claude Haiku: Table A1.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""
TA1 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Claude Haiku: main results}\label{tab:haiku}
\begin{tabular}{@{}lr@{}}
\toprule
Quantity & Estimate \\
\midrule
Pairwise choice, parent + leave: mother / father & .110 / .130 \\
Pairwise choice, parent: mother / father & .233 / .276 \\
Shortlisting ratio: mothers / fathers & .25 / .23 \\
Fit rating, parent $-$ none (women; 10-point scale) & $+0.34$ \\
Interruption (travel gap vs.\ .50), points & $-18.4$ ($t=-8.5$) \\
Caregiving label, points & $-1.1$ [$-3.2$, $+0.9$] \\
Family signals on top of leave, points & $-17.4$ [$-20.2$, $-14.5$] \\
Parenthood net of disclosure, points & $-19.2$ [$-23.4$, $-15.0$] \\
Personal placebo, points & $+3.7$ \\
No gender $-$ names: parent / parent + leave, points & $+0.6$ / $+0.9$ (both equivalent) \\
Mother $-$ father choice, parent, points & $-4.3$ (Holm $p=.02$) \\
Direct choice, mother vs.\ father: L0 / L1 / L2 & .544 / .498 / .471 \\
Refusal to choose: mother vs.\ father / parent + leave / placebos & 5.4\% / 4.9\% / $\approx$0.1\% \\
Salary withheld: pregnant / childless women (L1: pregnant) & 19.8\% / 3.1\% (27.5\%) \\
Interview if offer withheld vs.\ made (pregnant) & 29.9\% vs.\ 100\% \\
Generic prompt: change in parent / leave penalty & $+6.6$ / $+12.2$ points \\
Four-fifths threshold (women's signal prevalence; men 5\%) & 31\% \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Same designs and clustering as the main tables. Refusal rates from the second phase, first attempts.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""
TABLES = {"tab1": T1, "tab2": T2, "tab3": T3, "tab4": T4, "tab5": T5, "tab6": T6, "tabA1": TA1}
