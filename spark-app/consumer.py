import argparse

from utils import config
from utils.schemas import schemas
from utils.transform import transform
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', help='Topic Name')
    parser.add_argument('-tw', '--table', help='Postgres Table')

    args = parser.parse_args()
    return args

def postgres_sink(df, table):
    postgres_cfg = config.get("postgres")

    url = f"jdbc:postgresql://{postgres_cfg['host']}:{postgres_cfg['port']}/{postgres_cfg['database']}"
    df.write.format(postgres_cfg['format']) \
        .option("url", url) \
        .option("dbtable", table) \
        .option("user", postgres_cfg['user']) \
        .option("password", postgres_cfg['password']) \
        .option("driver", postgres_cfg['driver']) \
        .mode('append') \
        .save()

def foreach_batch_function(df, epoch_id, table):
    postgres_sink(df, table)

if __name__ == '__main__':
    args = get_arguments()
    topic = args.topic
    table = args.table

    kafka_cfg = config.get('kafka')
    schema = schemas[topic]

    spark = SparkSession.builder \
        .appName("KafkaSparkConsumer") \
        .getOrCreate()

    
    spark.sparkContext.setLogLevel("DEBUG")

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_cfg["url"]) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load()
    
    data = df.select(
        from_json(
            col("value").cast("string"), schema
        ).alias("value")
    )

    cleaned_data = transform[topic](data)
    cleaned_data.printSchema()

    # Load
    writeStream = cleaned_data \
        .writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: foreach_batch_function(df, epoch_id, table)) \
        .start()
    
    writeStream.awaitTermination()


