

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

## _LangSmith Engine : “Los agentes se ajustan solos”_ 





**Notas:** https://www.langchain.com/blog/introducing-langsmith-engine 

## _LangSmith Engine : ¿Cuáles son los patrones?_ 



Trace your agent to understand what it's doing <mark>|</mark> 

Identify patterns in failures or gaps in functionality 

_Ciclo de los agentes_ 

Make changes to prompts, tools, logic, or structure 

Create ground truth datasets from production traces <mark>|</mark> Run experiments to confirm improvements and check for regressions and then ship and repeat <mark>|</mark> 





<!-- Start of picture text -->
LangSmith ~ 1D Wortspecet / Tracing / ts chatbot-duoe-ve<br>force© Aiappiicstions . tg chatbot-duoc-uc1, Tracing «Evaluators Automations insights. Engine @ Retention34d = Omnbowsi RE<br>book Sm<br>fasuies3 Net cea: 2b rue i<br>O Home " 7 defaultTracing instrumentation rootname ~ gaps: orphan guardrail roots, null cost, no thread_id, # Crometvalusor Cony Fixconten SEE<br>tg Trang ” «Hf Tracing instrumentation. gaps: orphan guardrail roots, null cost,ania no t.. al High » Tracing Quality © Open » Uplatetoday or Pad ONE<br>(th Monitoring<br>© Datwsets6 Experiments —«-=*«:_ Agni fabricates course class counts uncer user pressure<br>alieieaaiail Sdiabiaibias) <4 veces pan ‘Four stacked LangSmith instrumentason gaps break core observablity for this project the three guararallChatOpenAI cats runinaraw ThreadPoolfxecuter so<br>7 ‘they appear a6 orphan root runs (3 per tum, ~75% of the trace ist), every LUM run is mnissing Lsprovider/ \s_sadel_name so total_cost is mult project-wide,<br>& ‘danctation Quanies ’ «Agent loops rag_search 3-5x on unanswerable questions, retrying |... nO thread_id is mirrored into root-run metadata so the Threads view cannot group a user's Telegram conversation, and the root run is named Langfiraph (the<br>@ Prompts FailegError Recovery 4 voces 5m ogo noisefrarreworkare afdefault)broken  sosimultaneously.run rules and trace filter queries cannot scope to this app. Cost dashboerts, the Threads view, run-rule scoping, and trace-fist signal-t0-<br>®@ Playground<br>{Studio .<br>—— : ==<br>© Deployments s ther oo wan ne -™ ™ _ a~ “ o~ ™<br>1 Sanctooxes<br>‘Unked Traces (& Engine proposedJ examows EB Add offline examples:<br>Bi cesopenai 1D, Orphan ChatOpend! guardrail root run that should be a chtd span of trace OtednG6-2 02. aSmago OLS<br>B vraoron TD. LangGrwph root run With Gtault na, No Prresdid metadsta, null cow; has 3 siting orphan guertrak ChatOpenal roots 45m ago | 5035<br>B Lmao 1D LangGingh root with Ik_provider and la. tmodel name missing on every chitd LLM spar; totel.tost nut Atmago 15828<br>Proposed Fix D Retresty<br>‘Close af four LangSmith tracing gaps in one commit: propagate the LangGraph run context into the quardiraé thread post so the three quardra® ChatOpenal calla<br>‘attach as child spans instead of orphan roots, pin Langchain-apenai>=®.3 $0 (s_arovider/ 1s nodel_nane (and total_cost<br>Py — mirrorthe Tetegran thread_id and chat_id wtp root-run metadata so the Threads view can group turns, and name the compiled) are graph emittedasistente_claritaon every LLM run, so<br>fun ules and trace filter queries can scope to this app.<br>B ‘Workspacefrancisco.macaya22@yn.1 ©) quardrails.py +4 -1<br><!-- End of picture text -->

_LangSmith Engine : ¿Cómo realmente luce?_ 

## _LangSmith Engine : El ciclo se cierra._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->



<!-- Start of picture text -->
P or ary<br>pz<br>-.<br>o<br>‘;<br>5 ‘i<br>;<br>..<br>.’<br>*3%.. ’<br>é<br>ee<br><!-- End of picture text -->

**Notas:** https://www.langchain.com/blog/introducing-langsmith-engine 

## _Cuesta al menos 50 dólares …_ 



### _¿Que realmente hay detrás de_ **_LangSmith Engine?_** 

LangSmith Engine is powered by a **deep agent** that has access to your **trace data, evaluator feedback, and your agent's source code** (if connected to your repo). 

It **monitors traces for several signal types** : explicit errors (tool call failures, timeouts), online evaluator failures, trace anomalies (latency spikes, token blowouts, unexpected step counts), negative user feedback, and unusual behaviors like users asking questions the agent wasn't built to answer. **When Engine spots a pattern across multiple traces, it clusters them into a single named issue rather than surfacing each failure individually.** 

LangSmith Engine is built on top of LangSmith's existing tracing and evaluation infrastructure. It uses your existing evaluator results as inputs, so failures your evals catch feed directly into issue detection. When Engine proposes a new evaluator, it's because it detected a gap in your current coverage. When it creates a dataset example, it goes directly into your existing offline eval workflow. 



## _Etapa final: Las próximas actividades del semestre._ 

**16-06-2026** :  LangSmith Enginer + Avance del Proyecto 

**23-06-2026** :  Clase sobre Claude Code (Skills, MCP, SubAgentes) 

**30-06-2026** :  Sintesis del modulo. -Presentación de la Evaluación 3 en la Plataforma. 

**07-07-2026** : Presentación del Examen Final, donde cada grupo entre 5 a 10 minutos para su presentación. 

