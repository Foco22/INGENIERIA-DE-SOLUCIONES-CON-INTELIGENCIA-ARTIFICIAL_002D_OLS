

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-2_ 

#### _Noticias: Yann LeCun, pionero en AI, reclama que los LLMs no son capaces de entender el mundo físico._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
I GE DI SECURITY POLITICS THE BIG STORY BUSINESS SCIENCE CULTURE REVIEWS QA NEWSLETTERS sunscerse<br>BUSINESS MAR 18. 2826 1:88 AM F }<br>Yann LeCun Raises $1 Billion q (Me<br>Ui n S ee' \j ee,* ri<br>to Build Al That Understand Sn Ce<br>the Physical World 4<br>Meta’shuman-level former Al chief will come Al scientist from mastering the has long argued physical that > é ey ?<br>world, not language. His new startup, AMI, aims to<br>prove it.<br><!-- End of picture text -->

**_Nota:_** https://www.wired.com/story/yann-lecun-raises-dollar1-billion-to-build-ai-that-understands-the-physical-world/ 

#### _Noticias: World Models, la forma para entender el mundo._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
To build an AI capable of true invention, we must there-<br>fore move beyond systems that merely read scientific liter-<br>ature to systems that can perceive the physical world. The<br>emergence of physically consistent World Models offers a<br>pathway to a synthetic laboratory. By enabling agents to<br>run counterfactual simulations—to experience the physi-<br>cal consequences of a thought experiment—we may finally<br>mechanize the feedback loop between intuition and logic.<br><!-- End of picture text -->



<!-- Start of picture text -->
co _*,<br>Position: LLM: ses<br>osition: s can’t jump<br>I<br>Tom Zahavy !<br>Abstract<br>HibIna  taletterwe to Riaciavcnally Maurice Solovine, aisacwverAlbertwa Einstein thine? Taine]| Enneiee Sys—toms<br>pneeg ere eisoovery asiaicyctical: process ump (2) 7<br>rience toig aiaxioms, mativefollowedTennbyeeelogicalseededuction. Pe (s]_Peorermets{s]<br>While / experiments<br>{iities]ing Deduction pattemGenerative matching)(formal AI hasproof), mastered and is-rapidlly we Induction argue conquer:it lacks(sta- Figure; siiaa1, AEssar generative.  AlEeSEY reconstruction<coction ofof Einstein’s Finetein's E-J-A dia- 7<br>the mechanism for Abduction—the generation of gram. Einstein drew this diagram in a letter to Maurice Solovine,<br>aca capiry nnanetneer eas RNaeTE showinga cyclical line jumping from Sense Experience<br>raltional‘ormulation i case study,ofppl weGeneral sd demonstrate ee)Relativitythatasig thea computa-prevail- iomsIronically,the very (A) difficultyviathea hallucinationJump of automating(J),and thenof the the deducingaxiomatic jump.  logicalsymbols consequences.highlights(E) to Ax-<br><!-- End of picture text -->



<!-- Start of picture text -->
Finally,lored to we the emphasize physical sciences, that thiswhere proposalthe isobject specificallyof studytai-is<br>external material reality. In abstract domains such as Mathe-<br>matics or Computer Science, the Sense Experience (£) ma:<br>Pp’ . Pp 'y<br>be grounded in high-dimensional topology or have other<br>goals such as generalityg  or minimality.: 2 While the necessity<br>of the Abductive Jump remains universal, the nature of the<br>simuforjanu physics, la iation‘  mustthe  besubstrateis adaptedadiapieal‘is totheGs thnworld;the ontology; ffor mathematics,off thethe discipline:discipline:its. ititiis<br>the abstract landscape of formal systems.<br><!-- End of picture text -->

**_Nota:_** https://openreview.net/forum?id=klU4737opt 

#### _Noticias: DashAI, la plataforma chilena de AI._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
| UNIVERSIDAD<br>49 DE CHILE Postlartes Esuclantes Académicasios Funccnariaglos Exresadasios<br>ADMSION CARRERAS ~—»«~POSTGRADOS ©—»—«INVESTIGACION «EXTENSION ©» BIBLIOTECAS ~—»-LAUNIVERSIDAD<br>nica > Noticias<br>NOTICIAS<br>MAS NOTICIAS Intetigencia artificial<br>ude U. de Chile presento dashAl, plataforma chilena que permite<br>de decoradochile tidera ena becas chile trabaj a rne sin entregar datos<br>extranjero 2026<br>CongresolEi2c6 Laity LaIneligencia Facultad Atifde CienciasID Fisicasaad y Matematicasun sofware de ite la yratut Universidadde que pemiteentrnar Chile, através desumodelosIniciativa dentin de Datose artical<br>— sinnecesidad de saber programar, La herramienta opera de forma 100% local en el computador del usuaro/a, sin<br>is Sameer ARS ab pee al Soe vale<br><!-- End of picture text -->



<!-- Start of picture text -->
H<br>air. prelphrtnemfney<br>- —<br>me feewe Cee<br>en |<br>as ae<br>;<br>:<br>Cs<br>_—> ‘<br>cr . $ a<br>:<br>~ o~ =<br>. — ae sf ‘ 4“ fi<br>t . ~ aa |,<br>Comunicaciones FCFM re a 7<br><!-- End of picture text -->

**_Nota:_** https://www.youtube.com/watch?v=guFF97F0Ctc&t=2639s 

#### _Clase 1.2: Técnicas de Prompt Engineering_ 



Se cubrirán los siguientes tópicos en la clase: • Zero-shot. 

• Few-shot learning. • Chain-of-thought. • Prompts Especializados. 

No obstante, esta clase _<u>no cubrirá</u>_ los siguientes tópicos: • fine-tunning. • RAG. 

## _Reminder: Que hemos visto hasta ahora…_ 

_Los LLMs tiene una estructura de mensajes:_ **_-Prompt de Sistema -Human Message -Asistent Message_** 



LLMs 

_Los LLMs tiene una parámetros de entrada -Tempuratura -Max token_ 



_Los LLMs entregan los siguiente output: - Texto generado (response/completion) - Usage_prompt ( Prompt, completion and total tokens) - Finished reason._ 

**_Nota_** : https://arxiv.org/pdf/2509.04664 

## _Reminder: Que hemos visto hasta ahora…_ 

**_Prompt Engineering: Estructurar la llamada._** 

Los LLMs tienen una estructura de mensajes, compuesta por: 



-Prompt de sistema -Human message -Assistant message 

LLMs 

Los LLMs tienen parámetros de entrada, entre los que se encuentran: 

Los proveedores más conocidos de LLMs son **Meta, OpenAI, Anthropic** **_,_ Google** 

- Temperatura 

- Max tokens 



Los LLMs entregan los siguientes outputs: 

1-) Texto generado (response/completion) 2)- Usage prompt: incluye prompt tokens, completion tokens y total tokens. 

