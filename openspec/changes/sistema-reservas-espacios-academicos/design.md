# Design

## Context

El proyecto aún no contiene implementación ni especificaciones previas. El alcance y el stack quedan definidos en `PLAN_INGENIERIA.md`: Python 3.12, Django + Django REST Framework, PostgreSQL en Supabase y monolito modular por aplicaciones `usuarios`, `espacios` y `reservas`. Las reglas observables están detalladas en los cinco archivos bajo `specs/`.

## Goals / Non-Goals

**Goals:**
- Traducir las cinco capacidades en una API REST con límites modulares y autorización consistente.
- Mantener integridad de reservas bajo concurrencia real en PostgreSQL.
- Preservar trazabilidad de transiciones y referencias históricas.

**Non-Goals:**
- Introducir microservicios, frontend separado, reservas recurrentes, pagos, notificaciones o integración institucional.
- Definir una política de expiración automática para solicitudes pendientes, que no está en el alcance actual.

## Decisions

- **Monolito modular en capas.** Usar las aplicaciones Django `usuarios`, `espacios` y `reservas`, con endpoints DRF, lógica de negocio en servicios/validaciones y persistencia mediante ORM. Esto sigue el plan y separa responsabilidades sin la carga operativa de microservicios.

- **Usuario propio con rol explícito y permisos centralizados.** Definir el modelo de usuario antes de las primeras migraciones, usando la autenticación de Django y los roles solicitante/administrador del plan. Crear el primer administrador con `createsuperuser`. Aplicar autorización en cada endpoint: catálogo y disponibilidad requieren autenticación; solo solicitantes crean reservas; solo el propietario cancela; el administrador no actúa sobre reservas ajenas. Ocultar controles en la interfaz administrativa no sustituye permisos de API. Se elige este enfoque frente a dejar roles implícitos en endpoints porque las reglas deben ser verificables y uniformes.

- **Modelo relacional para espacios, reservas y eventos.** Una reserva referencia al solicitante y al espacio y contiene inicio, fin, motivo y estado (`pendiente`, `aprobada`, `rechazada` o `cancelada`). Un registro de eventos asociado conserva creación y transiciones con estado anterior/nuevo, actor y marca temporal; solo el propietario o un administrador consulta esos eventos. No se borran físicamente reservas ni eventos. Desactivar un espacio bloquea nuevas reservas, pero conserva las existentes y no modifica su estado ni vigencia.

- **Intervalos semiabiertos y marcas temporales conscientes de zona horaria.** Interpretar las franjas como `[inicio, fin)`, por lo que una reserva que comienza justo cuando termina otra es válida. Recibir fechas con zona horaria y normalizarlas para comparación y persistencia consistente; rechazar inicios pasados e intervalos no positivos conforme a las especificaciones.

- **Doble protección de disponibilidad en PostgreSQL.** Validar solapamientos dentro de una transacción y serializar las creaciones por espacio mediante bloqueo de fila. Añadir una restricción de exclusión PostgreSQL sobre espacio y rango horario semiabierto para filas pendientes o aprobadas. El bloqueo ordena solicitudes concurrentes y la restricción de base de datos protege la invariante ante otros caminos de escritura; un conflicto se transforma en una respuesta de disponibilidad consistente. La validación solo en DRF no se considera suficiente.

- **Decisiones sobre solicitudes vencidas.** No permitir aprobar una solicitud pendiente cuyo inicio ya pasó, pero permitir que un administrador la rechace para liberar la franja. Esta distinción evita confirmar tardíamente una reserva y mantiene un camino explícito para retirar la ocupación pendiente.

- **Pruebas sobre PostgreSQL para las garantías de concurrencia.** Cubrir validaciones, permisos y transiciones con pruebas de modelo y API. Ejecutar la prueba de solicitudes simultáneas y la restricción de solapamiento en PostgreSQL; SQLite no demuestra las garantías de concurrencia ni la restricción elegida.

## Risks / Trade-offs

- [La extensión/tipo de operador requerido por la restricción GiST puede no estar habilitado en el PostgreSQL administrado] → Verificar disponibilidad en Supabase durante la configuración inicial y documentar la migración; mantener el bloqueo transaccional por espacio como protección complementaria.
- [Una solicitud pendiente puede ocupar una franja indefinidamente] → Mantener la regla explícita en esta versión; acordar una política de expiración como cambio posterior, no inventar un vencimiento silencioso.
- [Roles o permisos aplicados solo en una capa pueden permitir acceso indebido] → Probar denegaciones en los endpoints de cada rol, incluidos acceso a historial global y modificación de espacios.
- [Las pruebas de concurrencia pueden ser inestables si se ejecutan sobre SQLite o conexiones compartidas] → Usar PostgreSQL y pruebas transaccionales con conexiones independientes para ese escenario.
- [La modificación del modelo de usuario después de las primeras migraciones es costosa] → Definirlo en la fase inicial antes de crear migraciones de otras aplicaciones.

## Migration Plan

1. Configurar Django, DRF y conexión PostgreSQL por variables de entorno; crear primero el modelo de usuario y migraciones base.
2. Incorporar en orden usuarios/roles, espacios, reservas y después aprobación, cancelación e historial, con migraciones y pruebas por etapa.
3. Habilitar la protección de solapamientos en PostgreSQL antes de aceptar tráfico de reservas y validar las pruebas de concurrencia contra esa base.
4. Para una instalación nueva, rollback mediante migraciones reversibles solo antes de guardar datos de usuarios o reservas. En entornos con datos, respaldar y restaurar según un procedimiento operativo; no eliminar tablas con historial como rollback automático.

## Open Questions

- Ninguna que impida iniciar la implementación según el alcance actual. La política para vencer solicitudes pendientes queda fuera de esta versión.
