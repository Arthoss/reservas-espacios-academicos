# Spec Delta

## Purpose

Definir la revisión administrativa de solicitudes pendientes y las transiciones permitidas hacia los estados aprobada y rechazada.

## ADDED Requirements

### Requirement: Aprobación administrativa
El sistema DEBE permitir que un administrador apruebe una solicitud pendiente y denegar la aprobación a otros roles.

#### Scenario: Administrador aprueba una solicitud pendiente
- **DADO** que existe una solicitud pendiente y el actor autenticado es administrador
- **CUANDO** el administrador la aprueba
- **ENTONCES** el sistema cambia su estado a aprobada y conserva quién realizó la decisión

#### Scenario: Solicitante intenta aprobar una solicitud
- **DADO** que el actor autenticado tiene rol de solicitante
- **CUANDO** intenta aprobar una solicitud pendiente
- **ENTONCES** el sistema deniega la acción y mantiene el estado pendiente

### Requirement: Rechazo administrativo
El sistema DEBE permitir que un administrador rechace una solicitud pendiente y liberar la franja para futuras solicitudes.

#### Scenario: Administrador rechaza una solicitud pendiente
- **DADO** que existe una solicitud pendiente y el actor autenticado es administrador
- **CUANDO** el administrador la rechaza
- **ENTONCES** el sistema cambia su estado a rechazada, registra quién tomó la decisión y deja de contar la franja como ocupada

### Requirement: Decisión única sobre solicitudes
El sistema DEBE permitir una transición de decisión solo desde el estado pendiente y no modificar solicitudes ya resueltas.

#### Scenario: Intento de aprobar una solicitud ya rechazada
- **DADO** que una solicitud está rechazada
- **CUANDO** un administrador intenta aprobarla o rechazarla de nuevo
- **ENTONCES** el sistema informa que la transición no es válida y conserva el estado rechazado

#### Scenario: Intento de resolver una solicitud cancelada
- **DADO** que una solicitud está cancelada
- **CUANDO** un administrador intenta aprobarla o rechazarla
- **ENTONCES** el sistema informa que la transición no es válida y conserva el estado cancelado
