# api.py
from flask import Flask, jsonify
import redis
from config import REDIS_HOST, REDIS_PORT
import json

app = Flask(__name__)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

@app.route('/orders', methods=['GET'])
def get_orders():
    # Get all orders from Redis
    orders = []
    for key in redis_client.keys("order:*"):
        order_data = redis_client.get(key)
        if order_data:
            orders.append(json.loads(order_data))
    return jsonify(orders)

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    # Get specific order from Redis
    order_data = redis_client.get(f"order:{order_id}")
    if order_data:
        return jsonify(json.loads(order_data))
    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
