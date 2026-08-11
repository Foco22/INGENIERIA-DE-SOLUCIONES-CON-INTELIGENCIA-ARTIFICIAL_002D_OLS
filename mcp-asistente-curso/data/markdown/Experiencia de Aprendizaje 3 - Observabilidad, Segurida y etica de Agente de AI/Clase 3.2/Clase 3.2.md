

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

### _Noticias: LangChain Lanza LangSmith Engine ._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
$x LangChain Products v Learn» Docs Company » Pricing Get a demo<br>LangSmith<br>Introducing LangSmith Engine<br>£) MayBen Tannyhill13, 2026 =<br><!-- End of picture text -->

_Nota: https://www.langchain.com/blog/introducing-langsmith-engine_ 

## _LangSmith Engine : Los fallos terminan siendo oportunidades._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Engine surfaces this as a single named issue, “Agent fails to handle subscription cancellation<br>requests accurately.” It shows you the severity (high, affecting 12% of support sessions this<br>week), the timeline (started four days ago, correlating with a recent deployment), and links to the<br>specific traces as evidence.<br>With your repository connected, Engine reads the relevant code and identifies the root cause.<br>The cancellation tool description is ambiguous, causing the agent to attempt cancellation<br>when users are only asking about their options. Engine drafts a PR with a targeted fix to the<br>tool description.<br>To keep tracking this behavior going forward, Engine proposes a custom online evaluator scoped<br>to this exact issue, so if the failure pattern recurs after the fix ships, the issue gets resurfaced<br>automatically with updated details.<br>Engine also pulls the failing traces into a dataset for your offline eval suite, with per-example<br>criteria that define what the correct output should contain. The failures that madeit to production<br>become the test cases that keep them out.<br>That's the full cycle, run autonomously and surfaced for your review. Production signal becomes<br>a clustered issue, then a diagnosed root cause, a proposed fix, and eval coverage.<br><!-- End of picture text -->



<!-- Start of picture text -->
Monitor ge ng Build<br>Cluster and Diagnose Proposed Fix<br>Issues via PR<br>- a<br>aN a<br>= :<br>De ploy Test<br>Ship Tested See Add evals to<br>Changes test suite<br><!-- End of picture text -->

_Nota: https://www.langchain.com/blog/introducing-langsmith-engine_ 

## _¿Que es la Observabilidad?_ 

**_Observability_** is the ability to understand the internal state of a system by examining its outputs. 

In software, this is typically achieved by analyzing telemetry data such as traces, metrics, and logs. 

To make a system observable, it must be instrumented. That is, the code must emit traces, metrics, or logs. The instrumented data must then be sent to an observability backend. 





_Nota: https://www.langchain.com/blog/introducing-langsmith-engine_ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->



<!-- Start of picture text -->
Eventos discretos (prompts, respuestas, uso de<br>herramientas, pensamientos del agente).<br>Mejores Practicas: Estructurados, contextuales,<br>centralizados.<br>Tres Pilares de la © Valoresdel tiempo numéricos(latencia, agregados uso de tokens,a lo largo<br>Observabilidad tasa de exito).<br>Mejores Practicas: Etiquetado,<br>agregacion, alertas.<br>El camino completo de una solicitud a través del<br>sistema, mostrando la secuencia de operaciones.<br>Mejores Practicas: Instrumentacidon,<br>visualizacién, correlacién.<br><!-- End of picture text -->

_Tres “Stones”: Logs, Métricas e Traces(Trazas)._ 

## _Métricas: “Click” a métricas de performances._ 



-Latency (End-to-End Latency) _:_ Tiempo total desde la solicitud hasta la respuesta completa. Es más importante para respuestas cortas y no transmitidas en tiempo real (non-streamed). 

-Requests per Second (RPS): cuántos usuarios concurrentes puede manejar el sistema. 

-Costo por interacción = (Prompt tokens × precio) + (Completion tokens × precio) 

- Prompt tokens — todo lo que entra al modelo: system prompt, historial de 

- conversación y mensaje del usuario 

- Completion tokens — los tokens generados por el modelo como respuesta 

## _Ejercicios: Mide, evalúa y plantea mejoras._ 



_1- Utilizar la API descrita en el README para evaluar costos, modelos y latencia de una solución._ 

_2- En base a lo encontrado, ¿Qué mejoras se puede hacer en el código para poder disminuir la latencia de la solución?_ 

