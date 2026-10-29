# Conectar Mercado Libre con Home Assistant

## 1. Crear una aplicación

1. Entra a [DevCenter de Mercado Libre Chile](https://developers.mercadolibre.cl/devcenter) con tu cuenta principal y crea una aplicación.
2. Configura la URL de redirección:
   `https://my.home-assistant.io/redirect/oauth`
3. Activa **PKCE**, acceso de **lectura** y **acceso offline**.
4. Guarda la aplicación y copia su **App ID** y **Client Secret**.

## 2. Añadir las credenciales en Home Assistant

1. Ve a **Ajustes → Dispositivos y servicios → ⋮ → Credenciales de aplicación**.
2. Añade credenciales para **Mercado Libre Compras**.
3. Introduce el **App ID** en Client ID y el **Client Secret** en el campo correspondiente. Guarda.

Mantén el Client Secret privado.

## 3. Autorizar tu cuenta

1. En **Dispositivos y servicios**, pulsa **Añadir integración → Mercado Libre Compras**.
2. Selecciona las credenciales que guardaste.
3. Inicia sesión en Mercado Libre y autoriza el acceso a tu cuenta.
4. Cuando aparezca My Home Assistant, selecciona tu instancia de HA y completa la conexión.

Al finalizar aparecerá el sensor de envíos en seguimiento. Los datos se actualizan cada 30 minutos y la autorización se renueva automáticamente.

## Volver a autorizar

Si HA solicita reautorización, abre la integración y sigue el aviso con la misma cuenta de Mercado Libre.

## Si no puedes conectar

- **Error de redirección:** comprueba que la URL registrada coincida exactamente con la indicada arriba.
- **Credenciales inválidas:** revisa el App ID y el Client Secret.
- **Acceso denegado:** comprueba que usas la cuenta principal y que completaste las verificaciones de identidad de Mercado Libre.

[Instalación](INSTALL.md) · [Ayuda de Mercado Libre](https://developers.mercadolibre.cl/autenticacion-y-autorizacion)
