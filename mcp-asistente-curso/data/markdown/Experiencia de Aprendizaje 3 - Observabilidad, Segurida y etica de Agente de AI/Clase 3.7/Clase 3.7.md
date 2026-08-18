

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 



_Experiencia de Aprendizaje 1 Fundamentos de AI Generativa y Prompt Engineering_ 



## _Historia : Deep Learning_ 

_John Hopfield Yann LeCun pioneers introduce a Hopfield Convolutional Neural Newtwork, recurrent Networks (CNNs), neural network that laying the server as associative groundwork for AlphaGo defeated modern computer memory vision_ 2006 **2012 2015** _the world champion of Go in 2016._ **2017 2022** **_Lee Sedol_** _1986 1982 1990 AlexNet, created by Elon Musk, Sam Google researchers Fei-Fei Li begins OpenAI launched Alex Krizhevsky and Altman, Greg introduce the creating ImageNet, a ChatGPT in massive labeled visual co-supervised by Brockman, and others Transformer 1939-1945 Geoffrey Hinton, dataset to advance machine learning_ . _Geoffrey Hinton, wins co-found OpenAI to_ **2016** _architecture with the Novembre of 2022. David Rumelhart, and the ImageNet promote safe and paper “Attention is All Alan Turing Ronald Williams design and develop Challenge, open AI development. You Need,” backpropagation, demonstrating the revolutionizing NLP build the first making the training computer of multi-layered power of deep and leading to during the neural networks learning. models like BERT and Second World feasible GPT. War_ 

## _Breakpoint:_ Attention Is All You Need 



<!-- Start of picture text -->
DuocUCc<br><!-- End of picture text -->



<!-- Start of picture text -->
Provided proper attribution is provided, Google hereby grants permission to<br>reproduce the tables and figures in this paper solely for use in journalistic or<br>scholarly works.<br>eee<br>Attention Is All You Need<br>faa)<br>aN<br>S Ashish Vaswani* Noam Shazeer* Niki Parmar* Jakob Uszkoreit”<br>os Google Brain Google Brain Google Research Google Research<br>on avasvani€google.com noam@google.com nikip®google.com usz@google.com<br>=<br>< Liion Jones" Aidan N. Gomez" | Lukasz Kaiser”<br>“ Google Research University of Toronto Google Brain<br>— llion®google.com aidan@cs.toronto.edu lukaszkaiser@google.com<br>—_O Illia Polosukhin® *<br>=f illia.polosukhin®gmail.com<br>rs)<br><!-- End of picture text -->

**Self-attention** : captura y mira directamente todas las palabras. 

El paper “Attention Is All You Need”, publicado por Ashish Vaswani, Noam Shazeer, Niki Parmar y otros investigadores de Google, introdujo la arquitectura Transformer. 

Los beneficios son: 

- Capturar dependencias largas. 

- • Todas las palabras se analizan al mismo tiempo. (mejor uso de GPU). 

- Mejor compresión del texto. 

- Escala mejor con modelos con más parámetros. 

**_Nota:_** https://arxiv.org/pdf/1706.03762 

## ¿Qué son los _tokens_ ? 



<!-- Start of picture text -->
aah<br>aardvark<br>aardwolf<br>aargh<br>ab<br>aback<br>abacterial<br>abacus<br>abalone<br>abandon<br>: All words, ~ 50k<br>aysoid ?<br>zygomatic<br>zygomorphic<br>zy gosis<br>zygote<br>zygotic<br>zyme<br>zymogen<br>zymosis<br><!-- End of picture text -->



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

Los computadores no procesan palabras, sino que procesan números. (representaciones binarias). 

Los tokens es el conjunto de “palabras” que hay en el conjunto de los datos de entrenamiento del modelo. _Ejemplo: Hola, como estas? Lista de Tokens: [“Hola”, “,como”, “estas?”]_ 

El input del usuario se divide en tokens mediante un tokenizador. Luego se buscan los IDs de esos tokens y cada ID se transforma en un embedding. 

Los tokens forman parte central del modelo de negocio de los LLMs, ya que cada consulta realizada a estos sistemas se cobra considerando tanto los tokens de entrada (prompt tokens) como los tokens de salida (completion tokens). 

**_Nota:_** _https://www.youtube.com/watch?v=wjZofJX0v4M&t=183s_ 

## ¿Qué son los _Embeddings_ ? 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

Los embeddings son vectores de números que representan el significado de palabras, frases o documentos para que un computador pueda procesarlos. 

Los embeddings son importantes por el propio modelo, y por otras técnicas, tales como: **_RAG. (Retrieval-Augmented Generation)._** 



