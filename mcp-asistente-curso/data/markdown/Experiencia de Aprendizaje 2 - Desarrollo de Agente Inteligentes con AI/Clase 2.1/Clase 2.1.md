

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

_Noticias : Some files were leaked in Claude Code._ 





## _Noticias : Gemma 4, un modelo multimodal._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
ft) RNOUTONGAD > TEOAOLOGY > DEVROPRTOOIS<br>Gemma 4:' Byte for byte, the most<br>capable open models<br>Apr (2,2025 - 6minread<br>6 CementVP of Research, FartetGoogle 0) GroupOivier Product LacombeManager, < Sue<br>Deepling Google Deepind<br><!-- End of picture text -->



<!-- Start of picture text -->
F Models Docs Pricing 9 seca Signin<br>gama<br>& UMDowrioads © Updated ystercay<br>Gemma 4 models are designed to deliver frontierlevel performance at each size. They are well-suited for<br>reasoning, agentic woefloas, coding, nd multimodal understanding.<br>wsion too’ thinking autio hud edb of) 26) 3th<br>-.<br>cllaxa run gems!<br><!-- End of picture text -->

**_Nota_** : https://ollama.com/library/gemma4 



_¿Qué es un agente? “An agent is anything that can perceive its environment and act upon that environment.”_ 

_Nota: Huyen, C. (2025). AI engineering. O'Reilly Media_ 

## _¿Cuáles son sus componentes?_ 

_Plan_ 

_Memoria mecanismos que permiten a un modelo retener y utilizar información. . LLMs_ 





_Capacidad del modelo de descomponer un problema en tareas para resolverlo. ._ 





_Tools Funciones que le permiten al modelo conectarse con el mundo exterior. ._ 

_El motor del modelo. Los principales proveedor son OpenAI, Google y Anthropic_ 





<!-- Start of picture text -->
Duocuc:.<br><!-- End of picture text -->



<!-- Start of picture text -->
SWE-agent Agent-computer interface wile.<br>A NavigateLM-friendly repocommandsFe) Search files yr<br>pot<br>> LM agent CT View files A ‘dit tines De viii 5<br>LM-friendly conan<br>environment feedback ,<br>Figure 6-8. SWE-agent (Yang et al., 2024) is a coding agent whose environment is the computer and whose ac-<br>tions include navigation, search, and editing. Adapted from an original image licensed under CC BY 4.0.<br><!-- End of picture text -->

_Los agentes de código tienen herramientas que les permiten conectarse a los archivos (comandos de Linux)._ 



<!-- Start of picture text -->
DuocUC:<br><!-- End of picture text -->

_Tarea: Proyección de las ventas para Fruity Fedora sobre los próximos tres años._ 

1. Razonar sobre cómo realizar esta tarea. Podría decidir que, 

1. Reason about how to accomplish this task. It might decide that to predict fupara predecir las ventas futuras, primero necesita los 

ture sales, números de ventas de los últimos cinco años. El it first needs the sales numbers from the last five years. Note that razonamiento del agente se muestra como su respuesta 

the agent’s reasoning is shown as its intermediate response. intermedia. 

2. Invoke SQL query generation to generate the query to get sales numbers from 2. Invocar la generación de consultas SQL para obtener los 

the last números de ventas de los últimos cinco años. five years. 

3. Invoke 3. Invocar la ejecución de consultas SQL para ejecutar esta SQL query execution to execute this query. consulta. 

4. Reason about the tool outputs and how they help with sales prediction. It 4. Razonar sobre los resultados de las herramientas y cómo 

might decide that these numbers are insufficient to make a reliable projection, contribuyen a la predicción de ventas. Podría concluir que 

perhaps because of missing values. It then decides that it also needs informaestos números son insuficientes para hacer una proyección 

tion about confiable, quizás por valores faltantes. Entonces decide que past marketing campaigns. también necesita información sobre campañas de marketing 

5. Invoke SQL query generation to generate the queries for past marketing anteriores. 

campaigns. 5. Invocar la generación de consultas SQL para obtener los 

6. Invoke SQL query execution. datos de campañas de marketing pasadas. 

7. Reason 6. Invocar la ejecución de consultas SQL. that this new information is sufficient to help predict future sales. It 7. Razonar que esta nueva información es suficiente para 

then generates a projection. predecir las ventas futuras. Luego genera una proyección. 

8. Reason that the task has been successfully completed. 8. Razonar que la tarea se ha completado exitosamente. 

_Nota: Huyen, C. (2025). AI engineering. O'Reilly Media_ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

## _LLMs: Clave de los agentes._ 



