

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

_Noticias: Magnifica Humanitas, reacción del Papa sobre la AI._ 



<!-- Start of picture text -->
riday M<br>rsMagnifica2 ye Humanitas’:. 9 Al and the Pope<br>@ vrscncomrnoonee AS Bg y in 8<br>Member ratings :<br>Wellargued: [BJ] interesting points: BJ Agreewith arguments: Latest articles<br>:<br>The Prado<br>' little platoon<br>yo “a Popski's Private Army: a very<br>= - Howto innovate in business<br>»<br>. j and embrace change<br>\e [aisseueonss)<br>Movebound: the art of<br>“<= Zugzwang<br>\ ‘Magnifica Humanitas’: Al and<br>, H the Pope<br><!-- End of picture text -->



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

_Nota: https://www.thearticle.com/magnifica-humanitas-ai-and-the-pope_ 



## _<u>REPASO</u>_ 

_¿Cuál es la diferencia entre la inteligencia artificial que uso en visual studio code o el chatGPT y el código de mi agente de la evaluación 2?_ 



## _<u>REPASO</u>_ 

_¿Qué es un sistema multi-agente? https://github.com/Foco22/INGENIERIA-DE-SOLUCIONES-CON-INTELIGENCIAARTIFICIAL_002D_OLS/tree/main/Experiencia%20de%20Aprendizaje%202%20%20Desarrollo%20de%20Agente%20Inteligentes%20con%20AI/Clase%202.3_ 



<!-- Start of picture text -->
DuocUC:.<br><!-- End of picture text -->

## _¿Cuál es la diferencia entre AI y ML?_ 

## _<u>REPASO</u>_ 



<!-- Start of picture text -->
Artificial Intelligence<br>:<br>Machine Learning<br><!-- End of picture text -->

Artificial intelligence (AI) is technology that enables computers and machines to simulate human learning, comprehension, problem solving, decision making, creativity and autonomy 

_https://www.ibm.com/think/topics/artificial-intelligence_ 

## _¿Cuál arquitectura es más escalable?_ 



<!-- Start of picture text -->
DuocUC:<br><!-- End of picture text -->

#### **_Plan A_** 

**_Plan B_** 

_<u>REPASO</u>_ 

El agente supervisor decide a qué nodo dirigirse en función de las palabras proporcionadas por el usuario. Por ejemplo, si el usuario utiliza términos como "comprar", "compras", "comprarías" o similares, el supervisor selecciona el Agente A. 

El agente supervisor invoca a un LLM, que en base a un prompt de sistema, y una instrucción clara, decide a que agente debe llamar en cada momento. 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

## _<u>REPASO</u> ¿Cómo se escribe un endpoint (API) correctamente?_ 