- Finish reason: indica la razón por la cual el modelo terminó de generar la respuesta. 

#### _Why: ¿Por qué los LLMs no me responden como quiero?_ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
= ChatGPT5.2> G@-<br>When was your training data<br>cutoff date?<br>My training data cutoff date is March 2025.<br>This means my knowledge includes<br>information and patterns available up to that<br>point, but | do not have awareness of events,<br>product changes, launches, pricing updates,<br>or announcements that occurred after that<br>date unless you explicitly provide them in this<br>conversation.<br><!-- End of picture text -->

Los modelos de lenguaje son entrenados con toda la información del internet, y tiene una fecha de corte de entrenamiento (“cut-off”). 

- Los LLMs son generalistas. 

- Tienen una fecha de corte. 

- Se construyen en base a datos públicos, no privados. 

Hay técnicas para resolver estos _problemas._ 

#### _Hallucinate : El talón de Aquiles de los LLMs._ 



<!-- Start of picture text -->
DuocUC:<br><!-- End of picture text -->



<!-- Start of picture text -->
Why Language Models Hallucinate<br>Adam Tauman Kalai* Ofir Nachum Santosh S. Vempalat Edwin Zhang<br>OpenAL OpenAL Georgia Tech OpenAI<br>September 4, 2025<br>a)<br>Qa Abstract<br>So<br>AN Like students facing hard exam questions, large language models sometimes guess when<br>Q, uncertain, producing plausible yet incorrect statements instead of admitting uncertainty, Such<br>oO “hallucinations” persist even in state-of-the-art systems and undermine trust. We argue that<br>Nn language models hallucinate because the training and evaluation procedures reward guessing over<br>=p acknowledging uncertainty, and we analyze the statistical causes of hallucinations in the modern<br>a) training pipeline. Hallucinations need not be mysterious they originate simply as errors in binary<br>o classification. If incorrect statements cannot be distinguished from facts, then hallucinations<br>O in pretrained language models will arise through natural statistical pressures. We then argue<br>nan that hallucinations persist due to the way most evaluations are graded—language models are<br>(S “epidemic”optimized toof bepenalizing good test-takers,uncertainandresponsesguessingcanwhenonlyuncertainbe addressedimprovesthroughtest performance,a socio-technicalThis<br>mitigation: modifying the scoring of existing benchmarks that are misaligned but dominate<br>break leaderboards, rather than introducing additional hallucination evaluations, This change may<br>= steer the field toward more trustworthy AI systems,<br><!-- End of picture text -->

Las alucinaciones son originadas como errores en la clasificación binaria durante el entrenamiento de los modelos. Si las declaraciones incorrectas no son distinguidas de los hechos, entonces las alucinaciones de los modelos son perpetuadas a través del proceso de entrenamiento. 

Mucho LLMs son optimizados para ser buenos testeadores, y adivinar, lo que mejora el rendimiento de las métricas de testeos. 

**_Nota_** : https://arxiv.org/pdf/2509.04664 

#### _0’REILLY : AI Engineering_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
O'REILLY<br>Al Engineering<br>Building Applications<br>with Foundation Models<br>eS ><br>2 ete<br>7rp33  ayio<br><!-- End of picture text -->

“ _Anyone can communicate, but not everyone can communicate effectively_ ”. 



**_Prompt engineering_** _refers to methods for writing and organizing LLM instructions for optimal outcomes_ 

**_Context engineering_** _refers to the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts_ . 

**_Nota_** : https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents 

##### _Los_ **_conceptos_** _se comprenden mejor en una imagen_ **_._** 



<!-- Start of picture text -->
Duocuc:.<br><!-- End of picture text -->



<!-- Start of picture text -->
Prompt engineering vs. context engineering<br>Prompt engineering Context engineefo r agentsing<br>for single turn queries<br>Context window Possible context to give model Context window<br>==) BES b=<br>c=) SS |e<br>| ‘tj: cet<br>Po ma<br><!-- End of picture text -->

