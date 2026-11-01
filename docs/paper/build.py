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
    ("Figure 1 lays out the framework", ["fig1"]),
    ("Table 1 lists the signals.", ["tab1"]),
    ("The same signals are costly when applicants compete", ["tab2"]),
    ("Comparison does not merely magnify", ["fig2"]),
    ("Table 3 and Figure 3 decompose", ["tab3", "fig3"]),
    ("*What the models say (exploratory).*", ["fig4"]),
    ("*Removing gender.*", ["fig5"]),
    ("*Fathers.*", ["tab4"]),
    ("What remains of gender is", ["tab5", "fig6"]),
    ("One vendor's gender layer also appears", ["fig7"]),
    ("Deployers often add fairness instructions", ["tab6"]),
    ("The caregiver penalty is blind to gender, but", ["fig8"]),
    ("Figure 9 returns to the framework", ["fig9"]),
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
assert used == 15, used
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
