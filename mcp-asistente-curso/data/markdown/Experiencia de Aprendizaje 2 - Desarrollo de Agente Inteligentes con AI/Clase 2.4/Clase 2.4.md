

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

## _Noticias: Agentic Arquitecture as small, honest programs._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Medium Q Search Write { sonvp ] Sign in<br>ee| ee ee<br>Beyond the workflow: agentic<br>Architecture as small, honest<br>programs<br>How we rebuilt our Al workflow engine around agents and tools that<br>own their behavior — and why “who answers the user” becamea first-<br>class design question.<br>@ Dario Andrés Mufioz Prudant | Follow ) Tminread - Apr 1,2026<br><!-- End of picture text -->

_Nota: https://ai.plainenglish.io/beyond-the-workflow-agentic-architecture-as-small-honest-programs-24e6b2facd3a_ 





_¿Quién es el? Jawed Karim , “ Me at the zoo”._ 

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

#### _¿Cómo funcionan?:_ 

El agente principal decide que subagente invocar, que información proporcional y como combinar los resultados. El agente principal puede invocar a múltiples agentes en paralelo. 

#### _Ideal:_ 

Aplicaciones con múltiples dominios distintos donde se necesita un control centralizado del flujo de trabajo y los subagentes no necesitan conversar directamente con los usuarios. 

#### _¿Trade-off?:_ 

Añade una llamada al modelo adicional por interacción, ya que los resultados deben volver a pasar por el agente principal. 



<!-- Start of picture text -->
Wa Subagent A<br>User Request —]}| Main Agent le==__| subagentubage B<br>X<br>Final Response<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _Skills: Divulgación progresiva._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

#### _¿Cómo funcionan?:_ 

Las habilidades son especializaciones basadas principalmente en prompts, empaquetadas como directorios que contienen instrucciones, scripts y recursos. Al iniciarse, el agente solo conoce los nombres y descripciones de las habilidades. Cuando una habilidad se vuelve relevante, el agente carga su contexto completo. 

#### _Ideal:_ 

Agentes únicos con muchas especializaciones posibles, situaciones donde no se necesita imponer restricciones entre capacidades, o equipos distribuidos donde distintos equipos mantienen diferentes habilidades. 

###### _¿Trade-off?:_ 

El contexto se acumula en el historial de la conversación a medida que se cargan las habilidades, lo que puede generar una acumulación excesiva de tokens en llamadas posteriores. 



<!-- Start of picture text -->
SkillA<br>Userer RRequest —>| Mainin AgentAgent |—> skillB<br>X=<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _Handoffs: Transiciones impulsadas por el estado._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

#### _¿Cómo funcionan?:_ 

Cuando un agente invoca una herramienta de transferencia, actualiza el estado que determina cuál será el próximo agente en activarse. Esto puede implicar cambiar a un agente diferente o modificar el prompt del sistema y las herramientas disponibles del agente actual. _Ideal:_ Flujos de atención al cliente que recopilan información por etapas, experiencias conversacionales en múltiples fases, o cualquier escenario que requiera restricciones secuenciales donde las capacidades se desbloquean solo después de cumplir ciertas condiciones previas. 

#### _¿Trade-off?:_ 



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

#### _¿Cómo funcionan?:_ 

El enrutador descompone la consulta, invoca cero o más agentes especializados en paralelo y sintetiza los resultados en una respuesta coherente. 

#### _Ideal:_ 

Aplicaciones con verticales distintas (dominios de conocimiento separados), escenarios que requieren consultas a múltiples fuentes en paralelo, o situaciones donde se necesita sintetizar resultados de múltiples agentes. 



<!-- Start of picture text -->
az.<br><!-- End of picture text -->

##### _¿Trade-off?:_ 

El diseño sin estado garantiza un rendimiento consistente por solicitud, pero genera una sobrecarga repetida de enrutamiento si se necesita historial de conversación. 

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

## _¿Cuál elegir?: Depende._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
Multiple distinct domains (calendar, email, CRM), need parallel execution Subagents<br>Single agent with many possible specializations, lightweight composition Skills<br>Sequential workflow with state transitions, agent converses with user throughout Handoffs<br>Distinct verticals, query multiple sources in parallel and synthesize results Router<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langchain/multi-agent#router-4_ 

### _Libro: Warren Buffet, Interpreation of financial statements._ 



<!-- Start of picture text -->
DuocuCc:.<br><!-- End of picture text -->



<!-- Start of picture text -->
nene<br>WARREN<br>Arne ree<br>INTERPRETATION OF<br>FINANCIAL STATEMENTS<br>Dine Seay the the Company vit 6 lien te L compeminy Adbunmage<br>MARY QUPTETE & DAVID CLARK<br>beeeing Note<br>RUIPETroOLOGY<br>se<br>THE TAG OF PARREN BUTTETT<br>| manners oom<br><!-- End of picture text -->

_Nota: https://www.buscalibre.cl/libro-warren-buffett-and-the-interpretation-of-financial-statements-the-search-for-the-company-with-a-durablecompetitive-advantage/9781416573180/p/2018929?srsltid=AfmBOoqBwiCPD64ZTjIK1B5Vx2dnq53ESfb3gbcHtiHaiNIRIrIOW29H_ 

### _Actividad 1: Nuestro mejor analista de datos._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
SQL Agente<br>START Supervisor<br>Python<br>END<br>Agente<br>END<br><!-- End of picture text -->

### _Actividad 1: Solución_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Agente<br>END<br>Reporteria<br>SQL Agente<br>START Supervisor<br>Python<br>END<br>Agente<br>END<br><!-- End of picture text -->

