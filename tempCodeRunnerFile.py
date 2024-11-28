@app.route('/locationvp', methods=['GET'])
def ubicacion_pv():
    

        # Obtener el índice del producto desde el parámetro de consulta
    result = exec_mostar_tienda()
    productid_str = request.args.get('productid')# Por defecto, 0
    productid = int(productid_str)
    producto_seleccionado = result[productid]
    pointid = producto_seleccionado['IDPV']
    print(f"Pointid:{pointid}")
    intpointid = int(pointid)
    
    products = get_products_by_point_id(intpointid)

    # Pasar todos los productos y el producto seleccionado al template
    return render_template('seller_location.html',Producto=producto_seleccionado,productseller=products)
