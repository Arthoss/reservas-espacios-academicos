# Spec Delta

## Purpose

Establecer cómo se solicitan reservas, cómo se consulta la disponibilidad y cómo se impide que dos solicitudes ocupen franjas incompatibles de un mismo espacio.

## ADDED Requirements

### Requirement: Creación de solicitudes de reserva
El sistema DEBE permitir a un solicitante autenticado crear una solicitud para un espacio activo, indicando inicio, fin y motivo, y registrar la solicitud inicialmente como pendiente.

#### Scenario: Solicitud válida
- **DADO** que el solicitante está autenticado y el espacio está activo
- **CUANDO** envía una franja futura válida y un motivo
- **ENTONCES** el sistema crea una reserva pendiente asociada al solicitante y al espacio

#### Scenario: Usuario no autenticado solicita una reserva
- **DADO** que la persona no está autenticada
- **CUANDO** intenta crear una solicitud de reserva
- **ENTONCES** el sistema deniega la acción y no crea una reserva

### Requirement: Validación de franjas horarias
El sistema DEBE rechazar una solicitud cuya fecha de inicio no sea anterior a la fecha de fin o cuyo inicio no sea futuro.

#### Scenario: Intervalo vacío o invertido
- **DADO** que el solicitante envía inicio igual o posterior al fin
- **CUANDO** intenta crear la reserva
- **ENTONCES** el sistema informa un error de validación y no crea la solicitud

#### Scenario: Inicio pasado
- **DADO** que el inicio solicitado ya ocurrió
- **CUANDO** el solicitante envía la solicitud
- **ENTONCES** el sistema la rechaza y no ocupa disponibilidad

### Requirement: Consulta de disponibilidad
El sistema DEBE informar si un espacio activo está disponible durante una franja, considerando las reservas pendientes y aprobadas.

#### Scenario: Franja disponible
- **DADO** que el espacio está activo y no hay reservas pendientes o aprobadas que se solapen con la franja consultada
- **CUANDO** un usuario consulta su disponibilidad
- **ENTONCES** el sistema informa que la franja está disponible

#### Scenario: Franja ocupada
- **DADO** que existe una reserva pendiente o aprobada que se solapa con la franja consultada
- **CUANDO** un usuario consulta la disponibilidad
- **ENTONCES** el sistema informa que la franja no está disponible

### Requirement: Rechazo de solapamientos
El sistema DEBE impedir que una solicitud pendiente o aprobada se solape con otra reserva pendiente o aprobada del mismo espacio.

#### Scenario: Solicitud solapada
- **DADO** que existe una reserva pendiente o aprobada para el mismo espacio
- **CUANDO** se solicita una franja que comparte cualquier tiempo con la reserva existente
- **ENTONCES** el sistema rechaza la nueva solicitud e informa un conflicto de disponibilidad

#### Scenario: Reservas consecutivas
- **DADO** que una reserva ocupa el intervalo desde las 10:00 hasta las 11:00
- **CUANDO** se solicita el mismo espacio desde las 11:00 hasta las 12:00
- **ENTONCES** el sistema acepta la solicitud porque los intervalos solo comparten el límite y no tiempo ocupado

### Requirement: Prevención de reservas simultáneas
El sistema DEBE garantizar que solicitudes concurrentes para franjas solapadas del mismo espacio no puedan persistir ambas como pendientes o aprobadas.

#### Scenario: Dos solicitudes simultáneas para la misma franja
- **DADO** que dos solicitantes envían simultáneamente solicitudes válidas para el mismo espacio y una franja solapada
- **CUANDO** el sistema procesa ambas solicitudes concurrentemente
- **ENTONCES** exactamente una solicitud queda creada como pendiente y la otra recibe un conflicto, sin dejar dos reservas incompatibles persistidas

### Requirement: Solicitudes sobre espacios inactivos
El sistema DEBE impedir la creación de nuevas reservas para un espacio inactivo.

#### Scenario: Solicitud de espacio inactivo
- **DADO** que el espacio solicitado está inactivo
- **CUANDO** un solicitante intenta reservarlo
- **ENTONCES** el sistema rechaza la solicitud y no crea una reserva