<!-- Start of picture text -->
| Gemini 3.1 Pro Preview 9 1M G Google 37 $450 136 3251 3620 Model A Providers 7<br>| GPt-s.4 (xhigh) 9 1.05M ® Openal 57 $5.63 74 163.52 17027 Model 7 Providers 7<br>| GPT-5.3 Codex (xhigh) 9 400k ® Openal 54 $481 75 6224 6891 Model 7 Providers 7<br>| Claude Opus 4.6 (max) 9 IM A Anthropic 53 $10.00 4B 9.22 2089 Model 2 Providers 7<br>| Claude Sonnet 4.6 (max) 9 1M A Anthropic 52 $6.00 72 107.86 11483 Model 7 Providers 7<br>| GPT-5.2 (xhigh) 9 400k ® Openal 51 $481 76 10536 11191 Model 7 Providers 7<br>| Gim-s o 200k ZAl 50 $155 78 1.66 47.70 Model 7 Providers 7<br>| Claude Opus 4.5 9 200k A Anthropic 50 $10.00 a7 11.16 21.80 Model 7 Providers 7<br>| Minimax-m27 9 205k a MiniMax 50 $053 53 210 5852 Model 7 Providers 7<br>| Mimo-v2-Pro 9 1M Xizomi 49 $150 = “ = Model 2 Providers 7<br>rn<br><!-- End of picture text -->

_Nota: https://artificialanalysis.ai/leaderboards/models_ 

## _Plan: Divida las tareas complejas en subtareas más simples._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
sequence of manageable actions, so this process is also called task<br>1. Plan generation: come up with a plan for accomplishing this task. A plan is a<br>decomposition.<br>2. Reflection and error correction: evaluate the generated plan. If it’s a bad plan,<br>generate a new one.<br>3. Execution: take the actions outlined in the generated plan. This often involves<br>calling specific functions.<br>4. Reflection|  and error correctioo n: uu pon receicei v inging thehe actionat  outcomes, evaluate<br>these outcomes and determine whether the goal has been accomplished.<br>Identify and correct mistakes. If the goal is not completed, generate a new<br>plan.<br><!-- End of picture text -->



<!-- Start of picture text -->
|<br>eseeeticeseey<br>iiaTool outputsial ec<br>teseeesenensas desannsnnsnne<br>eed© cy of rr Lo;plantta rater<br>Figure 6-9. Decoupling planning and execution so that only validated plans are executed.<br><!-- End of picture text -->

_Nota: https://artificialanalysis.ai/leaderboards/models_ 

## _Tools: La conexión con el entorno._ 



<!-- Start of picture text -->
Duocuc::<br><!-- End of picture text -->

_Function calling_ es una forma de llamar tools usando modelos de lenguaje. 

Los principales consejos que hay que tener al momento de usar tools son: 

' 1- Definir correctamente el nombre de la tool. 

- H}' irequired": ["lbs*] i description »\ 

2- Definir la funcionalidad de la tool (descripción). 

3- Definir correctamente el nombre de los argumentos. 

- 4- Definir el tipo de dato de los argumentos. 

- 5- Definir los parámetros requeridos. 

Los modelos usan, seleccionan e implementan mejor las tools con mayor información. 

_Nota: Huyen, C. (2025). AI engineering. O'Reilly Media_ 

## _Agente : Búsqueda profunda._ 





<!-- Start of picture text -->
cee‘Scope ayResearch pisWrite:<br>~ _<br>Deep research has broken out as one of the most popular agent applications. This is a simple, configurable, fully open<br>source deep research agent that works across many model providers, search tools, and MCP servers. It's performance.<br>is on par with many popular deep research agents (see Deep Research Bench leaderboard),<br>clarity_withuser<br>\ ‘researc supersor<br>\ a<br><!-- End of picture text -->

_Arquitectura agentica propuesta por LangChain para hacer una búsqueda profunda._ 

_Esta arquitectura tiene tres etapas:_ 

_1. Scope_ 

_2. Research_ 

_3. Write_ 

_Las etapas están compuestas de nodos, que tienen tools y capacidades de razonamiento._ 

_Nota: https://github.com/langchain-ai/open_deep_research_ 

## _Memoria : Próxima clase…_ 



<!-- Start of picture text -->
Ic6nica (visual)<br>a Ecoica (auditiva)<br>MEMORIA.<br>SENSORIAL<br>Haptica (tactil)<br>mehr MEMORIA.A Memoria de trabajo<br>Funcién cognitiva GORTOPLAZO —. (WT) u operative<br>‘superior<br>SemGntica<br>Explicita (declarativa) (conocimiento; lenguaje)<br>MEMORIA A (experienciaEpisédica personal)<br>~ LARGO PLAZO<br>(MLP)<br>Implicita Habilidades motoras<br>(procedimental o no<br>declarativa) Condicionamiento<br><!-- End of picture text -->



<!-- Start of picture text -->
DuocUCc<br><!-- End of picture text -->

_Si fueran agentes, ¿Qué memoria seria útil tener?_ 

## _Agentes más que solo LLMs ._ 

_Plan_ 

_Memoria_ 





_Capacidad del modelo de descomponer un problema en tareas para resolverlo. ._ 

_mecanismos que permiten a un modelo retener y utilizar información._ 



_. LLMs_ 



_Tools Funciones que le permiten al modelo conectarse con el mundo exterior. ._ 

_El motor del modelo. Los principales proveedor son OpenAI, Google y Anthropic_ 



