

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 

### _Noticias: Prompt injection es todavía una amenaza._ 





<!-- Start of picture text -->
= som FST@MPANY Ea: Il<br>There’s no rogue McDonald's Al bot,<br>but ‘prompt injection’ is still a risk for Considerinea<br>companies career at Citi?<br>People hacking<br>brandedAI bot result in t Teputat ancia a) a<br>1 uen t<br>=> aa he 2<br>{\t\ i iF %, Global benefits<br>Hi iy citi<br>so sansa aia FEATURED VIDEO<br><!-- End of picture text -->

_Nota: https://www.fastcompany.com/91532091/mcdonalds-ai-bot-didnt-go-rogue_ 

## _¿Por qué es relevante la seguridad?_ 



<!-- Start of picture text -->
1- Utilizar la API descrita en el README para evaluar costos, modelos y<br>Protecci6on de datos ) Generacion de confianza de confianza confianza<br>latencia de una solución.<br>sensibles. del usuario y<br>cumplimiento normativo.<br>2- En base a lo encontrado, ¿Qué mejoras se puede hacer en el código para  Los agentes de IA,<br>poder disminuir la latencia de la solución? con su capacidad de<br>razonary actuar,<br>presentan riesgos<br>Prevenci6én de abusos y significativos si no se Mantenimiento de la<br>usos maliciosos disehanygestionan reputacion<br>adecuadamente. a .<br>organizacional.<br><!-- End of picture text -->



<!-- Start of picture text -->
Generacion de confianza de confianza confianza<br><!-- End of picture text -->



<!-- Start of picture text -->
uocUC<br><!-- End of picture text -->

_La seguridad es el piso mínimo de un diseño, no es un característica_ 

## _Ataques comunes de AI._ 



<!-- Start of picture text -->
uocUC<br><!-- End of picture text -->

ATAQUES COMUNES _1- Utilizar la API descrita en el README para evaluar costos, modelos y latencia de una solución._ 

_2- En base a lo encontrado, ¿Qué mejoras se puede hacer en el código para poder disminuir la latencia de la solución?_ 01 02 03 04 



<!-- Start of picture text -->
DuocUC:<br><!-- End of picture text -->



<!-- Start of picture text -->
OpenAl says China's DeepSeek trained<br>its Al by distilling US models, memo<br>shows<br>By Deepa Seetharaman and Fabiola Aramburo =<br>February 12, 2026 10:16 PM GMT - Updated February 13, 2026 Ls |ae | s |<br>»%<br>aby gooree™<br>China's DeepSeek shook markets early last year with a set of Al models<br>that rivaled some of the best offerings from the U.S.<br><!-- End of picture text -->

_Deep Seek: ¿Cómo inicialmente fueron tan baratos?_ 

### _Destilación (Distillation): Aprende de los mayores._ 





<!-- Start of picture text -->
Prompt System : Eres un experto<br>en reinforcement learning.<br>Pregunta : …<br>1<br>Deep Seek 1 GPT 5.5<br>O -<br>Respuesta :…<br>2<br>Deep Seek 1<br>Deep Seek 3<br>Input: …<br>Output : …<br>O - [ ||<br>Mucho más barato que entrenar un modelo con millones de parámetros. Deep Seek crearon miles<br>de cuentas de OpenAI para entrenar su propio modelo .<br><!-- End of picture text -->

### _Guardrails: Protege tu sistema ante filtraciones ._ 



<!-- Start of picture text -->
Duocuc:<br><!-- End of picture text -->

#### _Inputs Guardrails_ 

Las dos principales fugas que evitan son: 

1. filtrar información privada a API externas. 

2. ejecutar mensajes maliciosos que comprometen su sistema 

¿Cómo puede pasar?: 

1. Un empleado copia información confidencial de la empresa o información privada de un usuario en un mensaje y la envía a una API de terceros.<sup>1</sup>. 

2. Un desarrollador de aplicaciones introduce políticas y datos internos de la empresa en el mensaje del sistema de la aplicación. 

3. Una herramienta recupera información privada de una base de datos interna y la agrega al contexto. 



<!-- Start of picture text -->
T got 403 error on this code. What did I do wrong?<br>5Gl pat url response= = “secret_token_that_shouldn’t_be “https: = get(url,  //apt.github.con/repos/(repo}/{ssuestpage=30" access_token=pat) leaked”<br>T got 483 error on this code. What did I do wrong? ReversiblePil map<br>pat = {ACCESS TOKEN) Bese nyo eae<br>E url response  = “https:/fapt.github.con/repos/{repo}/issuestpage=32” = get(url, access token=pat) shouldn’t_be_leaked"<br>GI The UAL you provided contains @ syntax error. The correct<br>URL should use ? to denote query parameters instead of &.<br>Ff lHere’s a corrected version of your code:<br>SB |pat = [ACCESS_TOKEN]<br>3 url = “https: //apt.github.con/repos/ (repo}/tssues?page=38"<br>Sj response = get(url, access_token=pat)<br>g<br>©] The URL you provided contains a syntax error. The correct<br>BURL should use ? to denote query paraneters instead of &.<br>z Here’spat = “seca co r rectedet_token_that_shouldn’t_be_version of your code:<br>g response = get(url, access_token=pat) leaked”<br>FE url = “https: //api.github.con/repos/{repo}/issues?page=38<br>Figure 10-3, An example of masking and unmasking PI information using a reverse PII map to avoid sending<br>itto external APIs.<br><!-- End of picture text -->

### _Guardrails: Protege tu sistema ante filtraciones ._ 



<!-- Start of picture text -->
Duocuc:,<br><!-- End of picture text -->

#### _Output Guardrails_ 

##### Sus funciones son: 

1. Detectar fallos de salida. 

2. Especificar la política para gestionar los diferentes modos de fallo. 



<!-- Start of picture text -->
* Quality<br>¢ Malformatted responses that don’t follow the expected output format. For<br>example, the application expects JSON, and the model generates invalid<br>JSON.<br>¢ Factually inconsistent responses hallucinated by the model.<br>* Generally bad responses. For example, you ask the model to write an essay,<br>and that essay is just bad.<br>¢ Security<br>¢ Toxic responses that contain racist content, sexual content, or illegal<br>activities.<br>¢ Responses that contain private and sensitive information.<br>¢ Responses that trigger remote tool and code execution.<br>¢ Brand-risk responses that mischaracterize your company or your<br>competitors.<br><!-- End of picture text -->

### _¿Cómo implementarlo?_ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
aspe.8., agent,ng, Input guardrailsp<br>iting) (e.g., Pll redaction)<br>eeeony  || ome Model API<br>(© 3) 210 “acon || Gg.eton e s,<br>Response | Output guardrails<br>+ Safety/verification<br>+ Structured outputs<br>Figure 10-4. Application architecture with the addition of input and output guardrails.<br><!-- End of picture text -->

_Sistema protegido, con input y output guardrails para resolver cualquier problema de filtraciones y seguridad._ 

### _Éticas y Seguridad: La AI es una herramienta, no el fin ._ 



<!-- Start of picture text -->
uocUC<br><!-- End of picture text -->

_Output Guardrails_ entrenamiento TRANSPARENCIA Y Sus funciones son: EXPLICABILIDAD (XAI) 1. Detectar fallos de salida. Entender por qué un agente tomé una decision. 2. Especificar la política para gestionar los diferentes modos de fallo. 

