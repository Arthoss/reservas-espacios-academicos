# Spec Delta

## Purpose

Define cómo se identifican y autentican los usuarios, y cómo los roles de solicitante y administrador limitan las acciones disponibles en el sistema.

## ADDED Requirements

### Requirement: Registro de solicitantes
El sistema DEBE permitir que una persona cree una cuenta con identidad y credenciales únicas, asignándole inicialmente el rol de solicitante.

#### Scenario: Registro válido
- **DADO** que no existe una cuenta con el correo electrónico proporcionado
- **CUANDO** la persona envía datos de registro válidos
- **ENTONCES** el sistema crea una cuenta activa con rol de solicitante

#### Scenario: Correo ya registrado
- **DADO** que ya existe una cuenta con el correo electrónico proporcionado
- **CUANDO** una persona intenta registrarse de nuevo con ese correo
- **ENTONCES** el sistema rechaza el registro e informa que la identidad ya está en uso

### Requirement: Inicialización del primer administrador
El sistema DEBE permitir crear el primer usuario administrador mediante el comando `createsuperuser` de Django, sin requerir una cuenta administradora previa.

#### Scenario: Operador crea el primer administrador
- **DADO** que el sistema aún no tiene una cuenta administradora
- **CUANDO** un operador ejecuta `createsuperuser` con credenciales válidas
- **ENTONCES** el sistema crea una cuenta activa con permisos de administrador

### Requirement: Autenticación de usuarios
El sistema DEBE autenticar a los usuarios mediante sus credenciales y no revelar si el correo o la contraseña fueron incorrectos.

#### Scenario: Credenciales válidas
- **DADO** que una cuenta activa existe
- **CUANDO** el usuario envía sus credenciales correctas
- **ENTONCES** el sistema autentica al usuario y habilita acceso conforme a su rol

#### Scenario: Credenciales inválidas
- **DADO** que una cuenta existe o no existe
- **CUANDO** se envían credenciales incorrectas
- **ENTONCES** el sistema deniega la autenticación con una respuesta que no distingue entre correo inexistente y contraseña incorrecta

### Requirement: Autorización basada en roles
El sistema DEBE restringir cada acción protegida al rol autorizado y denegar el acceso a usuarios no autenticados o sin permiso.

#### Scenario: Solicitante intenta administrar espacios
- **DADO** que un usuario autenticado tiene rol de solicitante
- **CUANDO** intenta crear, modificar o desactivar un espacio
- **ENTONCES** el sistema deniega la acción sin cambiar el catálogo

#### Scenario: Usuario no autenticado accede a una acción protegida
- **DADO** que no hay una sesión o credencial válida
- **CUANDO** se solicita una acción que requiere autenticación
- **ENTONCES** el sistema deniega el acceso

### Requirement: Asignación administrativa de roles
El sistema DEBE permitir que solo un administrador asigne o cambie el rol de una cuenta existente.

#### Scenario: Administrador cambia un rol
- **DADO** que el actor autenticado es administrador y la cuenta objetivo existe
- **CUANDO** asigna a esa cuenta uno de los roles admitidos
- **ENTONCES** el sistema guarda el nuevo rol y aplica sus permisos en solicitudes posteriores

#### Scenario: Solicitante intenta cambiar un rol
- **DADO** que el actor autenticado es solicitante
- **CUANDO** intenta cambiar el rol propio o el de otra cuenta
- **ENTONCES** el sistema deniega la acción y conserva los roles existentes
