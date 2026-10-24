# PLAN DE INGENIERÍA — Sistema de Gestión de Reservas de Espacios Académicos

> Documento de planificación técnica. Se elabora **antes** de instalar OpenSpec, generar especificaciones o escribir código.

---

## 1. Análisis del problema

### 1.1 Problemática
La institución gestiona las reservas de laboratorios, auditorios y salas de cómputo mediante correos electrónicos y hojas de cálculo. Esto produce:
- Solicitudes duplicadas para un mismo espacio.
- Conflictos de horario (dos reservas en el mismo espacio y franja).
- Dificultad para consultar qué espacios están disponibles y cuándo.
- Falta de trazabilidad: no hay un historial confiable de quién reservó, quién aprobó y qué cambió.

### 1.2 Necesidades de la institución
- Centralizar el proceso de reservas en un único sistema.
- Consultar la disponibilidad de los espacios de forma confiable.
- Impedir reservas simultáneas sobre un mismo espacio.
- Controlar quién puede solicitar, aprobar y administrar.
- Conservar un historial de reservas consultable.

### 1.3 Actores involucrados
| Actor | Descripción | Acciones principales |
|---|---|---|
| **Solicitante** (estudiante o docente) | Usuario que necesita un espacio | Consultar espacios y disponibilidad, crear solicitudes, cancelar sus reservas, ver su historial |
| **Administrador** | Personal encargado de los espacios | Gestionar espacios y usuarios, asignar roles, aprobar o rechazar solicitudes, ver todo el historial |

Los roles podrán ajustarse durante el desarrollo; cualquier cambio quedará registrado en el informe final.

### 1.4 Alcance
Incluye: gestión de espacios académicos, registro y administración de usuarios, roles y permisos, solicitudes de reserva, validación de disponibilidad, prevención de reservas simultáneas, aprobación y rechazo, cancelación e historial.

### 1.5 Limitaciones (fuera de alcance)
- Pagos o costos por uso de espacios.
- Notificaciones por correo o mensajería.
- Integración con sistemas académicos institucionales.
- Aplicación móvil e interfaz web elaborada (se entrega una API REST y el panel de administración de Django).
- Reservas recurrentes (semanales, mensuales).

---

## 2. Propuesta de solución

### 2.1 Descripción general
Un sistema web con **API REST** que centraliza las reservas. Los usuarios se autentican, consultan espacios, solicitan reservas en una franja horaria y un administrador las aprueba o rechaza. El sistema valida la disponibilidad y bloquea cualquier solapamiento de horarios sobre un mismo espacio.

### 2.2 Funcionalidades prioritarias
| Prioridad | Funcionalidad |
|---|---|
| Alta | Gestión de espacios (CRUD) |
| Alta | Usuarios, roles y permisos |
| Alta | Creación de solicitudes de reserva |
| Alta | Validación de disponibilidad y prevención de reservas simultáneas |
| Alta | Aprobación y rechazo de solicitudes |
| Media | Cancelación de reservas |
| Media | Historial de reservas |
| Baja | Filtros de búsqueda (por tipo de espacio, fecha) |

### 2.3 Módulos del sistema
1. **Usuarios y roles:** registro, autenticación, asignación de rol y permisos.
2. **Espacios:** catálogo de laboratorios, auditorios y salas de cómputo (nombre, tipo, capacidad, estado activo).
3. **Reservas:** solicitudes, estados, validación de disponibilidad, aprobación o rechazo, cancelación.
4. **Historial:** consulta de reservas pasadas y cambios de estado.

### 2.4 Estrategia progresiva
Se construye por capas de valor, de modo que cada etapa deje algo funcionando y probado:
1. Base del proyecto, configuración y conexión a PostgreSQL.
2. Usuarios y roles.
3. Espacios.
4. Reservas con validación de disponibilidad.
5. Aprobación, rechazo y cancelación.
6. Historial.
7. Gestión de cambios (nueva regla de negocio) y cierre.

---

## 3. Decisiones de arquitectura y tecnología

### 3.1 Arquitectura seleccionada
**Monolito modular en capas** con Django: cada módulo es una aplicación Django (`usuarios`, `espacios`, `reservas`) con sus modelos, serializadores, vistas y pruebas. Capas: presentación (API REST) → lógica de negocio (servicios y validaciones) → persistencia (ORM).