**(1) La compactación** mantiene el flujo de la conversación en tareas que requieren una interacción extensa de ida y vuelta. 

- **(2) La toma de notas** destaca en el desarrollo iterativo con hitos claramente definidos. 

**(3) Las arquitecturas multiagente** gestionan investigaciones y análisis complejos en los que la exploración en paralelo aporta beneficios. 

**_Nota_** : https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents 

#### _Tipos de comunicaciones: Sistema, humano y asistente ._ 



<!-- Start of picture text -->
DuocuCc:.<br><!-- End of picture text -->

_Prompt System : d_ efine el comportamiento del modelo _. User Message :_ mensaje del usuario _._ 

_Assistant Message :_ respuesta del modelo de lenguaje. Si existe una conversación, cada interacción se debe almacenar para entregarla como parámetro al request _._ 

Las técnicas de **_Prompt Engineering_** buscan personalizar y ajustar el Prompt System, no los demás mensajes **_._** 



_¿Cuáles son las técnicas de Prompt Engineering?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

_Mensaje directo al LLM, sin ningún ejemplo previo._ 

Ventajas: 

- Implementación fácil y rápida. 

#### _Zero – Shot Prompting_ 

Desventajas: 

- Poco confiable. 

- Los problemas reales son complejos, entonces muy poco usado en la industria. 



