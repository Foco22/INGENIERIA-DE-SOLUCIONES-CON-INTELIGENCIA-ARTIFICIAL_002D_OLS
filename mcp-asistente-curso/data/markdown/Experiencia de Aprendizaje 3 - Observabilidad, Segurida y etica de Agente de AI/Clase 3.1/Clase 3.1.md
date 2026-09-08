

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

### _Noticias: Agentes need feedback to work well ._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
$< LangChain vedio) lmxkO) Diss, (ees “paeng =<br>Agent observability veoce sodack to power learning<br><!-- End of picture text -->

_Nota: https://www.langchain.com/blog/agent-observability-needs-feedback-to-power-learning_ 

_Observabilidad no es solo detectar fallos, sino que mejorarlos._ 



<!-- Start of picture text -->
uC<br><!-- End of picture text -->



<!-- Start of picture text -->
Agent observability powers learning loops<br>Sieh anes apinkoiSag ttasTaba<br><!-- End of picture text -->



<!-- Start of picture text -->
What agent observability needs to support<br>learning<br><!-- End of picture text -->



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->



<!-- Start of picture text -->
Eventos discretos (prompts, respuestas, uso de<br>herramientas, pensamientos del agente).<br>Mejores Practicas: Estructurados, contextuales,<br>centralizados.<br>Tres Pilares de la © Valoresdel tiempo numéricos(latencia, agregados uso de tokens,a lo largo<br>Observabilidad tasa de exito).<br>Mejores Practicas: Etiquetado,<br>agregacion, alertas.<br>El camino completo de una solicitud a través del<br>sistema, mostrando la secuencia de operaciones.<br>Mejores Practicas: Instrumentacidon,<br>visualizacién, correlacién.<br><!-- End of picture text -->

_Tres “Stones”: Logs, Métricas e Traces(Trazas)._ 

## _Logs: Eventos discretos, uso de tools, etc ._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
7 Messages Details<br>trace > wate O  O B oetecrome 10 funinStudio = + Addto 2<br>B® crutopensl goe-to-mev<br>2.28 ©? Foodtiack<br>B om . + Act feta<br>07% ©2080<br>cal_modet ~ out Markdown ©<br>0.005<br>Prompt B0 ve o<br>B castoponas ger-de-min<br>078s ©2008 Output Markdown ~<br>00% .<br>{woe B otschoma 2<br>(CREATE<br>4B ger.schema 2.005 SS INTEGERTABLEPRIMARY clientes {KEY,<br>B agent v nombre‘oma TEXT,TEXT NOT NULL,<br>89: 0432 hua TEXT<br>B caurmodo! . )<br>sures‘i CREATE TABLE dotalie_peaicns|<br>Promen 0.010% Idpedido_id INTEGER PRIMARY INTEGER REFERENCESKEY, padidos(dl,<br>Beattie18s 432 | eesrnns cantidadproducto_tdpreciountarioINTEGER NOT INTEGER REFERENCES productos,NULL,<br>REAL NOT NULL<br>B wos oo . CREATE‘INTEGERTABLEPRIMARYpoctiosKEY,(<br>BD execute query 00% chente_iofecha TEXT INTEGER NOT NULLREFERENCES clientesfc),<br>estado TEXT NOT NULL<br>: = : )<br><!-- End of picture text -->

|_Un llamado a una_|
|---|
|_tool es un log, una_<br>_acción que hay que_<br>_monitorear y_<br>_trackear._|



## _Traces: El camino completo ._ 



<!-- Start of picture text -->
» * Messages Details<br>Trace = wants @ 5° @ |G getecnema 10 funin Sudo + Addo OO<br>B® crutopensl goe-to-mev<br>2.28 ©? Foodtiack<br>Bom07% ©2080 " + Ac feetack<br>cal_modet ~ out Markdown ©<br>o7%s 208<br>B ve o<br>Prompt 0.005<br>0<br>B castoponas ger-4e-mnini<br>078 © = Output Markdown ~<br>{woe 00% . BD oetschome a<br>(CREATE<br>$B getschems 0.00 ss INTEGERTABLEPRIMARY clientes {KEY,<br>nombre<br>B agent ¥ ‘emat TEXT,TEXT NOT NULL,<br>tees © 432 (chung TEXT<br>B car mode! . )<br>sures‘a CREATE TABLE dotalie_peaicns|<br>Promen 0.00% Id‘pedida_id INTEGER PRIMARY INTEGER REFERENCESKEY, pedicioe(ic,<br>BetteVive eas | eoetenns ‘cantedproducto_tdpreciountario INTEGER INTEGERNOT NULL, REFERENCES productos,<br>REAL NOT NULL<br>tools 0015 . ‘INTEGERCREATE TABLEPRIMARYpoctiosKEY,(<br>B seamen toe chente_iofecha TEXT INTEGERNOT NULREFERENCES clientesfc),<br>estado TEXT NOT NULL<br><!-- End of picture text -->



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

_Usuario : ¿Cuáles fueron las ventas del 2025?_ **_Todo el camino es el trace._** _Asistente: Las ventas fueron $250.000.000 en el 2025._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
METRICAS CLAVE DE RENDIMIENTO (KPIS)<br>owes GI}<br>aeo KN<br>EXITO/FALLO<br>Tiempo de Uso de tokensy<br>respuesta del coste monetario Qué tan bien el Frecuenciaconla Qué herramientas<br>agente (total y por de las llamadas a agente cumple su que el agente se usan mas y con<br>componente). la API. objetivo (requiere completa las qué éxito.<br>evaluacion). tareas sin errores.<br><!-- End of picture text -->

_Métricas: Datos cuantificables del modelo._ 

## _Tool Call Accuracy: ¿Llamo a las tools correctamente?_ 



<!-- Start of picture text -->
FofromimportAneragas.messagesasyncio importTsAlMessage, Po TESHumantessage, ToolCall<br>eactedAare tan erate uy cone<br>Conte on<br>HumanMessage(content="Wwhat's the weather like in New York right now?"),<br>AlMessage(<br>Se St<br>» — ~ / /<br>Humantiessage(content="Can you translate that to Celsius?”),<br>AlMessage(<br>content="Let me convert that to Celsius for you.",<br>tool_calls=[<br>TEELTETENfame="temperature_conversion",. args={"temperature_fahrenheit":. 75}<br>»<br>L<br>»<br>1<br>Sone<br>REGRET<br>ToolCall(name="weather_check",GE Ot args={"location": "New York"}),<br>1 ToolCall(name="tenperature_conversion", args=("temperature_fahrenheit™: 75)),<br># Evaluate<br>metricresult == ToolCallAccuracy()await metric.ascore(<br>user_input=user_input,<br>reference_tool_calls-reference_tool_calls,<br>)<br>CE GRA Pareea GSR)<br>oon<br>asyncio.run(evaluate_tool_call_accuracy())<br>TS}<br><!-- End of picture text -->



<!-- Start of picture text -->
Tool call Accuracy<br>ToolCeliAccuracy measures how accurately an LLM agent invokes tools compared to expected<br>tool calls. It evaluates both the sequence of tool calls and the accuracy of their arguments. This<br>metric is particularly useful for validating that agents call the right tools with the right parameters<br>in multi-step workflows.<br>The metric requires user_input (conversation messages) and reference tool_calls (expected<br>tool calls). It returns a score between 0 and 1, where higher values indicate better performance.<br>Key Features<br>‘Two Evaluation Modes:<br>1. Strict Order (default): Too! calls must match exactly in sequence<br>© Use for: Sequential workflows where order matters<br>* Example: Must search before filtering results<br>2. Flexible Order: Tool calls can be in any order<br>* Use for: Parallel operations where order doesn't matter<br>Example: Fetching weather for muktiple cities simultaneously<br>Seong:_<br>* Evaluates sequence alignment (correct tools in correct order)<br>«Evaluates argument accuracy (correct parameters for each tool)<br>. Final score =-) (argument accuracy) xx (sequence aligned ?1 a 1 : 0)<br><!-- End of picture text -->





<!-- Start of picture text -->
Duocuc::<br><!-- End of picture text -->



<!-- Start of picture text -->
Agent Goal Accuracy<br>Agent goal accuracy is a metric that can be used to evaluate the performance of the LLM in<br>identifying and achieving the goals of the user. This is a binary metric, with 1 indicating that the<br>Al has achieved the goal and 0 indicating that the Al has not achieved the goal.<br>With Reference<br>AgentGoalAccuracyWithReference evaluates whether the agent achieved the user's goal by<br>- ; ;<br>comparing the workflow’s end state against a provided reference outcome. The reference<br>represents the expected/ideal outcome.<br><!-- End of picture text -->



<!-- Start of picture text -->
teport asyncto ms<br>fromfromfrom epenairagesragas.setrice.coliectionslinsimpartbassAsyncopenasimport Ln _factoryinsert agentGoalAccuracyiithReference<br>fron raga= messages import AiMessage, tumantessage, TooiCall, ToolMersage<br>async def evaluste_agent_gosl_accurscy_uith_reference(}:<br># Setup tim<br>Eliene ~ Azyncopenat()<br>Lim ~ Lin_factory(“gpt-So-mini*, <lient-client)<br>user_insut - [<br>PnAinoszage( Seanwe Geek & hea ea Sane eee a ee cel<br>anes Ae me tte Sie Haak erehene toe yaacr<br>te arnt —_——<br>PN AisiSees cE So<br>3<br>TootMesease’content-"Found = few options: 1. Golden Gragon, 2. jade Palace”<br>><br>Ainessage(<br>45 content-"i aoefound cone - great options: GoldenSia mand Jade Palace. unich4 one<br>Himanttexsage(content-"Lot"s go with Golden Bragon.*),<br>Almersage(<br>content-"Great choice! 2°11 book = table for s:tapm at Golden Dragon”.<br>teel_calis-[<br>Foolcati(Senteraege-("name": “GoldenbeeSragon", “time”: “s:@epn"),<br>a<br>Toctnessagetcontent-“Tablle Sooked at colden Sragon for B:eapm.").<br>sumessaze!<br>content-"Your table at Golden Oragon i= hoaked for 8:80pm. Enjoy your meal!”<br>a.<br>Himarttezsage(content-"thanks”),<br>1<br>metric - AgentacalAccuracynithneference(Lie-1im}<br>result — quait metric-ancoret<br>erer_input—user_input,<br>reference-Tabls booked at one of the chines restaurants at © pe”.<br>Preax(f"agent Goal Accuracy: (resultiwalue}"><br>3 name == *_matn_*:<br>ssyncio.runCevaluate_agent_goal_accuracy_with_reference()}<br>————=———— »<br><!-- End of picture text -->

_Agent Goal Accuracy: ¿Logro el objetivo?_ 

## _¿Qué necesito?: El problema de los datos._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
Testing starts before production<br>Inputs Datasets Metrics Experiments<br>Expected tasks Examples Correctness Compare versions<br>Dogfo sding trace Regression coverage Policy compliance Decide readiness<br>Simulations<br><!-- End of picture text -->

_Tienes que construir un dataset, pero no será suficiente. Tendrás que llevarlo a producción en un marcha blanca._ 

## _Vambe: Start-up chilena de asistente de AI._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
ESTAMOS MULTIPLICANDO NUESTRO EQUIPO. Postuia aqui ><br>Ovambe Plataforma Clentes Recursos:  Precias Nosotros *™—IniciarSesion Agenda Demo<br>ELCAOS<br>COMERCIAL.<br>TERMINAAQUI:<br>| !<br>UNA EXTENSIONDE TU EQUIPO QUE IMPULSATU NEGOCIO<br><!-- End of picture text -->



<!-- Start of picture text -->
2 Onboarding Vambe Q :<br>G:<br>+ @ &<br><!-- End of picture text -->

_Se implementa un agente, se “entrena” con personas del equipo, luego se da a otras personas (no clientes aun), y luego se libera a clientes._ 

## _Vambe: Desde prospectos a conversión ._ 





_https://www.youtube.com/watch?v=FfA2h-ZUG5Q_ 

