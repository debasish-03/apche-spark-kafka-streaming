#!/bin/bash

# Function to check if a container is ready
check_container() {
    container_name=$1
    docker ps --filter "name=$container_name" --filter "status=running" | grep $container_name > /dev/null
    return $?
}

# Function to wait for a service
wait_for_service() {
    service_name=$1
    max_attempts=30
    attempt=1

    echo "Waiting for $service_name to be ready..."
    while ! check_container $service_name
    do
        if [ $attempt -eq $max_attempts ]; then
            echo "$service_name failed to start after $max_attempts attempts"
            exit 1
        fi
        echo "Attempt $attempt: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo "$service_name is ready!"
}

# Start all services
echo "Starting services..."
docker-compose up -d

# Wait for essential services
wait_for_service "zookeeper"
wait_for_service "kafka"
wait_for_service "postgres"
wait_for_service "spark-master"
wait_for_service "spark-worker"
wait_for_service "spark-app"

# Function to create a Kafka topic if it doesn't exist
create_topic_if_not_exists() {
    topic_name=$1
    topic_exists=$(docker exec kafka kafka-topics --list --bootstrap-server kafka:9093 2>/dev/null | grep "^$topic_name$")

    if [ -z "$topic_exists" ]; then
        echo "Creating Kafka topic: $topic_name"
        docker exec kafka kafka-topics --create \
            --bootstrap-server kafka:9093 \
            --replication-factor 1 \
            --partitions 1 \
            --topic $topic_name
    else
        echo "Kafka topic '$topic_name' already exists"
    fi
}

# Check and create topics
echo "Checking and creating Kafka topics..."
create_topic_if_not_exists "product"
create_topic_if_not_exists "order"




