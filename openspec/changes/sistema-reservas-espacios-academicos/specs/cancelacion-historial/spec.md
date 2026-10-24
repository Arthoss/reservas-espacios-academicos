# Spec Delta

## Purpose

Asegurar que las cancelaciones respeten la propiedad de la reserva y que las consultas de historial permitan seguir las solicitudes y sus cambios de estado.

## ADDED Requirements

### Requirement: Cancelación por el solicitante propietario
El sistema DEBE permitir solo al solicitante propietario cancelar sus reservas pendientes o aprobadas antes del inicio de la franja; un administrador no puede cancelar reservas ajenas.

#### Scenario: Solicitante cancela su reserva futura
- **DADO** que el solicitante autenticado es propietario de una reserva pendiente o aprobada cuyo inicio no ha ocurrido
- **CUANDO** solicita cancelarla
- **ENTONCES** el sistema cambia el estado a cancelada y libera la franja para nuevas solicitudes

#### Scenario: Solicitante cancela una reserva ajena
- **DADO** que la reserva pertenece a otra persona
- **CUANDO** el solicitante autenticado intenta cancelarla
- **ENTONCES** el sistema deniega la acción y conserva el estado de la reserva

#### Scenario: Administrador intenta cancelar una reserva ajena
- **DADO** que la reserva pertenece a un solicitante distinto del administrador
- **CUANDO** el administrador intenta cancelarla
- **ENTONCES** el sistema deniega la acción y conserva el estado de la reserva

#### Scenario: Cancelación después del inicio
- **DADO** que la franja de la reserva ya comenzó
- **CUANDO** el solicitante intenta cancelarla
- **ENTONCES** el sistema rechaza la cancelación y conserva el estado actual

#### Scenario: Intento de cancelar una reserva rechazada o ya cancelada
- **DADO** que la reserva está rechazada o ya está cancelada
- **CUANDO** el solicitante propietario intenta cancelarla
- **ENTONCES** el sistema informa que la transición no es válida y conserva el estado existente

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
El sistema DEBE conservar un registro consultable de la creación y de cada transición de estado de una reserva, incluyendo estado anterior y nuevo, actor y fecha y hora del cambio; solo el propietario de la reserva o un administrador puede consultar sus eventos.

#### Scenario: Consulta de cambios de una reserva
- **DADO** que una reserva fue creada y luego aprobada o cancelada
- **Y** el actor autenticado es su propietario o un administrador
- **CUANDO** un usuario autorizado consulta el historial de esa reserva
- **ENTONCES** el sistema devuelve los eventos en orden cronológico con estado anterior, estado nuevo, actor y fecha y hora

#### Scenario: Otro solicitante intenta consultar los eventos
- **DADO** que el actor autenticado es solicitante y no es propietario de la reserva
- **CUANDO** consulta los eventos de esa reserva
- **ENTONCES** el sistema deniega el acceso y no revela sus eventos

#### Scenario: Cambio de estado no elimina eventos previos
- **DADO** que una reserva ya tiene eventos de historial
- **CUANDO** cambia nuevamente de estado por una transición permitida
- **ENTONCES** el sistema agrega un evento nuevo y conserva todos los eventos anteriores
