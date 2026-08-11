

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 



<!-- Start of picture text -->
ANTHROP\C<br>System Card:<br>Claude Mythos<br>Preview<br><!-- End of picture text -->



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

_Noticias: Capacidades, limitaciones y evaluaciones de seguridad de un nuevo modelo llamado Claude Mythos ._ 

_Nota: https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf_ 



_¿Qué es la memoria? “Lo que te hace tú no es tu cuerpo — sino que recuerdas haber sido tú antes.”_ 

_John Locke (1689)_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Ic6nica (visual)<br>1 Ecoica (auditiva)<br>MEMORIA<br>SENSORIAL<br>Haptica (tactil)<br>MEMORIA MEMORIA A Memoria de trabajo<br>Funci6n cognitiva eA 7 (MT) u operative<br>‘superior<br>Seméntica<br>Explicita (declarativa) (conocimiento; lenguaje)<br>MEMORIA A Episédica(experiencia personal)<br>- LARGO PLAZO<br>(MLP)<br>Implicita Habilidades motoras<br>(procedimental o no<br>declarativa) Condicionamiento<br><!-- End of picture text -->

_Memoria : Tipos de memoria en el humano_ . 

## _Memoria : Tipo de memoria en los agentes_ . 



<!-- Start of picture text -->
DuocUCc:<br><!-- End of picture text -->



