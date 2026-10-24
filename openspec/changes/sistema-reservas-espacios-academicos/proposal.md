# Proposal

## Why

La institución administra reservas mediante correos y hojas de cálculo, lo que permite solicitudes duplicadas, conflictos horarios y poca trazabilidad. Este cambio define de manera verificable una API central para usuarios, espacios y el ciclo de vida de las reservas antes de iniciar la implementación.

## What Changes

- Definir la gestión de usuarios, autenticación, roles y permisos para solicitantes y administradores.
- Definir el catálogo y administración de espacios académicos.
- Especificar solicitudes de reserva, consulta de disponibilidad y rechazo de solapamientos, incluso bajo concurrencia.
- Especificar aprobación y rechazo por administradores, cancelación por solicitantes y consulta del historial.
- Mantener el alcance acordado: API REST y panel de administración de Django; sin pagos, notificaciones externas, integraciones institucionales, reservas recurrentes ni frontend completo.
- Como supuesto verificable para proteger disponibilidad, solicitudes pendientes y reservas aprobadas ocupan la franja; los intervalos se interpretan como inicio inclusivo y fin exclusivo.

## Capabilities

### New Capabilities
- `usuarios-roles`: identidad, autenticación, asignación de roles y autorización de acciones.
- `espacios`: catálogo, disponibilidad operativa y administración de espacios académicos.
- `reservas`: creación de solicitudes, validación de franjas y prevención de reservas simultáneas.
- `aprobacion-reservas`: revisión administrativa y transiciones a aprobada o rechazada.
- `cancelacion-historial`: cancelación permitida y consulta del historial trazable.

### Modified Capabilities

Ninguna. El proyecto no tiene especificaciones existentes.

## Impact

- Contrato de la API REST y permisos de sus endpoints.
- Futuras aplicaciones Django `usuarios`, `espacios` y `reservas`, sus modelos, servicios, serializadores, vistas y pruebas.
- Persistencia PostgreSQL mediante ORM y migraciones; las reglas de integridad deben cubrir concurrencia, no solo validación previa en la aplicación.
- No se modifica código en esta etapa.
