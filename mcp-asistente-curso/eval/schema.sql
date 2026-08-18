-- Tabla de interacciones (plan.md §4.5). Correr en Supabase Studio -> SQL Editor.
--
-- RLS: el server MCP en Cloud Run usa la anon key y solo puede INSERT (nivel 1,
-- §4.5) -- no puede leer ni actualizar filas de otros estudiantes. eval/judge.py
-- corre con la service_role key (bypassa RLS), así que no necesita política de
-- select/update explícita.

create table if not exists interacciones (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  tool text not null,                      -- 'buscar_contenido' | 'detalle_pruebas'
  query text not null,
  fragmentos jsonb not null,                -- [{experiencia, clase, archivo, score}, ...]
  conceptos_relacionados jsonb,             -- solo buscar_contenido; null en detalle_pruebas
  latencia_ms integer,
  respuesta text,                           -- solo si el cliente reporta (nivel 2, reportar_interaccion)
  util boolean,
  reportado_at timestamptz,
  evaluado_at timestamptz,                  -- lo llena eval/judge.py cuando corre el LLM-as-judge
  relevancia_score real,                    -- salida del LLM-as-judge: fragmentos relevantes a la query
  fundamentacion_score real                 -- salida del LLM-as-judge: respuesta bien fundamentada en los fragmentos
);

alter table interacciones enable row level security;

create policy "anon puede insertar interacciones"
  on interacciones
  for insert
  to anon
  with check (true);