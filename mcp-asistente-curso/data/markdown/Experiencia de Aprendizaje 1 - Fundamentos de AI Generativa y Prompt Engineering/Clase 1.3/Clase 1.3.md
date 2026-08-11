

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

## _Noticias:_ AI no es solo software, sino hardware. 





<!-- Start of picture text -->
Semestre 2026-1<br><!-- End of picture text -->

_Recapitulemos: Los LLMs como un sistema aislado._ **Prompt Engineering** _Texto Generado, tokens. Prompts & Parametros._ **_LLMs_** ~~—C}-~~ _Modelos_ 



_Recapitulemos: Los LLMs como un sistema aislado._ **Prompt Engineering** _Texto Generado, tokens. Prompts & Parametros._ **_LLMs_** ~~—C}-~~ _Modelos_ 



_¿Qué falta?_ 

_Recapitulemos: Los LLMs como un sistema aislado._ **Prompt Engineering** _Texto Generado, tokens. Prompts & Parametros._ **_LLMs_** ~~—C}-~~ _Modelos Los modelos no tienen acceso a datos actuales ni privados.  No tienen memoria . No tienen acceso aplicaciones, ni al mundo real. No pueden ejecutar algo. Son como un niño que solo me sirve para tareas generalistas._ 





<!-- Start of picture text -->
De generalista a especialista:  El camino de la AI.<br>LLMs LLMs + RAG<br>Agentes<br>Context Tools Memoria<br>Input<br>Input Input<br>LLM<br>LLM LLM<br>Output<br>Output<br>= Output | =<br><!-- End of picture text -->



## _¿Qué es RAG?: Retrieval-Augmented Generation_ 



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

## _Retrieval: Dos caminos, mismo objetivo._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

**_Term base retrieval_** 

### **_Embedding base retrieval_** 

**_Term Frecuency (TF)_** _:_ Numero de veces que un termino aparece en un documento.  Si el termino aparece más veces, es más relevante. 

Transforma la información en vectores, se encuentran los más parecidos, y luego se inyectan al modelo de lenguaje como parte del prompt. 

**_Inverse document frecuency (IDF)_** _:_ La importancia de un termino es inversamente proporcional a la cantidad de documentos donde aparece el termino. 

_Las soluciones más típicas a este tipo de retrieval son:_ **_ElasticSearch_** _y_ **_BM25_** _._ **_Esta solución se enfoca en el lexical level_** 

Los vectores son capaces de capturar la representación semántica del texto. 



**_Esta solución se enfoca en el semantic level._** 

## _¿Qué pasaría si solo usamos term base?_ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
Consulta<br>os ..<br>_<br><!-- End of picture text -->

## _¿Qué pasaría si solo usamos term base?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Consulta<br>os . External<br>aa Memory<br><!-- End of picture text -->

## _¿Qué pasaría si solo usamos term base?_ 





<!-- Start of picture text -->
External<br>Memory<br><!-- End of picture text -->

**_Consulta ¿Qué es la arquitectura Transfomers?_** 



<!-- Start of picture text -->
yA<br><!-- End of picture text -->



