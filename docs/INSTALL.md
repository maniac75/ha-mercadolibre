# Instalación con HACS

Necesitas HACS y Home Assistant 2026.10.4 o posterior.

1. Abre **HACS → ⋮ → Repositorios personalizados**.
2. Añade `https://github.com/maniac75/ha-mercadolibre` con categoría **Integración**.
3. Busca **Mercado Libre Compras** y descárgala. Para instalar una beta, habilita la visualización de versiones preliminares en su descarga.
4. Reinicia Home Assistant.
5. Sigue la [guía de autorización](AUTHORIZATION.md) para conectar tu cuenta.

## Comprobar la conexión

En **Ajustes → Dispositivos y servicios → Mercado Libre Compras**, comprueba que aparezca el sensor de envíos en seguimiento. Si no tienes envíos activos, puede mostrar cero.

## Tarjeta opcional

En el panel, pulsa **Editar → Añadir tarjeta → Manual** y pega el contenido de [mercadolibre-card.yaml](mercadolibre-card.yaml). Ajusta el identificador del sensor en las dos primeras referencias si tu instalación usa uno diferente.

La tarjeta también se incluye en la descarga de HACS, en `custom_components/mercadolibre_tracking/examples/mercadolibre-card.yaml`.

Muestra productos y cantidades, estado y detalle, número de seguimiento, identificador del envío, fechas de eventos e historial completo disponible. Los entregados y los cancelados/no entregados se consultan en secciones desplegables. Las horas se muestran en la zona horaria de Home Assistant.

## Actualizar

Descarga la actualización desde HACS y reinicia Home Assistant. La cuenta configurada se conserva.

## Desinstalar

Elimina la integración desde **Ajustes → Dispositivos y servicios**, retira la tarjeta si la añadiste y elimina la descarga desde HACS. Reinicia Home Assistant.
