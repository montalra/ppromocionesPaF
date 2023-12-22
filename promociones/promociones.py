from .models import PromocionArticulo, ItemNotaVenta

def aplicar_promociones(notaventa, item=None):
    item_venta = ItemNotaVenta.objects.filter(nota_venta=notaventa.nota_venta_id)

    for item in item_venta:
        promociones = PromocionArticulo.objects.filter(
            promocion_id__fecha_inicio__lte=notaventa.fecha_pedido,
            promocion_id__fecha_fin__gte=notaventa.fecha_pedido,
            arti=item.articulo,
        )

        for promocion in promociones:
            bonificacion_unidades = promocion.promocion_id.bonificacion_unidades
            descuento = promocion.promocion_id.descuento
            tipo_promocion = promocion.promocion_id.tipo_promocion.tipo_promocion_nombre
            if tipo_promocion == 'unidad':
                aplicar_promocion_unidad(notaventa, item, promocion, bonificacion_unidades)
            elif tipo_promocion == 'soles':
                aplicar_promocion_soles(notaventa, item, promocion, bonificacion_unidades, descuento)

def aplicar_promocion_unidad(notaventa, item, promocion, bonificacion_unidades):
    cantidad_adquirida = item.cantidad
    cantidad_promocion = promocion.promocion_id.limite
    bonificacion_unidades = bonificacion_unidades 

    unidades_b = cantidad_adquirida // cantidad_promocion
    unidades_bonificada = unidades_b * bonificacion_unidades

    if unidades_bonificada > item.cantidad:
        unidades_bonificada = item.cantidad

    if unidades_bonificada > 0:
        # Verifica si ya existe un registro de bonificación para esta promoción y artículo
        item_bonificado, created = ItemNotaVenta.objects.get_or_create(
            nota_venta=notaventa,
            articulo=item.articulo,
            promocion_aplicada=promocion.promocion_id,
            defaults={
                'cantidad': unidades_bonificada,
                'precio_unitario': 0,
                'total_item_bruto': 0,
            }
        )

        # Si ya existe, actualiza la cantidad bonificada
        if not created:
            item_bonificado.cantidad += unidades_bonificada
            item_bonificado.save()

        print(f"Bonificado {unidades_bonificada} de {item.articulo.nombre_articulo}")

def aplicar_promocion_soles(venta, item, promocion, bonificacion_unidades, descuento):
    monto_limite = promocion.monto

    if venta.total_pedido >= monto_limite:
        unidades_bonificadas = promocion.bonificacion_unidades

        # Verifica si ya existe un registro de bonificación para esta promoción y artículo
        item_bonificado, created = ItemNotaVenta.objects.get_or_create(
            nota_venta=venta,
            articulo=promocion.articulo_bonificado,
            promocion_aplicada=promocion.promocion_id,
            defaults={
                'cantidad': unidades_bonificadas,
                'precio_unitario': 0,
                'total_item_bruto': 0,
            }
        )

        # Si ya existe, actualiza la cantidad bonificada
        if not created:
            item_bonificado.cantidad += unidades_bonificadas
            item_bonificado.save()

        print(f"Bonificado {unidades_bonificadas} de {item.articulo.nombre_articulo}")