import psycopg2
import os
from flask import jsonify
import json
from datetime import datetime, timedelta


# Parámetros de conexión
dbname = "postgres"
user = "mrodriguez"
password = os.environ['POS_SECRET']
host = "dbmelt.cpqssd8fh2nq.us-east-1.rds.amazonaws.com"  # O la dirección IP del servidor
port = "5432"  # Puerto por defecto de PostgreSQL



def get_order_data(order_id):

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )



    hoy = datetime.today()
    antiayer = hoy - timedelta(days=1)

    fecha_inicio = datetime.strftime(antiayer, '%Y-%m-%d')
    fecha_fin = datetime.strftime(hoy, '%Y-%m-%d')

    query = """
    SELECT order_detail
    FROM order_converter
    WHERE ("createdAt" BETWEEN '{fecha_inicio}' AND '{fecha_fin}')
    AND order_detail::json ->> 'ReferenceNumber' = '{order_id}'
    """.format(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, order_id=order_id)

    print(query)



    cursor = conn.cursor()

    inicio_query = datetime.now()


    cursor.execute(query, (order_id,))


    result = cursor.fetchone()
    fin_query = datetime.now()
    print("Tiempo de ejecución de la query: ", fin_query - inicio_query)
    try:
        result_json = json.loads(result[0])
    except:
        print('No se encontró un registro con orderId {0}'.format(order_id))
        result_json = None

    cursor.close()
    conn.close()


    return result_json

import re

def is_valid_order_id(order_id):
    pattern = re.compile(r'^M\d{12}$')
    return bool(pattern.match(order_id))

def order_info(request):
    request_json = request.get_json()

    if request.args and 'orderId' in request.args:
        order_id = request.args.get('orderId')
    elif request_json and 'orderId' in request_json:
        order_id = request_json['orderId']
    else:
        return jsonify({"error": "No se proporcionó un orderId"}), 400

    if not is_valid_order_id(order_id):
        return jsonify({"error": "El orderId proporcionado no tiene una estructura válida"}), 400

    order_id = order_id[1:]  # Eliminar la letra 'M' inicial

    order_data = get_order_data(order_id)

    if order_data:
        return jsonify(order_data)
    else:
        return jsonify({"error": f"No se encontró un registro con orderId {order_id}"}), 404



if __name__ == '__main__':
    print(get_order_data('1680047392879'))





