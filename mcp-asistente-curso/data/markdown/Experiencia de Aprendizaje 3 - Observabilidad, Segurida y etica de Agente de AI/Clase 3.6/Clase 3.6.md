

# _Ingeniería de soluciones con AI_ 

**_Docente:_** _Francisco Macaya_ 

_Semestre 2026-1_ 



<!-- Start of picture text -->
DuocuCc:.<br><!-- End of picture text -->



**_Claude Code_** _es una herramienta de linea de comandos que convierte a Claude en un agente de coding autonomo. Puede leer y editar archivos, ejecutar comandos, explorar tu codebase completo y completar tareas complejas de principio a fin._ 

**Notas:** https://code.claude.com/docs/en/best-practices 



_Claude Code : “La mejor manera de programar en el mercado”_ **_¿Dónde aprender? https://www.anthropic.com/_** Alresearch _Claude Code es una herramienta de linea de_ and _comandos que convierte a Claude en un agente de coding autonomo. Puede leer y editar archivos, ejecutar comandos, explorar tu codebase_ products that put **A** nthropicisT will have aa publ cvast **i** mpact benefiton corporationthe world. _completo y completar tareas complejas de_ u dedicated to securing its benefits and _principio a fin._ 

**Notas:** https://code.claude.com/docs/en/best-practices 