<!-- Start of picture text -->
Short-term memory ; Long-term memory<br>'<br>|SSee<br>|| (Seen<br>'<br>Gnome} | | SSeS<br>(| NN ~#<br>!<br>Checkpointer i Store<br><!-- End of picture text -->

Short-term memory: _Es todo lo que el agente puede "ver" y recordar en este momento — su ventana de atención activa._ 

Long-term memory: _Es todo lo que el agente puede recordar más allá de su context window — información persistente que sobrevive entre sesiones._ 

## _LangChain: Técnicas avanzadas de memoria._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Memory Type What is Stored Human Example Agent Example<br>Semantic Facts Things |learnedin school Facts about a user<br>Episodic Experiences Things | did Past agent actions<br>Procedural Instructions Instincts or motor skills Agent system prompt<br><!-- End of picture text -->

_La memoria también puede clasificarse según el tipo de conocimiento que almacena, tomando como base la ciencia cognitiva. Se distingue la semántica , episódica y procedimental._ 

_Nota: https://docs.langchain.com/oss/python/langgraph/memory_ 

## _Semántica: Tu perfil._ 

_Los recuerdos semánticos pueden gestionarse de distintas maneras. Por ejemplo, los recuerdos pueden consistir en un único "perfil" continuamente actualizado con información bien definida y específica sobre un usuario, organización u otra entidad (incluido el propio agente)._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Conversation Old profile<br>[Human message= | "friends":age": None,["Bob"]<br>}<br>{<br>“name: Tom,<br>"age": 22,<br>“friends”: ["Bob", “Joe"]<br>3<br>New profile<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langgraph/memory_ 

## _Episódica: Acciones o episodios pasadas ._ 



_La memoria episódica, tanto en humanos como en agentes de IA, implica recordar eventos o acciones pasadas. El artículo CoALA lo plantea de forma clara: los hechos pueden escribirse en la memoria semántica, mientras que las experiencias pueden escribirse en la memoria episódica. En el caso de los agentes de IA, la memoria episódica se utiliza frecuentemente para ayudar al agente a recordar cómo llevar a cabo una tarea._ 



<!-- Start of picture text -->
Lngfiewth = oc<br>ee ee ee en<br>es pioneer compen ;<br>mm<br>sans<br>petGaetan a aes sci: ‘he| “a Raat ip<br>cha —"e: «<br>pan<br>pes Lo | ih<br>saa<br>i » &<br>anicataie<br>winaai<br>Setentinizn<br>mt<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langgraph/memory_ 

## _Procedural: Ejecutar acciones o habilidades ._ 



<!-- Start of picture text -->
Conversation Old instructions<br>You are an expert<br>tweet writer...<br>You are an expert<br>tweet writer. Do not<br>use hashtags...<br>New instructions<br><!-- End of picture text -->

_Son las reglas utilizadas para realizar tareas. En los humanos, la memoria procedimental es como el conocimiento interiorizado de cómo ejecutar acciones, como montar en bicicleta mediante habilidades motoras básicas y equilibrio. La memoria episódica, en cambio, implica recordar experiencias específicas, como la primera vez que se montó en bicicleta sin ruedines o un paseo memorable por una ruta pintoresca. En el caso de los agentes de IA, la memoria procedimental es una combinación de los pesos del modelo, el código del agente y el prompt del agente, que en conjunto determinan la funcionalidad del agente._ 



<!-- Start of picture text -->
DuocUCc<br><!-- End of picture text -->

_Nota: https://docs.langchain.com/oss/python/langgraph/memory_ 

## _The Forgetting Problem: ¿Qué recordar?_ 



<!-- Start of picture text -->
DuocuCc:<br><!-- End of picture text -->

**_Andrej Karpathy_** : _“One common issue with personalization in all LLMs: a casual question from two months ago gets permanently treated as a deep interest and keeps resurfacing.” The real problem isn’t remembering - it’s knowing what to forget”._ 

_Nota: Andrej Karpathy, who co-founded and formerly worked at OpenAI_ 

## _Arquitecturas de memoria: Flat hasta grafos._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

_La memoria puede ser almacenada como:_ 

_1. Base de datos vectorial (Vector Database)_ 

_2. Sistema de archivos (File System)_ 

_3. Contexto (Context Window)_ 

_4. Base de datos de grafos (Graph_ 

_Database)._ 



<!-- Start of picture text -->
Product Company / Founder Stars Funding Architecture Backend LongMemEval<br>Memd Deshraj Yadav (YC) 50K $24M Series A Vector + Graph 20+ backends + Neodj 49%<br>Graphiti/Zep Zep Al MK Temporal KG Neodj 712%<br>Letta/MemGPT UC Berkeley 2K = S10M LLM-as-0S SQLite/PG -<br>OpenViking ByteDance/Volcengine 19K Internal Context DB Volcengine -<br>Supermemory Dhravya Shah (age 19) 17K © $2.6MSeed Atomic facts + relations Cloudflare KV 85.2%<br>Cognee Cognee Al BK OST.5M ECL + Memify LanceDB + Kuzu -<br>Memori GibsonAl (Bobur U.) 12K - Pure SQL PG/SQLite -<br>Nowledge Nowledge Labs 18 - Local personal KG Local + MCP -<br>Hindsight 64K - net + 4yay retrieval Graph + Vector + BM25 91.4%<br>HydraDB HydraDB Inc Closed $6.5 Git-style append KG Custom graph + vector 90.8%<br>Mem0S MemTensor 19K - Memory 0S Qdrant + Neodj 75.8%<br>mem9 (SJTU/IAAR)PingCAP (Ed Huang) 751 - Stateless plugin TiDB -<br>Platform Built-in Memory<br>ChatGPT OpenAl - - User facts + history retrieval Closed source =<br>Claude.ai Anthropic - - Project Knowledge Base Closed source -<br>Claude Code Anthropic - - CLAUDE.md + MEMORY.md File system -<br>Codex Opendl - - File system + sandbox File system -<br><!-- End of picture text -->

## _Una mirada a nivel de producto._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

_A nivel de producto, el memoria puede ser catalogada en dos ejes:_ 

_1. Structured Graph vs Flat Storage_ 

_2. Active Managment or Passive Store._ 



<!-- Start of picture text -->
Active Mgmt @ Hindsight<br>Letta/MemGPT @ @ Zep/Graphiti<br>ChatGPT @ Memos<br>Claude.ai<br>Mem0 @ @ Supermemory @ HydraDB<br>Flat Storage Memori @ @ Cognee<br>OpenViking @ Structured Graph<br>Claude Code low! r )<br>Codex<br>Passive Store<br><!-- End of picture text -->

_Agentes más que solo LLMs . Plan Memoria mecanismos que permiten a un Capacidad del modelo de modelo retener y utilizar descomponer un problema en información. tareas para resolverlo. . . La memoria no es solo un accesorio en los agentes, es parte fundamental para su auto evolución Tools LLMs Funciones que le permiten al El motor del modelo. Los principales proveedor modelo conectarse con el mundo son OpenAI, Google y Anthropic exterior. ._ 



