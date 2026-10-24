# Tasks

## 1. Base del proyecto

- [x] 1.1 Crear el proyecto Django y configurar Django REST Framework con configuración por entorno para PostgreSQL.
- [x] 1.2 Crear las aplicaciones modulares `usuarios`, `espacios` y `reservas`.
- [x] 1.3 Definir el modelo de usuario personalizado y el rol inicial en `usuarios` antes de generar migraciones de las demás aplicaciones, y verificar migraciones y conexión con PostgreSQL.
- [x] 1.4 Crear el primer administrador mediante el comando `createsuperuser` de Django y verificar sus permisos.

## 2. Usuarios, roles y permisos

- [x] 2.1 Implementar el registro de solicitantes informando si el correo ya existe; usar una respuesta genérica indistinguible solo para autenticación fallida, tanto por correo inexistente como por contraseña incorrecta.
- [x] 2.2 Implementar asignación administrativa de roles y permisos por endpoint, incluyendo denegación a solicitantes y usuarios no autenticados.
- [x] 2.3 Probar registro válido y duplicado con respuesta explícita, autenticación válida e inválida con respuesta genérica, creación del primer administrador, cambio de roles y restricciones de acceso.

## 3. Catálogo de espacios

- [x] 3.1 Implementar creación, consulta, edición, activación y desactivación de espacios con validación de nombre, tipo y capacidad.
- [x] 3.2 Exigir autenticación para consultar y filtrar el catálogo; restringir su administración a administradores y exponer solo espacios activos para nuevas reservas.
- [x] 3.3 Al desactivar un espacio, conservar las reservas existentes con su estado y vigencia; probar que solo se bloquean nuevas reservas.
- [x] 3.4 Proteger espacios referenciados por reservas contra eliminación permanente y probar cada operación y denegación por rol.

## 4. Solicitudes y disponibilidad

- [x] 4.1 Permitir solo a solicitantes autenticados crear solicitudes con propietario, espacio, inicio, fin, motivo y estado inicial pendiente; validar que el espacio esté activo y la franja sea futura y válida.
- [x] 4.2 Exigir autenticación para consultar disponibilidad, usando intervalos semiabiertos y considerando pendientes y aprobadas como ocupadas.
- [x] 4.3 Serializar la creación concurrente por espacio dentro de una transacción y añadir la restricción de exclusión en PostgreSQL para evitar solapamientos pendientes o aprobados.
- [x] 4.4 Convertir conflictos de integridad/disponibilidad en una respuesta API consistente sin dejar solicitudes duplicadas persistidas.
- [x] 4.5 Probar permisos de creación y consulta, solapamientos, franjas consecutivas, espacio inactivo y dos solicitudes concurrentes contra PostgreSQL con conexiones independientes.

## 5. Aprobación y rechazo

- [ ] 5.1 Implementar transiciones administrativas solo desde pendiente hacia aprobada o rechazada, guardando quién tomó la decisión; impedir aprobar después del inicio, pero permitir rechazar para liberar la franja.
- [ ] 5.2 Liberar disponibilidad al rechazar y denegar nuevas decisiones sobre reservas ya resueltas o canceladas.
- [ ] 5.3 Probar aprobaciones, rechazos, permisos por rol y transiciones inválidas mediante pruebas de API.

## 6. Cancelación e historial

- [ ] 6.1 Permitir solo al solicitante propietario cancelar reservas pendientes o aprobadas antes de su inicio y liberar la franja; denegar cancelaciones ajenas, por administradores sobre reservas ajenas, posteriores al inicio o desde estados rechazado/cancelado.
- [ ] 6.2 Registrar creación y cada transición en eventos de historial con estados anterior/nuevo, actor y fecha y hora, sin eliminar eventos previos; permitir consultar eventos solo al propietario o a un administrador.
- [ ] 6.3 Implementar consulta de historial propio para solicitantes y consulta global solo para administradores.
- [ ] 6.4 Probar propiedad, permisos de lectura de eventos, transiciones inválidas al cancelar, disponibilidad tras cancelar, orden cronológico y preservación de eventos.

## 7. Verificación y documentación

- [ ] 7.1 Asociar cada escenario de las cinco especificaciones con una o más pruebas automatizadas de modelo o API.
- [ ] 7.2 Ejecutar la suite completa sobre PostgreSQL y verificar el caso de concurrencia y la restricción de integridad.
- [ ] 7.3 Documentar configuración de variables de entorno y endpoints REST; generar la documentación OpenAPI acordada con drf-spectacular.
