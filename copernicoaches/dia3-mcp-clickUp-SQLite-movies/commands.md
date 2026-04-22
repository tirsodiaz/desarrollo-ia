# 1. Prompt commands (VS Code – “prompt files” / comandos)

**Documentación oficial (punto de partida):**
[https://code.visualstudio.com/docs/copilot/customization/prompt-files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)

Qué son:

* Son archivos Markdown (`.prompt.md`)
* Definen comandos reutilizables que puedes ejecutar desde el chat
* Se invocan con `/nombre`

Dónde se guardan:

* `.github/prompts` (en el proyecto)
* o en configuración de usuario

Ejemplo:

```md
---
name: create-api
description: Genera una API REST
---

Crea una API REST con:
- Node.js
- Express
- Endpoints CRUD
```

Uso:

```
/create-api
```

Punto clave:

* Son **comandos ejecutables definidos en lenguaje natural**
* Funcionan como “funciones” reutilizables para Copilot

---

# 2. Custom instructions (instrucciones globales)

**Documentación oficial:**
[https://code.visualstudio.com/docs/copilot/customization/custom-instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)

Qué son:

* Instrucciones persistentes para el modelo
* Se aplican automáticamente a todas las interacciones

Dónde se definen:

```
.github/copilot-instructions.md
```

Ejemplo:

```md
- Usa Java 17
- Aplica arquitectura hexagonal
- Prefiere objetos inmutables
```

Diferencia clave:

* Instructions → siempre activas
* Prompt commands → se ejecutan manualmente

---

# 3. Custom agents (agentes personalizados)

**Documentación oficial:**
[https://code.visualstudio.com/docs/copilot/customization/custom-agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

Qué son:

* Un agente es una **configuración de rol + reglas + capacidades**

Ejemplos de roles:

* arquitecto
* revisor de código
* planificador

Se definen como:

```
.agent.md
```

Ejemplo:

```md
Eres un revisor de seguridad.

Reglas:
- No modifiques código
- Solo analiza
- Busca vulnerabilidades
```

Capacidades:

* Definir comportamiento
* Limitar acciones
* Encadenar agentes

Diferencia clave:

* Prompt → tarea puntual
* Agent → rol persistente

---

# 4. Skills (capacidades reutilizables)

**Documentación oficial (visión general):**
[https://code.visualstudio.com/docs/copilot/customization/overview](https://code.visualstudio.com/docs/copilot/customization/overview)

Qué son:

* Capacidades reutilizables que combinan:

  * prompts
  * herramientas
  * lógica

Se usan para:

* Automatizaciones complejas
* Flujos multi-paso
* Integración con sistemas externos

Modelo mental:

* Prompt → “haz esto”
* Agent → “piensa así”
* Skill → “haz esto de forma completa y reutilizable”

Ejemplo conceptual:

* Prompt: generar API
* Agent: arquitecto backend
* Skill: generar API + tests + documentación + validación

---

# 5. Cómo encajan juntos

| Concepto     | Función                           |
| ------------ | --------------------------------- |
| Prompt files | Ejecutar tareas                   |
| Instructions | Definir comportamiento global     |
| Agents       | Definir rol                       |
| Skills       | Automatizar capacidades complejas |

Relación:

* Un prompt puede usar un agente
* Un agente puede usar skills
* Las skills pueden usar herramientas (MCP)

---

# 6. Comandos útiles en VS Code

Dentro de VS Code:

* `Chat: New Prompt File`
* `Chat: Open Chat Customizations`
* `/create-prompt`
* `/create-agent`
* `/create-skill`

Estos ayudan a generar las estructuras básicas.

---

# 7. Ruta mínima para una demo

Para enseñar esto rápidamente:

1. Crear `.github/copilot-instructions.md`
2. Crear `.github/prompts/create-api.prompt.md`
3. Ejecutar `/create-api`
4. Crear un `.agent.md`
5. Cambiar el agente en el chat

Con esto ya se demuestra:

* comandos
* comportamiento
* especialización

---

# Conclusión

* **Prompt commands** → comandos reutilizables en lenguaje natural
* **Custom agents** → roles configurables del modelo
* **Skills** → capacidades compuestas y reutilizables

Los tres forman un sistema modular dentro de Visual Studio Code que permite pasar de prompts simples a automatización estructurada.
