# Tarea Practica — RAG con Documento Propio

**Asignatura:** Ingenieria de Soluciones con Inteligencia Artificial
**Clase:** 1.3 — Fundamentos de AI Generativa y Prompt Engineering
**Entrega:** Repositorio personal en GitHub (fork del proyecto de clase)

---

## Objetivo

Aplicar el pipeline RAG visto en clases sobre un documento de tu eleccion, construir una base de conocimiento con preguntas y respuestas esperadas, y evaluar si el sistema es capaz de responder correctamente.

---

## Parte 1 — Subir tu propio documento

1. Elige un documento PDF de tu interes (puede ser un manual, articulo, reglamento, guia tecnica, etc.). El archivo debe tener al menos 5 paginas y contener informacion factual verificable.

2. Coloca el archivo en la carpeta `input/` del proyecto:

```
input/
└── tu-documento.pdf      <-- tu archivo aqui
```

3. Abre los archivos `rag_pypdf.py` y `rag_ocr.py` y cambia la variable `PDF_PATH` para que apunte a tu nuevo documento:

```python
# Antes
PDF_PATH = "input/Experiencia de Aprendizaje 1 - Fundamentos de AI Generativa y Prompt Engineering.pdf"

# Despues (ejemplo)
PDF_PATH = "input/tu-documento.pdf"
```

---

## Parte 2 — Ejecutar los contenedores Docker

Asegurate de tener tu archivo `.env` con tu `OPENAI_API_KEY` configurada. Luego, desde la raiz del proyecto, construye la imagen y ejecuta cada script por separado:

**Paso 1 — Construir la imagen Docker:**
```bash
docker build -t rag-clase .
```

**Paso 2 — Ejecutar Script 1 (RAG con pypdf):**
```bash
docker run --rm -it --env-file .env -v "$(pwd)/input:/app/input:ro" -v "$(pwd)/md:/app/md" rag-clase python rag_pypdf.py
```

**Paso 3 — Ejecutar Script 2 (RAG con OCR / markitdown):**
```bash
docker run --rm -it --env-file .env -v "$(pwd)/input:/app/input:ro" -v "$(pwd)/md:/app/md" rag-clase python rag_ocr.py
```

> Cada comando abre un chat interactivo. Podras escribir preguntas y ver las respuestas del modelo en tiempo real.

---

## Parte 3 — Construir la base de conocimiento

Antes de ejecutar los scripts, lee tu documento y redacta **5 preguntas** sobre su contenido. Para cada pregunta define la respuesta correcta esperada segun lo que dice el documento.

Crea un archivo llamado `knowledge_base.json` en la raiz del proyecto con la siguiente estructura:

```json
[
  {
    "id": 1,
    "pregunta": "Escribe aqui tu primera pregunta sobre el documento",
    "respuesta_esperada": "Escribe aqui la respuesta correcta segun el documento, citando o parafraseando el contenido relevante"
  },
  {
    "id": 2,
    "pregunta": "Escribe aqui tu segunda pregunta",
    "respuesta_esperada": "Respuesta correcta segun el documento"
  },
  {
    "id": 3,
    "pregunta": "Escribe aqui tu tercera pregunta",
    "respuesta_esperada": "Respuesta correcta segun el documento"
  },
  {
    "id": 4,
    "pregunta": "Escribe aqui tu cuarta pregunta",
    "respuesta_esperada": "Respuesta correcta segun el documento"
  },
  {
    "id": 5,
    "pregunta": "Escribe aqui tu quinta pregunta",
    "respuesta_esperada": "Respuesta correcta segun el documento"
  }
]
```

**Criterios para las preguntas:**
- Deben ser preguntas que solo se pueden responder con la informacion del documento (no de conocimiento general).
- Deben variar en tipo: definiciones, comparaciones, datos especificos, procedimientos, etc.
- La respuesta esperada debe ser concreta y verificable en el texto del PDF.

---

## Parte 4 — Evaluar las respuestas del modelo

Ejecuta cada una de las 5 preguntas de tu `knowledge_base.json` en **ambos scripts** (`rag-pypdf` y `rag-ocr`) y anota los resultados.

Agrega al archivo `knowledge_base.json` los campos `respuesta_pypdf` y `respuesta_ocr` con la respuesta real que dio el modelo, y un campo `correcto` con `true` o `false` segun si la respuesta coincide con lo esperado:

```json
[
  {
    "id": 1,
    "pregunta": "Tu pregunta",
    "respuesta_esperada": "La respuesta correcta segun el documento",
    "respuesta_pypdf": "Lo que respondio el modelo con rag_pypdf.py",
    "respuesta_ocr": "Lo que respondio el modelo con rag_ocr.py",
    "correcto_pypdf": true,
    "correcto_ocr": true
  }
]
```

---

## Parte 5 — Reflexion (README_TAREA.md)

Crea un archivo `README_TAREA.md` en la raiz del proyecto respondiendo las siguientes preguntas en un minimo de 3 oraciones cada una:

1. **Que documento elegiste y por que?** Describe brevemente su contenido y su relevancia para ti.

2. **Que diferencias observaste entre `rag-pypdf` y `rag-ocr`?** Considera la calidad del texto extraido, la precision de las respuestas y el tiempo de procesamiento.

3. **Cuantas preguntas respondio correctamente cada script?** Analiza los resultados de tu tabla de evaluacion.

4. **En que tipo de preguntas fallo el modelo?** Identifica si los errores se deben a la extraccion del texto, al chunking, al reranking o al modelo generativo.

5. **Que aprendiste sobre RAG con este ejercicio?** Relaciona tu experiencia practica con los conceptos vistos en clase.