_¿Cómo empezar?: Es gratis, pero si quieres usar los modelos de Anthropic, debes pagar al menos USD 17._ 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
Free Pro Max<br>Try Claude For everyday productivity Get the most out of Claude<br>o$ 17$ From 100 $<br>Free for everyone Per month with annual subscription discount (200 $ Per month<br>billed<br>up front). 20$ if billed monthly<br>Try Claude Try Claude Try Claude<br>Chat on web, iOS, Android, and on Everythingin Free, plus: Everything in Pro, plus:<br>Your desktop / More usage* Choose 5x or 20x more usage than Pro*<br>Rensata cai and visualep sata<br>V Includes Claude Code VY Higher output limits for all tasks<br>¥ Write, edit, and create content<br>/ Includes Claude Cowork Early access to advanced Claude features<br>Anny, to search ine.wen / Includes Claude Design / Priority access at high traffic times<br>of (Mamiojy acries conversations Access to unlimited projects to organize<br>Create files and execute code Chats wel doCUTTBAtS<br>/ Unlock more from Claude with / ‘Access to Research<br>eckibp extensions<br>/ Ability to use more Claude models<br>» Goninech Slack and Google Claude for Microsoft 365<br>WorkspaceIntegrate anyservicescontext or tool through VY Claude for Microsoft Outlook<br>connectors with remote MCP<br>/ Extended thinking for complex work<br><!-- End of picture text -->

**Notas:** https://claude.com/pricing 

### _¿Cómo empezar?: From 0 To Hero._ 



<!-- Start of picture text -->
DuocuCc:.<br><!-- End of picture text -->

- **_Instalar Claude Code_** _._ 

- **_1_** _Npm install –g @anthropic-ai/claude-code_ 

- **_2 Iniciar Sesión_** _claude_ 

- **_3 Abrir en tu proyecto_** 

   - _cdmiproyecto_ 

**_Primer prompt 4_** _Explícame la arquitectura del proyecto._ 

### _¿Por qué es útil?: Muchos usos, poco problemas útiles._ 



|**_Instalar Claude_**<br>_Npm install –g @_<br>**_1_**<br>**_Flujo de bugs_**|**_Code_**_._<br>_anthropic-ai/claude-code_||
|---|---|---|
|**_Iniciar Sesión_**<br>_claude_<br>**_Abrir en tu proy_**<br>**_2_**<br>|**_ecto_**<br>**_Construir Codebase_**|**_Testing_**|
|<br>**_-_**_cdmiproyecto_<br>**_3_**<br>**_Refactoring_**|||
|**_Primer prompt_**<br>_Explícame la arq_<br>**_4_**|_uitectura del proyecto._|**_Documentación_**|



_¿Comando?: Trucos fáciles para trabajar con Claude Code._ 



- **_/help_** 

- **_1_** _Lista de todos los comando disponibles._ 

- **_2 /clear_** _Limpia el historial de conversación_ 

- **_3 /compact_** _Comprime el contexto para conversaciones largas_ **_._** 

- **_/review_** 

- **_4_** _Revisa los cambios pendientes del repo_ 

- **_/init_** 

- **_5_** _Crea Claude.md con docs del proyecto._ 

- **_/memory_** 

- **_6_** _Gestiona los archivos de memoria._ 

- **_/doctor_** 

- **_7_** _Verifica si el entorno esta bien configurado._ 

### _MCP: Model Context Protocol_ 

_MCP es un protocolo que permite a Claude conectarse con herramientas y datos externos: bases de datos, APIs, Slack, GitHub y mas._ 

**_Github MCP 1_** _Repos, PRs, Issues, commits._ 

**_Slack MCP_** 

**_2_** 

_Mensajes, canales, usuarios_ 

**_PostgresSQL MCP 3_** _Queries directo desde Claude._ 

_Queries directo desde Claude._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

```
claude mcp add my-server \
```

```
-e API_KEY=xxx \
```

```
--npx server-package
```

**_FileSystem MCP 4_** _Acceso a archivos locales._ 

**_5 CopyWriting MCP_** _Acceso al browers._ 

### _Hooks: Automatización con Control_ 

_Los Hooks son scripts que se ejecutan automaticamente antes o despues de acciones de Claude Code. Dan control deterministico sobre el comportamiento del agente._ 

**_1_** 

**_2_** 

**_3_** 

#### **`PreToolUse`** 

```
Antes de ejecutarunaherramienta.
```

#### **`PostToolUse`** 

```
Despues de ejecutar.
```

```
Stop
```

_Cuando Claude termina de responder._ 



**`Notification`** **_4_** _Cuando Claude envía una notificación al usuario._ 

### _Skills: Instrucciones Reutilizables._ 

_Un Skill es un archivo Markdown con instrucciones que Claude aplica automaticamente cuando la tarea coincide. Define las instrucciones una vez, Claude las reutiliza siempre._ 



<!-- Start of picture text -->
i<br>## Cuando revisar up PR:<br>- Verifica que haya tests<br>- Revisa manejo de errores<br>- Sugiere mejoras de performance<br>#H#t Forma ie respuesta<br>Usa: OK, WARN o BLOCK<br><!-- End of picture text -->



<!-- Start of picture text -->
uc<br><!-- End of picture text -->

### **_¿Como funciona?_** 

Creas un archivo SKILL.md con instrucciones **_1_** 

_Lo guardas en .claude/skills/_ **_2_** 

Claude lo detecta y aplica automaticamente **_3_** 

**_4_**<sup>_Puedes compartirlo con tu equipo via git_</sup> 

### _Agentes: Divide y Vencerás._ 



<!-- Start of picture text -->
uc<br><!-- End of picture text -->



<!-- Start of picture text -->
¿Como funciona?<br>Un Skill es un archivo Markdown con<br>Creas un archivo SKILL.md con instrucciones<br>instrucciones que Claude aplica<br>Agente Principal 1<br>automaticamente cuando la tarea<br>Lo guardas en .claude/skills/<br>coincide. Define las instrucciones una vez,  2<br>Claude las reutiliza siempre.<br>Claude lo detecta y aplica automaticamente<br>3<br>Explorer Editor Tester Docs<br>4 Puedes compartirlo con tu equipo via git<br>Li e archivos Modifica Corre tests CSCI be<br>Cada subagente tiene su propio contexto, herramientasy sistema prompt. Ideal para tareas paralelas o especializadas<br><!-- End of picture text -->

### _¿A quien escuchar?: Daniel Ávila._ 

## **_https://aitmpl.com/_** 



<!-- Start of picture text -->
DuocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
| Foe > Search components. ak tithe<br>¿Como funciona?<br>Un Skill es un archivo Markdown con  ans = 2<br>WORCLACE .<br>instrucciones que Claude aplica 1 https://aitmpl.com/<br>“hy aerate laff hi) | alll ML beak edt he | Seo,<br>automaticamente cuando la tarea ye io a as it<br>https://aitmpl.com/<br>coincide. Define las instrucciones una vez,  Y Sills w 2<br>: =>  * 4 PATIREDSOTESUTIONS Sat<br>Claude las reutiliza siempre.<br>B48) | = ==<br>i = 3 Claude lo detecta y aplica automaticamente Complete Web Date Template Alia gant Paton a beara<br>R Settings :<br>Daniel Avila Arias 9 «2 | Hedgineer dims Sait bret 2 a<br>icp a A Acers& Sls Plan.<br>BuildingNueva York,Al ToolsNueva with LLMsYork, Estados Unidos - Informacion de contacto dePontificiaChile Universidad Catdlica seses . 4 Puedes compartirlo con tu equipo via git wal iBul Very. Repeat _ =<br>22.855 sequidores Mas de 500 contactos  Plogins =<br>§e Victor, Daniel y 234 contactos mas en comiin wane<br>nis Q§ — Micategories v  W Fitters 9 = Soy MostPopular v<br>¥Siguiendo } | Mas r ot tt,<br>2 Sanh Adlcemnenents: 4 Ard Dana tn Stare x mes<br><!-- End of picture text -->

## _¿A quien escuchar?: Ian Lee, fundador de Nexor ._ 



<!-- Start of picture text -->
uocUC<br><!-- End of picture text -->



<!-- Start of picture text -->
J ; - =<br>@ buscalib} s https://aitmpl.com/ MS Pitch<br>1 1<br>https://aitmpl.com/<br>2<br>—_- ~~ 7<br>im<br><!-- End of picture text -->

https://www.youtube.com/watch?v=JXn8lYzU_eg 