<!-- Start of picture text -->
E(queen) Es un tipo de arquitectura de red neuronal diseñada  - E(king) * E(woman) - E(man)<br>para trabajar con secuencia de datos.<br>El diseño de esta arquitectura es importante, ya<br>que predice el próximo “token” no solo por la<br>ultima palabra, sino no que el conjunto de todas las<br>palabras anteriores.<br>| E(man)<br>El paper “ Attention Is All You Need”,  publicado<br>* E (woman)<br>Ashish Vaswani, Noam Shazeer, Niki Parmar, et al<br>(Google).<br>\<br>. \<br><!-- End of picture text -->

**_Nota:_** _https://www.youtube.com/watch?v=wjZofJX0v4M&t=183s_ 



_Prompt Engineering es una técnica para mejorar las respuestas de los modelos, buscando consistencia, reducción de alucinaciones y personalización de los LLMs._ 



_¿Es la solución perfecta? No, pero ayuda._ 

## _¿Cómo construir un buen prompt?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

**_Simplicity is the ultimate sophistication. (Leonardo da Vinci)_** 

### _¿Qué es RAG?: Retrieval-Augmented Generation_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
External<br>Memory<br><!-- End of picture text -->



<!-- Start of picture text -->
Retrieval<br>Consulta<br>LLMs<br>Resultado<br><!-- End of picture text -->



<!-- Start of picture text -->
3<br>a<br><!-- End of picture text -->

_RAG es una metodología para dotar a los LLMs con información que no tenían al momento de entrenarlos._ 

**_1. Retrieval (Recuperar):_** _Encontrar las fuentes relevantes a la pregunta._ 

**_2. Aumentar (Augment):_** _La información recuperada se inyecta al prompt._ 

**_3. Generar (Generative):_** _El LLM produce una respuesta en base a la información dada._ 

### _Retrieval: Dos caminos, mismo objetivo._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

**_Term base retrieval_** 

###### **_Embedding base retrieval_** 

**_Term Frecuency (TF)_** _:_ Numero de veces que un termino aparece en un documento.  Si el termino aparece más veces, es más relevante. 

Transforma la información en vectores, se encuentran los más parecidos, y luego se inyectan al modelo de lenguaje como parte del prompt. 

**_Inverse document frecuency (IDF)_** _:_ La importancia de un termino es inversamente proporcional a la cantidad de documentos donde aparece el termino. 

_Las soluciones más típicas a este tipo de retrieval son:_ **_ElasticSearch_** _y_ **_BM25_** _._ **_Esta solución se enfoca en el lexical level_** 

Los vectores son capaces de capturar la representación semántica del texto. 



**_Esta solución se enfoca en el semantic level._** 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

### _Control: Métricas de Recuperación y Generación._ 

Retrieval Generation **_Precision Faithfulness_ Answer Relevancy** 

**_Faithfulness_** 

**_Recall_** 

_De los documentos De los documentos ¿La pregunta se basa relevantes que en el contexto recuperados, existen en la base, ¿cuantos son proporcionado? ¿Cuántos realmente recuperaste? relevantes?_ **_Etiquetar Una baja indica el AI Agent podría documentos modelo alucinada o validar inventa._** 

_¿La respuesta aborda de forma directa y útil la pregunta original?_ 

**_Una respuesta puede ser fiel al contexto, pero no útil_** 



_Experiencia de Aprendizaje 2 Desarrollo de Agente Inteligentes con AI_ 

## _¿Cuáles son sus componentes?_ 

_Plan_ 

_Memoria mecanismos que permiten a un modelo retener y utilizar información. . LLMs_ 





_Capacidad del modelo de descomponer un problema en tareas para resolverlo. ._ 





_Tools Funciones que le permiten al modelo conectarse con el mundo exterior. ._ 

_El motor del modelo. Los principales proveedor son OpenAI, Google y Anthropic_ 



## _Memoria : Tipo de memoria en los agentes_ . 



<!-- Start of picture text -->
DuocUCc:<br><!-- End of picture text -->