**Justificación:** el sistema es de tamaño acotado y lo desarrolla una sola persona en tiempo limitado. Un monolito modular evita la complejidad operativa de los microservicios (despliegue, comunicación entre servicios) y mantiene los módulos separados para poder evolucionar.

### 3.2 Stack tecnológico
- **Lenguaje:** Python 3.12
- **Framework:** Django + Django REST Framework (DRF)
- **Base de datos:** PostgreSQL (alojada en Supabase)
- **Autenticación:** autenticación de Django (sesión o token)
- **Pruebas:** `TestCase` de Django / pytest
- **Documentación de la API:** Swagger (drf-spectacular) y Postman para pruebas manuales
- **Control de versiones:** Git y GitHub
- **Especificaciones:** OpenSpec
- **Agente de IA:** Claude Code

### 3.3 Estrategia de persistencia
- PostgreSQL como base de datos relacional, gestionada mediante el ORM y migraciones de Django.
- Entidades principales: `Usuario` (con rol), `Espacio` y `Reserva` (espacio, usuario, fecha y hora de inicio y fin, estado, motivo).
- Estados de reserva: `pendiente`, `aprobada`, `rechazada`, `cancelada`.
- La integridad de los horarios se protege tanto en la lógica de negocio como en la base de datos (ver riesgos).
- Las credenciales de conexión se guardan en variables de entorno, nunca en el repositorio.

### 3.4 Organización de componentes
```
proyecto/
├── config/            # configuración de Django
├── usuarios/          # usuarios, roles, permisos
├── espacios/          # gestión de espacios
├── reservas/          # reservas, disponibilidad, aprobación, historial
├── openspec/          # especificaciones y cambios
├── PLAN_INGENIERIA.md
├── README.md
└── INFORME_FINAL.md
```

### 3.5 Comparación de decisiones técnicas
| Decisión | Elegida | Alternativa descartada | Razón |
|---|---|---|---|
| Framework backend | **Django + DRF** | Flask | Django ya incluye usuarios, permisos, ORM, migraciones y panel de administración; con Flask habría que construirlos a mano. Además, el estudiante tiene más experiencia con Django. |
| Base de datos | **PostgreSQL (Supabase)** | SQLite | La prevención de reservas simultáneas exige buen manejo de concurrencia y transacciones; SQLite lo soporta de forma limitada. PostgreSQL permite restricciones más robustas. |
| Alcance de interfaz | **API REST + panel admin de Django** | Frontend completo (React o plantillas) | Reduce el alcance para concentrarse en la lógica de negocio y en el proceso SDD, que es el objetivo de la evaluación. |
| Arquitectura | **Monolito modular** | Microservicios | Menor complejidad operativa y de despliegue para un sistema pequeño; los módulos separados permiten evolucionar después. |

---

## 4. Estrategia de desarrollo

### 4.1 Metodología de trabajo
**Spec-Driven Development (SDD) con un flujo iterativo e incremental:** plan → especificación → revisión → implementación → verificación. Cada funcionalidad se especifica y revisa antes de implementarse. Se trabaja con commits pequeños y frecuentes, y se usa Git para demostrar el orden del proceso.

### 4.2 Etapas, orden y criterio de terminado
| # | Etapa | Depende de | Criterio para considerarla terminada |
|---|---|---|---|
| 0 | Plan de ingeniería | — | Documento completo, en commit independiente |
| 1 | Especificaciones y revisión | 0 | Todas las funcionalidades con requisitos y escenarios verificables; sin contradicciones ni ambigüedades pendientes; tareas definidas |
| 2 | Base del proyecto y BD | 1 | Proyecto corre, migra y conecta a PostgreSQL |
| 3 | Usuarios y roles | 2 | Registro, autenticación y permisos por rol con pruebas pasando |
| 4 | Espacios | 3 | CRUD solo para administradores, con pruebas pasando |
| 5 | Reservas y disponibilidad | 3, 4 | Se crean solicitudes; se rechaza cualquier solapamiento; pruebas pasando |
| 6 | Aprobación, rechazo, cancelación e historial | 5 | Transiciones de estado válidas y consulta de historial, con pruebas |
| 7 | Cambio de regla de negocio | 6 | Specs actualizadas antes del código; nuevas pruebas; sin regresiones |
| 8 | Verificación y cierre | 7 | Todas las pruebas pasan; README e INFORME_FINAL listos |

### 4.3 Dependencias entre componentes
`usuarios` es la base (los demás módulos necesitan saber quién actúa). `espacios` es necesario para `reservas`. `historial` depende de los estados de `reservas`.