<!-- Start of picture text -->
Instruccidén clara + Contexto > Resultado esperado<br>"Clasifica el siguiente email como spam o no spam: [email]"<br><!-- End of picture text -->

**_Nota:_** https://blog.langchain.com/few-shot-prompting-to-improve-tool-calling-performance/ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

_Mensaje directo al LLM, pero con ejemplos de entradas y salidas. Le doy ejemplos al LLM de como quiero que trabaje._ 

Ventajas: 

### _Few-Shot Prompting_ 

- Mas preciso en la tarea. Le enseño como comportarse. 

Desventajas: 

- Output más estándar. 

- Necesito tener los ejemplos. 

- El prompt puede tomar más tiempo en construirlo. 



<!-- Start of picture text -->
Ejemplos + Patron + Nueva entrada + Resultado<br>Ejemplo 1: Input > Output<br>Ejemplo 2: Input > Output<br>Nueva entrada: [input] > ?<br><!-- End of picture text -->

## _Chain-of-Thought (COF)_ 

_Antes de tener una respuesta, lo correcto es “pensar”. El COF busca que los LLMs construyan una secuencia de pasos antes de entregar la respuesta, como si estuvieran haciendo el calculo matemático de una expresión compleja en “Voz Alta”._ 

Ventajas: 

- Mayor confiabilidad. 

- Trazabilidad del pensamiento respecto a la respuesta dada. 

- Descompone, razona y construye la respuesta. 

- • Debugging. 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

Desventajas: 

- Toma mayor tiempo de inferencia. 

- No aplica para todos los casos. 



<!-- Start of picture text -->
Problema + "Piensa paso a paso" > Razonamiento + Solucién<br>"Resuelve: 23 x 17. Piensa paso a paso."<br><!-- End of picture text -->

## _Técnicas avanzadas de Prompting_ 

###### **_Program-Aided Language Models (PAL)_** 

###### **_MetaPrompting_** 

###### **_Self-Consistency_** 

###### **_Tree of Thoughts (ToT)_** 

Meta-prompting usa el LLM para generar y optimizar prompts para tareas específicas. 

Tree of Thoughts permite al modelo explorar múltiples caminos de razonamiento de manera sistemática, evaluando y seleccionando las mejores opciones. 

PAL combina el razonamiento de LLMs con la precisión de código ejecutable para cálculos exactos. Se utiliza para cálculos numéricos más complejos, que necesitan una secuencia de etapas. 

Self-Consistency mejora la confiabilidad generando múltiples respuestas y seleccionando la más consistente. 



**_Prompt Chaining_** Prompt chaining conecta múltiples prompts en secuencia, donde la salida de uno alimenta al siguiente 



<!-- Start of picture text -->
aA<br><!-- End of picture text -->

## _¿Cómo construir un buen prompt?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

**_Simplicity is the ultimate sophistication. (Leonardo da Vinci)_** 

## _¿Cómo luce un buen prompt?_ 





