# Anexo funcional — Cambios de requisitos

## ANX-001 — Archivo histórico de casos procesados

**Fecha:** 2026-03-23  
**Estado:** Implementado

### Requisito original

Al terminar de procesar un caso, el archivo temporal en `processing/` era **eliminado**.

### Nuevo requisito

Al terminar de procesar un caso (con éxito o con error), el archivo temporal en `processing/` debe **moverse** a una carpeta `processed/`, añadiendo al nombre del fichero el **día y la hora de ejecución** con el formato `YYYYMMDD_HHMMSS`.

### Ejemplo

```
processing/CASE_001.json  →  processed/CASE_001_20260323_104918.json
```

### Estructura de carpetas actualizada

```plaintext
/inbox/         → casos pendientes de procesar
/processing/    → casos en curso (transitorio)
/processed/     → casos ya procesados (histórico con timestamp)
/outbox/        → resultados correctos
/errors/        → resultados con error
/config/        → datos de configuración y simulación
```

### Motivación

Permite trazar cuándo se procesó cada caso y conservar un histórico de las ejecuciones sin pérdida de información.

### Impacto en la implementación

| Componente | Cambio |
|---|---|
| `infrastructure/file_case_reader.py` | `cleanup()` usa `shutil.move` hacia `processed/` con timestamp en nombre |
| `__main__.py` | Se crea y pasa el directorio `processed/` al lector de casos |
| `step-06-servicio-de-aplicacion.md` | Actualizado para reflejar el nuevo ciclo de vida |
| `step-09-validacion-y-ejecucion.md` | Actualizado: verificar `processed/` en lugar de vacío de `processing/` |
