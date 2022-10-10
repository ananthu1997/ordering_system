from flask import Flask
from flask import request, jsonify
from pymongo import MongoClient, UpdateOne
from datetime import date

today = date.today()

cluster = MongoClient("mongodb+srv://ananthu:tlLaA4MvkMGFTnXA@cluster0.j1riy.mongodb.net/?retryWrites=true&w=majority")

db = cluster["Delivery"]
collection = db["delivery_system"]

db_1 = cluster["Logistics"]
collection_1 = db_1["logistic_system"]

app = Flask(__name__)


@app.route("/getDeliveryStatus", methods=["GET"])
def get_delivery_status():
    """
    Method to fetch the delivery status for all the customers
    """
    delivery_status = list(collection.find({}))
    if delivery_status:
        return jsonify(delivery_status)
    else:
        return "There is no delivery status to be pending for any orders", 200


@app.route("/getDeliveryById/<int:cust_id>", methods=["GET"])
def get_delivery_status_by_id(cust_id):
    """
    Method to fetch the delivery status for individual customer by their customer Id
    """
    delivery_status = collection.find_one({"customer_id": cust_id})
    if delivery_status:
        return jsonify(delivery_status)
    else:
        return f"There is no delivery status to be pending for the CustomerId {cust_id}", 200


@app.route("/updateDeliveryStatus", methods=["POST"])
def update_delivery_status():
    """
    Method to update delivery status for each order based on customerId
    """
    request_payload = request.json
    delivery_data = request_payload["delivery_info"]
    delivery_info = list(collection.find({}))
    delivery_cust_ids = [data["customer_id"] for data in delivery_info]
    logistics_info = list(collection_1.find({}))
    logistic_data = {data["customer_id"]: data for data in logistics_info}
    update_queries = []
    for data in delivery_data:
        if data["customer_id"] in delivery_cust_ids:
            if logistic_data[data["customer_id"]]["expected_date"] == today.strftime("%b-%d-%Y"):
                query = {"customer_id": data["customer_id"]}
                param = {"$set": {"status": "Order is out for delivery and will be arriving today"}}
                update_queries.append({"query": query, "params": param})
            else:
                query = {"customer_id": data["customer_id"]}
                param = {"$set": {
                    "status": f"Order is shipped and will be arriving by {logistic_data[data['customer_id']]['expected_date']}"}}
                update_queries.append({"query": query, "params": param})
        else:
            return f"There is no customerId {data['customer_id']} present in the Delivery Data", 200
    update_queries = [
        UpdateOne(query["query"], query["params"], upsert=False) for query in update_queries
    ]
    collection.bulk_write(update_queries, ordered=False)
    return "Successfully updated the Delivery Status for orders", 200


@app.route("/updateLogisticData", methods=["POST"])
def update_logistics_data():
    """
    Method to update logistics data for each order based on the customerId
    """
    request_payload = request.json
    logistic_data = request_payload["logistic_info"]
    delivery_info = list(collection.find({}))
    update_queries = []
    delivery_cust_ids = [id["customer_id"] for id in delivery_info]
    for data in logistic_data:
        if data["customer_id"] in delivery_cust_ids:
            query = {"customer_id": data["customer_id"]}
            param = {"$set": {"location": data["location"], "expected_date": data["expected_date"]}}
            update_queries.append({"query": query, "params": param})
        else:
            return f"There is no customerId {data['customer_id']} present in the logistic data", 200
    update_queries = [
        UpdateOne(query["query"], query["params"], upsert=False) for query in update_queries
    ]
    collection_1.bulk_write(update_queries, ordered=False)
    return "Successfully updated the Logistic data for orders", 200


if __name__ == "__main__":
    app.run(debug=True, port=5002, host="0.0.0.0")
