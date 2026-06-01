% Bishop's University thesis document class
% (c) 2006-2025 Stefan D. Bruda <stefan@bruda.ca>
%
% You can redistribute this class and/or modify it under the terms of
% the GNU Lesser General Public License as published by the Free
% Software Foundation <http://www.gnu.org/licenses/lgpl.html>; either
% version 3 of the License, or (at your option) any later version.
% 
% This document class is distributed in the hope that it will be
% useful, but WITHOUT ANY WARRANTY; without even the implied warranty
% of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
% Lesser General Public License for more details.
%
% This document class was inspired by the circa 2002 version of the
% Queen's University thesis style by Bob Burke, which is in turn based
% as far as I know on the Stanford University PhD thesis style.

\long\def\comment#1{}
\comment{

  This document class defines the style requirements of Master's
  theses in Computer Science at Bishop's University.  The class
  inherits most of its features from the ``book'' standard document
  class.  Additionally we define the front matter, we set the margins
  and fonts, we set page headers and footers, and we set the style of
  all the hyperlinks (such as references and citations).  We also
  define proofs and theorem-like environments as per the ``amsthm''
  style with explicit numbering rules.

  Font sizes of 10-, 11-, and 12-point are all acceptable.  The
  recommended size (and also the default) is 11-point.  Provide the
  document class option ``10pt'' or ``12pt'' to use a 10-point or
  12-point font size, respectively.

  To produce a thesis proposal rather than a dissertation use the
  ``proposal'' option.

  The use of this document class is compulsory for all the
  dissertations and thesis proposals in the department.  We further
  recommend (but do not require) the use of BibTeX to manage
  references with the `siam' bibliography style.

  See below for an example of use.

  The title of the dissertation and the author need to be defined as
  usual using the \title and \author commands.  The following commands
  further control what goes in the front matter material.  All are
  optional and have sensible default values if omitted.

  \dept{author's department}, defaults to ``Computer Science''

  \degree{degree expected}, defaults to ``Master of Science''

  \submitdate{month and year in which the final version is submitted},
  defaults to the full name of the current month followed by the
  current year

  \copyrightyear{year degree conferred}, defaults to the current year

  \figurespagetrue or \figurespagefalse produce or do not produce a
  List of Figures page (true by default)

  \tablespagetrue or \tablespagefalse produce or do not produce a List
  of Tables page (true by default)

  Then the \beforepreface command creates the title page.  Preface
  section(s) (abstract, etc.)  are introduced by the following
  command:

  \prefacesection{section title}

  The front matter pages are numbered with roman numerals.

  The \afterpreface command then produces the tables of contents,
  tables and figures, and sets things up to start the main body (on
  arabic page 1).

  Note that it is very easy to overrun the length of the page with the
  default running title (the chapter name).  When this happens the
  user needs to provide a running title just after the \chapter
  command like this:

  \chapterrunning{a running title for the chapter}

  This will result in the following running title for the current
  chapter:

  CHAPTER x. A RUNNING TITLE FOR THE CHAPTER

  where x is the current chapter number.

  Example of use:

    \documentclass{buthesis}
    % For a thesis proposal use:
    % \documentclass[proposal]{buthesis}

    \begin{document}
    \title{How to Write Theses\\
      With Two Line Titles}
    \author{John Henry Candidate}
   
    \beforepreface
    \prefacesection{Abstract}
        This dissertation tells you all you need to know about...
    \prefacesection{Acknowledgments}
        I would like to thank...
    \afterpreface
   
    \chapter{Introduction}
        ...
    \chapter{Conclusions of Why It All Matters and Let's Make This Title Very Long}
    \chapterrunning{conclusions}
        ...
    \bibliographystyle{siam}
    \bibliography{mybib}
        ...
    \appendix
    \chapter{A Long Proof}
        ...
    \end{document}

}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{buthesis}[2026/05/06 v2.6 Bishop's University thesis document class]
\typeout{`buthesis.cls' is free software; you are welcome to redistribute it under certain conditions, see http://www.gnu.org/licenses/lgpl.html.}

\def\baseFontSize#1{\gdef\@BaseFontSize{#1}}

\def\@BaseFontSize{11pt}

\DeclareOption{8pt}{\PackageWarning{bureport}{Font size '\CurrentOption' is too small, use at least 10pt.}}
\DeclareOption{9pt}{\PackageWarning{bureport}{Font size '\CurrentOption' is too small, use at least 10pt.}}
\DeclareOption{10pt}{\baseFontSize{10pt}}
\DeclareOption{11pt}{\baseFontSize{11pt}}
\DeclareOption{12pt}{\baseFontSize{12pt}}

\newif\ifisathesis
\isathesistrue

\DeclareOption{thesis}{\isathesistrue}
\DeclareOption{proposal}{\isathesisfalse}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}