---

## 5. Estrategia de calidad

### 5.1 Tipos de pruebas
- **Pruebas unitarias:** validaciones de modelos y reglas de negocio (por ejemplo, detección de solapamiento).
- **Pruebas de integración / de API:** endpoints con distintos roles, códigos de respuesta y flujos completos.
- **Pruebas de regresión:** se ejecutan toda la suite tras cada cambio, especialmente tras el cambio de regla de negocio.
- **Pruebas de aceptación:** cada escenario de las especificaciones tiene al menos una prueba que lo verifique.

### 5.2 Riesgos y mitigación
| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Reservas simultáneas que se cruzan por condiciones de carrera | Validación dentro de una transacción con bloqueo de filas y restricción en la base de datos; prueba específica de solapamiento |
| 2 | Especificaciones ambiguas que llevan a una implementación incorrecta | Fase de revisión previa; escenarios de aceptación concretos y verificables |
| 3 | El agente de IA implementa funcionalidades no especificadas o rompe la arquitectura | Instrucciones acotadas por tarea; revisión de cada cambio antes del commit; contrastar el código con las specs |
| 4 | Tiempo insuficiente para el alcance | Priorización de funcionalidades; alcance reducido (API sin frontend); entregar de forma incremental |
| 5 | Fallo en la conexión o configuración de la base de datos en Supabase | Variables de entorno documentadas en el README; posibilidad de usar la configuración local para pruebas |
| 6 | Acceso no autorizado a acciones de administrador | Permisos por rol aplicados en cada endpoint; pruebas de permisos |
| 7 | El cambio de regla (límite de horas) genera regresiones | Cambio gestionado por OpenSpec; ejecución de la suite completa antes y después |

### 5.3 Verificación del cumplimiento de requisitos
- Cada requisito de OpenSpec tiene escenarios de aceptación, y cada escenario se mapea a una o más pruebas automatizadas.
- Una matriz de trazabilidad (requisito → código → prueba) se mantiene en la documentación final.
- Antes del cierre se ejecuta toda la suite y se revisa la correspondencia entre especificaciones y código.

---

## 6. Uso de SDD e inteligencia artificial

### 6.1 ¿Cómo se utilizará OpenSpec?
Se inicializa OpenSpec en el repositorio y se usa para escribir las especificaciones de cada capacidad (espacios, usuarios y roles, reservas, disponibilidad, aprobación, cancelación e historial) como requisitos con escenarios verificables. Cada cambio se gestiona mediante una propuesta con sus tareas, y al terminar se incorpora a las especificaciones vigentes. Esto deja registro de cada decisión y de cada modificación.

### 6.2 ¿Cómo se transforma este plan en especificaciones?
Cada funcionalidad prioritaria (sección 2.2) se convierte en una capacidad de OpenSpec. Los actores definidos (sección 1.3) determinan los permisos de cada requisito. Las decisiones de arquitectura y de persistencia (sección 3) se incluyen como restricciones. Los criterios de terminado (sección 4.2) y los riesgos (sección 5.2) dan origen a escenarios de aceptación, por ejemplo el de reservas simultáneas.

### 6.3 Actividades que se delegan a la IA
- Redactar borradores de especificaciones a partir de este plan (que luego se revisan).
- Generar código de modelos, serializadores, vistas y pruebas conforme a las tareas aprobadas.
- Proponer pruebas automatizadas para los escenarios de aceptación.
- Ayudar a detectar ambigüedades o inconsistencias entre documentos.

### 6.4 ¿Cómo se verifica el código generado?
- Leer y entender cada cambio antes de hacer el commit.
- Ejecutar la suite de pruebas automatizadas.
- Contrastar el código con los requisitos y escenarios de la especificación.
- Rechazar o corregir cualquier funcionalidad que no esté especificada o que se aparte de la arquitectura definida.
- Probar manualmente los endpoints críticos con Postman o Swagger.

### 6.5 Decisiones que son responsabilidad del estudiante
- Elegir la arquitectura, el stack y la estrategia de persistencia, y justificarlos.
- Definir y aprobar las especificaciones y el alcance.
- Aprobar o rechazar cada cambio propuesto por la IA.
- Decidir cómo gestionar los cambios de reglas de negocio.
- Interpretar los resultados de las pruebas y documentar las decisiones que cambien durante el desarrollo.
- Sustentar el sistema y el proceso.
