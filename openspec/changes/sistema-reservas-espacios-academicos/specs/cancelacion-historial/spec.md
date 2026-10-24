# Spec Delta

## Purpose

Asegurar que las cancelaciones respeten la propiedad de la reserva y que las consultas de historial permitan seguir las solicitudes y sus cambios de estado.

## ADDED Requirements

### Requirement: Cancelación por el solicitante propietario
El sistema DEBE permitir a un solicitante cancelar sus reservas pendientes o aprobadas antes del inicio de la franja, sin permitir cancelar reservas de otra persona.

#### Scenario: Solicitante cancela su reserva futura
- **DADO** que el solicitante autenticado es propietario de una reserva pendiente o aprobada cuyo inicio no ha ocurrido
- **CUANDO** solicita cancelarla
- **ENTONCES** el sistema cambia el estado a cancelada y libera la franja para nuevas solicitudes

#### Scenario: Solicitante cancela una reserva ajena
- **DADO** que la reserva pertenece a otra persona
- **CUANDO** el solicitante autenticado intenta cancelarla
- **ENTONCES** el sistema deniega la acción y conserva el estado de la reserva

#### Scenario: Cancelación después del inicio
- **DADO** que la franja de la reserva ya comenzó
- **CUANDO** el solicitante intenta cancelarla
- **ENTONCES** el sistema rechaza la cancelación y conserva el estado actual

### Requirement: Consulta del historial propio
El sistema DEBE permitir a cada solicitante consultar las reservas propias con sus datos de espacio, franja y estado actual.

#### Scenario: Solicitante consulta su historial
- **DADO** que el solicitante autenticado tiene reservas registradas
- **CUANDO** consulta su historial
- **ENTONCES** el sistema devuelve solo las reservas asociadas a ese solicitante con sus fechas, espacio y estado actual

#### Scenario: Solicitante intenta consultar reservas ajenas
- **DADO** que existen reservas de otros usuarios
- **CUANDO** un solicitante consulta su historial
- **ENTONCES** el sistema no incluye datos de reservas ajenas

### Requirement: Consulta administrativa del historial
El sistema DEBE permitir a un administrador consultar el historial de reservas de todos los usuarios.

#### Scenario: Administrador consulta historial global
- **DADO** que el actor autenticado es administrador
- **CUANDO** consulta el historial
- **ENTONCES** el sistema devuelve las reservas de todos los usuarios con su propietario, espacio, franja y estado actual

#### Scenario: Solicitante intenta consultar historial global
- **DADO** que el actor autenticado es solicitante
- **CUANDO** solicita el historial global
- **ENTONCES** el sistema deniega el acceso y no revela reservas de otros usuarios

### Requirement: Trazabilidad de cambios de reserva
El sistema DEBE conservar un registro consultable de la creación y de cada transición de estado de una reserva, incluyendo estado anterior y nuevo, actor y fecha y hora del cambio.

#### Scenario: Consulta de cambios de una reserva
- **DADO** que una reserva fue creada y luego aprobada o cancelada
- **CUANDO** un usuario autorizado consulta el historial de esa reserva
- **ENTONCES** el sistema devuelve los eventos en orden cronológico con estado anterior, estado nuevo, actor y fecha y hora

#### Scenario: Cambio de estado no elimina eventos previos
- **DADO** que una reserva ya tiene eventos de historial
- **CUANDO** cambia nuevamente de estado por una transición permitida
- **ENTONCES** el sistema agrega un evento nuevo y conserva todos los eventos anteriores
