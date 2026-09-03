KAFKA_BOOTSTRAP_SERVERS = "localhost:19092"

CDC_TOPICS = [
    "food_delivery.app.orders",
    "food_delivery.app.order_items",
    "food_delivery.app.deliveries",
]

CDC_CONSUMER_GROUP_ID = "food-delivery-raw-writer"