<!-- Start of picture text -->
i.i~ 9 ‘A (A<br>TRANSFORMERS<br>Rite<br>4 8 > =. % a<br>a4 Aa,<br><!-- End of picture text -->



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

## _¿Qué pasaría si solo usamos term base?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

**_Consulta_** ~~@_~~ External Memory **_¿Qué es la arquitectura Transfomers?_** Transformer (=) 

## _¿Qué pasaría si solo usamos term base?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Le I<br>Consulta<br>a Mey , a i<br>3 External ae:<br>Memory<br>¿Qué es la<br>arquitectura<br>Transfomers?<br>\ Transformer se<br>Attention Is All You Need les =|<br><!-- End of picture text -->

**_El LLMs seria alimentado tanto con la información de la arquitectura de los LLMs, junto con la película de Transformers._** 

## _¿Qué pasaría si solo usamos term base?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Le I<br>Consulta<br>a Mey , a i<br>3 External ae:<br>Memory<br>¿Qué es la<br>arquitectura<br>Transfomers?<br>\ Transformer se<br>Attention Is All You Need les =|<br><!-- End of picture text -->

**_Hybrid Search:_** Lo mejor de los dos mundos **_._** 

## _Arquitectura de RAG:_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
File<br>Embedding<br>User Query<br>Query<br>Emebdding Index &<br>Vector DB<br>Model Splitter<br>ee<br>2— 8<br>1.Embedding Model:  Se<br>convierte la consulta del usuario<br>Response Context relevant<br>en un embedding.<br>to query<br>Generative  2.Retriever:  Se obtiene  k  data<br>Retriever<br>Model chunks con los embeddings más<br>cercanos a la query del usuario.<br><!-- End of picture text -->

## _Divide and Conquer: Divide el texto en fragmentos._ 



<!-- Start of picture text -->
DuocUC*<br><!-- End of picture text -->



<!-- Start of picture text -->
‘TWP re ALPOPOT ited! ef ULAR coterie bined en ttake btciiitachiew. wed tratving obgettiien:<br><!-- End of picture text -->

_Los archivos son divididos en_ **_chunks,_** _lo que permite localizar y recuperar únicamente la información relevante para cada consulta._ 

**1. Chunk size** — el tamaño de cada fragmento (medido en tokens o caracteres). Define cuánto texto va en cada chunk. Si es muy grande pierdes precisión en el retrieval; si es muy pequeño pierdes contexto. 

**2. Chunk overlap** — cuántos tokens/caracteres se repiten entre un chunk y el siguiente. Sirve para evitar que una idea importante quede cortada justo en el borde entre dos chunks. 

## _Los LLMs se pierden con infinito contexto ._ 



<!-- Start of picture text -->
DuoOCcUC:<br><!-- End of picture text -->



<!-- Start of picture text -->
Lost i i n the Middle:: HHow Language Models Use Long Contexts<br>igelson F. Liu'* Kevin LiLin’ John Ashwin Paranj<br>MicheleBevilacqua’Bevi Fabio Petroni?Hewitt! PercyLiang’Li ijape’<br>1 ‘StanfordiversityUni “Universinfliuécs.Iniversity‘ - st ofofanford.eduCaliforniCali fornia, Berkeleyy — *Samaya Al<br>Albstract 2070 tal Retrieved Documents (~4K tokens)<br>Whilerecent Langgrape nodes kav<br>ity wtakeJong contexts asi ve the abil-f 5<br>m little isis  known aboutrhea» well atraatythey = 7<br>Q ger context.We analyze the 3<br>bedN> identifyingofsical’ angusfyiig and key-age relewmodels-valueon retrieval twoyini tasksperformancequestionthat questa an-requil gy<g<br>significantly when — we peg. 4<br>can degrades |. We find that 60<br>_~ perf<br>changing the post<br>io) Leen mance<br>N tion, indicat ion of relevant 5th 15th 20th<br>— do not robustlyting thatmake currus e ntoflanguageinformationi informa-modelsA  in =AstPosition of Document10th with theAnswer<br><!-- End of picture text -->



<!-- Start of picture text -->
apart<br>ighof ons, nd OPP 3.5<br>Mrs rt ed35.09 89%<br>56.0%<br>fe 16KPitan xropiceatsAPI; Cli(sky aah:  tia<br>18 (00aximum contexteerieCha:nitgt os<br>Claudsa maxi nthropi SandtextCl length HesGPT-3.$-ESyourpeoTut 16k)K) Dre“ee76.1%<br>esveeo(100K) hs {length of ahented8KecnieatChie i and ere GPE:5-Tuo f oe BAK<br>Hoes topenaateirtetitemulti-documa ae question  scouracyicf aaseeie  lal takask,<br>23 Results ‘ead Dikcoasion<br>Weeipa ig ipeealiates er at using reljevantcurve—modelinformatiationsarethatoftenoccursmiLaiat<br>prrecant sed doesent monte containing 1C<br>mt informationawithinwithin 0 ¥ery‘ginningbeginnl (pri macy bias) and<br>varying scant irene 5 prescite ma} is<br>the input cwealpositionTo pegebeliigcor performancemodel  ayperfor. ti- FinisSO" performance informati perfor-the<br>chacleweneracle settings we also evafaluatentextualizeon th¢ closed-book bia pleteeectof (recencyitsIti-documerinput biasPalant QA. RecaiekForperforms examphiple, aeGPT-3,3,5-<br>ihodile foe (Table 1), In the Suitekice oe<br>n 20%—in<br>re eliend aitst nisrely oronbtthethe i rcaretparametretric i  memor sagI mises by m heefea sh aaduefie: lower than  endof<br>to gener insct answer, On the Tore! NY in 20:yore tha any input d I Mince<br>petisinglef the oracledocum setting,setti 2,questionlanguagemn. swer andmust bomaethatbokiceito perforo withoutmance; netiisilal a  56.nyeen0iWi1%). dahaingsTheselocuments isae snehlyeoceashed reason(i oo ptedindicoveper a fortein<br>forModelperformance relevant ine 40Eee ks. a<br>;input Pntod  context,  Seueran rf the ie Wigheak  beginnin,  Sian cheat ts at using inputmodicontext.els areWhe:not neswessarily bet:<br>ing the positilox Puiters illustrated i gor endinthein.of iHe ie context windowWi ofnthePasii a modk con:<br>ier coohen substantial decreases in miail OMoe fits in th<br>perfsiane leads toparespapar, We see a disAryieee. 5, chang- Extended-context¢ between them ii nterpart, W lel<br>pees‘We use the digparticular, perfiexamformanesextended-context cout<br>Pitan ‘on a subset<br>documentas 0ther modelRicaaiacsiindliments, pdmsfind8 versionson 8 uurbo (16K), and ofGPT-3,5-Turboposition of at theiroth<br>ee as & function we observe th and<br>ion is nearl id purple<br>pneuSpends D frcabotOPT PrplnyaiereimudSalpreaesdCoheneueatMich9-9ion,cor performanGPT.Bilisinformatiaerisd e ote bokwindowessuperimposedinoi)Figure 5), settings(sTh‘eserelativeresultsfed<br><!-- End of picture text -->

_https://arxiv.org/pdf/2307.03172_ 

## _Similitud de Coseno: “Cercanía” en los chunks._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

La similitud de coseno es la manera para determinar algebraicamente si dos vectores son similares o no. 



<!-- Start of picture text -->
.+ a-b [ro ly<br>similitud(a,b) = a2 ee ! -)<br>\|a |\|b ‘va<br>--5--4<br><!-- End of picture text -->

El resultado va de **-1 a 1** : 

- **1** = vectores idénticos (misma 

- dirección) 

- **0** = vectores perpendiculares (sin relación) 

- **-1** = vectores opuestos 

Los embeddings de texto producen vectores cuyos valores de similitud coseno van de 0 a 1 en la práctica, donde valores cercanos a 1 indican mayor similitud semántica entre los textos comparados. 



_¿Qué falta aquí?_ 



_¿Qué falta aquí?_ 

**_Lo que se mide, se gestiona._** _Peter Drucker (1909-2005)_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->

## _Control: Métricas de Recuperación y Generación._ 

Retrieval Generation **_Precision Faithfulness_ Answer Relevancy** 

**_Faithfulness_** 

**_Recall_** 

_De los documentos De los documentos ¿La pregunta se basa relevantes que en el contexto recuperados, existen en la base, ¿cuantos son proporcionado? ¿Cuántos realmente recuperaste? relevantes?_ **_Etiquetar Una baja indica el AI Agent podría documentos modelo alucinada o validar inventa._** 

_¿La respuesta aborda de forma directa y útil la pregunta original?_ 

**_Una respuesta puede ser fiel al contexto, pero no útil_** 

## _RAGAS: Librería especializada para medir RAGs_ 





<!-- Start of picture text -->
Ragas Office Hours - If you need help setting up Evals for your Al application, sign up for our Office Hours x<br>AA Ragas @ Q Sea oovibrantlabsai/ragas<br>$i“ TrOGUCTIOI Copypage - WhyTableRagas?of contents<br>Ragas is a library that helps you move from ‘vibe checks" to systematic evaluation loops for your Key Features<br>Al applications. It provides tools to supercharge the evaluation of Large Language Model (LLM) Want help improving your Al<br>applications, enabling you to evaluate your LLM applications with ease and confidence. application using evals?<br>Why Ragas<br>Traditional evaluation metrics don't capture what matters for LLM applications. Manual<br>evaluation doesn't scale. Ragas solves this by combining LLM-driven metrics with systematic<br>experimentation to create a continuous improvement loop.<br>Key Features<br>+ Experiments-first approach: Evaluate changes consistently with experiments . Make<br>changes, run evaluations, observe results, and iterate to improve your LLM application.<br>+ Ragas Metrics: Create custom metrics tailored to your specific use case with simple<br>decorators or use our library of Learn more about<br>* Easy to integrate: Built-in dataset management, result tracking, and integration with popular<br>frameworks like LangChain, Llamaindex, and more. |<br><!-- End of picture text -->

_https://docs.ragas.io/en/stable/_ 



_Todo parece bien, pero … como mido realmente. Necesito registros de buggs, errores, llamadas a las Tools ... etc._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
LangSmith<br>The platform for SignwsUp LogIn<br>agent engineering eee<br>Logim wath<br>=<G Google © Gita Discord<br>Observe, evaluate, and deploy your agents. —_______~<br>Build agents without code. of continuewith email<br>Emat<br>~- * francisco macaya22@gmail.com<br>.<br>Trusted by Password<br>——<br><!-- End of picture text -->

_LangSmith: Todo en un lugar ._ 

