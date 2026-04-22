---
name: analyst-workflow-skills
agent: iterative-analyst-agent
---
# Skills de Análisis y Control

## extract_uncertainties
Analiza el documento del workspace y genera una lista priorizada de vacíos de información (dudas, hipótesis, información pendiente, dependencias, inconsistencias).

## track_resolution_state
Mantiene un registro de las dudas:
- `PENDING`: Aún no presentada.
- `ACTIVE`: Presentada al usuario, esperando respuesta.
- `RESOLVED`: Validada e incorporada al contexto.

## update_context_with_answer
Toma la respuesta del usuario y la traduce a reglas de negocio o requerimientos funcionales para el documento final.