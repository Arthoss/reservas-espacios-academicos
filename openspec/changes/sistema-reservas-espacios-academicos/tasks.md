# Tasks

## 1. Base del proyecto

- [ ] 1.1 Crear el proyecto Django y configurar Django REST Framework con configuración por entorno para PostgreSQL.
- [ ] 1.2 Definir el modelo de usuario personalizado y el rol inicial antes de generar migraciones de las demás aplicaciones.
- [ ] 1.3 Crear las aplicaciones modulares `usuarios`, `espacios` y `reservas`, y verificar migraciones y conexión con PostgreSQL.

## 2. Usuarios, roles y permisos

- [ ] 2.1 Implementar registro de solicitantes y autenticación con respuestas que no revelen si existe el correo.
- [ ] 2.2 Implementar asignación administrativa de roles y permisos por endpoint, incluyendo denegación a solicitantes y usuarios no autenticados.
- [ ] 2.3 Probar registro válido y duplicado, autenticación válida e inválida, cambio de roles y restricciones de acceso.

## 3. Catálogo de espacios

- [ ] 3.1 Implementar creación, consulta, edición, activación y desactivación de espacios con validación de nombre, tipo y capacidad.
- [ ] 3.2 Restringir administración a administradores, exponer solo espacios activos en el catálogo disponible y permitir filtrar por tipo.
- [ ] 3.3 Proteger espacios referenciados por reservas contra eliminación permanente y probar cada operación y denegación por rol.

## 4. Solicitudes y disponibilidad

- [ ] 4.1 Implementar creación de solicitudes con propietario, espacio, inicio, fin, motivo y estado inicial pendiente; validar que el espacio esté activo y la franja sea futura y válida.
- [ ] 4.2 Implementar consulta de disponibilidad usando intervalos semiabiertos y considerando pendientes y aprobadas como ocupadas.
- [ ] 4.3 Serializar la creación concurrente por espacio dentro de una transacción y añadir la restricción de exclusión en PostgreSQL para evitar solapamientos pendientes o aprobados.
- [ ] 4.4 Convertir conflictos de integridad/disponibilidad en una respuesta API consistente sin dejar solicitudes duplicadas persistidas.
- [ ] 4.5 Probar solapamientos, franjas consecutivas, espacio inactivo y dos solicitudes concurrentes contra PostgreSQL con conexiones independientes.

## 5. Aprobación y rechazo

- [ ] 5.1 Implementar transiciones administrativas solo desde pendiente hacia aprobada o rechazada, guardando quién tomó la decisión.
- [ ] 5.2 Liberar disponibilidad al rechazar y denegar nuevas decisiones sobre reservas ya resueltas o canceladas.
- [ ] 5.3 Probar aprobaciones, rechazos, permisos por rol y transiciones inválidas mediante pruebas de API.

## 6. Cancelación e historial

- [ ] 6.1 Permitir a los propietarios cancelar reservas pendientes o aprobadas antes de su inicio y liberar la franja; denegar cancelaciones ajenas o posteriores al inicio.
- [ ] 6.2 Registrar creación y cada transición en eventos de historial con estados anterior/nuevo, actor y fecha y hora, sin eliminar eventos previos.
- [ ] 6.3 Implementar consulta de historial propio para solicitantes y consulta global solo para administradores.
- [ ] 6.4 Probar propiedad, permisos, disponibilidad tras cancelar, orden cronológico y preservación de eventos.

## 7. Verificación y documentación

- [ ] 7.1 Asociar cada escenario de las cinco especificaciones con una o más pruebas automatizadas de modelo o API.
- [ ] 7.2 Ejecutar la suite completa sobre PostgreSQL y verificar el caso de concurrencia y la restricción de integridad.
- [ ] 7.3 Documentar configuración de variables de entorno y endpoints REST; generar la documentación OpenAPI acordada con drf-spectacular.
