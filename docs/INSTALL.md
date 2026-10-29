# Instalación con HACS

Necesitas HACS y Home Assistant 2026.10.4 o posterior.

1. Abre **HACS → ⋮ → Repositorios personalizados**.
2. Añade `https://github.com/maniac75/mercadolibre-compras` con categoría **Integración**.
3. Busca **Mercado Libre Compras** y descárgala. Para instalar una beta, habilita la visualización de versiones preliminares en su descarga.
4. Reinicia Home Assistant.
5. Sigue la [guía de autorización](AUTHORIZATION.md) para conectar tu cuenta.

## Comprobar la conexión

En **Ajustes → Dispositivos y servicios → Mercado Libre Compras**, comprueba que aparezca el sensor de envíos en seguimiento. Si no tienes envíos activos, puede mostrar cero.

## Tarjeta opcional

Copia [mercadolibre-card.yaml](mercadolibre-card.yaml) en una tarjeta manual del panel. Ajusta el identificador del sensor si tu instalación usa uno diferente.

## Actualizar

Descarga la actualización desde HACS y reinicia Home Assistant. La cuenta configurada se conserva.

## Desinstalar

Elimina la integración desde **Ajustes → Dispositivos y servicios**, retira la tarjeta si la añadiste y elimina la descarga desde HACS. Reinicia Home Assistant.
