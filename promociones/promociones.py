from .models import  PromocionArticulo, ItemNotaVenta

def aplicar_promociones(notaventa,item=None):
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
                aplicar_promocion_unidad(notaventa, item, promocion,bonificacion_unidades)
   
            elif tipo_promocion == 'soles':
                aplicar_promocion_soles(notaventa, item, promocion,bonificacion_unidades,descuento)
    return None

def aplicar_promocion_unidad(notaventa, item, promocion, bonificacion_unidades):
    cantidad_adquirida = item.cantidad
    cantidad_promocion = promocion.promocion_id.limite
    bonificacion_unidades = bonificacion_unidades

    unidades_b = cantidad_adquirida // cantidad_promocion
    unidades_bonificada = unidades_b * bonificacion_unidades

    if unidades_bonificada > item.cantidad:
        unidades_bonificada = item.cantidad

    if unidades_bonificada > 0:
        # Buscar registros existentes para el mismo artículo y nota de venta
        item_principal = ItemNotaVenta.objects.filter(
            nota_venta=notaventa,
            articulo=item.articulo,
            promocion_aplicada=promocion.promocion_id,
            es_bonificacion=True  # Asegúrate de seleccionar el item principal y no la bonificación
        )

        if item_principal.exists():
            # Si ya existe, actualizar la cantidad
            item_bonificado = item_principal.first()
            item_bonificado.cantidad += unidades_bonificada
            item_bonificado.save()
        else:
            # Si no existe, crear uno nuevo para el item principal
            ItemNotaVenta.objects.create(
                nota_venta=notaventa,
                articulo=item.articulo,
                promocion_aplicada=promocion.promocion_id,
                cantidad=cantidad_adquirida,  # Usar la cantidad del artículo principal
                precio_unitario=item.precio_unitario,
                total_item_bruto=item.total_item_bruto,
                es_bonificacion=False  # No es bonificación
            )

        print(f"Bonificado {unidades_bonificada} de {item.articulo.nombre_articulo}")

    # Asignar la promoción aplicada al item original
    item.promocion_aplicada = promocion.promocion_id
    item.save()

    return promocion.promocion_id  # Devuelve la promoción aplicada

        
def aplicar_promocion_soles(venta, item, promocion,articulo_bonificado):
    monto_limite = promocion.monto

    if venta.total_pedido >= monto_limite:
        unidades_bonificadas = promocion.bonificacion_unidades

        item_bonificado = ItemNotaVenta()
        item_bonificado.nota_venta = venta
        item_bonificado.articulo = articulo_bonificado
        item_bonificado.cantidad = unidades_bonificadas
        item_bonificado.precio_unitario = 0
        item_bonificado.total_item_bruto = 0
        item_bonificado.save()

        print(f"Bonificado {unidades_bonificadas} de {item.articulo.nombre_articulo}")