<!-- Start of picture text -->
Calibrating the system prompt<br>Too specific Just right Too vague<br>BL | | ERED.<br>‘You‘You|.Agenarai_inquiry”,ForIdentify everyaremust aheipful respanduserthe azer request toassietant Intent“order_resubminsion”,theyou nameasforMUSTone Claude'sClaude.ofFOLLOWthe following’Bakery,“aecaunt_mointenance’,THESE“incidentSTEPS; rosolution", ‘You‘You‘questions{hcYou tanuwhavespecializeare acestomeraccessfelonyabeutin to the cusisting order and bakery.suppart pretension. monagementcustomersagentUse the forteotswith tystems,Clovde’savaliabletheir ordersBakery,productto youandcatatogs, tebasicresolve ‘Youattempt‘mannerCamgerodensearsore consistenta bakerytospp salve oftne ecenancenassistant,customers comwith e  the principlesnt byy rentsyousavesshould ino<br>“requires_eeceletion”) and store policies. Your goal is to resolve issues quickly when possible<br>2 if oper intent Is “incident_reselution”, ask 3 followup questions: selutions,‘Start by understanding esk follow-up theqvestionscompleteif yousituation do not beforeunderstand.proposing<br>to gather information, then elways call the resolve tool<br>if veer intent is *general_inquiry”, do not aek follawup Response Framework:<br>questions and anawer in one shot 1. Identify the core issue - Look beyond surface complaints:<br>3. Hare isoH= aneseexhavative intent, lint of cases that should be tugged os a\ guitardetails,to understandseoeapery ventnehscheck inventory,what the customerar reviewUsn alates policiesactually brneeds: e foree treetresponding ne<br>“requires_escelation”:if the intent in incident. resolution but 3.‘stepsProvidewithclear resolution realistic timelines- Offer concrete next<br>the wear na @ifereetcourtry 4: Goren sulstocWen’ tasars Oe suplamer indersionde<br>- If the user beft @ physical belonging in the store the resolution and knows how to follow up if needed<br>4. Once you've ruled out escalation scenorivs you showk! consider ait the Qvidelines:<br>sole at your diaposat, = When multiple solutions exist, choose the simplest one<br>Intant‘5 If theax veer_requestarder-recchenlsin?” contoine anunasorder_id you the waar moateuhould tog5/7 the af theveer = ‘thatWivesfullymnpaneaddressesonthe andes issuechuck Re shobes haters<br>fobowing=~ User Userraquirements:isis ashing fer asking for timelecationvpdate update -> suggestingForWhenlegat uncertain,issues,next stopshealth/atiergycall the human_emergencies, assistance toolor situctions<br>6.‘another if the order—user wants in flight, te requestyou should@ newFolloworder, thesebut 5theyutepsaireadyof the reestutionhave = Acknowledgerequiringcall the human, financial ossittonce  odjustmentstool beyond stondard policies,<br>preceore= 1 Callt cheek_order toot to see where the current order is Aaatcnd peapandfrustrotionwae appor u r gencyopiste innpety the user's<br><!-- End of picture text -->

**_Simplicity is the ultimate sophistication. (Leonardo da Vinci)_** 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

_Idea: ¿Qué construir?_ **_Enjoyable Vices Wholesome (vicios) (sano)_** _playing games_ **_Bad for you Good for you Toxic Chores (toxico) (tareas rutinarias)_** _Cursos de entrenamiento Control de gastos (trabajo)_ **_Unpleasant_** * Se ~~<mark>oe</mark>~~ • **Wholesome (actividades sanas):** No uses IA. Disfrútalas. **Toxic (actividades tóxicas):** Usa IA para automatizarlas o eliminarlas. No queremos lidiar con ellas. **Chores (tareas domésticas o rutinarias):** Usa IA para hacerlas más placenteras. **_Cementerios de Startup:_** _https://startups.rip/_ 

**Toxic (actividades tóxicas):** Usa IA para automatizarlas o eliminarlas. No queremos lidiar con ellas. 

**Chores (tareas domésticas o rutinarias):** Usa IA para hacerlas más placenteras. _(Sigan pensando.)_ 

**Vices (vicios):** Usa IA para evitar hacerlas. 

