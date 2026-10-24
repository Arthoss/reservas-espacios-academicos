# Spec Delta

## Purpose

Definir el catálogo consultable de espacios académicos y las acciones administrativas que mantienen sus datos y disponibilidad operativa confiables.

## ADDED Requirements

### Requirement: Consulta del catálogo de espacios activos
El sistema DEBE permitir únicamente a usuarios autenticados consultar los espacios activos y sus datos de identificación, tipo y capacidad.

#### Scenario: Usuario consulta espacios activos
- **DADO** que existen espacios activos e inactivos
- **CUANDO** un usuario consulta el catálogo
- **ENTONCES** el sistema devuelve los espacios activos con nombre, tipo y capacidad, sin exponer los inactivos como disponibles

#### Scenario: Usuario filtra por tipo
- **DADO** que existen espacios activos de varios tipos
- **CUANDO** un usuario filtra el catálogo por un tipo admitido
- **ENTONCES** el sistema devuelve únicamente los espacios activos de ese tipo

#### Scenario: Usuario no autenticado consulta el catálogo
- **DADO** que la persona no está autenticada
- **CUANDO** intenta consultar o filtrar el catálogo
- **ENTONCES** el sistema deniega el acceso y no devuelve espacios

### Requirement: Administración del catálogo
El sistema DEBE permitir a los administradores crear, modificar, activar y desactivar espacios, y denegar estas acciones a los solicitantes.

#### Scenario: Administrador crea un espacio válido
- **DADO** que el actor autenticado es administrador
- **CUANDO** registra un espacio con nombre, tipo admitido y capacidad positiva
- **ENTONCES** el sistema guarda el espacio activo y lo incluye en el catálogo

#### Scenario: Administrador desactiva un espacio
- **DADO** que el actor autenticado es administrador y el espacio existe
- **Y** el espacio tiene reservas existentes
- **CUANDO** desactiva el espacio
- **ENTONCES** el sistema lo oculta del catálogo para nuevas reservas y conserva todas las reservas existentes con su estado y vigencia sin cambios

#### Scenario: Solicitante modifica el catálogo
- **DADO** que el actor autenticado es solicitante
- **CUANDO** intenta crear o modificar un espacio
- **ENTONCES** el sistema deniega la acción y no altera el catálogo

### Requirement: Validación de datos del espacio
El sistema DEBE rechazar espacios con campos obligatorios ausentes, tipo no admitido o capacidad menor que uno.

#### Scenario: Datos de espacio inválidos
- **DADO** que el actor es administrador
- **CUANDO** envía un espacio sin nombre, con tipo no admitido o capacidad no positiva
- **ENTONCES** el sistema informa errores de validación y no guarda el espacio

### Requirement: Protección de espacios con historial
El sistema DEBE impedir la eliminación permanente de un espacio referenciado por una reserva y permitir su desactivación administrativa.

#### Scenario: Eliminación de espacio con reservas
- **DADO** que un espacio está referenciado por al menos una reserva
- **CUANDO** un administrador solicita eliminarlo permanentemente
- **ENTONCES** el sistema rechaza la eliminación y conserva tanto el espacio como el historial

#### Scenario: Eliminación de espacio sin reservas
- **DADO** que un espacio no está referenciado por ninguna reserva
- **CUANDO** un administrador solicita eliminarlo permanentemente
- **ENTONCES** el sistema elimina el espacio del catálogo
