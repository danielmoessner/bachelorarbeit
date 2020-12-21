%% sosy-letter.cls,
%% (c) D. Beyer, 2010-03-01
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sosy-letter}[2010/03/01 (c) D. Beyer]
\LoadClass[a4paper,11pt]{dinbrief}
\RequirePackage{graphicx}
\RequirePackage{german} 
\RequirePackage[T1]{fontenc} 
\RequirePackage[utf8]{inputenc}
\RequirePackage{helvet}
\RequirePackage{hyperref}
\RequirePackage{url}
\RequirePackage{microtype}
\frenchspacing
%
\pagestyle{empty}
%
\renewcommand\familydefault{\sfdefault}
%
\addtolength{\textheight}{42mm}
%
\def\isomonth{\ifcase\month\or
  01\or 02\or 03\or 04\or 05\or 06\or
  07\or 08\or 09\or 10\or 11\or 12\fi}
\def\isoday{\ifcase\day\or
  01\or 02\or 03\or 04\or 05\or 06\or 07\or 08\or 09\or 10\or
  11\or 12\or 13\or 14\or 15\or 16\or 17\or 18\or 19\or 20\or
  21\or 22\or 23\or 24\or 25\or 26\or 27\or 28\or 29\or 30\or
  31\fi}
\def\isotoday{\number\year-\isomonth-\isoday}
%
%\nowindowtics
\nowindowrules
\nobackaddressrule
\Datum{}
\newcommand{\datum}[1]{\newcommand{\currdate}{#1}}
%
\newcommand{\sosyletterdef}[2]{\newcommand{\sosyletter}[4]{
 \address{
  \begin{minipage}[b][25mm]{9cm}
    Professor Dr. rer. nat. Dirk Beyer \\[1ex]
    {\bf Chair for Software and Computational Systems}\\[2ex]
  \end{minipage}
  \hfill
  \begin{minipage}[b][25mm]{50mm}
    \hfill #1
  \end{minipage}\\
  \hfill
  \begin{minipage}{44mm}
    \scriptsize
    \vspace{14.5mm}
    \begin{picture}(0,0)
      \linethickness{1.5pt}
      \put(43,72){\line(0,-1){140}}
    \end{picture}
    \begin{tabular}{rl}
            & Prof. Dr. Dirk Beyer\\
    Telefon & +49 89 2180-9150\\
            & Sekretariat: ~-9151\\
            & Marianne Diem\\
            & \\
    Telefax & +49 89 2180-9175\\
            & \\
    E-Mail  & marianne.diem\\
            & @lmu.de\\
            & \\
    Zeichen & db/md \\
            & \\
    Datum   & \currdate \\
    \end{tabular}
  \end{minipage}\\
  \vspace{160mm}
  \hfill
  \begin{minipage}{62mm}
    \scriptsize
    \vspace{23mm}
    \begin{picture}(0,0)
      \linethickness{1.5pt}
      \put(76.5,15){\line(0,-1){35}}
    \end{picture}
    \begin{tabular}{rl}
    Besucheradresse & Oettingenstr. 67, D-80538 München\\
    Internetadresse & \href{https://www.sosy-lab.org/}{www.sosy-lab.org}
    \end{tabular}
  \end{minipage}
 }
 #2
}}
%
\newcommand{\logo}{\includegraphics[width=5cm]{logos/Uni-Logo-LMU}}
\newcommand{\nologo}{}
%
\backaddress{\hspace{4mm}LMU Munich $\cdot$ Software and Computational Systems $\cdot$ D-80538 München}
%
\signature{Prof. Dr. Dirk Beyer}
\newcommand{\setsignature}{\includegraphics[scale=0.1]{SignatureDirk}}
%%
%% End of file `sosy-letter.cls'.

