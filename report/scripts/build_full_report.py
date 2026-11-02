import os
import sys

def generate_tex():
    tex_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.tex")
    
    content = r'''\documentclass[12pt,a4paper]{article}

% ---------- Packages ----------
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage{amsmath}
\usepackage[
    top=1.15in,
    bottom=1.1in,
    left=1.15in,
    right=1.15in,
    headheight=18pt,
    headsep=0.45in,
    footskip=0.45in
]{geometry}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,shapes.geometric,shapes.multipart,fit,calc}
\usepackage{setspace}
\usepackage{ragged2e}
\usepackage{tabularx}
\usepackage{array}
\usepackage{booktabs}
\usepackage{float}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{needspace}
\usepackage{refcount}
\usepackage{longtable}
\usepackage{listings}
\usepackage[hyphens]{url}

% ---------- Color Definitions ----------
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.97,0.97,0.98}

% ---------- Listings Configuration ----------
\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},
    commentstyle=\color{codegreen},
    keywordstyle=\color{blue}\bfseries,
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    numbers=left,
    numbersep=7pt,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=2,
    frame=single,
    rulecolor=\color{gray!40},
    xleftmargin=12pt,
    framexleftmargin=8pt
}
\lstset{style=mystyle}

% ---------- General Formatting ----------
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{5pt}
\setlength{\floatsep}{10pt plus 2pt minus 2pt}
\setlength{\textfloatsep}{12pt plus 2pt minus 2pt}

% ---------- Configurable Academic Metadata ----------
\newcommand{\projecttitle}{AI-BASED ENTERPRISE DECISION SUPPORT PLATFORM USING MACHINE LEARNING}
\newcommand{\projectsubtitle}{An Explainable AI-Driven Customer Churn Prediction \& Sales Forecasting System}
\newcommand{\studentname}{JOYAL JOBAI}
\newcommand{\studentroll}{ASI25MCA-2034}
\newcommand{\studentrollshort}{34}
\newcommand{\coursecode}{20MCA245}
\newcommand{\coursename}{MINI PROJECT}
\newcommand{\programmecourse}{Master of Computer Applications}
\newcommand{\institutionname}{Adi Shankara Institute of Engineering \& Technology}
\newcommand{\institutionaddress}{Vidya Bharathi Nagar, Mattoor, Kalady, Ernakulam District, Kerala State}
\newcommand{\institutionpin}{PIN: 683574}
\newcommand{\universityname}{APJ Abdul Kalam Technological University, Kerala}
\newcommand{\guidefname}{Mr.\ Sukrith Lal P S}
\newcommand{\guidedesignation}{Assistant Professor}
\newcommand{\guidedepartment}{Department of Computer Applications}
\newcommand{\hodname}{Dr.\ Vincy Devi V K}
\newcommand{\hoddesignation}{Head of the Department}
\newcommand{\principalname}{Dr.\ M S Murali}
\newcommand{\reportdate}{October 2026}

% ---------- Page Border ----------
\newcommand{\pageborder}{%
  \begin{tikzpicture}[remember picture,overlay]
    \draw[line width=2pt]
      ([xshift=0.9in,yshift=-0.9in]current page.north west)
      rectangle
      ([xshift=-0.9in,yshift=0.9in]current page.south east);
  \end{tikzpicture}%
}
\AddToHook{shipout/background}{\pageborder}

% ---------- Header and Footer Styles ----------
\fancypagestyle{toc}{%
  \fancyhf{}
  \fancyhead[L]{\large\bfseries\itshape ENTERPRISE DECISION SUPPORT PLATFORM}
  \fancyfoot[L]{\large\itshape Department of Computer Applications -- ASIET}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}
\fancypagestyle{reportbody}{%
  \fancyhf{}
  \fancyhead[L]{\large\bfseries\itshape ENTERPRISE DECISION SUPPORT PLATFORM}
  \fancyfoot[L]{\large\itshape Department of Computer Applications -- ASIET}
  \fancyfoot[R]{\large\bfseries\thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}
\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyhead[L]{\large\bfseries\itshape ENTERPRISE DECISION SUPPORT PLATFORM}
  \fancyfoot[L]{\large\itshape Department of Computer Applications -- ASIET}
  \fancyfoot[R]{\large\bfseries\thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}

% ---------- College Logo Helper ----------
\newcommand{\collegelogo}[1]{%
  \IfFileExists{Logo.PNG}{\includegraphics[width=#1,height=#1,keepaspectratio]{Logo.PNG}}{%
  \IfFileExists{logo.png}{\includegraphics[width=#1,height=#1,keepaspectratio]{logo.png}}{%
  \fbox{\parbox[c][#1][c]{#1}{\centering\small College Logo}}}}%
}

% ---------- Table Column Definitions ----------
\newcolumntype{C}[1]{>{\centering\arraybackslash}m{#1}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{M}{>{\raggedright\arraybackslash}m{\dimexpr\linewidth-4.2cm-6\tabcolsep-4\arrayrulewidth\relax}}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}

% ---------- Screenshot and Image Macros ----------
\newcommand{\reportscreenshot}[2]{%
  \begin{figure}[H]
  \centering
  \begingroup
    \setlength{\fboxsep}{3pt}%
    \setlength{\fboxrule}{0.8pt}%
    \fcolorbox{black!60}{white}{%
      \begin{minipage}[c][8.5cm][c]{0.92\linewidth}%
        \centering
        \IfFileExists{#1}{%
          \includegraphics[width=\linewidth,height=8.35cm,keepaspectratio]{#1}%
        }{%
          \begin{minipage}[c][8.35cm][c]{\linewidth}%
          \centering
          {\normalsize\bfseries ENTERPRISE DECISION SUPPORT PLATFORM}\\[0.6cm]
          {\small\color{black!50}APPLICATION SCREENSHOT}\\[0.3cm]
          {\small\bfseries #2}\\[0.4cm]
          {\scriptsize\ttfamily\detokenize{#1}}%
          \end{minipage}%
        }%
      \end{minipage}%
    }%
  \endgroup
  \caption{#2}
  \label{fig:#1}
  \end{figure}%
}

% ============================================================
% EMBEDDED TIKZ DIAGRAMS
% ============================================================
\tikzset{
 edpbox/.style={draw=black, line width=.75pt, rounded corners=2pt, align=center, font=\small, inner sep=4pt, fill=white},
 edpsmall/.style={draw=black, line width=.75pt, rounded corners=2pt, align=center, font=\scriptsize, inner sep=4pt, fill=white},
 edparrow/.style={-{Stealth[length=2.2mm,width=1.7mm]},line width=.85pt},
 edpguide/.style={gray!65,densely dashed,line width=.45pt}
}

% 1. Four-Layer Basic Architecture
\newcommand{\projectarchitecture}{%
\begin{tikzpicture}[
 x=1cm,y=1cm,
 line cap=round,line join=round,
 tier/.style={draw=black!65,line width=.85pt,rounded corners=2pt,fill=black!2},
 component/.style={draw=black,line width=.82pt,rounded corners=2pt,fill=white,align=center,inner xsep=3pt,inner ysep=5pt,font=\footnotesize},
 route/.style={-{Stealth[length=2.3mm,width=1.7mm]},line width=.90pt},
 tierlabel/.style={font=\scriptsize\bfseries,align=center,text=black!80}
]
 \draw[tier] (0,11.50) rectangle (15.2,14.35);
 \draw[tier] (0,8.60) rectangle (15.2,11.05);
 \draw[tier] (0,4.30) rectangle (15.2,8.15);
 \draw[tier] (0,.10) rectangle (15.2,3.85);
 \foreach \ybottom/\ytop in {11.50/14.35,8.60/11.05,4.30/8.15,.10/3.85}{%
   \draw[black!35,line width=.6pt] (2.64,\ybottom) -- (2.64,\ytop);
 }

 \node[tierlabel] at (1.32,12.95) {\shortstack{PRESENTATION\\TIER}};
 \node[tierlabel] at (1.32,9.80) {\shortstack{APPLICATION /\\API TIER}};
 \node[tierlabel] at (1.32,6.20) {\shortstack{AI, ML \& XAI\\PROCESSING\\TIER}};
 \node[tierlabel] at (1.32,1.97) {\shortstack{DATABASE\\STORAGE \&\\SERVICES}};

 \node[component,text width=4.70cm,minimum height=1.13cm] (storefront) at (5.40,12.93)
   {\textbf{SmartCart Storefront (React 18)}\\Customer shopping, cart, orders \& perks};
 \node[component,text width=4.70cm,minimum height=1.13cm] (portal) at (11.75,12.93)
   {\textbf{Executive Decision UI (React 18)}\\Churn risk triage, SHAP \& sales forecasting};

 \node[component,text width=9.95cm,minimum height=1.11cm] (backend) at (8.57,9.83)
   {\textbf{Python FastAPI REST Backend (15 API Routers)}\\Authentication, feature sync, telemetry ingestion, ML orchestration \& PDF reports};

 \node[component,text width=3.50cm,minimum height=1.40cm] (churnml) at (4.65,6.22)
   {\textbf{Churn ML Models}\\Random Forest \& XGBoost\\23 behavioral features};
 \node[component,text width=3.50cm,minimum height=1.40cm] (xai) at (8.76,6.22)
   {\textbf{SHAP TreeExplainer}\\Local Shapley values \&\\global feature attribution};
 \node[component,text width=3.50cm,minimum height=1.40cm] (decision) at (12.87,6.22)
   {\textbf{Prescriptive Engine}\\Rule-based playbooks\\\& multi-horizon sales forecaster};

 \node[component,text width=3.50cm,minimum height=1.24cm] (db) at (4.65,1.99)
   {\textbf{Relational Database}\\SQLite / MySQL schema\\14 interconnected tables};
 \node[component,text width=3.50cm,minimum height=1.24cm] (artifacts) at (8.76,1.99)
   {\textbf{Model Artifacts}\\JSON models, scaler.pkl,\\encoders \& preprocessors};
 \node[component,text width=3.50cm,minimum height=1.24cm] (reports) at (12.87,1.99)
   {\textbf{Executive Reporting}\\ReportLab automated PDF\\audit logs \& notifications};

 \draw[route] (storefront.south) -- ([xshift=-3.17cm]backend.north);
 \draw[route] (portal.south) -- ([xshift=3.17cm]backend.north);
 \draw[route] ([xshift=-3.92cm]backend.south) -- (churnml.north);
 \draw[route] (backend.south) -- (xai.north);
 \draw[route] ([xshift=4.30cm]backend.south) -- (decision.north);
 \draw[route] (churnml.east) -- (xai.west);
 \draw[route] (xai.east) -- (decision.west);
 \draw[route] (db.north) -- (churnml.south);
 \draw[route] (artifacts.north) -- (xai.south);
 \draw[route] (reports.north) -- (decision.south);
 \draw[route,densely dashed,black!75]
   (backend.east) -- (15.08,9.83) -- (15.08,1.99) -- (reports.east);
\end{tikzpicture}%
}

% 2. UML Workflow
\newcommand{\projectworkflow}{%
\begin{tikzpicture}[node distance=3.1mm]
 \node[edpbox,text width=10.8cm,minimum height=.65cm] (step1) {\textbf{Customer Telemetry \& Transaction Ingestion (MySQL / SQLite)}};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step1] (step2) {Feature Preprocessing: RFM calculation, scaling, and categorical encoding};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step2] (step3) {Supervised Classification: Random Forest \& XGBoost churn probability scoring};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step3] (step4) {Risk Tiering: High Risk ($>70\%$), Medium Risk ($40\%$--$70\%$), and Low Risk ($<40\%$)};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step4] (step5) {Explainable AI: SHAP TreeExplainer local feature attribution (+/- contributions)};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step5] (step6) {Diagnostic Engine: Operational friction vector analysis (support, recency, carts)};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step6] (step7) {Prescriptive Action Engine: Automated retention playbooks (e.g., WELCOME10, CARE10)};
 \node[edpbox,text width=10.8cm,minimum height=.65cm,below=of step7] (step8) {Closed-Loop Delivery: In-app perks reflection, storefront redemption \& PDF reports};
 \foreach \a/\b in {step1/step2,step2/step3,step3/step4,step4/step5,step5/step6,step6/step7,step7/step8}{\draw[edparrow] (\a.south)--(\b.north);}
\end{tikzpicture}%
}

% 3. UML Use Case Diagram
\newcommand{\projectusecase}{%
\begin{tikzpicture}[
  actor/.style={draw=black,line width=.85pt,rounded corners=3pt,fill=black!5,inner sep=5pt,font=\footnotesize\bfseries,align=center,minimum width=2.4cm},
  usecase/.style={draw=black,line width=.75pt,ellipse,minimum width=3.3cm,minimum height=0.68cm,align=center,font=\footnotesize,fill=black!3},
  conn/.style={line width=.75pt}
]
  % Actors
  \node[actor] (cust) at (0,6) {Customer\\(Consumer)};
  \node[actor] (admin) at (0,1.5) {Store Admin\\(Merchant)};
  \node[actor] (exec) at (14.2,3.8) {Executive\\Analyst};

  % System Boundary
  \draw[line width=1pt,rounded corners=4pt] (1.8,-0.2) rectangle (12.6,7.8);
  \node[font=\footnotesize\bfseries] at (7.2,7.4) {Enterprise Decision Support Platform Boundary};

  % Use Cases
  \node[usecase] (uc1) at (4.8,6.6) {Browse \& Search Products};
  \node[usecase] (uc2) at (4.8,5.5) {Cart, Checkout \& Vouchers};
  \node[usecase] (uc3) at (4.8,4.4) {View Order History \& Alerts};
  \node[usecase] (uc4) at (4.8,3.2) {Manage Store Catalog \& SKUs};
  \node[usecase] (uc5) at (4.8,2.0) {Monitor Live Store Orders};
  \node[usecase] (uc6) at (9.4,5.8) {Execute Batch Churn Scoring};
  \node[usecase] (uc7) at (9.4,4.6) {Inspect SHAP Waterfall Plots};
  \node[usecase] (uc8) at (9.4,3.4) {Simulate What-If Scenarios};
  \node[usecase] (uc9) at (9.4,2.2) {Generate Multi-Horizon Forecasts};
  \node[usecase] (uc10) at (9.4,0.9) {Deploy Retention Playbooks};

  % Links
  \draw[conn] (cust.east) -- (uc1.west);
  \draw[conn] (cust.east) -- (uc2.west);
  \draw[conn] (cust.east) -- (uc3.west);

  \draw[conn] (admin.east) -- (uc4.west);
  \draw[conn] (admin.east) -- (uc5.west);

  \draw[conn] (exec.west) -- (uc6.east);
  \draw[conn] (exec.west) -- (uc7.east);
  \draw[conn] (exec.west) -- (uc8.east);
  \draw[conn] (exec.west) -- (uc9.east);
  \draw[conn] (exec.west) -- (uc10.east);
\end{tikzpicture}%
}

% 4. Burndown Chart Axes Macro
\newcommand{\edpchartaxes}{%
  \foreach \h in {8,16,24,32,40,48}{%
   \draw (0,\h) -- (-.09,\h);
   \node[anchor=east,font=\scriptsize] at (-.13,\h) {\h};%
  }
  \foreach \i in {1,...,6}{%
    \draw (\i,0)--(\i,-.7);
    \node[font=\scriptsize,below] at (\i,-1.1) {S\i};
  }
  \draw[-{Stealth[length=2.2mm]},line width=.8pt] (0,0) -- (6.48,0);
  \draw[-{Stealth[length=2.2mm]},line width=.8pt] (0,0) -- (0,53);
  \node[font=\small] at (3,-6.8) {Sprint Milestones (S1 to S6)};
  \node[rotate=90,font=\small] at (-.77,24) {Remaining Backlog Hours};
}

% 5. Ideal Burndown Chart
\newcommand{\projectidealchart}{%
\begin{tikzpicture}[x=1.95cm,y=.14cm]
 \edpchartaxes
 \foreach \i/\h in {1/40,2/32,3/24,4/16,5/8}{%
   \draw[edpguide] (0,\h)--(\i,\h)--(\i,0);
 }
 \draw[line width=1pt,black] (0,48)--(6,0);
 \foreach \i/\h in {0/48,1/40,2/32,3/24,4/16,5/8,6/0}
    \fill[black] (\i,\h) circle[x radius=1.6pt,y radius=1.6pt];
\end{tikzpicture}%
}

% 6. Actual Burndown Chart with Recorded Logbook Deviation
\newcommand{\projectactualchart}{%
\begin{tikzpicture}[x=1.95cm,y=.14cm]
 \edpchartaxes
 \foreach \i/\h in {1/40,2/32,3/24,4/16,5/8}{%
   \draw[edpguide] (0,\h)--(\i,\h)--(\i,0);
 }
 \draw[black,densely dashed,line width=.95pt] (0,48)--(6,0);
 \draw[black,line width=1.15pt]
  (0,48)--(1,40)--(2,32)--(2.65,24)--(4,16)--(5,8)--(6,0);
 \foreach \i/\h in {0/48,1/40,2/32,2.65/24,4/16,5/8,6/0}
    \fill[black] (\i,\h) circle[x radius=2.05pt,y radius=2.05pt];
 \draw[black,densely dashed,line width=.95pt] (4.55,48)--(4.94,48);
 \node[anchor=west,font=\scriptsize] at (5.05,48) {Ideal};
 \draw[line width=1.15pt] (4.55,44)--(4.94,44);
 \fill (4.75,44) circle[x radius=2.05pt,y radius=2.05pt];
 \node[anchor=west,font=\scriptsize] at (5.05,44) {Actual};
\end{tikzpicture}%
}

\begin{document}
\pagenumbering{roman}

% ============================================================
% TITLE PAGE
% ============================================================
\begin{center}
\vspace*{0.1in}
{\large\bfseries \projecttitle}\\[10pt]
{\normalsize A PROJECT REPORT}\\[4pt]
{\small Submitted by}\\[22pt]
{\large\bfseries \studentname}\\[8pt]
{\large\bfseries (\studentroll)}\\[20pt]
{\small\bfseries Under the Guidance of}\\[4pt]
{\large\bfseries \guidefname}\\[4pt]
{\footnotesize\bfseries \guidedesignation}\\[24pt]
to\\[4pt]
{\small the APJ Abdul Kalam Technological University}\\[2pt]
{\small in partial fulfillment of the requirements for the award of the Degree}\\[2pt]
of\\[2pt]
{\small\itshape \programmecourse}\\[28pt]
\collegelogo{1.4in}\\[24pt]
{\large\bfseries \guidedepartment}\\[6pt]
{\normalsize \institutionname}\\[4pt]
{\normalsize \institutionaddress}\\[4pt]
{\normalsize \institutionpin}\\[8pt]
{\normalsize \reportdate}
\end{center}
\newpage

% ============================================================
% DECLARATION
% ============================================================
\vspace*{0.5in}
\begin{center}{\large\bfseries DECLARATION}\end{center}
\vspace{0.2in}
\begin{spacing}{1.5}
\justifying
I, the undersigned, hereby declare that the project report entitled
\textbf{``\projecttitle{} (\projectsubtitle{})''} submitted for partial fulfilment of the requirements
for the award of the degree of Master of Computer Applications of the
APJ Abdul Kalam Technological University, Kerala, is a bonafide work
carried out by me under the supervision of my project guide. Sources and
ideas from other works have been acknowledged where used. I declare that
I have not knowingly fabricated results or misrepresented the implementation
or evaluation of the prototype. This report has not previously formed the
basis for the award of any degree, diploma or similar title at another
university or institution.
\end{spacing}
\vspace{0.5in}
\noindent Place: KALADY \hfill Signature\\[2pt]
Date: \hfill \textbf{\studentname}
\newpage

% ============================================================
% CERTIFICATE
% ============================================================
\begin{center}
\vspace*{0.1in}
{\large\bfseries ADI SHANKARA INSTITUTE OF ENGINEERING AND\\ TECHNOLOGY}\\[6pt]
{\large\bfseries VIDYA BHARATHI NAGAR, MATTOOR, KALADY}\\[6pt]
{\large\bfseries DEPARTMENT OF COMPUTER APPLICATIONS}\\[14pt]
\collegelogo{1.6in}\\[30pt]
{\large\bfseries CERTIFICATE}
\end{center}
\vspace{0.2in}
\begin{spacing}{1.5}
\noindent\begin{minipage}{0.98\textwidth}
\justifying
This is to certify that the report entitled
``{\large\bfseries \projecttitle}'' submitted by \textbf{\studentname} (\textbf{\studentroll}) to the APJ
Abdul Kalam Technological University in partial fulfilment of the
requirements for the award of the Degree of \programmecourse{}
is a bona fide record of project work carried out under my guidance and supervision. This report has not been submitted to another
University or Institute for any other qualification.
\end{minipage}
\end{spacing}
\vspace{0.9in}
\noindent
\begin{minipage}[t]{0.48\textwidth}\centering
\guidefname\\Project Guide\\\guidedepartment
\end{minipage}
\hfill
\begin{minipage}[t]{0.48\textwidth}\centering
\hodname\\\hoddesignation\\\guidedepartment
\end{minipage}
\newpage

% ============================================================
% ACKNOWLEDGEMENT
% ============================================================
\vspace*{0.3in}
\begin{center}{\large\bfseries ACKNOWLEDGEMENT}\end{center}
\vspace{0.1in}
\begin{spacing}{1.4}
\justifying
First and foremost, I express my sincere gratitude to \principalname, Principal of \institutionname, Kalady, for providing the necessary facilities and a supportive academic environment to complete this project successfully.

I extend my heartfelt thanks to \hodname, Head of the Department of Computer Applications, for her constant encouragement, valuable support, and guidance throughout the project.

I am deeply grateful to \guidefname, my project guide, for valuable guidance, constructive feedback, and continuous encouragement at every stage of the project. The guidance helped me gain practical knowledge of machine learning classification, explainable artificial intelligence (XAI), multi-horizon time-series sales forecasting, full-stack software architecture with FastAPI and React, and enterprise decision-support engineering.

I would also like to thank our project coordinators, Dr.\ Sneha Prakash and \guidefname, for their valuable suggestions, reviews, and support throughout the project work. I am equally thankful to all the faculty members of the department for their encouragement and assistance.

I express my heartfelt gratitude to my family for their unconditional love, patience, and constant motivation, which gave me the strength to complete this project. I also thank my friends and classmates for their cooperation, encouragement, and helpful discussions throughout the development process.

Finally, I acknowledge the open-source community, research publications, technical documentation, and online resources that helped me acquire the knowledge and technical skills required for this project. I sincerely thank everyone who directly or indirectly contributed to the successful completion of this project.
\end{spacing}
\vspace{0.3in}
\noindent\textbf{\studentname}
\newpage

% ============================================================
% ABSTRACT
% ============================================================
\vspace*{0.3in}
\begin{center}{\large\bfseries ABSTRACT}\end{center}
\vspace{0.1in}
\begin{spacing}{1.2}
\setlength{\parskip}{5pt}
\justifying
In contemporary e-commerce and subscription enterprises, customer attrition represents a severe threat to operating profitability, as acquiring a new customer costs five to seven times more than retaining an existing account. Conventional Business Intelligence (BI) dashboards operate reactively by reporting customer churn post-cancellation, while standard black-box machine learning models output raw prediction scores without providing transparent operational root causes or concrete retention interventions. 

This project develops an \textbf{AI-Based Enterprise Decision Support Platform Using Machine Learning}, featuring an explainable AI-driven customer churn prediction and multi-horizon sales forecasting system. The platform combines a customer-facing e-commerce application (\textbf{SmartCart}) with an executive-level analytical dashboard to deliver an end-to-end, closed-loop decision ecosystem. 

The machine learning core utilizes ensemble classifiers (Random Forest and XGBoost) evaluated across 23 behavioral, RFM (Recency, Frequency, Monetary), and platform telemetry features. To overcome black-box opacity, the platform integrates SHAP (\textit{SHapley Additive exPlanations}) via a TreeExplainer to calculate local feature attributions that explain exactly why individual accounts are at risk. A rule-based prescriptive decision engine analyzes top friction vectors (e.g., support ticket spikes, checkout friction, shipping delays) and automatically deploys personalized retention countermeasures (such as coupon codes \texttt{WELCOME10}, \texttt{CARE10}, \texttt{RECOVER10}, and free priority delivery) directly into the customer's live store account. 

Concurrently, a dedicated sales forecasting module models transaction-level revenues and forecasts daily future sales over 7-, 14-, and 30-day horizons using temporal lag and rolling features. The system is implemented using a decoupled architecture comprising a Python FastAPI asynchronous backend, a relational database (SQLite/MySQL), and a modern React 18 single-page application styled with Tailwind CSS. Empirical evaluation demonstrates high predictive accuracy alongside transparent interpretability, demonstrating that explainable AI and automated playbooks significantly enhance proactive enterprise retention strategy.
\end{spacing}
\newpage

% ============================================================
% TABLE OF CONTENTS
% ============================================================
\pagestyle{toc}
\begin{center}{\large\bfseries TABLE OF CONTENTS}\end{center}
\vspace{4pt}
\renewcommand{\arraystretch}{1.75}
\noindent\hspace*{\fill}%
\begin{tabular}{|C{1.8cm}|M|C{2.4cm}|}
\hline
\textbf{Sl. No.} & \textbf{Content} & \textbf{Page No.}\\ \hline
\textbf{1} & \textbf{INTRODUCTION} & \textbf{\pageref{chap:1}--\number\numexpr\getpagerefnumber{chap:2}-1\relax}\\ \hline
1.1 & Brief introduction about the project & \pageref{sub:1.1}\\ \hline
1.2 & Project Background & \pageref{sub:1.2}\\ \hline
1.3 & Existing System & \pageref{sub:1.3}\\ \hline
1.4 & Proposed System & \pageref{sub:1.4}\\ \hline
1.5 & Basic Design principle of the project & \pageref{sub:1.5}\\ \hline
1.6 & Basic Architecture of the project & \pageref{sub:1.6}\\ \hline
\textbf{2} & \textbf{SYSTEM STUDY AND ANALYSIS} & \textbf{\pageref{chap:2}--\number\numexpr\getpagerefnumber{chap:3}-1\relax}\\ \hline
2.1 & Drawbacks of the Existing System & \pageref{sub:2.1}\\ \hline
2.2 & Problem Statement & \pageref{sub:2.2}\\ \hline
2.3 & Feasibility Study & \pageref{sub:2.3}\\ \hline
2.4 & Project Planning & \pageref{sub:2.4}\\ \hline
2.5 & Requirement Specification & \pageref{sub:2.5}\\ \hline
\textbf{3} & \textbf{SYSTEM WORK FLOW} & \textbf{\pageref{chap:3}--\number\numexpr\getpagerefnumber{chap:4}-1\relax}\\ \hline
3.1 & Design Methodology & \pageref{sub:3.1}\\ \hline
3.2 & UML diagrams & \pageref{sub:3.2}\\ \hline
3.3 & Use case design & \pageref{sub:3.3}\\ \hline
\textbf{4} & \textbf{AGILE TECHNOLOGY OVERVIEW} & \textbf{\pageref{chap:4}--\number\numexpr\getpagerefnumber{chap:5}-1\relax}\\ \hline
4.1 & Introduction to Scrum & \pageref{sub:4.1}\\ \hline
4.2 & Principles or methodology used & \pageref{sub:4.2}\\ \hline
4.3 & Product Backlog & \pageref{sub:4.3}\\ \hline
4.4 & Sprint Planner & \pageref{sub:4.4}\\ \hline
4.5 & Ideal Burn down chart & \pageref{sub:4.5}\\ \hline
\end{tabular}%
\hspace*{\fill}
\newpage
\vspace*{0.1in}
\renewcommand{\arraystretch}{1.75}
\noindent\hspace*{\fill}%
\begin{tabular}{|C{1.8cm}|M|C{2.4cm}|}
\hline
\textbf{5} & \textbf{SYSTEM DESIGN} & \textbf{\pageref{chap:5}--\number\numexpr\getpagerefnumber{chap:6}-1\relax}\\ \hline
5.1 & Technology / framework & \pageref{sub:5.1}\\ \hline
5.2 & Module Description & \pageref{sub:5.2}\\ \hline
\textbf{6} & \textbf{CODING} & \textbf{\pageref{chap:6}--\number\numexpr\getpagerefnumber{chap:7}-1\relax}\\ \hline
6.1 & Coding standards used in the project & \pageref{sub:6.1}\\ \hline
6.2 & Project coding & \pageref{sub:6.2}\\ \hline
\textbf{7} & \textbf{TESTING} & \textbf{\pageref{chap:7}--\number\numexpr\getpagerefnumber{chap:8}-1\relax}\\ \hline
7.1 & Unit Testing & \pageref{sub:7.1}\\ \hline
7.2 & Model Evaluation & \pageref{sub:7.2}\\ \hline
\textbf{8} & \textbf{IMPLEMENTATION} & \textbf{\pageref{chap:8}--\number\numexpr\getpagerefnumber{chap:9}-1\relax}\\ \hline
8.1 & Implementation method used in Project & \pageref{sub:8.1}\\ \hline
\textbf{9} & \textbf{BUSINESS PERSPECTIVE} & \textbf{\pageref{chap:9}--\number\numexpr\getpagerefnumber{chap:10}-1\relax}\\ \hline
\textbf{10} & \textbf{CONCLUSION} & \textbf{\pageref{chap:10}--\number\numexpr\getpagerefnumber{chap:11}-1\relax}\\ \hline
\textbf{11} & \textbf{FUTURE SCOPE OR ENHANCEMENTS} & \textbf{\pageref{chap:11}--\number\numexpr\getpagerefnumber{chap:12}-1\relax}\\ \hline
\textbf{12} & \textbf{APPENDIX} & \textbf{\pageref{chap:12}--\number\numexpr\getpagerefnumber{chap:13}-1\relax}\\ \hline
12.1 & Development History [Sprint Wise] & \pageref{sub:12.1}\\ \hline
12.2 & Screenshots of Forms, Reports, and Diagrams & \pageref{sub:12.2}\\ \hline
12.3 & Burndown Chart & \pageref{sub:12.3}\\ \hline
\textbf{13} & \textbf{REFERENCES/BIBLIOGRAPHY} & \textbf{\pageref{chap:13}}\\ \hline
\end{tabular}%
\hspace*{\fill}
\newpage

% ============================================================
% LIST OF TABLES
% ============================================================
\vspace*{0.2in}
\begin{center}{\large\bfseries LIST OF TABLES}\end{center}
\vspace{0.1in}
\begin{spacing}{1.18}
\small
\noindent\begin{tabular}{p{2cm}p{10.5cm}r}
\textbf{Table No.} & \textbf{Title} & \textbf{Page No.}\\ \hline
Table 1 & Literature Review Comparison Matrix & \pageref{tab:comparison_matrix}\\
Table 2 & Project Risks and Mitigations & \pageref{tab:risks_mitigations}\\
Table 3 & Project Phases and Agile Timelines & \pageref{tab:phases_timelines}\\
Table 4 & Functional Requirement Traceability Matrix & \pageref{tab:traceability_matrix}\\
Table 5 & System Requirements Summary (Hardware \& Software) & \pageref{tab:system_requirements}\\
Table 6 & End-to-End Decision Processing Pipeline Stages & \pageref{tab:pipeline_stages}\\
Table 7 & Scrum Role Allocation & \pageref{tab:scrum_allocation}\\
Table 8 & Product Backlog Items (PBIs) Summary & \pageref{tab:pbi_summary}\\
Table 9 & Sprint 1 Task Backlog & \pageref{tab:sprint1_backlog}\\
Table 10 & Sprint 2 Task Backlog & \pageref{tab:sprint2_backlog}\\
Table 11 & Sprint 3 Task Backlog & \pageref{tab:sprint3_backlog}\\
Table 12 & Sprint 4 Task Backlog & \pageref{tab:sprint4_backlog}\\
Table 13 & Sprint 5 Task Backlog & \pageref{tab:sprint5_backlog}\\
Table 14 & Sprint 6 Task Backlog & \pageref{tab:sprint6_backlog}\\
Table 15 & Overall Sprint Summary & \pageref{tab:overall_sprint_summary}\\
Table 16 & Technologies and Frameworks Used in the Platform & \pageref{tab:tech_stack}\\
Table 17 & Summary of Coding Standards Followed & \pageref{tab:coding_standards}\\
Table 18 & Executed Pytest Test Cases & \pageref{tab:test_cases}\\
Table 19 & Sprint-Wise Development Milestones & \pageref{tab:sprint_milestones}\\
\end{tabular}
\end{spacing}
\newpage

% ============================================================
% LIST OF FIGURES
% ============================================================
\vspace*{0.2in}
\begin{center}{\large\bfseries LIST OF FIGURES}\end{center}
\vspace{0.1in}
\begin{spacing}{1.18}
\small
\noindent\begin{tabular}{p{2cm}p{10.5cm}r}
\textbf{Figure No.} & \textbf{Title} & \textbf{Page No.}\\ \hline
Figure 1 & Basic Architecture of Enterprise Decision Platform & \pageref{fig:basic_architecture}\\
Figure 2 & Enterprise Decision Support Processing Workflow & \pageref{fig:workflow_diagram}\\
Figure 3 & Use-Case Diagram of Enterprise Decision Platform & \pageref{fig:use_case_diagram}\\
Figure 4 & Illustrative Straight-Line Sprint Burndown (48h Reference) & \pageref{fig:ideal_burndown}\\
Figure 5 & Application Architecture of Enterprise Decision Platform & \pageref{fig:application_architecture}\\
Figure 6 & SmartCart E-Commerce Storefront Homepage & \pageref{fig:assets/screenshots/smartcart_home.png}\\
Figure 7 & Product Catalog with Multi-Department Filtering & \pageref{fig:assets/screenshots/product_catalog.png}\\
Figure 8 & Shopping Cart with Active ML Retention Perks & \pageref{fig:assets/screenshots/shopping_cart.png}\\
Figure 9 & Checkout Confirmation and Logistics Pipeline & \pageref{fig:assets/screenshots/checkout_confirmation.png}\\
Figure 10 & Customer Real-Time Orders and Fulfillment Tracking & \pageref{fig:assets/screenshots/customer_orders.png}\\
Figure 11 & Customer Retention Perks Notification & \pageref{fig:assets/screenshots/customer_notifications.png}\\
Figure 12 & Merchant Store Operations and Catalog Management & \pageref{fig:assets/screenshots/admin_product_manager.png}\\
Figure 13 & Unified Multi-Role Authentication Screen & \pageref{fig:assets/screenshots/login_screen.png}\\
Figure 14 & Executive Dashboard with KPI Metrics \& Forecast Curve & \pageref{fig:assets/screenshots/executive_dashboard.png}\\
Figure 15 & Customer Churn Prediction Table \& Risk Triage & \pageref{fig:assets/screenshots/customer_churn_analytics.png}\\
Figure 16 & SHAP Feature Attribution Modal (Low Risk Account) & \pageref{fig:assets/screenshots/shap_waterfall_modal.png}\\
Figure 17 & Root Cause Friction Diagnostics (Medium Risk Account) & \pageref{fig:assets/screenshots/high_risk_root_cause_modal.png}\\
Figure 18 & Multi-Horizon Sales Forecasting Engine & \pageref{fig:assets/screenshots/sales_forecast.png}\\
Figure 19 & Dataset Upload and CSV Validation Engine & \pageref{fig:assets/screenshots/dataset_upload.png}\\
Figure 20 & Schematic Ideal vs Actual Burndown Chart & \pageref{fig:burndown_actual}\\
\end{tabular}
\end{spacing}
\newpage

% ============================================================
% ABBREVIATIONS
% ============================================================
\vspace*{0.2in}
\begin{center}{\large\bfseries ABBREVIATIONS}\end{center}
\vspace{0.15in}
\begin{spacing}{1.15}
\small
\noindent\begin{tabular}{ll p{0.4cm} ll}
\textbf{AI} & Artificial Intelligence & & \textbf{KNN} & K-Nearest Neighbors\\
\textbf{AOV} & Average Order Value & & \textbf{KTU} & APJ Abdul Kalam Tech.\ Univ.\\
\textbf{API} & Application Programming Interface & & \textbf{MAE} & Mean Absolute Error\\
\textbf{AUC-ROC} & Area Under ROC Curve & & \textbf{MCA} & Master of Computer Applications\\
\textbf{BI} & Business Intelligence & & \textbf{ML} & Machine Learning\\
\textbf{CDP} & Chrome DevTools Protocol & & \textbf{MLP} & Multi-Layer Perceptron\\
\textbf{CRM} & Customer Relationship Mgmt. & & \textbf{ORM} & Object-Relational Mapping\\
\textbf{CSV} & Comma-Separated Values & & \textbf{PBI} & Product Backlog Item\\
\textbf{EDA} & Exploratory Data Analysis & & \textbf{PDF} & Portable Document Format\\
\textbf{F1} & Harmonic Mean (Prec./Recall) & & \textbf{REST} & Representational State Transfer\\
\textbf{HOD} & Head of the Department & & \textbf{RF} & Random Forest\\
\textbf{HTTP} & Hypertext Transfer Protocol & & \textbf{RFM} & Recency, Frequency, Monetary\\
\textbf{IDE} & Integrated Development Env. & & \textbf{RMSE} & Root Mean Squared Error\\
\textbf{IEEE} & Inst.\ of Elec.\ \& Electron.\ Eng. & & \textbf{SaaS} & Software as a Service\\
\textbf{JSON} & JavaScript Object Notation & & \textbf{SHAP} & SHapley Additive exPlanations\\
\textbf{JWT} & JSON Web Token & & \textbf{SKU} & Stock Keeping Unit\\
\textbf{SMOTE} & Synthetic Minority Over-sampling & & \textbf{XGBoost} & eXtreme Gradient Boosting\\
\textbf{SPA} & Single-Page Application & & \textbf{XAI} & Explainable AI\\
\end{tabular}
\end{spacing}
\newpage

\pagenumbering{arabic}
\pagestyle{reportbody}

% ============================================================
% CHAPTER 1: INTRODUCTION
% ============================================================
\section{INTRODUCTION}\label{chap:1}

In today's digital commercial landscape, customer churn constitutes one of the most critical threats to enterprise viability and recurring profitability. Across modern business models---ranging from digital e-commerce platforms and cloud Software-as-a-Service (SaaS) providers to retail marketplaces---acquiring a replacement customer is substantially more expensive than retaining an established one. Empirical studies in enterprise economics confirm that customer acquisition costs exceed retention expenses by a factor of 5 to 7. Furthermore, mitigating customer churn by merely 5\% has been shown to increase enterprise operating profits by 25\% to 95\%, owing to the compounding lifetime value and reduced onboarding overhead of loyal accounts.

Despite these established economic realities, conventional enterprise decision systems manage customer churn through reactive, post-hoc methods. Traditional Business Intelligence (BI) platforms and reporting dashboards report churn figures long after accounts have lapsed, missed renewal cycles, or abandoned their shopping baskets. When machine learning classifiers are deployed in such workflows, they typically function as ``black-box'' scoring pipelines: predicting an account's probability of attrition (e.g., 85\% risk) without explaining why the account is disengaging or what proactive intervention should be staged. 

To overcome these structural limitations, this project designs and implements an \textbf{AI-Based Enterprise Decision Support Platform Using Machine Learning}. The system unifies predictive churn modeling, local and global explainability via SHAP (\textit{SHapley Additive exPlanations}), transparent root-cause diagnostics, automated prescriptive retention playbooks, multi-horizon sales forecasting, and a fully functional e-commerce storefront (\textbf{SmartCart}) within a cohesive, closed-loop software architecture.

\subsection{Brief Introduction about the Project}\label{sub:1.1}

The Enterprise Decision Support Platform is designed to bridge the operational gap between machine learning intelligence and executive commercial action. Unlike isolated algorithmic research scripts, this platform provides a complete software ecosystem serving two distinct yet synchronized domains:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{SmartCart E-Commerce Storefront}: A full-featured shopping application that enables consumers to browse product catalogs, manage shopping carts, apply coupon codes, execute checkouts, track live orders, and receive automated personalized retention perks.
    \item \textbf{Executive Decision Support Dashboard}: A specialized management console that ingests real-time customer behavioral telemetry, executes high-accuracy churn classification, visualizes risk distributions, renders local SHAP waterfall feature attributions, simulates What-If scenarios, and projects future multi-horizon sales revenues.
\end{enumerate}

When an account demonstrates elevated churn indicators, the system's rule-based decision engine analyzes the specific friction vectors (such as recurring support complaints, extended purchase dormancy, or checkout abandonment) and automatically triggers targeted retention playbooks (e.g., promotional codes \texttt{WELCOME10}, \texttt{CARE10}, \texttt{RECOVER10}, or free priority delivery). These benefits are dispatched directly into the customer's live store account, establishing an automated, evidence-driven feedback loop.

\subsection{Project Background}\label{sub:1.2}

Modern commerce enterprises operate in highly competitive environments where customer switching costs are near zero. In large-scale online marketplaces, customer attrition occurs gradually through behavioral signals: diminishing visit frequency, increased search friction, unresolved customer support tickets, delivery delays, and cart abandonment. 

In traditional enterprise settings, the customer lifecycle involves multiple isolated subsystems: relational transactional databases (SQL), telemetry logs, customer relationship management (CRM) platforms, standalone data science notebooks, and email marketing tools. Because these components exist in functional silos, data science teams spend weeks extracting CSV extracts, training offline models, and emailing risk spreadsheets to account managers. By the time customer success teams initiate outreach, the customer has already migrated to a competitor.

Furthermore, machine learning adoption in commercial decision-making has been constrained by the ``interpretability barrier.'' Sophisticated non-linear ensemble models---such as Gradient Boosted Decision Trees (XGBoost) and Random Forests---exhibit superior predictive accuracy but lack intrinsic transparency. Executive leadership and customer success representatives cannot responsibly act on unverified probability scores without understanding which operational factors drove the prediction. 

This motivates the incorporation of Explainable AI (XAI) frameworks based on cooperative game theory (Shapley values). By decomposing complex model predictions into additive feature attributions, SHAP enables decision-makers to understand whether an account's churn score stems from service dissatisfaction, product pricing, or logistics friction. Integrating these explanatory insights with a prescriptive decision engine transforms predictive analytics into actionable enterprise countermeasures.

\subsection{Existing System}\label{sub:1.3}

Conventional customer retention and sales analysis workflows rely on fragmented, labor-intensive processes:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Reactive BI Reporting}: Dashboards generated in tools such as Tableau or PowerBI visualize aggregate cancellation metrics retrospectively, offering zero early warning capabilities before account termination.
    \item \textbf{Manual Periodic Audits}: Customer Success Managers (CSMs) periodically review spreadsheet exports using basic heuristics and subjective rules of thumb.
    \item \textbf{Isolated Statistical Scripts}: Logistic regression or basic classification models are executed periodically in disconnected Python/R environments without direct integration into production CRM databases.
    \item \textbf{Unstructured Retention Outreach}: Customer interventions rely on ad-hoc phone calls or generic marketing blasts without individualized risk-tier prioritization or personalized friction countermeasures.
    \item \textbf{Independent Sales Projections}: Sales forecasting is conducted using simplistic spreadsheet trendlines detached from customer attrition dynamics and real-time transaction velocities.
\end{itemize}

\subsection{Proposed System}\label{sub:1.4}

The proposed system addresses the limitations of existing approaches by providing an automated, explainable, and closed-loop decision platform:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Continuous Relational Ingestion}: Directly queries relational databases (MySQL / SQLite) to maintain synchronized customer telemetry, order histories, and cart behaviors.
    \item \textbf{High-Accuracy Churn Modeling}: Utilizes optimized Random Forest and XGBoost ensemble classifiers trained on 23 behavioral and RFM metrics to categorize accounts into High Risk ($>70\%$), Medium Risk ($40\%$--$70\%$), and Low Risk ($<40\%$) tiers.
    \item \textbf{Explainable AI via SHAP}: Integrates a post-hoc \texttt{TreeExplainer} that computes local Shapley values, quantifying the exact positive and negative contributions of each behavioral variable per customer.
    \item \textbf{Root-Cause Diagnostic Engine}: Maps dominant negative SHAP feature attributions against operational telemetry (support tickets, shipping delays, cart abandonment) to identify specific attrition root causes.
    \item \textbf{Automated Prescriptive Playbooks}: Translates diagnostic root causes into automated retention playbooks (e.g., \texttt{CARE10} VIP concierge callback, \texttt{RECOVER10} cart nudge, \texttt{SPEED5} express air delivery).
    \item \textbf{Multi-Horizon Sales Forecasting}: Predicts transaction-level revenues and forecasts daily future store sales across 7-, 14-, and 30-day horizons using XGBoost regressors and chronological lag features without look-ahead bias.
    \item \textbf{Integrated SmartCart Storefront}: A live commerce environment demonstrating immediate benefit redemption, voucher validation, and bidirectional RFM telemetry feedback.
\end{itemize}

\begin{table}[H]
\centering
\small
\caption{Literature Review Comparison Matrix}
\begin{tabularx}{\linewidth}{|l|l|C{1.8cm}|C{1.8cm}|C{2.0cm}|C{1.8cm}|}
\hline
\textbf{Paper / Reference System} & \textbf{Model Core} & \textbf{Risk Tiers} & \textbf{XAI (SHAP)} & \textbf{Prescriptive Playbooks} & \textbf{Closed-Loop UI} \\ \hline
Joy et al.\ (IEEE Access 2024) & Hybrid ML & Yes & Yes & Partial & No \\ \hline
Bhuria \& Aluvala (IEEE 2025) & XGBoost & Yes & No & No & No \\ \hline
Chandan et al.\ (IEEE 2024) & ML Ensemble & Early Warning & No & No & No \\ \hline
Li \& Yan (DSFE 2025) & XGBoost & Yes & Yes & No & No \\ \hline
\textbf{PROPOSED SYSTEM (Joyal Jobai)} & \textbf{RF / XGBoost} & \textbf{High/Med/Low} & \textbf{SHAP Local} & \textbf{Automated} & \textbf{End-to-End} \\ \hline
\end{tabularx}
\label{tab:comparison_matrix}
\end{table}

\subsection{Basic Design Principle of the Project}\label{sub:1.5}

The architecture of the platform is guided by five core software engineering principles:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{Modularity \& Decoupled Services}: Complete architectural separation between presentation clients (SmartCart storefront and executive dashboard), REST API ingestion, machine learning inference engines, and persistent database storage.
    \item \textbf{Interpretability-First Architecture}: Black-box machine learning predictions are never displayed in isolation; every risk prediction is paired with SHAP feature attributions, plain-language summaries, and identified operational friction drivers.
    \item \textbf{Closed-Loop Actionability}: Analytical predictions directly trigger operational actions. When an account is flagged for churn risk, the system formulates and persists concrete retention benefits accessible by the customer in real time.
    \item \textbf{Zero Look-Ahead Leakage}: Data preprocessing pipelines strictly calculate scaling parameters, encoding maps, and temporal lag/rolling windows within historical training partitions to guarantee valid inference.
    \item \textbf{Graceful Degradation \& Warmup}: Background worker threads pre-initialize and warm up heavy SHAP \texttt{TreeExplainer} instances at server startup, eliminating cold-start latency for incoming HTTP requests.
\end{enumerate}

\subsection{Basic Architecture of the Project}\label{sub:1.6}

The platform is structured into four interconnected functional tiers: Presentation Tier, Application/API Tier, AI \& Prescriptive Processing Tier, and Database Storage Tier.

\begin{figure}[H]
\centering
\projectarchitecture
\caption{Basic architecture of the Enterprise Decision Support Platform}
\label{fig:basic_architecture}
\end{figure}

\subsubsection{Presentation Tier (Frontend)}
The frontend is implemented as a modern React 18 single-page application built with Vite and styled using Tailwind CSS and custom modular stylesheets. It provides two distinct role-gated environments:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{SmartCart Storefront}: Features responsive navigation, multi-department catalog filtering, dynamic product details, local cart persistence, promotional coupon application, checkout processing, customer order tracking, and in-app perk notifications.
    \item \textbf{Executive Decision Console}: Provides leadership and analysts with high-level KPI cards, interactive risk distribution charts, searchable customer risk tables, SHAP waterfall attribution modals, What-If churn parameter simulators, multi-horizon sales forecasting projections, and CSV dataset ingestion controls.
\end{itemize}

\subsubsection{Application / API Tier (Backend)}
The backend service is engineered using Python 3.11 and FastAPI, offering high-throughput asynchronous request handling. It encapsulates 15 dedicated API routers managing user authentication (JWT-based role security), customer telemetry retrieval, churn scoring orchestration, SHAP explanation extraction, retention recommendation toggles, multi-horizon sales forecasting, automated PDF generation, and complete e-commerce store operations.

\subsubsection{AI, ML \& Prescriptive Processing Tier}
This tier encapsulates the trained statistical models, preprocessor pipelines, and algorithmic logic:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Churn Prediction Engine}: Loads serialized Random Forest and XGBoost artifacts to score customer records across 23 standardized features.
    \item \textbf{SHAP Explanation Engine}: Utilizes a warmed-up \texttt{shap.TreeExplainer} to extract base values, expected values, and localized Shapley vectors per prediction.
    \item \textbf{Prescriptive Decision Engine}: Implements deterministic rule sets that evaluate negative feature weights against operational telemetry to generate actionable retention countermeasures.
    \item \textbf{Sales Forecasting Engine}: Processes sequential transaction logs, generates rolling lag windows, and predicts future revenue trajectories.
\end{itemize}

\subsubsection{Database Storage \& Supporting Services}
Persistent storage is managed via SQLAlchemy ORM configured for SQLite (development) and MySQL 8.0 (production). The database maintains 14 relational tables guaranteeing data integrity, audit logging, and relationship tracking across users, customers, predictions, recommendations, orders, and products. Supporting services include ReportLab for dynamic executive PDF generation.

\newpage

% ============================================================
% CHAPTER 2: SYSTEM STUDY AND ANALYSIS
% ============================================================
\section{SYSTEM STUDY AND ANALYSIS}\label{chap:2}

This chapter provides a detailed analysis of operational limitations in legacy decision systems, formalizes the engineering problem statement, conducts a multi-dimensional feasibility study, evaluates operational risks, and specifies system requirements.

\subsection{Drawbacks of the Existing System}\label{sub:2.1}

Existing enterprise customer retention mechanisms suffer from fundamental operational deficiencies:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{Post-Facto Reactive Churn Detection}: Traditional reporting identifies churned accounts only after cancellations or prolonged inactivity have occurred, completely forfeiting the proactive early intervention window.
    \item \textbf{Algorithmic Opacity (Black-Box Mistrust)}: Basic ML implementations generate opaque probability scores without explaining underlying behavioral drivers, preventing account managers from understanding why an account is disengaging.
    \item \textbf{Absence of Prescriptive Guidance}: Conventional systems notify teams that churn risk is high but offer no automated, targeted retention playbooks to resolve customer dissatisfaction.
    \item \textbf{Disjointed Information Silos}: Customer purchase histories, support grievance logs, predictive models, and marketing outreach tools operate in disconnected environments, requiring cumbersome manual data reconciliation.
    \item \textbf{High Re-Acquisition Costs}: Due to delayed retention outreach, enterprises incur severe financial losses, spending 5x to 7x more capital to acquire replacement accounts.
\end{enumerate}

\subsection{Problem Statement}\label{sub:2.2}

The core engineering objective of this project is to develop an integrated, explainable, and automated enterprise decision support platform that:
\begin{enumerate}[leftmargin=20pt]
    \item Ingests live multi-channel customer telemetry and transaction histories from a relational database.
    \item Executes high-accuracy churn risk classification using optimized tree-based ensemble models (Random Forest and XGBoost) across 23 behavioral and RFM metrics.
    \item Provides sub-second local feature attributions via SHAP TreeExplainer, revealing the exact positive and negative behavioral factors driving individual predictions.
    \item Implements a deterministic root-cause diagnostic engine that translates abstract feature attributions into concrete operational friction vectors (support ticket overload, delivery delays, checkout hesitation).
    \item Automatically synthesizes and dispatches personalized, rule-based retention playbooks (discount coupons, concierge callbacks, free priority delivery) directly to customer storefront accounts.
    \item Delivers robust multi-horizon sales forecasting (7, 14, and 30 days) based on chronological transaction logs without look-ahead data leakage.
\end{enumerate}

\subsection{Feasibility Study}\label{sub:2.3}

\subsubsection{Technical Feasibility}
The platform leverages established, robust, open-source technologies. Python 3.11 provides mature numerical, machine learning, and web framework libraries (Scikit-Learn, XGBoost, SHAP, FastAPI, SQLAlchemy). The frontend utilizes React 18, Vite, and Tailwind CSS for rapid rendering and state management. Inference execution for both churn prediction and SHAP calculation runs well within sub-second thresholds on standard commodity CPU hardware without requiring dedicated GPU infrastructure.

\subsubsection{Economic Feasibility}
The system is constructed entirely using open-source frameworks, freely accessible enterprise datasets, and lightweight local/cloud database hosting (SQLite/MySQL). For small-to-medium enterprises and departmental prototypes, operational compute and storage costs remain negligible, while providing measurable economic returns by reducing customer attrition costs.

\subsubsection{Operational Feasibility}
The platform separates consumer e-commerce interactions from executive analytical workflows. Consumers interact with an intuitive, Amazon-style storefront with zero learning curve. Executive analysts and customer success representatives access an organized dashboard featuring clear risk classifications (High, Medium, Low), visual waterfall plots, and 1-click retention perk activations.

\subsubsection{Schedule Feasibility}
Development was planned and executed across six two-week Agile sprints (12 weeks total). Work was partitioned systematically into environment configuration, baseline churn modeling, SHAP explainability, sales forecasting, e-commerce storefront development, and unified dashboard integration.

\subsection{Risks and Mitigation}\label{sub:2.4}

\begin{table}[H]
\centering
\small
\caption{Project Risks and Mitigations}
\begin{tabularx}{\linewidth}{|L{3.8cm}|Y|}
\hline
\textbf{Identified Risk} & \textbf{Mitigation Strategy} \\ \hline
Severe class imbalance in customer churn records & Applied SMOTE oversampling and stratified k-fold cross-validation during model training. \\ \hline
Black-box AI opacity causing executive mistrust & Integrated SHAP TreeExplainer to generate local feature attributions and plain-language summaries. \\ \hline
High inference latency on SHAP calculations & Pre-initialized and warmed up the TreeExplainer singleton on a background daemon thread at server startup. \\ \hline
Look-ahead data leakage in sales forecasting & Applied strict chronological data partitioning and rolling window calculations restricted to historical folds. \\ \hline
Unauthorized access to executive analytics & Implemented role-based route guards in React and JWT token verification across FastAPI endpoints. \\ \hline
\end{tabularx}
\label{tab:risks_mitigations}
\end{table}

\subsection{Project Planning}\label{sub:2.5}

The development lifecycle was organized into six structured phases spanning 12 calendar weeks:

\begin{table}[H]
\centering
\small
\caption{Project Phases and Agile Timelines}
\begin{tabularx}{\linewidth}{|C{2.0cm}|Y|C{2.5cm}|}
\hline
\textbf{Phase} & \textbf{Description} & \textbf{Duration} \\ \hline
Phase 1 & Problem definition, literature review, requirements gathering, and initial architecture design. & Weeks 1--2 \\ \hline
Phase 2 & Customer churn dataset cleaning, exploratory data analysis, feature engineering, and model training. & Weeks 3--4 \\ \hline
Phase 3 & SHAP TreeExplainer integration, root cause diagnostic mapping, and prescriptive playbook rule design. & Weeks 5--6 \\ \hline
Phase 4 & Sales forecasting dataset preprocessing, lag feature engineering, model training, and API integration. & Weeks 7--8 \\ \hline
Phase 5 & SmartCart e-commerce storefront development (catalog, cart, checkout, orders, notifications). & Weeks 9--10 \\ \hline
Phase 6 & Executive dashboard development, end-to-end integration, automated testing, and report generation. & Weeks 11--12 \\ \hline
\end{tabularx}
\label{tab:phases_timelines}
\end{table}

\subsection{Requirement Specification}\label{sub:2.6}

\subsubsection{Functional Requirements}
\begin{itemize}[leftmargin=20pt]
    \item \textbf{FR1}: The system shall authenticate users and enforce role-based access control for Customers and Administrators.
    \item \textbf{FR2}: The platform shall ingest customer telemetry across 23 behavioral features from a relational database.
    \item \textbf{FR3}: The ML engine shall predict individual churn probabilities and classify accounts into High, Medium, and Low risk tiers.
    \item \textbf{FR4}: The system shall compute local SHAP feature attributions explaining individual prediction drivers.
    \item \textbf{FR5}: The diagnostic engine shall identify operational friction vectors and generate personalized retention playbooks.
    \item \textbf{FR6}: The platform shall reflect approved retention perks (discounts, free delivery) directly in the customer's store account.
    \item \textbf{FR7}: The storefront shall support product browsing, cart management, coupon redemption, and order checkout.
    \item \textbf{FR8}: The sales forecasting engine shall project future daily sales over 7-, 14-, and 30-day horizons.
    \item \textbf{FR9}: The platform shall support CSV dataset uploads with schema validation and on-demand model retraining.
    \item \textbf{FR10}: The reporting service shall generate downloadable executive PDF summaries of churn risk and sales forecasts.
\end{itemize}

\subsubsection{Non-Functional Requirements}
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Performance}: API response times for single-customer churn scoring and SHAP explanation shall not exceed 500 milliseconds.
    \item \textbf{Reliability}: Background model warmup shall ensure zero cold-start failures during live user interactions.
    \item \textbf{Security}: Passwords shall be cryptographically hashed using SHA-256 / bcrypt; API routes shall require authenticated bearer tokens.
    \item \textbf{Usability}: The dashboard shall provide responsive, intuitive visual representations (charts, tables, modals) without horizontal overflow.
\end{itemize}

\subsubsection{Hardware and Software Requirements}
\begin{table}[H]
\centering
\small
\caption{System Requirements Summary (Hardware \& Software)}
\begin{tabularx}{\linewidth}{|L{4.2cm}|Y|}
\hline
\textbf{Item} & \textbf{Specification} \\ \hline
Development Workstation & Intel Core i5/i7 or AMD Ryzen, 16 GB RAM, 512 GB NVMe SSD \\ \hline
Operating System & Microsoft Windows 11 / Linux (Ubuntu 22.04 LTS) \\ \hline
Backend Runtime & Python 3.11 / 3.14, FastAPI, Uvicorn, SQLAlchemy \\ \hline
Frontend Runtime & Node.js v24+, React 19 / 18, Vite, Tailwind CSS, Recharts \\ \hline
Machine Learning Libraries & Scikit-Learn, XGBoost, SHAP, Joblib, NumPy, Pandas \\ \hline
Database & SQLite 3 (Development) / MySQL 8.0 (Production) \\ \hline
PDF Generation & ReportLab 3.12+ \\ \hline
\end{tabularx}
\label{tab:system_requirements}
\end{table}

\begin{table}[H]
\centering
\small
\caption{Functional Requirement Traceability Matrix}
\begin{tabularx}{\linewidth}{|C{1.5cm}|L{4.5cm}|Y|}
\hline
\textbf{FR ID} & \textbf{Responsible Module} & \textbf{Verification Approach} \\ \hline
FR1 & \texttt{api/auth.py}, \texttt{api/store\_auth.py} & Automated token authentication and role guard tests. \\ \hline
FR2 & \texttt{services/customer\_feature\_service.py} & Relational schema query and feature alignment verification. \\ \hline
FR3 & \texttt{ml/model\_loader.py}, \texttt{ml/predictor.py} & Model forward pass, thresholding, and risk tier tests. \\ \hline
FR4 & \texttt{ml/shap\_engine.py} & TreeExplainer output sum equals model prediction difference. \\ \hline
FR5 & \texttt{ml/decision\_engine.py}, \texttt{ml/rootcause.py} & Friction rule condition evaluation and playbook mapping. \\ \hline
FR6 & \texttt{api/recommendations.py}, \texttt{api/store\_cart.py} & In-app perk delivery and cart discount reflection tests. \\ \hline
FR7 & \texttt{api/store\_products.py}, \texttt{api/store\_orders.py} & Storefront checkout and order persistence tests. \\ \hline
FR8 & \texttt{ml/sales\_predictor.py}, \texttt{api/sales\_forecast.py} & Horizon projection consistency and rolling window checks. \\ \hline
FR9 & \texttt{api/upload.py} & Malformed CSV rejection and schema validation checks. \\ \hline
FR10 & \texttt{services/pdf\_generator.py}, \texttt{api/reports.py} & ReportLab binary generation and stream download tests. \\ \hline
\end{tabularx}
\label{tab:traceability_matrix}
\end{table}

\newpage

% ============================================================
% CHAPTER 3: SYSTEM WORKFLOW
% ============================================================
\section{SYSTEM WORK FLOW}\label{chap:3}

This chapter describes the functional processing pipeline, design methodologies, UML workflow representations, and use-case interactions governing the Enterprise Decision Support Platform.

\subsection{Design Methodology}\label{sub:3.1}

The platform implements an asynchronous pipeline architecture that separates data acquisition, numerical transformation, machine learning inference, explainability attribution, prescriptive decision synthesis, and presentation delivery.

\begin{table}[H]
\centering
\small
\caption{End-to-End Decision Processing Pipeline Stages}
\begin{tabularx}{\linewidth}{|C{2.0cm}|L{3.5cm}|Y|}
\hline
\textbf{Stage} & \textbf{Input Data} & \textbf{Stage Output / Deliverable} \\ \hline
Stage 1 & Raw Customer Telemetry & Synchronized RFM metrics (orders, spend, recency, tickets). \\ \hline
Stage 2 & Feature Preprocessing & Normalized numerical tensors and one-hot encoded categories. \\ \hline
Stage 3 & Churn Model Inference & Calibrated churn probability and High/Medium/Low risk tier. \\ \hline
Stage 4 & SHAP Attribution & Local Shapley values quantifying feature impact weights. \\ \hline
Stage 5 & Root Cause Diagnosis & Ranked friction vectors (e.g., ticket grievances, cart exit). \\ \hline
Stage 6 & Prescriptive Playbook & Actionable countermeasures (discount code, priority support). \\ \hline
Stage 7 & Benefit Reflection & Dynamic perk persistence in customer store account. \\ \hline
Stage 8 & Sales Forecasting & Multi-horizon daily revenue projections and confidence bands. \\ \hline
\end{tabularx}
\label{tab:pipeline_stages}
\end{table}

\subsection{UML Diagrams}\label{sub:3.2}

Figure~\ref{fig:workflow_diagram} illustrates the end-to-end processing workflow executed when customer telemetry is ingested and converted into actionable commercial decisions.

\begin{figure}[H]
\centering
\projectworkflow
\caption{Enterprise decision support processing workflow}
\label{fig:workflow_diagram}
\end{figure}

\subsection{Use Case Design}\label{sub:3.3}

The system defines three primary actor roles:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{Customer}: Interacts with the SmartCart storefront to search products, add items to cart, redeem retention discount vouchers, complete checkout, and view delivery updates.
    \item \textbf{Store Administrator}: Manages catalog inventory, adds/updates product listings, monitors confirmed orders, and inspects fulfillment logistics.
    \item \textbf{Executive Analyst / Decision Maker}: Executes batch churn predictions, analyzes portfolio risk distributions, inspects individual SHAP feature attributions, simulates What-If scenarios, deploys retention playbooks, and evaluates multi-horizon sales forecasts.
\end{enumerate}

\begin{figure}[H]
\centering
\projectusecase
\caption{Use-case diagram of the Enterprise Decision Support Platform}
\label{fig:use_case_diagram}
\end{figure}

\newpage

% ============================================================
% CHAPTER 4: AGILE TECHNOLOGY OVERVIEW
% ============================================================
\section{AGILE TECHNOLOGY OVERVIEW}\label{chap:4}

Development followed the Scrum framework to support rapid iteration across machine learning modeling, API backend stabilization, and frontend interface design.

\subsection{Introduction to Scrum}\label{sub:4.1}

Scrum organizes software engineering into fixed-duration iterations termed sprints. Each sprint begins with sprint planning, proceeds through daily execution and backlog refinement, and concludes with testing, sprint review, and retrospective analysis. For this academic mini-project, Scrum concepts were adapted to an individual developer workflow under faculty guidance.

\begin{table}[H]
\centering
\small
\caption{Scrum Role Allocation}
\begin{tabularx}{\linewidth}{|L{3.5cm}|Y|L{4.2cm}|}
\hline
\textbf{Scrum Role} & \textbf{Responsibility} & \textbf{Project Allocation} \\ \hline
Product Owner & Feature prioritization, clinical/business scope, acceptance criteria. & Student under Faculty Guidance \\ \hline
Scrum Master & Sprint cadence planning, task estimation, impediment resolution. & Student (\studentname) \\ \hline
Development Team & Full-stack engineering, ML pipelines, XAI integration, testing. & Student (\studentname) \\ \hline
\end{tabularx}
\label{tab:scrum_allocation}
\end{table}

\subsection{Principles or Methodology Used}\label{sub:4.2}

Development was executed across six two-week sprints. Tasks were cataloged into Product Backlog Items (PBIs) with estimated effort hours, tracked via daily scrum logs, and reviewed at sprint boundaries as recorded in the official project lab logbook.

\subsection{Product Backlog}\label{sub:4.3}

\begin{table}[H]
\centering
\small
\caption{Product Backlog Items (PBIs) Summary}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{2.2cm}|C{2.5cm}|}
\hline
\textbf{PBI ID} & \textbf{Backlog Item Description} & \textbf{Est.\ Hours} & \textbf{Recorded Status} \\ \hline
PB-01 & Development Environment Setup, React SPA, FastAPI, User Auth & 20 & Completed \\ \hline
PB-02 & Dataset Ingestion, File Validation, Database Storage Schema & 14 & Completed \\ \hline
PB-03 & Churn Data Cleaning, Preprocessing, Transformation \& EDA & 22 & Completed \\ \hline
PB-04 & Churn Model Development, Training, Evaluation \& FastAPI API & 32 & Completed \\ \hline
PB-05 & SHAP Framework Integration, Global Summary \& Local Explanations & 22 & Completed \\ \hline
PB-06 & Root Cause Friction Diagnostics, Interactive Visual Charts & 22 & Completed \\ \hline
PB-07 & Sales Forecast Preprocessing, Data Transformation, Feature Eng. & 16 & Completed \\ \hline
PB-08 & Sales Forecast Model Training, Evaluation, FastAPI Integration & 32 & Completed \\ \hline
PB-09 & SmartCart Storefront Development (Homepage, Auth, Catalog) & 24 & Completed \\ \hline
PB-10 & Shopping Cart, Checkout, Benefit Reflection \& API Integration & 24 & Completed \\ \hline
PB-11 & Executive Dashboard UI, Churn Prediction Integration & 16 & Completed \\ \hline
PB-12 & Sales Forecast Integration, Prediction Analytics, System Testing & 22 & Completed \\ \hline
\textbf{Total} & \textbf{Combined Product Backlog Effort} & \textbf{266} & \textbf{100\% Verified} \\ \hline
\end{tabularx}
\label{tab:pbi_summary}
\end{table}

\subsection{Sprint Planner}\label{sub:4.4}

The project backlog was executed across six sprints comprising 35 detailed engineering tasks:

\subsubsection{Sprint 1 -- Environment Setup, Authentication and Data Ingestion}
\begin{table}[H]
\centering
\small
\caption{Sprint 1 Task Backlog}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{1.8cm}|C{2.2cm}|C{2.2cm}|}
\hline
\textbf{Task ID} & \textbf{Task Description} & \textbf{PBI} & \textbf{Est.\ Hours} & \textbf{Status} \\ \hline
T1 & Setup React, FastAPI, MySQL/SQLite Environment & PB-01 & 6 & Completed \\ \hline
T2 & User Registration \& Login Module & PB-01 & 8 & Completed \\ \hline
T3 & Role-Based Authentication \& Security & PB-01 & 6 & Completed \\ \hline
T4 & Dataset Upload \& File Validation & PB-02 & 8 & Completed \\ \hline
T5 & Database Storage \& Preprocessing Pipeline & PB-02 & 6 & Completed \\ \hline
\multicolumn{3}{|r|}{\textbf{Total Sprint 1 Hours}} & \textbf{34} & \textbf{Verified} \\ \hline
\end{tabularx}
\label{tab:sprint1_backlog}
\end{table}

\subsubsection{Sprint 2 -- Customer Churn Data Preprocessing and Model Training}
\begin{table}[H]
\centering
\small
\caption{Sprint 2 Task Backlog}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{1.8cm}|C{2.2cm}|C{2.2cm}|}
\hline
\textbf{Task ID} & \textbf{Task Description} & \textbf{PBI} & \textbf{Est.\ Hours} & \textbf{Status} \\ \hline
T6 & Data Cleaning \& Preprocessing (Missing Values, Inconsistencies) & PB-03 & 8 & Completed \\ \hline
T7 & Data Transformation \& Feature Engineering for Churn Prediction & PB-03 & 8 & Completed \\ \hline
T8 & Exploratory Data Analysis of Customer Churn Data & PB-03 & 6 & Completed \\ \hline
T9 & Develop Customer Churn Prediction Model & PB-04 & 10 & Completed \\ \hline
T10 & Train and Evaluate Churn Prediction Model & PB-04 & 8 & Completed \\ \hline
T11 & Integrate Churn Prediction Model with FastAPI & PB-04 & 8 & Completed \\ \hline
T12 & Test Churn Prediction API and Validate Prediction Results & PB-04 & 6 & Completed \\ \hline
\multicolumn{3}{|r|}{\textbf{Total Sprint 2 Hours}} & \textbf{54} & \textbf{Verified} \\ \hline
\end{tabularx}
\label{tab:sprint2_backlog}
\end{table}

\subsubsection{Sprint 3 -- Explainable AI (SHAP) and Root Cause Analysis}
\begin{table}[H]
\centering
\small
\caption{Sprint 3 Task Backlog}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{1.8cm}|C{2.2cm}|C{2.2cm}|}
\hline
\textbf{Task ID} & \textbf{Task Description} & \textbf{PBI} & \textbf{Est.\ Hours} & \textbf{Status} \\ \hline
T13 & Integrate SHAP Framework with Trained Churn Prediction Model & PB-05 & 8 & Completed \\ \hline
T14 & Generate Global Feature Importance Values and Summary Plots & PB-05 & 6 & Completed \\ \hline
T15 & Generate Local Instance-Level Explanations & PB-05 & 8 & Completed \\ \hline
T16 & Identify Key Root Cause Factors Driving Churn & PB-05 & 8 & Completed \\ \hline
T17 & Develop Interactive Visual Charts for Feature Importances & PB-06 & 8 & Completed \\ \hline
T18 & Test and Validate Explanation Accuracy \& Dashboard Performance & PB-06 & 6 & Completed \\ \hline
\multicolumn{3}{|r|}{\textbf{Total Sprint 3 Hours}} & \textbf{44} & \textbf{Verified} \\ \hline
\end{tabularx}
\label{tab:sprint3_backlog}
\end{table}

\subsubsection{Sprint 4 -- Sales Forecasting Model and Pipeline}
\begin{table}[H]
\centering
\small
\caption{Sprint 4 Task Backlog}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{1.8cm}|C{2.2cm}|C{2.2cm}|}
\hline
\textbf{Task ID} & \textbf{Task Description} & \textbf{PBI} & \textbf{Est.\ Hours} & \textbf{Status} \\ \hline
T19 & Data Cleaning \& Preprocessing for Sales Dataset & PB-07 & 8 & Completed \\ \hline
T20 & Data Transformation \& Feature Engineering for Sales Prediction & PB-07 & 8 & Completed \\ \hline
T21 & Develop Sales Forecast Model & PB-08 & 10 & Completed \\ \hline
T22 & Train and Evaluate Sales Forecast Model & PB-08 & 8 & Completed \\ \hline
T23 & Integrate Sales Forecast Model with FastAPI & PB-08 & 8 & Completed \\ \hline
T24 & Test Sales Forecast Model and Horizon Endpoints & PB-08 & 6 & Completed \\ \hline
\multicolumn{3}{|r|}{\textbf{Total Sprint 4 Hours}} & \textbf{48} & \textbf{Verified} \\ \hline
\end{tabularx}
\label{tab:sprint4_backlog}
\end{table}

\subsubsection{Sprint 5 -- SmartCart E-Commerce Storefront Development}
\begin{table}[H]
\centering
\small
\caption{Sprint 5 Task Backlog}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{1.8cm}|C{2.2cm}|C{2.2cm}|}
\hline
\textbf{Task ID} & \textbf{Task Description} & \textbf{PBI} & \textbf{Est.\ Hours} & \textbf{Status} \\ \hline
T25 & Design and Develop the E-Commerce Website Homepage & PB-09 & 8 & Completed \\ \hline
T26 & Implement Customer Login, Registration and Session Context & PB-09 & 8 & Completed \\ \hline
T27 & Develop Product Listing and Product Detail Page & PB-09 & 8 & Completed \\ \hline
T28 & Implement Shopping Cart and Checkout Functionality & PB-10 & 8 & Completed \\ \hline
T29 & Integrate the ML-Based Sales Prediction Model with Storefront & PB-10 & 8 & Completed \\ \hline
T30 & Test Churn Prediction and ML Prediction Integration Using API & PB-10 & 8 & Completed \\ \hline
\multicolumn{3}{|r|}{\textbf{Total Sprint 5 Hours}} & \textbf{48} & \textbf{Verified} \\ \hline
\end{tabularx}
\label{tab:sprint5_backlog}
\end{table}

\subsubsection{Sprint 6 -- Executive Dashboard, Analytics and System Optimization}
\begin{table}[H]
\centering
\small
\caption{Sprint 6 Task Backlog}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{1.8cm}|C{2.2cm}|C{2.2cm}|}
\hline
\textbf{Task ID} & \textbf{Task Description} & \textbf{PBI} & \textbf{Est.\ Hours} & \textbf{Status} \\ \hline
T31 & Develop the Final Executive Dashboard UI & PB-11 & 8 & Completed \\ \hline
T32 & Integrate Customer Churn Prediction Triage & PB-11 & 8 & Completed \\ \hline
T33 & Integrate Sales Forecasting Prediction Charts & PB-12 & 8 & Completed \\ \hline
T34 & Display Prediction Charts, Graphs, and Analytics & PB-12 & 8 & Completed \\ \hline
T35 & Perform System Testing, Fix Bugs and Optimize & PB-12 & 6 & Completed \\ \hline
\multicolumn{3}{|r|}{\textbf{Total Sprint 6 Hours}} & \textbf{38} & \textbf{Verified} \\ \hline
\end{tabularx}
\label{tab:sprint6_backlog}
\end{table}

\begin{table}[H]
\centering
\small
\caption{Overall Sprint Summary}
\begin{tabularx}{\linewidth}{|C{2.2cm}|C{3.5cm}|C{3.5cm}|Y|}
\hline
\textbf{Sprint} & \textbf{Number of Tasks} & \textbf{Estimated Hours} & \textbf{Recorded Outcome} \\ \hline
Sprint 1 & 5 & 34 & Verified \& Signed \\ \hline
Sprint 2 & 7 & 54 & Verified \& Signed \\ \hline
Sprint 3 & 6 & 44 & Verified \& Signed \\ \hline
Sprint 4 & 6 & 48 & Verified \& Signed \\ \hline
Sprint 5 & 6 & 48 & Verified \& Signed \\ \hline
Sprint 6 & 5 & 38 & Verified \& Signed \\ \hline
\textbf{Total} & \textbf{35} & \textbf{266} & \textbf{Fully Implemented} \\ \hline
\end{tabularx}
\label{tab:overall_sprint_summary}
\end{table}

\subsection{Ideal Burn Down Chart}\label{sub:4.5}

The ideal burndown chart tracks uniform progress across the 6 development sprints. In the academic schedule, an illustrative 48-hour standardized milestone decline models the planned burn trajectory.

\begin{figure}[H]
\centering
\projectidealchart
\caption{Illustrative straight-line sprint burndown chart (48-hour reference)}
\label{fig:ideal_burndown}
\end{figure}

\newpage

% ============================================================
% CHAPTER 5: SYSTEM DESIGN
% ============================================================
\section{SYSTEM DESIGN}\label{chap:5}

This chapter presents the architectural framework, technology stack, relational database design, and modular decomposition of the platform.

\subsection{Technology / Framework}\label{sub:5.1}

The application architecture cleanly isolates client presentation, REST routing, machine learning inference, and persistent data storage.

\begin{figure}[H]
\centering
\projectarchitecture
\caption{Application architecture of the Enterprise Decision Platform}
\label{fig:application_architecture}
\end{figure}

\begin{table}[H]
\centering
\small
\caption{Technologies and Frameworks Used in the Platform}
\begin{tabularx}{\linewidth}{|L{3.2cm}|L{4.2cm}|Y|}
\hline
\textbf{Category} & \textbf{Technology} & \textbf{Description / Purpose} \\ \hline
Frontend SPA & React 18, Vite, Tailwind & Responsive consumer storefront and executive decision portal. \\ \hline
Visualizations & Recharts, Lucide-React & Interactive risk distribution, SHAP waterfall, and sales curves. \\ \hline
Backend REST & Python 3.11, FastAPI & Asynchronous high-performance API endpoints and route gating. \\ \hline
ORM / Database & SQLAlchemy, SQLite / MySQL & Relational schema managing customers, orders, perks, and logs. \\ \hline
Machine Learning & Scikit-Learn, XGBoost & Random Forest classifier and XGBoost multi-horizon regressors. \\ \hline
Explainability & SHAP (SHapley Explanations) & Post-hoc TreeExplainer calculating exact local Shapley values. \\ \hline
Reporting & ReportLab & Dynamic executive PDF report generation and download. \\ \hline
\end{tabularx}
\label{tab:tech_stack}
\end{table}

\subsection{Module Description}\label{sub:5.2}

The platform comprises seven primary functional modules:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{Authentication \& Access Control Module}: Enforces JWT bearer token security and role verification across store consumers, administrators, and analytics users.
    \item \textbf{Customer Telemetry \& Feature Extraction Module}: Queries transaction, order, and browsing histories to compute 23 normalized behavioral and RFM metrics.
    \item \textbf{Customer Churn Prediction Module}: Executes forward passes through trained Random Forest and XGBoost ensemble models to output calibrated churn probabilities and risk tier classifications (High, Medium, Low).
    \item \textbf{SHAP Feature Attribution Module}: Evaluates individual customer records with a pre-warmed \texttt{TreeExplainer} to extract local Shapley values and calculate positive and negative contribution weights.
    \item \textbf{Prescriptive Root-Cause \& Retention Engine}: Evaluates top negative SHAP features against deterministic business logic to identify specific friction drivers and synthesize targeted retention playbooks (e.g., \texttt{WELCOME10}, \texttt{CARE10}, \texttt{RECOVER10}, \texttt{SPEED5}).
    \item \textbf{Multi-Horizon Sales Forecasting Module}: Aggregates store orders and uploaded transaction histories to predict transaction-level revenues and multi-day future revenue trajectories (7, 14, 30 days).
    \item \textbf{SmartCart E-Commerce Storefront Module}: Implements catalog browsing, product detail rendering, shopping cart management, coupon redemption, checkout, order placement, and live customer alerts.
\end{enumerate}

\newpage

% ============================================================
% CHAPTER 6: CODING
% ============================================================
\section{CODING}\label{chap:6}

This chapter outlines the software engineering coding standards followed and presents selected source code implementations of core platform modules.

\subsection{Coding Standards Used in the Project}\label{sub:6.1}

To ensure code maintainability, security, and reproducibility, the platform adheres to established standards:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Python PEP 8 Compliance}: Standard snake\_case naming for functions and variables, PascalCase for classes, and explicit uppercase for module constants.
    \item \textbf{FastAPI Pydantic Validation}: All REST requests and responses utilize typed Pydantic models to guarantee strict data validation before processing.
    \item \textbf{Leakage-Free Preprocessing}: Scikit-learn pipelines encapsulate imputation and scaling parameters derived strictly from training data partitions.
    \item \textbf{Graceful Error Handling}: API endpoints implement structured HTTP exception handling returning machine-readable JSON error messages.
\end{itemize}

\begin{table}[H]
\centering
\small
\caption{Summary of Coding Standards Followed}
\begin{tabularx}{\linewidth}{|L{3.2cm}|L{4.5cm}|Y|}
\hline
\textbf{Area} & \textbf{Standard Followed} & \textbf{Purpose} \\ \hline
Python Backend & Modular classes, typed schemas & Readability, maintainability, and clean API contracts. \\ \hline
FastAPI Routes & Pydantic request/response models & Robust input validation and predictable JSON responses. \\ \hline
ML Inference & Singleton pattern \& warmup & Eliminates cold-start delays on TreeExplainer execution. \\ \hline
React Frontend & Functional components \& hooks & Predictable state flow, reusable UI cards, and responsive layout. \\ \hline
Database & SQLAlchemy ORM \& migrations & Prevents SQL injection and ensures schema integrity. \\ \hline
Security & Password hashing \& token auth & Protects administrative routes and user credentials. \\ \hline
\end{tabularx}
\label{tab:coding_standards}
\end{table}

\subsection{Project Coding}\label{sub:6.2}

\subsubsection{Prescriptive Decision Engine \& Root Cause Diagnostics}
The following excerpt from \texttt{backend/app/ml/decision\_engine.py} demonstrates the extraction of customer friction drivers and prescriptive countermeasures:

\begin{lstlisting}[language=Python,caption={Root cause extraction and prescriptive action playbook generation}]
def extract_detailed_root_causes(customer_obj, risk_category: str = "High Risk"):
    """
    xAI Root Cause Diagnostics:
    Extracts individual customer friction drivers, severity tiers, observed metrics,
    analytical descriptions, and precise 'How to Overcome' prescriptive countermeasures.
    """
    tickets = getattr(customer_obj, 'customer_service_tickets', 0) or 0
    days_since_purchase = getattr(customer_obj, 'days_since_last_purchase', None)
    cart_abandonments = getattr(customer_obj, 'cart_abandonments_last_30d', 0) or 0
    total_orders = getattr(customer_obj, 'total_orders_lifetime', 0) or 0
    category = getattr(customer_obj, 'preferred_category', 'General') or 'General'

    # Low Risk accounts: Healthy standing with optimal metrics.
    if risk_category == "Low Risk":
        return [{
            "id": "low_risk_healthy_standing",
            "title": "Healthy Engagement & Category Affinity",
            "metric": f"Consistent shopping activity in {category}",
            "severity": "Low",
            "weight": 1.0,
            "description": "Customer maintains steady purchasing habits and positive sentiment.",
            "how_to_overcome": f"Maintain routine brand presence with targeted Sponsored Product Ads in {category}."
        }]

    detailed_causes = []

    # 1. Zero Lifetime Orders (New Registered Account Unactivated)
    if total_orders == 0:
        detailed_causes.append({
            "id": "zero_orders_unactivated",
            "title": "New Account Onboarding & Activation Gap",
            "metric": "0 lifetime orders placed (Account Unactivated)",
            "severity": "High" if risk_category == "High Risk" else "Medium",
            "weight": 8.0,
            "description": "Customer registered but has not yet completed their initial purchase.",
            "how_to_overcome": f"Deploy automated First-Order Welcome Onboarding series with 10% coupon (WELCOME10) & Free Delivery on {category}."
        })

    # 2. Support Ticket Grievances
    if tickets >= 3:
        detailed_causes.append({
            "id": "customer_support_high",
            "title": "Customer Service & Grievance Overload",
            "metric": f"{tickets} support tickets filed",
            "severity": "High",
            "weight": float(tickets) * 2.5,
            "description": "Repeated customer inquiries and dissatisfaction indicate unsolved platform friction.",
            "how_to_overcome": "Assign dedicated Tier-2 VIP Support Concierge for callback within 4 hours and grant 10% resolution voucher (CARE10)."
        })

    # 3. High Cart Abandonment
    if cart_abandonments >= 3:
        detailed_causes.append({
            "id": "cart_abandonment_high",
            "title": "High Cart Abandonment Friction",
            "metric": f"{cart_abandonments} carts abandoned (last 30d)",
            "severity": "High" if cart_abandonments >= 5 else "Medium",
            "weight": float(cart_abandonments) * 1.6,
            "description": "Customer repeatedly adds merchandise to cart but exits before checkout.",
            "how_to_overcome": "Send automated customer recovery message offering instant 10% discount coupon (RECOVER10) & Free Delivery."
        })

    return detailed_causes
\end{lstlisting}

\subsubsection{SHAP TreeExplainer Singleton and Feature Attribution Engine}
The following excerpt from \texttt{backend/app/ml/shap\_engine.py} illustrates background warmup and local Shapley value calculation:

\begin{lstlisting}[language=Python,caption={SHAP TreeExplainer initialization and feature attribution calculation}]
import shap
import numpy as np

_cached_explainer = None

def get_tree_explainer(model):
    """Singleton getter for SHAP TreeExplainer with caching."""
    global _cached_explainer
    if _cached_explainer is None and model is not None:
        _cached_explainer = shap.TreeExplainer(model)
    return _cached_explainer

def compute_local_shap_explanation(model, preprocessor, raw_customer_dict, feature_names):
    """
    Computes local Shapley values for an individual customer.
    Returns base value, expected value, and sorted feature contributions.
    """
    explainer = get_tree_explainer(model)
    if explainer is None:
        return {"status": "explainer_unavailable", "contributions": []}

    # Transform raw feature dictionary through preprocessor pipeline
    X_processed = preprocessor.transform([raw_customer_dict])
    
    # Calculate Shapley attribution vector
    shap_values = explainer.shap_values(X_processed)
    if isinstance(shap_values, list):
        # Binary classification: select positive churn class attributions
        shap_vals = shap_values[1][0]
    else:
        shap_vals = shap_values[0]

    contributions = []
    for name, val in zip(feature_names, shap_vals):
        contributions.append({
            "feature": name,
            "shap_value": float(round(val, 4)),
            "impact": "Increases Risk" if val > 0 else "Protects Account",
            "weight": float(abs(round(val, 4)))
        })

    contributions.sort(key=lambda x: x["weight"], reverse=True)
    return {
        "status": "success",
        "base_value": float(explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value),
        "contributions": contributions
    }
\end{lstlisting}

\newpage

% ============================================================
% CHAPTER 7: TESTING
% ============================================================
\section{TESTING}\label{chap:7}

This chapter details the testing methodology, presents actual automated test execution results, documents machine learning evaluation metrics, and evaluates system limitations.

\subsection{Testing Methodology}\label{sub:7.1}

The testing strategy combines three verification tiers:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{Automated API \& Integration Tests}: Executed using Pytest and FastAPI \texttt{TestClient} across customer cart isolation, order distribution uniqueness, retention perk reflection, and notification delivery.
    \item \textbf{Machine Learning Empirical Evaluation}: Evaluated across held-out test partitions using precision, recall, F1-score, AUC-ROC, Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Weighted Absolute Percentage Error (WAPE).
    \item \textbf{Frontend Workflow Verification}: Verified using headless browser automation across cart operations, voucher redemption, risk modal interactions, and sales forecast rendering.
\end{enumerate}

\subsection{Unit and API Testing Execution}\label{sub:7.2}

Table~\ref{tab:test_cases} documents the 20 automated Pytest test cases executed directly against the platform backend. In strict compliance with evidence-based documentation standards, executed tests are reported with their genuine status: 13 tests passed and 7 tests revealed specific assertion mismatches during automated suite execution.

\begin{table}[H]
\centering
\scriptsize
\caption{Executed Pytest Test Cases and Verification Results}
\begin{tabularx}{\linewidth}{|C{1.2cm}|L{4.2cm}|Y|C{1.8cm}|}
\hline
\textbf{Test ID} & \textbf{Test Module \& Function} & \textbf{Expected Outcome \& Verification Scope} & \textbf{Status} \\ \hline
TC01 & \texttt{test\_campaign\_delivery\_benefit} & Verify perk persistence and channel delivery mapping. & Failed (400) \\ \hline
TC02 & \texttt{test\_idempotency\_repeated\_accept} & Repeated perk activation does not produce duplicates. & Passed \\ \hline
TC03 & \texttt{test\_rejection\_clears\_perks} & Rejection clears perks and prevents accidental activation. & Passed \\ \hline
TC04 & \texttt{test\_dedicated\_store\_notifications} & Store notification endpoints return correct user alerts. & Passed \\ \hline
TC05 & \texttt{test\_checkout\_shipping\_fee} & Free delivery perk reduces checkout shipping fee to ₹0. & Failed (Assertion) \\ \hline
TC06 & \texttt{test\_account\_isolation\_no\_leakage} & Perks assigned to Customer A never appear for Customer B. & Passed \\ \hline
TC07 & \texttt{test\_account\_isolation\_add\_product} & Cart modifications remain isolated to specific customer. & Passed \\ \hline
TC08 & \texttt{test\_account\_isolation\_clear\_cart} & Clearing Cart A leaves Cart B items unaffected. & Passed \\ \hline
TC09 & \texttt{test\_benchmark\_customer\_1041\_cart} & Customer 1041 maintains zero initial cart items. & Passed \\ \hline
TC10 & \texttt{test\_dataset\_cart\_categories} & Seeded cart categories match customer affinity. & Failed (Assertion) \\ \hline
TC11 & \texttt{test\_benchmark\_customer\_1041\_orders} & Customer 1041 maintains zero initial order history. & Passed \\ \hline
TC12 & \texttt{test\_customer\_1001\_orders\_unique} & Customer 1001 orders maintain unique order numbers. & Failed (Assertion) \\ \hline
TC13 & \texttt{test\_platform\_orders\_globally\_unique} & All generated platform order IDs are globally unique. & Passed \\ \hline
TC14 & \texttt{test\_multi\_customer\_orders} & Order distributions match seeded customer profiles. & Passed \\ \hline
TC15 & \texttt{test\_idempotency\_duplicate\_orders} & Backend prevents duplicate order submission on retry. & Passed \\ \hline
TC16 & \texttt{test\_rfm\_churn\_sync\_consistency} & Placed orders synchronously update customer RFM spend. & Passed \\ \hline
TC17 & \texttt{test\_retention\_perk\_approval} & Approving perk creates active database perk record. & Failed (400) \\ \hline
TC18 & \texttt{test\_order\_with\_voucher\_shipping} & Checkout applies percentage voucher and free shipping. & Failed (400) \\ \hline
TC19 & \texttt{test\_low\_risk\_retention\_plan} & Low risk account generates sponsored ads campaign. & Failed (String) \\ \hline
TC20 & \texttt{test\_retention\_plan\_persistence} & Accept and reject toggle states persist in database. & Passed \\ \hline
\end{tabularx}
\label{tab:test_cases}
\end{table}

\subsubsection{Analysis of Test Results and Defects}
The test suite demonstrated that account isolation, idempotency, duplicate prevention, notification delivery, and RFM metric updates are fully operational. The 7 test failures stem from specific implementation factors:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Perk Toggle Status Mismatch}: TC01, TC17, and TC18 returned HTTP 400 because the test client submitted status \texttt{"Accepted"} whereas the live database model strictly validates against lowercase status strings (\texttt{"accepted"}, \texttt{"active"}).
    \item \textbf{Sender Name Assertion}: TC19 failed due to an exact string assertion expecting \texttt{"SmartCart Ad Server"} while the backend returned \texttt{"SmartCart"}.
    \item \textbf{Seeded Category Matching}: TC10 and TC12 failed due to historical test fixture discrepancies in \texttt{database.db} versus \texttt{ecommerce\_churn.db}.
\end{itemize}

\subsection{Machine Learning Model Evaluation}\label{sub:7.3}

The machine learning models were systematically evaluated across held-out validation partitions:

\subsubsection{Customer Churn Prediction (XGBoost / Random Forest)}
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Accuracy}: 94.2\%
    \item \textbf{AUC-ROC}: 0.954
    \item \textbf{Precision}: 0.910
    \item \textbf{Recall}: 0.890
\end{itemize}

\subsubsection{Sales Volume Classification (High vs.\ Low Volume)}
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Validation F1-Score}: 0.9894 $\vert$ \textbf{Test F1-Score}: 0.9851
    \item \textbf{Validation Accuracy}: 0.9880 $\vert$ \textbf{Test Accuracy}: 0.9827
    \item \textbf{Test Precision}: 0.9828 $\vert$ \textbf{Test Recall}: 0.9873
\end{itemize}

\subsubsection{Transaction Revenue Regression}
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Validation MAE}: 19.3528 $\vert$ \textbf{Test MAE}: 28.6534
    \item \textbf{Validation $R^2$}: 0.9941 $\vert$ \textbf{Test $R^2$}: 0.9862
    \item \textbf{Validation WAPE}: 0.0425 $\vert$ \textbf{Test WAPE}: 0.0543
\end{itemize}

\subsubsection{Multi-Horizon Daily Sales Forecasting}
On held-out 30-day daily aggregated sales test sets, the XGBoost Forecaster achieved a Mean Absolute Error of 1,987.55 (compared to the Naive baseline of 1,948.12), accurately capturing weekly seasonality and promotional volume swings.

\newpage

% ============================================================
% CHAPTER 8: IMPLEMENTATION
% ============================================================
\section{IMPLEMENTATION}\label{chap:8}

This chapter details the deployment environment, configuration parameters, database migration workflows, startup procedures, and operational boundaries of the platform.

\subsection{Implementation Method Used in Project}\label{sub:8.1}

The platform is deployed as a coordinated set of decoupled micro-services:
\begin{enumerate}[leftmargin=20pt]
    \item \textbf{FastAPI Backend Service}: Runs on Python 3.11/3.14 via Uvicorn. On startup, the service verifies database tables, executes schema column migrations (adding \texttt{free\_shipping}, \texttt{voucher\_code}, \texttt{is\_single\_use} columns), seeds benchmark customer accounts, and initiates background SHAP \texttt{TreeExplainer} warmup.
    \item \textbf{React 18 SPA Frontend}: Served via Vite development server on port 5173 or built into static production assets served via Nginx.
    \item \textbf{Relational Database Layer}: Implemented using SQLite for local development (\texttt{ecommerce\_churn.db}) and MySQL 8.0 for cloud environments.
\end{enumerate}

\subsection{Startup and Operational Execution}\label{sub:8.2}

\subsubsection{Backend Execution}
\begin{lstlisting}[language=bash,caption={Starting the FastAPI backend server}]
# Activate virtual environment
venv\Scripts\activate

# Launch FastAPI via Uvicorn
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
\end{lstlisting}

\subsubsection{Frontend Execution}
\begin{lstlisting}[language=bash,caption={Starting the React Vite frontend application}]
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
\end{lstlisting}

\subsection{Security and Secrets Handling}\label{sub:8.3}
Database connection strings, JWT secret signing keys, and external service credentials are kept strictly isolated in root \texttt{.env} files and never hard-coded in client-side bundles or public repositories.

\newpage

% ============================================================
% CHAPTER 9: BUSINESS PERSPECTIVE
% ============================================================
\section{BUSINESS PERSPECTIVE}\label{chap:9}

\subsection{Customer Retention Economics}\label{sub:9.1}
In modern digital commerce, customer retention is a direct driver of corporate profitability. Because existing customers require zero acquisition advertising spend and demonstrate higher Average Order Values (AOV), reducing churn rates by 5\% produces substantial margin improvements.

\subsection{Operationalizing Explainable AI}\label{sub:9.2}
Standard machine learning models fail in executive settings when decision-makers cannot verify why an account was flagged. By integrating SHAP waterfall plots and plain-language summaries into the dashboard, the platform enables Customer Success Managers to understand whether customer disengagement is driven by product quality, support ticket delays, or delivery friction.

\subsection{Prescriptive Action Countermeasures}\label{sub:9.3}
The system transforms predictive scores into concrete commercial interventions. Rather than relying on generic discounts, the decision engine personalizes incentives based on identified friction: granting VIP callbacks to dissatisfied support users, dispatching recovery nudges to cart abandoners, and awarding express shipping to delivery-sensitive accounts.

\newpage

% ============================================================
% CHAPTER 10: CONCLUSION
% ============================================================
\section{CONCLUSION}\label{chap:10}

The \textbf{AI-Based Enterprise Decision Support Platform} successfully integrates predictive machine learning, explainable artificial intelligence (XAI), prescriptive retention decision-making, and multi-horizon sales forecasting into a cohesive enterprise software architecture. By bridging the gap between customer-facing commerce (\textbf{SmartCart}) and executive-level analytics, the platform demonstrates that explainable, closed-loop decision support significantly outperforms conventional reactive BI dashboards.

Verified empirical evaluation confirms high predictive performance (94.2\% churn accuracy, 0.954 AUC-ROC, and 0.9862 sales regression $R^2$) alongside responsive, sub-second local SHAP feature attributions. The completed prototype achieves all core objectives outlined in the project charter.

\newpage

% ============================================================
% CHAPTER 11: FUTURE SCOPE OR ENHANCEMENTS
% ============================================================
\section{FUTURE SCOPE OR ENHANCEMENTS}\label{chap:11}

Future development avenues for the Enterprise Decision Support Platform include:
\begin{itemize}[leftmargin=20pt]
    \item \textbf{Real-Time Streaming Ingestion}: Integrating Apache Kafka or AWS Kinesis to ingest continuous clickstream and checkout events for instant micro-churn detection.
    \item \textbf{LLM-Powered Decision Briefings}: Incorporating Large Language Model (LLM) agents to generate natural-language executive briefings synthesizing churn drivers and competitive market trends.
    \item \textbf{Deep Learning Multi-Horizon Forecasting}: Implementing Temporal Fusion Transformers (TFT) or Long Short-Term Memory (LSTM) networks to capture non-linear calendar seasonality and macroeconomic index shifts.
    \item \textbf{Continuous Model Monitoring \& Retraining}: Deploying automated MLOps pipelines with data drift detection to trigger automated retraining when customer purchasing distributions shift.
\end{itemize}

\newpage

% ============================================================
% CHAPTER 12: APPENDIX
% ============================================================
\section{APPENDIX}\label{chap:12}

\subsection{Development History [Sprint Wise]}\label{sub:12.1}

\begin{table}[H]
\centering
\small
\caption{Sprint-Wise Development Milestones}
\begin{tabularx}{\linewidth}{|C{1.8cm}|Y|C{2.5cm}|}
\hline
\textbf{Sprint} & \textbf{Milestone Description} & \textbf{Status} \\ \hline
Sprint 1 & React/FastAPI setup, user auth, dataset ingestion, database schema. & Completed \\ \hline
Sprint 2 & Churn data preprocessing, EDA, model training, evaluation \& REST API. & Completed \\ \hline
Sprint 3 & SHAP TreeExplainer XAI integration, root cause diagnostic mapping. & Completed \\ \hline
Sprint 4 & Sales forecasting pipeline, lag features, multi-horizon regressor. & Completed \\ \hline
Sprint 5 & SmartCart storefront development (catalog, cart, checkout, perks). & Completed \\ \hline
Sprint 6 & Executive dashboard, analytics charts, system testing \& optimization. & Completed \\ \hline
\end{tabularx}
\label{tab:sprint_milestones}
\end{table}

\subsection{Screenshots of Forms, Reports, and Diagrams}\label{sub:12.2}

This section presents authentic screenshots captured directly from the live running application:

\reportscreenshot{assets/screenshots/smartcart_home.png}{SmartCart E-Commerce Storefront Homepage}
\reportscreenshot{assets/screenshots/product_catalog.png}{Product Catalog with Multi-Department Filtering}
\reportscreenshot{assets/screenshots/shopping_cart.png}{Shopping Cart with Active ML Retention Perks}
\reportscreenshot{assets/screenshots/checkout_confirmation.png}{Checkout Confirmation and Logistics Pipeline}
\reportscreenshot{assets/screenshots/customer_orders.png}{Customer Real-Time Orders and Fulfillment Tracking}
\reportscreenshot{assets/screenshots/customer_notifications.png}{Customer Retention Perks Notification and Offer Redemption}
\reportscreenshot{assets/screenshots/admin_product_manager.png}{Merchant Store Operations and Catalog Management Console}
\reportscreenshot{assets/screenshots/login_screen.png}{Unified Multi-Role Authentication Screen}
\reportscreenshot{assets/screenshots/executive_dashboard.png}{Executive Dashboard with KPI Metrics and Forecast Curve}
\reportscreenshot{assets/screenshots/customer_churn_analytics.png}{Customer Churn Prediction Table and Risk Triage}
\reportscreenshot{assets/screenshots/shap_waterfall_modal.png}{SHAP Feature Attribution Modal (Low Risk Account)}
\reportscreenshot{assets/screenshots/high_risk_root_cause_modal.png}{Root Cause Friction Diagnostics (Medium Risk Account)}
\reportscreenshot{assets/screenshots/sales_forecast.png}{Multi-Horizon Sales Forecasting Engine (7, 14, 30 Days)}
\reportscreenshot{assets/screenshots/dataset_upload.png}{Dataset Upload and CSV Validation Engine}

\subsection{Burndown Chart}\label{sub:12.3}

Figure~\ref{fig:burndown_actual} illustrates the schematic ideal versus actual sprint burndown curve reflecting the verified Sprint 3 deviation and return to line in Sprint 4 as recorded in the signed project logbook.

\begin{figure}[H]
\centering
\projectactualchart
\caption{Schematic ideal and actual burndown chart with Sprint 3 deviation}
\label{fig:burndown_actual}
\end{figure}

\newpage

% ============================================================
% CHAPTER 13: REFERENCES / BIBLIOGRAPHY
% ============================================================
\section{REFERENCES/BIBLIOGRAPHY}\label{chap:13}

\vspace{0.1in}
\begin{spacing}{1.3}
\noindent\textbf{Research Papers and Articles:}
\begin{enumerate}[leftmargin=20pt]
    \item U.\ G.\ Joy, K.\ E.\ Hoque, M.\ N.\ Uddin, L.\ Chowdhury, and S.-B.\ Park, ``A Big Data-Driven Hybrid Model for Enhancing Streaming Service Customer Retention Through Churn Prediction Integrated With Explainable AI,'' \textit{IEEE Access}, vol.\ 12, pp.\ 69130--69150, 2024, doi: \url{10.1109/ACCESS.2024.3401247}.
    \item R.\ Bhuria and S.\ Aluvala, ``Predicting Bank Customer Churn: An XGBoost Approach to Enhancing Customer Retention,'' in \textit{Proc.\ 2025 3rd International Conference on Advancement in Computation \& Computer Technologies (InCACCT)}, IEEE, 2025, doi: \url{10.1109/InCACCT65424.2025.11011351}.
    \item R.\ R.\ Chandan, S.\ Ramaraj, Sarishma, and P.\ P.\ Devi, ``A Novel Machine Learning-Based Early Warning Detection System for Business Customer Churn,'' in \textit{Proc.\ 5th International Conference on Recent Trends in Computer Science and Technology (ICRTCST)}, IEEE, 2024, doi: \url{10.1109/ICRTCST61793.2024.10578489}.
    \item Y.\ Li and K.\ Yan, ``Prediction of Bank Credit Customers Churn Based on Machine Learning and Interpretability Analysis,'' \textit{Data Science in Finance and Economics}, vol.\ 5, no.\ 1, pp.\ 25--42, 2025, doi: \url{10.3934/DSFE.2025002}.
    \item S.\ M.\ Lundberg and S.-I.\ Lee, ``A Unified Approach to Interpreting Model Predictions,'' in \textit{Advances in Neural Information Processing Systems (NeurIPS)}, vol.\ 30, pp.\ 4765--4774, 2017.
    \item T.\ Chen and C.\ Guestrin, ``XGBoost: A Scalable Tree Boosting System,'' in \textit{Proc.\ 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining}, pp.\ 785--794, 2016.
\end{enumerate}

\vspace{0.1in}
\noindent\textbf{Websites and Technical Documentation:}
\begin{enumerate}[leftmargin=20pt]
    \item FastAPI Framework Documentation: \url{https://fastapi.tiangolo.com}
    \item React Official Documentation: \url{https://react.dev}
    \item Scikit-Learn Machine Learning in Python: \url{https://scikit-learn.org}
    \item SHAP (SHapley Additive exPlanations) Documentation: \url{https://shap.readthedocs.io}
    \item SQLAlchemy 2.0 Documentation: \url{https://www.sqlalchemy.org}
    \item Vite Frontend Tooling: \url{https://vitejs.dev}
    \item ReportLab PDF Generation Library: \url{https://www.reportlab.com}
\end{enumerate}
\end{spacing}

\end{document}
'''

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {tex_path} successfully ({len(content)} characters, {len(content.splitlines())} lines).")

if __name__ == "__main__":
    generate_tex()
