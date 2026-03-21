import streamlit as st
import re

# Celda 2: Importaciones y configuración
import os
from openai import OpenAI
import json

# Importar las bibliotecas necesarias
from groq import Groq
from dotenv import load_dotenv
from openai import OpenAI
import os

# load .env
load_dotenv()


# Verificar que tenemos las bibliotecas correctas
print("OpenAI library version:", __import__('openai').__version__)
print("Python version:", __import__('sys').version)


print("✅ Librerías importadas correctamente")

st.set_page_config(page_title="Text Chunking Demo", page_icon="📝", layout="wide")

def chunking_text(text, chunk_size=200, overlap=50):
    """Divide el texto en chunks con solapamiento"""
    words = text.split()
    chunks = []
    
    # Validar que el solapamiento sea menor que el tamaño del chunk
    if overlap >= chunk_size:
        overlap = chunk_size - 1
    
    step = max(1, chunk_size - overlap)  # Asegurar que el paso sea al menos 1
    
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        
        if i + chunk_size >= len(words):
            break
    
    return chunks

def chunking_by_sentences(text, max_sentences=5, overlap_sentences=1):
    """Divide el texto por oraciones"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    
    # Validar que el solapamiento sea menor que el máximo de oraciones
    if overlap_sentences >= max_sentences:
        overlap_sentences = max_sentences - 1
    
    step = max(1, max_sentences - overlap_sentences)
    
    for i in range(0, len(sentences), step):
        chunk_sentences = sentences[i:i + max_sentences]
        chunk = '. '.join(chunk_sentences) + '.'
        chunks.append(chunk)
        
        if i + max_sentences >= len(sentences):
            break
    
    return chunks

def chunking_by_paragraphs(text):
    """Divide el texto por párrafos"""
    paragraphs = text.split('\n\n')
    chunks = [p.strip() for p in paragraphs if p.strip()]
    return chunks

def chunking_by_characters(text, chunk_size=500, overlap=100):
    """Divide el texto por número de caracteres"""
    chunks = []
    
    # Validar que el solapamiento sea menor que el tamaño del chunk
    if overlap >= chunk_size:
        overlap = chunk_size - 1
    
    step = max(1, chunk_size - overlap)
    
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        
        if i + chunk_size >= len(text):
            break
    
    return chunks

def main():
    st.title("📝 Demostrador de División de Texto en Chunks")
    st.write("Herramienta para visualizar diferentes métodos de división de texto")
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración")
    
    chunking_method = st.sidebar.selectbox(
        "Método de división:",
        ["Por palabras", "Por oraciones", "Por párrafos", "Por caracteres"]
    )
    
    # Configuraciones específicas según el método
    if chunking_method == "Por palabras":
        chunk_size = st.sidebar.slider("Tamaño del chunk (palabras):", 50, 500, 200, 25)
        overlap = st.sidebar.slider("Solapamiento (palabras):", 0, chunk_size-1, min(50, chunk_size-1), 10)
        if overlap >= chunk_size:
            st.sidebar.warning("⚠️ El solapamiento debe ser menor que el tamaño del chunk")
    elif chunking_method == "Por oraciones":
        max_sentences = st.sidebar.slider("Máximo oraciones por chunk:", 1, 10, 5)
        overlap_sentences = st.sidebar.slider("Solapamiento (oraciones):", 0, max_sentences-1, min(1, max_sentences-1))
        if overlap_sentences >= max_sentences:
            st.sidebar.warning("⚠️ El solapamiento debe ser menor que el máximo de oraciones")
    elif chunking_method == "Por caracteres":
        chunk_size = st.sidebar.slider("Tamaño del chunk (caracteres):", 100, 2000, 500, 100)
        overlap = st.sidebar.slider("Solapamiento (caracteres):", 0, chunk_size-1, min(100, chunk_size-1), 50)
        if overlap >= chunk_size:
            st.sidebar.warning("⚠️ El solapamiento debe ser menor que el tamaño del chunk")
    
    # Botón de calcular
    calculate_button = st.sidebar.button("🔄 Calcular Chunks", type="primary", use_container_width=True)
    
    # Área principal
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Texto Original")
        
        # Opciones de entrada
        input_method = st.radio("Método de entrada:", ["Texto manual", "Texto de ejemplo"])
        
        if input_method == "Texto manual":
            text_input = st.text_area(
                "Ingresa tu texto:",
                height=300,
                placeholder="Escribe o pega aquí el texto que quieres dividir en chunks..."
            )
        else:
            example_texts = {
                "Artículo científico": """La inteligencia artificial (IA) es una rama de la informática que se ocupa de la creación de sistemas capaces de realizar tareas que normalmente requieren inteligencia humana. Estos sistemas pueden aprender, razonar, percibir y tomar decisiones.

El aprendizaje automático es un subconjunto de la IA que permite a las máquinas aprender y mejorar automáticamente a partir de la experiencia sin ser programadas explícitamente. Los algoritmos de aprendizaje automático construyen un modelo matemático basado en datos de entrenamiento para hacer predicciones o decisiones.

Las redes neuronales artificiales son un modelo computacional inspirado en las redes neuronales biológicas. Están compuestas por nodos interconectados que procesan información de manera similar a como lo hacen las neuronas en el cerebro humano.

