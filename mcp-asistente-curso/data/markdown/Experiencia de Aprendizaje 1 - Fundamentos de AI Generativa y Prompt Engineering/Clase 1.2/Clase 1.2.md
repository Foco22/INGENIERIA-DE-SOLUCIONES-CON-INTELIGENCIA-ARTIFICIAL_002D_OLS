

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

#### _Noticias: Yann LeCun, pionero en AI, reclama que los LLMs no son capaces de entender el mundo físico._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
I GE DI SECURITY POLITICS THE BIG STORY BUSINESS SCIENCE CULTURE REVIEWS QA NEWSLETTERS sunscerse<br>BUSINESS MAR 18. 2826 1:88 AM F }<br>Yann LeCun Raises $1 Billion q (Me<br>Ui n S ee' \j ee,* ri<br>to Build Al That Understand Sn Ce<br>the Physical World 4<br>Meta’shuman-level former Al chief will come Al scientist from mastering the has long argued physical that > é ey ?<br>world, not language. His new startup, AMI, aims to<br>prove it.<br><!-- End of picture text -->

**_Nota:_** https://www.wired.com/story/yann-lecun-raises-dollar1-billion-to-build-ai-that-understands-the-physical-world/ 

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

**_Nota_** : https://arxiv.org/pdf/2509.04664 

#### _0’REILLY : AI Engineering_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
O'REILLY<br>Al Engineering<br>Building Applications<br>with Foundation Models<br>eS ><br>2 ete<br>7rp33  ayio<br><!-- End of picture text -->

“ _Anyone can communicate, but not everyone can communicate effectively_ ”. 



_Prompt Engineering es una técnica para mejorar las respuestas de los modelos, buscando consistencia, reducción de alucinaciones y personalización de los LLMs._ 



_Prompt Engineering es una técnica para mejorar las respuestas de los modelos, buscando consistencia, reducción de alucinaciones y personalización de los LLMs._ 



_¿Es la solución perfecta?_ 



_Prompt Engineering es una técnica para mejorar las respuestas de los modelos, buscando consistencia, reducción de alucinaciones y personalización de los LLMs._ 



_¿Es la solución perfecta? No, pero ayuda._ 

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

##### **_Program-Aided Language Models (PAL)_** 

##### **_MetaPrompting_** 

##### **_Self-Consistency_** 

##### **_Tree of Thoughts (ToT)_** 

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



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

_Idea: ¿Qué construir?_ **_Enjoyable Vices Wholesome (vicios) (sano)_** _playing games_ **_Bad for you Good for you Toxic Chores (toxico) (tareas rutinarias)_** _Cursos de entrenamiento Control de gastos (trabajo)_ **_Unpleasant_** * Se ~~<mark>oe</mark>~~ • **Wholesome (actividades sanas):** No uses IA. Disfrútalas. **Toxic (actividades tóxicas):** Usa IA para automatizarlas o eliminarlas. No queremos lidiar con ellas. **Chores (tareas domésticas o rutinarias):** Usa IA para hacerlas más placenteras. **_Cementerios de Startup:_** _https://startups.rip/_ 

**Toxic (actividades tóxicas):** Usa IA para automatizarlas o eliminarlas. No queremos lidiar con ellas. 

**Chores (tareas domésticas o rutinarias):** Usa IA para hacerlas más placenteras. _(Sigan pensando.)_ 

**Vices (vicios):** Usa IA para evitar hacerlas. 

