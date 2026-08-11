"""Middleware de autenticación: valida `Authorization: Bearer <token>` contra
el token compartido del curso (env var / secret). Rate limit básico por IP.

Ver plan.md §5.4.

TODO (Fase 5): middleware + rate limiting.
"""