<!-- Start of picture text -->
Short-term memory ; Long-term memory<br>'<br>|SSee<br>|| (Seen<br>'<br>Gnome} | | SSeS<br>(| NN ~#<br>!<br>Checkpointer i Store<br><!-- End of picture text -->

Short-term memory: _Es todo lo que el agente puede "ver" y recordar en este momento — su ventana de atención activa._ 

Long-term memory: _Es todo lo que el agente puede recordar más allá de su context window — información persistente que sobrevive entre sesiones._ 

## _Memoria : Tipo de memoria en los agentes_ . 



<!-- Start of picture text -->
DuocUCc:<br><!-- End of picture text -->



<!-- Start of picture text -->
Short-term memory ; Long-term memory<br>'<br>|SSee<br>|| (Seen<br>'<br>Gnome} | | SSeS<br>(| NN ~#<br>!<br>Checkpointer i Store<br><!-- End of picture text -->

Short-term memory: _Es todo lo que el agente puede "ver" y recordar en este momento — su ventana de atención activa._ 

Long-term memory: _Es todo lo que el agente puede recordar más allá de su context window — información persistente que sobrevive entre sesiones._ 

_Multi – Agents system: Cuando lo simple no es suficiente._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Supervisor<br>Agent<br>AgentHotel 1 N\q<br>..Other<br>Flight agents<br>Agent<br><!-- End of picture text -->

_“In 2025, the models out there are extremely intelligent. But even the smartest human won’t be able to do their job effectively without the context of what they’re being asked to do. “Prompt engineering” was coined as a term for the effort needing to write your task in the ideal format for a LLM chatbot. “Context engineering” is the next level of this. It is about doing this automatically in a dynamic system. It takes more nuance and is effectively the #1 job of engineers building AI agents.”_ 

## _Multi – Agents system: 4 patrones para mirar._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Pattern How it works<br>: . .<br>Subagents A main agent coordinates subagents as tools. All routing passes through the<br>main agent, which decides when and how to invoke each subagent.<br>Behavior changes dynamically based on state. Tool calls update a state<br>Handoffs variable that triggers routing or configuration changes, switching agents or<br>adjusting the current agent's tools and prompt.<br>Skills Specialized prompts and knowledge loaded on-demand. A single agent<br>=—— stays in control while loading context from skills as needed.<br>A routing step classifies input and directs it to one or more specialized<br>ee<br>———s agents. Results are synthesized into a combined response.<br>Custom workflow Build bespokeP execution. flows with sangtraph,LangGraph, mixing 9 deterministic logic9<br>an and agentic behavior. Embed other patterns as nodes in your workflow.<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _SubAgents: Orquestación centralizada._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

###### _¿Cómo funcionan?:_ 

El agente principal decide que subagente invocar, que información proporcional y como combinar los resultados. El agente principal puede invocar a múltiples agentes en paralelo. 

###### _Ideal:_ 

Aplicaciones con múltiples dominios distintos donde se necesita un control centralizado del flujo de trabajo y los subagentes no necesitan conversar directamente con los usuarios. 

###### _¿Trade-off?:_ 

Añade una llamada al modelo adicional por interacción, ya que los resultados deben volver a pasar por el agente principal. 



<!-- Start of picture text -->
Wa Subagent A<br>User Request —]}| Main Agent le==__| subagentubage B<br>X<br>Final Response<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _Skills: Divulgación progresiva._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

###### _¿Cómo funcionan?:_ 

Las habilidades son especializaciones basadas principalmente en prompts, empaquetadas como directorios que contienen instrucciones, scripts y recursos. Al iniciarse, el agente solo conoce los nombres y descripciones de las habilidades. Cuando una habilidad se vuelve relevante, el agente carga su contexto completo. 

###### _Ideal:_ 

Agentes únicos con muchas especializaciones posibles, situaciones donde no se necesita imponer restricciones entre capacidades, o equipos distribuidos donde distintos equipos mantienen diferentes habilidades. 

###### _¿Trade-off?:_ 

El contexto se acumula en el historial de la conversación a medida que se cargan las habilidades, lo que puede generar una acumulación excesiva de tokens en llamadas posteriores. 



<!-- Start of picture text -->
SkillA<br>Userer RRequest —>| Mainin AgentAgent |—> skillB<br>X=<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _Handoffs: Transiciones impulsadas por el estado._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

###### _¿Cómo funcionan?:_ 

Cuando un agente invoca una herramienta de transferencia, actualiza el estado que determina cuál será el próximo agente en activarse. Esto puede implicar cambiar a un agente diferente o modificar el prompt del sistema y las herramientas disponibles del agente actual. _Ideal:_ Flujos de atención al cliente que recopilan información por etapas, experiencias conversacionales en múltiples fases, o cualquier escenario que requiera restricciones secuenciales donde las capacidades se desbloquean solo después de cumplir ciertas condiciones previas. 

###### _¿Trade-off?:_ 



<!-- Start of picture text -->
yes<br><!-- End of picture text -->

Es más dependiente del estado que otros patrones, lo que requiere una gestión cuidadosa del mismo. 

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _Handoffs: Asistente de un banco._ 



