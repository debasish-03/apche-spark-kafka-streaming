from pyspark.sql.functions import (
    col,
    split,
    explode,
    to_timestamp,
    lit
)



def product_transform(data):
    userid = split(data['value']['userid'], '-')
    productid = split(data['value']['properties']['productid'], '-')

    products = data.select(
        userid.getItem(1).alias("userid").cast("integer"),
        productid.getItem(1).alias("productid").cast("integer"),
        data['value']['context']['source'].alias("source"),
        to_timestamp(lit(data['value']['timestamp']), 'MM-dd-yyyy HH:mm:ss.SSSS').alias("timestamp")
    )

    return products


def order_transform(data):
    userid = split(data['value']['userid'], '-')
    products_line_by_line = data.select(
        data['value']['orderid'].alias("orderid"), 
        userid.getItem(1).alias("userid"), 
        explode(data['value']['lineitems']).alias('products_line_by_line'),
        to_timestamp(lit(data['value']['timestamp']),'MM-dd-yyyy HH:mm:ss.SSSS').alias('timestamp')
    )

    product = split(products_line_by_line['products_line_by_line']['productid'], '-')

    cleaning_data = products_line_by_line.select(
        'orderid', 
        col('userid').cast('integer'), 
        product.getItem(1).alias('productid').cast('integer'), 
        products_line_by_line['products_line_by_line']['quantity'].alias("quantity"),
        'timestamp'
    )

    return cleaning_data

transform = {
    'product': product_transform,
    'order': order_transform
}