import re, subprocess, sys
from floats import FIGS, TABLES
src = open(sys.argv[1] if len(sys.argv) > 1 else "manuscript.md").read()

title = re.search(r"^# (.+)$", src, re.M).group(1)
abstract = re.search(r"## Abstract\n\n(.+?)\n\n---", src, re.S).group(1).strip()
body = src[src.index("## 1. Introduction"):]
body, refs = body.split("## References", 1)
refs = refs.split("## Figures and tables", 1)[0]
body = body.replace("\n---\n", "\n")
body = re.sub(r"^(#{2,3}) \d+(\.\d+)?\.? ", r"\1 ", body, flags=re.M)

anchors = [
    ("We propose that in aligned models *protection follows the label*.", ["fig1"]),
    ("Table 1 lists the signals.", ["tab1"]),
    ("*It appears where selection happens.*", ["tab2", "fig2"]),
    ("*It consists of the interruption and the family signals", ["tab3", "fig3"]),
    ("*It does not depend on gender.*", ["fig4", "tab4"]),
    ("At the named end, the label account expects", ["tab5", "fig5"]),
    ("Table 6 reports the remedies phase", ["tab6"]),
    ("Figure 6 returns to the framework", ["fig7"]),
    ("Protection that follows the label leaves", ["fig8"]),
    ("Claude Haiku 5.5 was audited with the same", ["tabA1", "figA1"]),
]
paras = body.split("\n\n")
out = []
for p in paras:
    out.append(p)
    for a, keys in anchors:
        if p.lstrip().startswith(a):
            for k in keys:
                raw = FIGS.get(k) or TABLES[k]
                out.append("```{=latex}\n" + raw.strip() + "\n```")
used = sum(1 for p in out if p.startswith("```{=latex}"))
assert used == 16, used
body = "\n\n".join(out)
open("body.md", "w").write(body)
subprocess.run(["pandoc", "body.md", "-f", "markdown+raw_attribute", "-t", "latex",
                "--shift-heading-level-by=-1", "-o", "body.tex"], check=True)
abs_tex = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex"], input=abstract,
                         capture_output=True, text=True, check=True).stdout

items = [l[2:].strip() for l in refs.splitlines() if l.startswith("- ")]
note = [l for l in refs.splitlines() if l.strip() and not l.startswith("- ")]
ref_tex = "\n".join(
    r"\noindent\hangindent=1.5em\hangafter=1 " +
    subprocess.run(["pandoc", "-f", "markdown", "-t", "latex"], input=i, capture_output=True,
                   text=True, check=True).stdout.strip() + "\\par\\smallskip" for i in items)
note_tex = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex"], input=" ".join(note),
                          capture_output=True, text=True, check=True).stdout

tex = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}\onehalfspacing
\usepackage{microtype,graphicx,booktabs,tabularx,threeparttable,xcolor}
\usepackage[labelfont=bf,font=small]{caption}
\usepackage{enumitem}\setlist{itemsep=2pt,topsep=4pt}
\usepackage[hidelinks]{hyperref}
\usepackage{newunicodechar}
\newunicodechar{−}{\ensuremath{-}}
\newunicodechar{κ}{\ensuremath{\kappa}}
\newunicodechar{±}{\ensuremath{\pm}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{†}{\textdagger}
\newunicodechar{◆}{\ensuremath{\diamond}}
\newunicodechar{§}{\S}
\providecommand{\tightlist}{\setlength{\itemsep}{2pt}\setlength{\parskip}{0pt}}
\setlength{\parskip}{0pt}
\renewcommand{\floatpagefraction}{0.75}
\renewcommand{\topfraction}{0.85}
\title{\textbf{%s}}
\author{Yuxin Hou\\\small Princeton University}
\date{\small Draft, %s}
\begin{document}
\maketitle
\begin{abstract}\noindent %s\end{abstract}
\vspace{0.5em}
%s
\section*{References}
{\small\setstretch{1.1}
\noindent\textit{%s}\par\medskip
%s}
\end{document}
""" % (title, "October 31, 2026", abs_tex.strip(), open("body.tex").read(), note_tex.strip(), ref_tex)
open("manuscript.tex", "w").write(tex)
print("tex written")