El procesamiento de lenguaje natural (PLN) es otra área importante de la IA que se centra en la interacción entre computadoras y lenguaje humano. El PLN permite a las máquinas leer, entender y generar texto de manera similar a como lo hacen los humanos.""",
                
                "Historia": """La Revolución Industrial fue un período de grandes cambios tecnológicos, socioeconómicos y culturales que comenzó en Gran Bretaña a finales del siglo XVIII y se extendió por Europa y América del Norte durante el siglo XIX.

Este período se caracterizó por el paso de una economía rural basada principalmente en la agricultura y el comercio a una economía de carácter urbano, industrializada y mecanizada. La introducción de maquinaria en los procesos de producción supuso un cambio radical en las formas de trabajo.

La máquina de vapor, inventada por James Watt, fue una de las innovaciones más importantes de este período. Permitió el desarrollo de fábricas que no dependían de fuentes de energía naturales como el agua o el viento.

El ferrocarril revolucionó el transporte de mercancías y personas, conectando ciudades y regiones de manera más eficiente que nunca antes. Esto facilitó el comercio y la migración de trabajadores hacia los centros industriales.""",
                
                "Receta": """Para preparar una deliciosa pasta carbonara necesitarás los siguientes ingredientes: 400g de espaguetis, 200g de panceta o guanciale, 4 huevos enteros, 100g de queso parmesano rallado, pimienta negra recién molida y sal.

Primero, pon a hervir abundante agua con sal en una olla grande. Mientras tanto, corta la panceta en cubitos pequeños y cocínala en una sartén grande a fuego medio hasta que esté dorada y crujiente.

En un bol, bate los huevos con el queso parmesano rallado y una generosa cantidad de pimienta negra. Esta mezcla será la base cremosa de tu carbonara.

Cuando el agua hierva, añade los espaguetis y cocínalos según las instrucciones del paquete hasta que estén al dente. Reserva una taza del agua de cocción antes de escurrir la pasta.

Inmediatamente después de escurrir, añade los espaguetis calientes a la sartén con la panceta. Retira del fuego y añade la mezcla de huevos y queso, removiendo rápidamente para crear una salsa cremosa. Si es necesario, añade un poco del agua de cocción reservada."""
            }
            
            selected_example = st.selectbox("Selecciona un texto de ejemplo:", list(example_texts.keys()))
            text_input = example_texts[selected_example]
            st.text_area("Texto seleccionado:", value=text_input, height=300, disabled=True)
    
    with col2:
        st.header("🔪 Chunks Generados")
        
        if text_input.strip() and calculate_button:
            # Generar chunks según el método seleccionado
            if chunking_method == "Por palabras":
                chunks = chunking_text(text_input, chunk_size, overlap)
            elif chunking_method == "Por oraciones":
                chunks = chunking_by_sentences(text_input, max_sentences, overlap_sentences)
            elif chunking_method == "Por párrafos":
                chunks = chunking_by_paragraphs(text_input)
            else:  # Por caracteres
                chunks = chunking_by_characters(text_input, chunk_size, overlap)
            
            # Mostrar estadísticas
            st.subheader("📊 Estadísticas")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("Total chunks", len(chunks))
            with col_stats2:
                st.metric("Palabras originales", len(text_input.split()))
            with col_stats3:
                avg_chunk_size = sum(len(chunk.split()) for chunk in chunks) / len(chunks) if chunks else 0
                st.metric("Promedio palabras/chunk", f"{avg_chunk_size:.1f}")
            
            # Mostrar chunks
            st.subheader("📋 Chunks Generados")
            
            for i, chunk in enumerate(chunks):
                with st.expander(f"Chunk {i+1} ({len(chunk.split())} palabras, {len(chunk)} caracteres)"):
                    st.write(chunk)
                    
                    # Mostrar información adicional del chunk
                    st.caption(f"Palabras: {len(chunk.split())} | Caracteres: {len(chunk)} | Oraciones: {len(re.split(r'[.!?]+', chunk))}")
        elif not text_input.strip():
            st.info("👆 Ingresa un texto en la columna izquierda para ver los chunks generados")
        else:
            st.info("👈 Haz clic en 'Calcular Chunks' en la barra lateral para generar los chunks")
    
    # Información adicional
    st.header("ℹ️ Información sobre Métodos de Chunking")
    
    with st.expander("📖 Detalles de cada método"):
        st.write("""
        **Por palabras:**
        - Divide el texto en chunks de un número específico de palabras
        - Permite solapamiento para mantener contexto
        - Útil para textos largos y uniformes
        
        **Por oraciones:**
        - Agrupa oraciones completas en cada chunk
        - Mantiene la coherencia semántica
        - Ideal para textos narrativos o explicativos
        
        **Por párrafos:**
        - Cada párrafo se convierte en un chunk
        - Preserva la estructura original del texto
        - Perfecto para textos bien estructurados
        
        **Por caracteres:**
        - División basada en número de caracteres
        - Control preciso del tamaño
        - Útil cuando hay limitaciones de longitud estrictas
        """)
    
    with st.expander("🎯 Cuándo usar cada método"):
        st.write("""
        - **Documentos largos y uniformes**: Por palabras con solapamiento
        - **Artículos y ensayos**: Por oraciones o párrafos
        - **Textos técnicos**: Por párrafos para mantener conceptos completos
        - **APIs con límites de caracteres**: Por caracteres
        - **Análisis de sentimientos**: Por oraciones para mantener contexto emocional
        """)

if __name__ == "__main__":
    main()
