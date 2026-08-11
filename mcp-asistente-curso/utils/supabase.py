"""Cliente de Supabase: insert/select/update sobre la tabla `interacciones`.

Usado por server/tools.py (insert al final de cada tool call, con permiso
de solo-insert) y por eval/judge.py (select + update de scores, con una
key distinta de select/update — ver plan.md §4.5).

TODO (Fase 8): insert_interaccion(), get_pendientes_de_evaluar(), update_scores().
"""
