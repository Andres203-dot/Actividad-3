"""Cliente TCP de demostración para interactuar con el cajero automático."""

from __future__ import annotations

import argparse
import json
import socket
from decimal import Decimal, InvalidOperation
from typing import Any

MAX_RESPONSE_BYTES = 4096


class AtmConnection:
    def __init__(self, host: str, port: int) -> None:
        self.socket = socket.create_connection((host, port), timeout=10)
        self.reader = self.socket.makefile("rb")
        self.writer = self.socket.makefile("wb")

    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.writer.write((json.dumps(payload) + "\n").encode("utf-8"))
        self.writer.flush()
        line = self.reader.readline(MAX_RESPONSE_BYTES + 1)
        if not line:
            raise ConnectionError("El servidor cerró la conexión.")
        if len(line) > MAX_RESPONSE_BYTES:
            raise ValueError("La respuesta del servidor es demasiado grande.")
        response = json.loads(line.decode("utf-8"))
        if not isinstance(response, dict):
            raise ValueError("El servidor devolvió una respuesta no válida.")
        return response

    def close(self) -> None:
        self.reader.close()
        self.writer.close()
        self.socket.close()


def format_money(amount_cents: int) -> str:
    return f"${amount_cents // 100}.{amount_cents % 100:02d}"


def read_amount_cents() -> int | None:
    raw_amount = input("Importe: ").strip().replace(",", ".")
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        print("Escriba un importe numérico con hasta dos decimales.")
        return None

    amount_cents = amount * 100
    if (
        not amount.is_finite()
        or amount <= 0
        or amount_cents != amount_cents.to_integral_value()
        or amount_cents > 2_147_483_647
    ):
        print("El importe debe ser positivo y tener como máximo dos decimales.")
        return None
    return int(amount_cents)


def print_response(response: dict[str, Any]) -> bool:
    if response.get("message"):
        print(response["message"])
    if response.get("balance_cents") is not None:
        print(f"Saldo disponible: {format_money(response['balance_cents'])}")
    return response.get("ok") is True


def run_client(host: str, port: int) -> None:
    connection = AtmConnection(host, port)
    try:
        print("=== Cajero automático de demostración ===")
        account_id = input("Número de cuenta: ").strip()
        pin = input("PIN: ").strip()
        if not print_response(connection.request(
            {"action": "login", "account_id": account_id, "pin": pin}
        )):
            return

        while True:
            print("\n1. Consultar saldo\n2. Depositar\n3. Retirar\n4. Salir")
            choice = input("Seleccione una opción: ").strip()
            if choice == "1":
                print_response(connection.request({"action": "balance"}))
            elif choice in {"2", "3"}:
                amount_cents = read_amount_cents()
                if amount_cents is None:
                    continue
                action = "deposit" if choice == "2" else "withdraw"
                print_response(
                    connection.request({"action": action, "amount_cents": amount_cents})
                )
            elif choice == "4":
                print_response(connection.request({"action": "logout"}))
                return
            else:
                print("Opción no válida.")
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente del cajero automático de demostración")
    parser.add_argument("--host", default="127.0.0.1", help="Servidor (por defecto: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Puerto (por defecto: 5000)")
    args = parser.parse_args()

    try:
        run_client(args.host, args.port)
    except (OSError, ConnectionError, ValueError, json.JSONDecodeError) as error:
        print(f"Error de comunicación con el cajero: {error}")


if __name__ == "__main__":
    main()
