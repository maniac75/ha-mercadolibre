# Mercado Libre Compras

Integración para consultar tus compras y envíos de Mercado Libre Chile en Home Assistant.

**Beta 0.2.0b1 · Home Assistant 2026.10.4 o posterior.**

- Un sensor con la cantidad de envíos activos.
- Productos, cantidades, seguimiento e historial en sus atributos.
- Compras que comparten envío agrupadas en un solo paquete.
- Actualización cada 30 minutos y renovación automática de la autorización.
- Tarjeta opcional con paquetes activos y finalizados.

## Instalar

Añade este repositorio a HACS como **Integración**, descárgalo y reinicia Home Assistant. Después conecta tu cuenta con las [instrucciones de autorización](docs/AUTHORIZATION.md).

[Instalación y actualización](docs/INSTALL.md) · [Tarjeta de ejemplo](docs/mercadolibre-card.yaml) · [Cambios](CHANGELOG.md)

## Alcance

La integración consulta compras; no modifica pedidos ni realiza pagos. Cada usuario configura sus propias credenciales de aplicación en Mercado Libre.

La consulta abarca hasta las 200 compras más recientes. Si el resultado es parcial o contiene estados desconocidos, el sensor muestra un valor desconocido en lugar de un total incompleto. Un error temporal deja el sensor no disponible; la pérdida de autorización solicita reconectar la cuenta.

El historial depende de lo que entregue la API; no es un archivo permanente de todas las compras. Esta versión no expone estimaciones de entrega ni recibe notificaciones push. Solo está validada con cuentas de Chile.

## Privacidad

Home Assistant conserva las credenciales y tokens en su almacenamiento y copias de seguridad. Los productos e historiales se mantienen disponibles en vivo; el atributo `shipments` se excluye de Recorder. Otros consumidores con acceso a HA pueden conservar estos datos.

## Ayuda

Para informar un problema, describe el error y la versión de Home Assistant. Revisa los registros antes de compartirlos y retira credenciales, identificadores y datos de compras. Consulta [SECURITY.md](SECURITY.md) si encontraste una vulnerabilidad.

Proyecto independiente, sin afiliación con Mercado Libre ni Home Assistant.