\ProcessOptions\relax

\LoadClass[oneside,letterpaper,\@BaseFontSize]{book}

% Most theses use external figures
\RequirePackage{graphicx}

% amsthm handles proofs nicely
\RequirePackage{amsthm}

% All the theorem-like environments are numbered together, but
% definition are numbered separately.

\newtheorem{definition}{Definition}[chapter]

\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}

%\newenvironment{proof}{\noindent \textbf{Proof.} \rm}{\hfill \qed}
%\newcommand{\qed}{$\Box$}

\RequirePackage{xcolor}
\RequirePackage{hyperref}

% Sensible hyperlink colors:
\hypersetup{
    colorlinks,
    linkcolor={red!50!black},
    citecolor={blue!50!black},
    urlcolor={blue!80!black}
}

\newcommand{\chapterrunning}[1]{
  \markboth{CHAPTER \thechapter.\  \expandafter\MakeUppercase\expandafter{#1}}
  {CHAPTER \thechapter.\  \expandafter\MakeUppercase\expandafter{#1}}}

% We used to use 1" except for the binding side at 1.5", which is is
% fine for double-spaced lines but rather narrow for single spacing.
% Therefore we now require 1.5" margins everywhere.
%
% Theses are single-sided, so we don't care about \evensidemargin
% \oddsidemargin 0.5in \evensidemargin 0.5in
% \marginparwidth 40pt \marginparsep 10pt
% \topmargin 0pt \headsep .5in
% \textheight 8.1in \textwidth 6in

% 1.5" margin size everywhere
\RequirePackage[left=1.5in, right=1.5in, top=1.5in, bottom=1.5in]{geometry}

% Use Palatino for most fonts and Computer Modern as fixed width font
% (which is a very nice combination):
%\RequirePackage{palatino,mathpple}
\RequirePackage{newpxtext}
\RequirePackage{newpxmath}
\renewcommand{\ttdefault}{cmtt}
\SetMathAlphabet\mathtt{normal}{OT1}{cmtt}{m}{n}

% Disallow page breaks at hyphens (this will give some underfull vbox's,
% so an alternative is to use \brokenpenalty=100 and manually search
% for and fix such page breaks)
\brokenpenalty=10000

% Only chapters and sections in the ToC
\setcounter{tocdepth}{1}

% Double spacing is no longer in effect so we no longer need to worry
% about any of the things related to double spacing.
%
% Set up double spacing (code taken from setspace.sty)
%\ifcase \@ptsize \relax % 10pt
%    \def\baselinestretch{1.667}
%  \or % 11pt
%    \def\baselinestretch{1.618}
%  \or % 12pt
%    \def\baselinestretch{1.655}
%  \fi
%
% \newlength{\singlebaselineskip}
% \newlength{\doublebaselineskip}
% \setlength{\singlebaselineskip}{\baselineskip}
% \setlength{\doublebaselineskip}{1.6\baselineskip}
%
% \newcommand{\singlespacing}{\setlength{\baselineskip}{\singlebaselineskip}}
% \newcommand{\doublespacing}{\setlength{\baselineskip}{1.6\baselineskip}}
%
% \newcommand{\adjustsingle}{\vspace*{-\singlebaselineskip}}
% %\newcommand{\adjustsingle}{}
%
% % Redefine the macro used for floats (including figures and tables)
% % so that single spacing is used.
% % (Note \def\figure{\@float{figure}set single spacing} doesn't work
% % because figure has an optional argument)
% \def\@xfloat#1[#2]{\ifhmode \@bsphack\@floatpenalty -\@Mii\else
%    \@floatpenalty-\@Miii\fi\def\@captype{#1}\ifinner
%       \@parmoderr\@floatpenalty\z@
%     \else\@next\@currbox\@freelist{\@tempcnta\csname ftype@#1\endcsname
%        \multiply\@tempcnta\@xxxii\advance\@tempcnta\sixt@@n
%        \@tfor \@tempa :=#2\do
%                         {\if\@tempa h\advance\@tempcnta \@ne\fi
%                          \if\@tempa t\advance\@tempcnta \tw@\fi
%                          \if\@tempa b\advance\@tempcnta 4\relax\fi
%                          \if\@tempa p\advance\@tempcnta 8\relax\fi
%          }\global\count\@currbox\@tempcnta}\@fltovf\fi
%     \global\setbox\@currbox\vbox\bgroup 
%     \def\baselinestretch{1}\@normalsize
%     \boxmaxdepth\z@
%     \hsize\columnwidth \@parboxrestore}
%
% % Redefine the macro used for footnotes to use single spacing
% \long\def\@footnotetext#1{\insert\footins{\def\baselinestretch{1}\footnotesize
%     \interlinepenalty\interfootnotelinepenalty 
%     \splittopskip\footnotesep
%     \splitmaxdepth \dp\strutbox \floatingpenalty \@MM
%     \hsize\columnwidth \@parboxrestore
%    \edef\@currentlabel{\csname p@footnote\endcsname\@thefnmark}\@makefntext
%     {\rule{\z@}{\footnotesep}\ignorespaces
%       #1\strut}}}

% \author, \title are defined in book;
% here are the rest of the front matter defining macros
\def\dept#1{\gdef\@dept{#1}}
\def\degree#1{\gdef\@degree{#1}}
\def\submitdate#1{\gdef\@submitdate{#1}}
\def\copyrightyear#1{\gdef\@copyrightyear{#1}}
\def\@title{}\def\@author{}
\def\@dept{Department of Computer Science}
\def\@degree{Master of Science}
\def\@submitdate{\ifcase\the\month\or
  January\or February\or March\or April\or May\or June\or
  July\or August\or September\or October\or November\or December\fi
  \space \number\the\year}
\def\@copyrightyear{\number\the\year}
\newif\iffigurespage \newif\iftablespage
\figurespagetrue \tablespagetrue

% Title page:
\def\titlep{%
    \thispagestyle{empty}%
    %\doublespacing%
    \begin{center}
      \mbox{} \vfill

        {\Large\sc\@title}\\
        \mbox{}\\
        \mbox{}\\
        by\\
        \mbox{}\\
        \mbox{}\\
        {\large\sc\@author}\\
    \end{center}
    \vfill\vfill
    \begin{center}
        A
        \ifisathesis
          dissertation 
        \else
          thesis proposal
        \fi
        submitted to the\\
        \@dept\\
        in conformity with the requirements for\\
        the degree of \@degree\\
    \end{center}
    \mbox{}
    \begin{center}
        Bishop's University\\
        Canada\\
         \@submitdate\\
        %\includegraphics[scale=0.2]{0_frontmatter/figures/logo3}   % width=3cm,scale=0.5,height=1cm
    \end{center}
    \mbox{}
    %\vfill 
   \begin{center}
        Copyright \copyright\ \@author, \@copyrightyear\\
        released under a \href{https://creativecommons.org/licenses/by-sa/4.0/}{CC BY-SA 4.0 License}
    \end{center}\clearpage}

\def\beforepreface{
    \titlep
    \pagenumbering{roman}
    \pagestyle{plain}}

\def\prefacesection#1{%
    \chapter*{#1}}

\def\afterpreface{\clearpage
    \tableofcontents
    \clearpage
    \iftablespage
        \listoftables
        \clearpage
    \fi
    \iffigurespage
        \listoffigures
        \clearpage
    \fi
    \pagenumbering{arabic}
    \pagestyle{headings}}

%\renewcommand{\appendix}{}

% Redefine \thebibliography to go to a new page and put an entry in the
% table of contents
\let\@ldthebibliography\thebibliography
\renewcommand{\thebibliography}[1]{\clearpage
    \addcontentsline{toc}{chapter}{Bibliography}
    \@ldthebibliography{#1}}

% Start out normal
\pagestyle{headings}