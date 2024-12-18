# services/precio_service.py

from decimal import Decimal

def calcular_precio_con_descuento(producto):
    if producto.descuento and producto.descuento.activo:
        descuento_decimal = Decimal(producto.descuento.porcentaje) / 100
        precio_descontado = producto.precio * (1 - descuento_decimal)
        return round(precio_descontado, 2)
    return producto.precio

def formatear_precio_mostrar(producto):
    precio_original = producto.precio
    precio_descuento = calcular_precio_con_descuento(producto)
    if precio_descuento < precio_original:
        return f"{precio_descuento} <del>{precio_original}</del>"
    return f"{precio_original}"