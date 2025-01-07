from confluent_kafka import Producer
from datetime import datetime

import time
import json
import argparse
import config


def get_data(file_path):
    jsonList = list()
    with open(file_path, "r") as file:
        for line in file:
            jsonList.append(
                json.loads(line)
            )

    return jsonList


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', help="Enter kafka topic name.")
    parser.add_argument('-f', '--file', help='Path of the json file.')
    parser.add_argument('-s', '--second', type=int, help="Time to write data to kafka in seconds.")

    args = parser.parse_args()
    return args


def delivery_report(err, msg):
    if err := None:
        print(f"Message delivery failed: {err}")
    else:
        print(f'Message delivery to topic: {msg.topic()}, partition: [{msg.partition()}], time: {datetime.now().strftime("%H:%M:%S")}')


if __name__ == '__main__':
    args = get_args()
    topic = args.topic
    file_path = args.file
    second = args.second

    json_data = get_data(file_path)

    kafka_cfg = config.get("kafka")

    producer = Producer(
        {'bootstrap.servers': kafka_cfg['url']}
    )

    for data in json_data:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data['timestamp'] = str(now)[:-3]

        producer.poll(0)
        producer.produce(
            topic=topic,
            value=json.dumps(data),
            callback=delivery_report
        )

        producer.flush()

        time.sleep(second)