<!-- Start of picture text -->
Situacién inicial: El usuario escribe "Quiero hacer una transferencia"<br>Elagente activo es el Agente de Bienvenida. Su unico trabajo es identificar qué quiere el<br>usuario. Cuando detecta que quiere hacer una transferencia, llama a una herramienta llamada<br>transferir_a_verificacion() .<br>¢Qué pasa internamente cuando se llama esa herramienta?<br>Se actualiza una variable de estado:<br>estado_actual = “verificacion_identidad"<br>Eso dispara un cambio: ahora el sistema activa el Agente de Verificacién, que tiene un<br>prompt diferente, y solo tiene acceso a herramientas como verificar_rut() 0<br>verificar_clave() . No puede hacer transferencias todavia.<br>El usuario pasa la verificacién. El agente llamaa transferir_a_operaciones() yelestado<br>cambia:<br>estado_actual = “operaciones_bancarias"<br>Ahorase activa el Agente de Operaciones, que si tiene accesoa ejecutar_transferencia() .<br>Esta herramienta no estaba disponible antes porque no se habian cumplido las condiciones<br>previas.<br><!-- End of picture text -->

_Internamente, el agente interactúa y cambia a otros agentes sin que el usuario expresamente haya guiado a esos nodos._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _Router: Dirige y ejecuta en paralelo._ 



<!-- Start of picture text -->
Duocuc:.<br><!-- End of picture text -->

###### _¿Cómo funcionan?:_ 

El enrutador descompone la consulta, invoca cero o más agentes especializados en paralelo y sintetiza los resultados en una respuesta coherente. 

###### _Ideal:_ 

Aplicaciones con verticales distintas (dominios de conocimiento separados), escenarios que requieren consultas a múltiples fuentes en paralelo, o situaciones donde se necesita sintetizar resultados de múltiples agentes. 



<!-- Start of picture text -->
az.<br><!-- End of picture text -->

###### _¿Trade-off?:_ 

El diseño sin estado garantiza un rendimiento consistente por solicitud, pero genera una sobrecarga repetida de enrutamiento si se necesita historial de conversación. 

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 



_Experiencia de Aprendizaje 3 Observabilidad, Segurida y etica de Agente de AI_ 



_Experiencia de Aprendizaje 3 Observabilidad, Segurida y etica de Agente de AI_ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->



<!-- Start of picture text -->
Eventos discretos (prompts, respuestas, uso de<br>herramientas, pensamientos del agente).<br>Mejores Practicas: Estructurados, contextuales,<br>centralizados.<br>Tres Pilares de la © Valoresdel tiempo numéricos(latencia, agregados uso de tokens,a lo largo<br>Observabilidad tasa de exito).<br>Mejores Practicas: Etiquetado,<br>agregacion, alertas.<br>El camino completo de una solicitud a través del<br>sistema, mostrando la secuencia de operaciones.<br>Mejores Practicas: Instrumentacidon,<br>visualizacién, correlacién.<br><!-- End of picture text -->

_Tres “Stones”: Logs, Métricas e Traces(Trazas)._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
METRICAS CLAVE DE RENDIMIENTO (KPIS)<br>owes GI}<br>aeo KN<br>EXITO/FALLO<br>Tiempo de Uso de tokensy<br>respuesta del coste monetario Qué tan bien el Frecuenciaconla Qué herramientas<br>agente (total y por de las llamadas a agente cumple su que el agente se usan mas y con<br>componente). la API. objetivo (requiere completa las qué éxito.<br>evaluacion). tareas sin errores.<br><!-- End of picture text -->

_Métricas: Datos cuantificables del modelo._ 

## _Ataques comunes de AI._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

ATAQUES COMUNES _1- Utilizar la API descrita en el README para evaluar costos, modelos y latencia de una solución._ 

_2- En base a lo encontrado, ¿Qué mejoras se puede hacer en el código para poder disminuir la latencia de la solución?_ O1 02 03 04 

### _Guardrails: Protege tu sistema ante filtraciones ._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

##### _Inputs Guardrails_ 

Las dos principales fugas que evitan son: 

1. filtrar información privada a API externas. 

2. ejecutar mensajes maliciosos que comprometen su sistema 

- ¿Cómo puede pasar?: 

1. Un empleado copia información confidencial de la empresa o información privada de un usuario en un mensaje y la envía a una API de terceros.<sup>1</sup>. 

2. Un desarrollador de aplicaciones introduce políticas y datos internos de la empresa en el mensaje del sistema de la aplicación. 

3. Una herramienta recupera información privada de una base de datos interna y la agrega al contexto. 



