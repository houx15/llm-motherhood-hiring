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
 "fig4": fig("fig5_invariance.pdf", "Removing all gender information leaves the penalty unchanged.", "invariance", w="0.85"),
 "fig5": fig("fig6_direct_gender.pdf", "Named gender: direct woman-versus-man choices by how gender is conveyed.", "direct"),
 "fig6": fig("fig7_withholding.pdf", "Caution as declining to decide: salary offers withheld (a) and interview recommendations for Haiku's pregnant applicants by whether an offer was made (b).", "withhold"),
 "fig7": fig("fig9_findings.pdf", "The framework revisited with Study 1's findings in place.", "findings"),
 "fig8": fig("fig8_disparate_impact.pdf", "Gender-neutral in form, gendered in effect: implied ratio of women's to men's shortlist rates as women's prevalence of caregiving signals rises (men fixed at 5\\%).", "di", w="0.9"),
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
\begin{tabular}{@{}lcccc@{}}
\toprule
Signal --- applicant & DeepSeek & Haiku & Luna & Qwen \\
\midrule
Parent --- mother & .357 & .233 & .297 & .387 \\
Parent --- father & .349 & .276 & .294 & .398 \\
Parent + commitment --- mother & .419 & .266 & .228 & .407 \\
Parent + leave --- mother & .310 & .110 & .186 & .230 \\
Parent + leave --- father & .308 & .130 & .184 & .256 \\
\midrule
\multicolumn{5}{@{}l}{\emph{Ranking: shortlist rate relative to the same résumé without the signal}} \\
Mothers & .71 & .25 & .78 & .75 \\
Fathers & .70 & .23 & .81 & .80 \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Pairwise choice against an equally qualified childless candidate of the same gender; .50 = equal treatment. Standard errors clustered by résumé pair (40 pairs) give 95\% confidence intervals of $\pm$.02--.07; no interval includes .50. Ranking ratios are résumé fixed-effect estimates from pools of six; .80 is the four-fifths threshold.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

T3 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Placebo decomposition of the parent-with-leave penalty (percentage points)}\label{tab:decomp}
\begin{tabular}{@{}lcccc@{}}
\toprule
Component (comparison) & DeepSeek & Haiku & Luna & Qwen \\
\midrule
Interruption & $-10.5$ & $-18.4$ & $-26.0$ & $-22.4$ \\
\quad(travel gap vs.\ .50) & ($t=-8.0$) & ($t=-8.5$) & ($t=-7.3$) & ($t=-8.9$) \\
Caregiving label & $+1.7$ & $-1.1$ & $+6.5$ & $+6.7$ \\
\quad(parental leave only $-$ travel gap) & [$+0.5$, $+2.9$] & [$-3.2$, $+0.9$] & [$+3.7$, $+9.2$] & [$+4.9$, $+8.5$] \\
Family signals on top of leave & $-10.6$ & $-17.4$ & $-11.5$ & $-12.1$ \\
\quad(parent + leave $-$ parental leave only) & [$-12.7$, $-8.6$] & [$-20.2$, $-14.5$] & [$-15.4$, $-7.5$] & [$-14.7$, $-9.5$] \\
Parenthood net of disclosure & $-10.4$ & $-19.2$ & $-12.1$ & $-7.3$ \\
\quad(parent $-$ personal placebo) & [$-12.8$, $-8.0$] & [$-23.4$, $-15.0$] & [$-16.3$, $-7.9$] & [$-10.3$, $-4.3$] \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Mothers; 20 main occupations; gender stated explicitly (levels L1 and L2 pooled); 40 résumé pairs. Brackets: 95\% confidence intervals clustered by résumé pair. The personal placebo itself costs 2.9--3.5 points for DeepSeek, Luna, and Qwen and raises Haiku's choice share by 3.7 points.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

T4 = r"""
\begin{table}[tbp]
\centering\small
\begin{threeparttable}
\caption{Mother--father differences for the parent signal (main run)}\label{tab:mf}
\begin{tabular}{@{}lcccc@{}}
\toprule
Outcome & DeepSeek & Haiku & Luna & Qwen \\
\midrule
Pairwise choice (points) & $+0.6$ & $\mathbf{-4.4}$ & $-0.4$ & $+0.1$ \\
 & ($t=0.6$) & ($t=-3.2$) & ($t=-0.4$) & ($t=0.0$) \\
Paired salary (\$) & $+138$ & $-150$ & $-109$ & $-16$ \\
Commitment rating, paired & $+.02$ & $\mathbf{-.14}$ & $+.00$ & $+.12$ \\
Commitment rating, single applicant & $\mathbf{-.09}$ & $\mathbf{-.06}$ & $+.03$ & $+.00$ \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Mother minus father on the same résumé pairs (choice, paired ratings) or résumés (single-applicant ratings). Bold: significant after Holm correction within outcome.
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
Qwen & childless / parents & .505 / .503 & .493 / .513 & \textbf{.518} / .491 \\
DeepSeek & childless / parents & .514 / \textbf{.535} & \textbf{.540} / \textbf{.540} & \textbf{.538} / \textbf{.548} \\
Luna & childless / parents & \textbf{.522} / \textbf{.577} & \textbf{.587} / \textbf{.647} & \textbf{.575} / \textbf{.634} \\
Haiku & childless / parents & \textbf{.528} / \textbf{.544} & .526 / .498 & .513 / .471 \\
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
\caption{Fairness instructions (phase 4): probability that a mother is chosen, by system prompt}\label{tab:fair}
\begin{tabular}{@{}lccc@{}}
\toprule
Model & Parent & Parent + leave & Travel gap \\
\midrule
DeepSeek & .361 / .325 / .369 & .317 / .301 / .386 & .422 / .420 / .451 \\
Haiku & .266 / .332 / .342 & .074 / .195 / .217 & .296 / .308 / .300 \\
Luna & .307 / .357 / .376 & .195 / .188 / .286 & .238 / .283 / .307 \\
Qwen & .381 / .333 / .351 & .234 / .181 / .279 & .274 / .286 / .339 \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Note:} Entries: no system prompt / generic equal-opportunity prompt / generic prompt plus ``do not penalize employment gaps taken for caregiving.'' Women; 20 main occupations; 40 résumé pairs; 48,000 calls; .50 = equal treatment. Hypotheses and tests were specified before the run.
\end{tablenotes}
\end{threeparttable}
\end{table}
"""
TABLES = {"tab1": T1, "tab2": T2, "tab3": T3, "tab4": T4, "tab5": T5, "tab6": T6}
