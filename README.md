# Cajero automático con sockets en Python

Ejemplo educativo de programación distribuida: un cliente y un servidor se comunican mediante sockets TCP. El cliente envía solicitudes JSON delimitadas por salto de línea; el servidor valida cada operación y mantiene las cuentas y sus saldos.

## Requisitos

- Python 3.10 o posterior
- No requiere instalar paquetes externos

## Cómo ejecutarlo

Abra dos terminales en esta carpeta.

En la primera, inicie el servidor:

```text
python cajero_server.py
```

En la segunda, inicie el cliente:

```text
python cajero_client.py
```

Credenciales precargadas:

| Cuenta | PIN | Saldo inicial |
|---|---|---:|
| 1001 | 1234 | $500.00 |
| 1002 | 5678 | $1250.00 |

El servidor escucha por defecto en `127.0.0.1:5000`. Para probar en una red local, inícielo con `python cajero_server.py --host 0.0.0.0 --port 5000` y conecte el cliente usando la IP del servidor, por ejemplo `python cajero_client.py --host 192.168.1.20 --port 5000`.

## Flujo de la comunicación

1. El servidor abre un socket TCP y espera conexiones.
2. El cliente establece una conexión y envía un mensaje JSON por línea para iniciar sesión.
3. El servidor valida la cuenta y el PIN, y responde con otro JSON.
4. El cliente solicita consultar saldo, depositar o retirar. El servidor procesa la operación y devuelve el resultado y el saldo.
5. El cliente envía la solicitud para cerrar sesión y termina la conexión.

TCP entrega un flujo de bytes, no mensajes completos; por eso este ejemplo usa una línea JSON por mensaje. El servidor puede atender varios clientes a la vez y protege el saldo compartido con un bloqueo.

## Pruebas

Ejecute desde esta carpeta:

```text
python -m unittest discover -s tests -v
```

Este proyecto es únicamente una simulación didáctica. Las cuentas viven en memoria y se reinician al detener el servidor. El PIN se transmite sin cifrado y no hay persistencia, límites de intentos ni controles bancarios reales. No lo exponga a Internet ni lo use para manejar dinero real.