<!-- Start of picture text -->
T got 403 error on this code. What did I do wrong?<br>5Gl pat url response= = “secret_token_that_shouldn’t_be “https: = get(url,  //apt.github.con/repos/(repo}/{ssuestpage=30" access_token=pat) leaked”<br>T got 483 error on this code. What did I do wrong? ReversiblePil map<br>pat = {ACCESS TOKEN) Bese nyo eae<br>E url response  = “https:/fapt.github.con/repos/{repo}/issuestpage=32” = get(url, access token=pat) shouldn’t_be_leaked"<br>GI The UAL you provided contains @ syntax error. The correct<br>URL should use ? to denote query parameters instead of &.<br>Ff lHere’s a corrected version of your code:<br>SB |pat = [ACCESS_TOKEN]<br>3 url = “https: //apt.github.con/repos/ (repo}/tssues?page=38"<br>S| response = get(url, access_token=pat)<br>g<br>©] The URL you provided contains a syntax error. The correct<br>BURL should use ? to denote query paraneters instead of &.<br>z Here’spat = “seca co r rectedet_token_that_shouldn’t_be_version of your code:<br>g response = get(url, access_token=pat) leaked”<br>FE url = “https: //api.github.con/repos/{repo}/issues?page=38<br>Figure 10-3, An example of masking and unmasking PI information using a reverse PII map to avoid sending<br>itto external APIs.<br><!-- End of picture text -->

### _Guardrails: Protege tu sistema ante filtraciones ._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

##### _Output Guardrails_ 

Sus funciones son: 

1. Detectar fallos de salida. 

2. Especificar la política para gestionar los diferentes modos de fallo. 



<!-- Start of picture text -->
* Quality<br>¢ Malformatted responses that don’t follow the expected output format. For<br>example, the application expects JSON, and the model generates invalid<br>JSON.<br>¢ Factually inconsistent responses hallucinated by the model.<br>¢ Generally bad responses. For example, you ask the model to write an essay,<br>and that essay is just bad.<br>* Security<br>* Toxic responses that contain racist content, sexual content, or illegal<br>activities.<br>¢ Responses that contain private and sensitive information.<br>¢ Responses that trigger remote tool and code execution.<br>¢ Brand-risk responses that mischaracterize your company or your<br>competitors.<br><!-- End of picture text -->

### _¿Cómo implementarlo?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
aspe.8., agent,ng, Input guardrailsp<br>iting) (e.g., Pll redaction)<br>eeeony  || ome Model API<br>(© 3) 210 “acon || Gg.eton e s,<br>Response | Output guardrails<br>+ Safety/verification<br>+ Structured outputs<br>Figure 10-4. Application architecture with the addition of input and output guardrails.<br><!-- End of picture text -->

_Sistema protegido, con input y output guardrails para resolver cualquier problema de filtraciones y seguridad._ 

### _¿Cómo implementarlo?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
aspe.8., agent,ng, Input guardrailsp<br>iting) (e.g., Pll redaction)<br>eeeony  || ome Model API<br>(© 3) 210 “acon || Gg.eton e s,<br>Response | Output guardrails<br>+ Safety/verification<br>+ Structured outputs<br>Figure 10-4. Application architecture with the addition of input and output guardrails.<br><!-- End of picture text -->

_Sistema protegido, con input y output guardrails para resolver cualquier problema de filtraciones y seguridad._ 

#### _LangSmith Engine : El ciclo se cierra._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->



<!-- Start of picture text -->
P or ary<br>pz<br>-.<br>o<br>‘;<br>5 ‘i<br>;<br>..<br>.’<br>*3%.. ’<br>é<br>ee<br><!-- End of picture text -->

**Notas:** https://www.langchain.com/blog/introducing-langsmith-engine 



_Consejos, ideas y pensamientos_ 

## Que me hubiese gustado saber antes… 



<!-- Start of picture text -->
DuocuCc:.<br><!-- End of picture text -->

_1. El cambio es lo único constante._ 

_2. Todo lo que aprendan en esta clase posiblemente será obsoleto en 1 o 2 años._ 

_3. Lean lo más posible.  (Papers, articulo y escuchen a personas)._ 

_4. Tengan coraje._ 

_5. La barrera de construcción software bajaran constamente. Cosas criticas: Infractuctura, Arquitectura (Design patron), Testings y Cyber Seguridad._ 

_6. Aprendan cosas diversas.  La creatividad viene de juntar distintos puntos de vista._ 

_7. Prioriza de rodearme con personas más inteligentes que tu._ 

**_Nota:_** _https://www.youtube.com/watch?v=DBPFU0Z5jV4_ 





Jim Rohn… _Padre del Desarrollo Personal_ . 





_Muchas gracias_ 

