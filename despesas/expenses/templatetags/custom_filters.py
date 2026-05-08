from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def format_pt(value):
    """
    Formata um valor numérico de acordo com o padrão português (Portugal).
    Exemplo: 1234.56 -> 1.234,56
    """
    try:
        if value is None or value == "":
            return "0,00"

        # Converter para Decimal para precisão
        if isinstance(value, str):
            # Remover simbolos de euro e espaços
            value = value.replace("€", "").replace(" ", "").strip()
            # Converter para Decimal
            value = Decimal(value)
        else:
            value = Decimal(str(value))

        # Separar em partes inteira e decimal
        value_str = f"{value:.2f}"
        parts = value_str.split(".")

        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else "00"

        # Adicionar separadores de milhares na parte inteira (ponto)
        # Reverter para adicionar separadores de trás para frente
        reversed_int = integer_part[::-1]
        formatted_int_parts = []
        for i in range(0, len(reversed_int), 3):
            formatted_int_parts.append(reversed_int[i : i + 3])

        # Juntar com ponto e reverter novamente
        formatted_int = ".".join(formatted_int_parts)[::-1]

        # Retornar no formato português: 1.234,56
        return f"{formatted_int},{decimal_part}"

    except (ValueError, TypeError, AttributeError):
        return str(value)


@register.filter
def format_currency_pt(value):
    """
    Formata um valor com símbolo de euro no formato português.
    Exemplo: 1234.56 -> 1.234,56€
    """
    try:
        formatted = format_pt(value)
        return f"{formatted}€"
    except Exception:
        return str(value)