<!-- Start of picture text -->
REST‘best practicesices (2/2(2/<br>OUse lowercase letters in URIs<br>Do not use file extensions<br>»http://stelios.io/api/users/user-data.json /* Do not use this */<br>@Never use CRUD function names in URIs<br>» http://stelios.io/api/users/get-users /* Do not use this */<br>» http: //stelios.io/api/users /* This is better */<br><!-- End of picture text -->



<!-- Start of picture text -->
REST best ppractices (1/2)/<br>© Use forward slash (/) to indicate hierarchical relationships<br>» http: //stelios.io/api<br>» http://stelios.io/api/users<br>» http://stelios.io/api/users/{id}<br>© Do not use trailing forward slash (/) in URIs<br>» http://stelios.io/api/users/ /*Do not use this*/<br>» http: //stelios.io/api/users /#this is bettert/<br>© Use hyphens (-) to improve the readability of URIs, do not use underscores(_ )<br>» http://stelios.io/api/users/mini_film/{id} /*Do not use this */<br>» http: //stelios.io/api/users/mini-film/{id} /*This is better*/<br><!-- End of picture text -->



<!-- Start of picture text -->
UC<br><!-- End of picture text -->



<!-- Start of picture text -->
Horizontal vs Vertical scaling<br>¢ Horizontal: Add more instances on a cluster<br>¢ Vertical: Increase the size of the virtualized resource (e.g., CPU, RAM, etc.)<br>= What is the problem with Vertical?<br>_oOo; =— @e * Servers have limits<br>7 — What is the problem with Horizontal?<br>o| = SJeIeaeS « It's a distributed system<br>Horizontal<br><!-- End of picture text -->

_Escalabilidad de un sistema: Mas maquinas o mas potencia._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
What are examples of vertical/horizontal scaling systems?<br>Vertical Horizontal<br>Monolithic Web Applications Web Applications with Load Balancing<br>= Relational Databases (e.g., MySQL) Microservices Architectures<br>= Virtualization and Virtual Machines NoSQL Databases (e.g., MongoDB)<br>= Legacy Enterprise Applications Containers and Kubernetes<br>lo<br>coca |cocme foc 9<br><!-- End of picture text -->

_Ejemplos: Un start-up, con pocos usuarios, suele ser monolito._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
A<br>Vertical scalability costs rise<br>sharply after a certain point. }<br>Vertical vs 2 Z<br>. Vy a<br>Horizontal 8 Initial costs associated “Horizontal scalability<br>cost 2 | with horizontal scalability —*" becomes much more<br>& | tend to be higher. ex efficient after a certain<br>Rs} a“ point.<br>Extra capacity needed 2<br><!-- End of picture text -->

_¿Cuánto moverse?: Suele ser una decisión económica ._ 

_Kubernetes: La solución escalable que soluciona cualquier tipo de problema de conexión entre VMs._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

_Este ramo no es sobre Kubernetes. No es complicado configurarlo, ya que hoy en día, con GCP, es bastante fácil montar estos servicios, el problema es el costos, y que aplica solo a empresas que tienen un flujo de información alta, no a pequeñas_ 

_empresas._ 

### _Optimización por modelamiento: Hazlo más pequeño._ 



<!-- Start of picture text -->
UC<br><!-- End of picture text -->



<!-- Start of picture text -->
Fine-Tuning Quantization Distillation<br>Adapt model to Reduce model size Transfer knowledge<br>specific data or tasks and computation to a smaller model<br><!-- End of picture text -->

**_Nota_** _: https://www.linkedin.com/pulse/fine-tuning-quantization-distillation-three-very-ways-alvin-kabwama-i47zc/._ 

### _Optimización por inferencia de servicio: GPU más eficiente._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Time<br>ee<br>rues QQQ OOOO O00 0 OQ<br>Figure 9-15. Dynamic batching keeps the latency manageable but might be less compute-efficient.<br><!-- End of picture text -->

_Requests esperan como en un Bus en_ **_Static batching_** _, y en_ **_Dynamic batching_** _, esperan como en un bus, o hasta un cierto tiempo._ 

### _Prompt caching: No te repitas a ti mismo._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
System Your task is to identify entities in a text.<br>Cachedand<br>reused | prompt ) °"°<br>between ~<br>queries Text: "Brave New Horld is a dystopian novel written by Aldous<br>Example ¢ Huxley, first published in 1932."<br>Entities: Brave New World, Aldous Huxley<br>Thetask{ cag,  TAT WT AT ATES A)<br>Figure 9-17. With a prompt cache, overlapping segments in different prompts can be cached and reused.<br><!-- End of picture text -->



<!-- Start of picture text -->
Table 9-3. Cost and latency reduced by prompt caching. Information from Anthropic (2024).<br>Latencyw/o Latency with Cost<br>Use case caching (time to _ caching (time to —<br>first token) first token)<br>Chat with a book (100,000-  11.5s 2.48 (-79%) 90%<br>token cached prompt)<br>;<br>Many-shotsa ia hetin; 1.6 . 1.1s Bea.31%) -86%<br>(10,000-token prompt)<br>Multi-turn conversation ~10s ~2.5 S (-75%) 53%<br>(10-turn convo with a long<br>system prompt)<br><!-- End of picture text -->

_Prompt caching esta disponible por los proveedores de APIs de LLMs, y es una buena forma de optimizar costos._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
_— = _—<br>rE i<br>. | : a<br><!-- End of picture text -->



<!-- Start of picture text -->
oY ><br>a<br>,<br><!-- End of picture text -->



<!-- Start of picture text -->
aay<br>Be re E stops<br>————3~<br><!-- End of picture text -->



<!-- Start of picture text -->
———SS }<br>—=<br>¢ 100, 120: 50: 10<br>3 “—_* K€ j z<br><!-- End of picture text -->

_Oxford Tech Week: Agentes, Iot y personas._ 

