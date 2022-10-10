from flask import Flask
from flask import request, jsonify
from pymongo import MongoClient, UpdateMany
import random, string
from datetime import date

today = date.today()

cluster = MongoClient("mongodb+srv://ananthu:tlLaA4MvkMGFTnXA@cluster0.j1riy.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Retail"]
collection = db["online_ordering_system"]

db_1 = cluster["Admins"]
collection_1 = db_1["admin_system"]

db_2 = cluster["Delivery"]
collection_2 = db_2["delivery_system"]

db_3 = cluster["Logistics"]
collection_3 = db_3["logistic_system"]

app = Flask(__name__)


@app.route("/custInfo", methods=["GET"])
def get_all_customer_info():
    """
    Method for Fetching all the customer info present in the record
    """
    all_customer = list(collection.find({}))
    if all_customer:
        return jsonify(all_customer)
    else:
        return "Customer Info not found", 200


@app.route("/addCustomer", methods=["POST"])
def add_customer():
    """
    Method for Adding/Updating the customer order details
    """
    request_payload = request.json
    customer = request_payload["order_details"]["customer_info"]
    order_details = request_payload["order_details"]["customer_info"]
    item_ids = [order["item_id"] for order in order_details["orders"]]
    updated_count, updated_amount, total_price = 0, 0, 0
    query, param = {}, {}
    update_queries, update_queries_1 = [], []
    existing_items = list(collection_1.find({}))
    existing_items_id = [item["item_id"] for item in existing_items]
    existing_customer = collection.find_one({"customer_id": customer["customer_id"]})
    if existing_customer:
        get_update_queries(customer["customer_id"], existing_customer, item_ids, order_details, update_queries,
                           existing_items_id)
        update_queries = [
            UpdateMany(query["query"], query["params"], upsert=False) for query in update_queries
        ]
        collection.bulk_write(update_queries, ordered=False)
    else:
        for order in order_details["orders"]:
            if order["item_id"] in existing_items_id:
                total_price = total_price + (order["Price"] * order["quantity"])
            else:
                return f"Item with itemId {order['item_id']} is not present in the stock", 200
        customer.update(
            {"_id": customer["customer_id"], "customer_id": customer["customer_id"], "Amount to be paid": total_price,
             "Status": "Order has been placed in the cart",
             "order_id": ''.join(
                 random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                 range(16))})
        collection.insert_one(customer)
    return "Successfully Added the customer", 200


def update_item_details(customer, existing_items, update_queries):
    """
    Method for deleting the total quantity from the Item list
    """
    existing_customer = collection.find_one({"customer_id": customer})
    existing_item_details = {order["item_id"]: order for order in existing_customer["orders"]}
    for item in existing_items:
        if item["item_id"] in existing_item_details:
            updated_count = int(item["total_quantity"]) - int(existing_item_details[item["item_id"]]["quantity"])
            query = {"item_id": item["item_id"]}
            param = {"$set": {f"total_quantity": updated_count}}
            update_queries.append({"query": query, "params": param})
    update_queries = [
        UpdateMany(query["query"], query["params"], upsert=False) for query in update_queries
    ]
    collection_1.bulk_write(update_queries, ordered=False)


@app.route("/custInfo/<int:custId>", methods=["GET"])
def get_customer_id(custId):
    """
    Method for fetching individual customer order details by passing the customer Id
    """
    customer = collection.find_one({"customer_id": custId})
    if customer:
        return jsonify(customer), 200
    else:
        return f"Customer Id {custId} not found", 200


@app.route("/transaction", methods=["POST"])
def post_transactions():
    """
    Method for posting the transaction for each order added by customer
    """
    request_payload = request.json
    customer_id = request_payload["customer_id"]
    existing_items = list(collection_1.find({}))
    update_queries = []
    customer = collection.find_one({"customer_id": customer_id})
    if customer and customer["Amount to be paid"] != 0:
        collection.update_one({"customer_id": customer_id}, {
            "$set": {"Amount to be paid": 0, "Status": "Transaction has been completed and order is confirmed"}})
        update_item_details(customer_id, existing_items, update_queries)
        collection_2.insert_one(
            {"_id": customer_id, "customer_id": customer_id, "order_id": customer["order_id"],
             "orders": customer["orders"],
             "status": f"Your Order for {customer['order_id']} has been placed in the queue"})
        collection_3.insert_one(
            {"_id": customer_id, "customer_id": customer_id, "customer_address": customer["customer_address"],
             "order_id": customer["order_id"], "orders": customer["orders"], "date": today.strftime("%b-%d-%Y")})
    else:
        return f"Customer Id {customer_id} not found and transaction is failed or transacton has been already completed", 200
    return f"Transaction was successfully completed for customerId {customer_id}", 200


@app.route("/updateItems/<int:custId>", methods=["PATCH"])
def update_orders(cust_id):
    """
    Method for adding/updating customer oder details
    """
    request_payload = request.json
    customer_id = request_payload["customer_id"]
    item_ids = [id["item_id"] for id in request_payload["orders"]]
    updated_count, updated_amount, Total_price = 0, 0, 0
    query, param = {}, {}
    update_queries, update_queries_1 = [], []
    existing_items = list(collection_1.find({}))
    existing_items_id = [item["item_id"] for item in existing_items]
    existing_customer = collection.find_one({"customer_id": cust_id})
    if existing_customer:
        get_update_queries(customer_id, existing_customer, item_ids, request_payload, update_queries)
        update_queries = [
            UpdateMany(query["query"], query["params"], upsert=False) for query in update_queries
        ]
        collection.bulk_write(update_queries, ordered=False)
        return f"Successfully update the items for customerId {customer_id}", 200
    else:
        return f"Failed to update the items for customerId {customer_id}", 200


@app.route("/deleteOrders", methods=["DELETE"])
def delete_orders():
    """
    Method for deleting orders placed by customer
    """
    request_payload = request.json
    customer_id = request_payload["customer_id"]
    if not request_payload["orders"]:
        return "Customer has not given any orders to be deleted", 200
    item_ids = [id["item_id"] for id in request_payload["orders"]]
    updated_count, updated_amount = 0, 0
    query, param = {}, {}
    update_queries = []
    existing_customer = collection.find_one({"customer_id": customer_id})
    if existing_customer:
        customer_orders = {order["item_id"]: order for order in request_payload["orders"]}
        updated_amount = 0
        for index, order in enumerate(existing_customer["orders"]):
            if order["item_id"] in item_ids:
                if customer_orders[order["item_id"]]["quantity"] > order["quantity"]:
                    return f"Total number of items for the deletion has been exceeded or item is not present in the cart", 200
                updated_count = abs(customer_orders[order["item_id"]]["quantity"] - order["quantity"])
                updated_amount = updated_amount + (
                        customer_orders[order["item_id"]]["Price"] *
                        customer_orders[order["item_id"]]["quantity"])
                query = {"_id": customer_id}
                param = {"$set": {f"orders.{index}.quantity": updated_count,
                                  "Amount to be paid": abs(
                                      int(existing_customer["Amount to be paid"]) - updated_amount)},
                         }
                update_queries.append({"query": query, "params": param})

        update_queries = [
            UpdateMany(query["query"], query["params"], upsert=False) for query in update_queries
        ]
        collection.bulk_write(update_queries, ordered=False)
        existing_customer = collection.find_one({"customer_id": customer_id})
        if existing_customer["Amount to be paid"] == 0:
            collection.delete_one({"customer_id": customer_id})
        return f"Successfully deleted the items for customerId {customer_id}", 200
    else:
        return f"Failed to delete the items for customerId {customer_id}", 400


def get_update_queries(customer_id, existing_customer, item_ids, request_payload, update_queries, existing_items_id):
    """
    Method to update the quantity and amount for each order placed by customer
    """
    existing_item_id = [order["item_id"] for order in existing_customer["orders"]]
    customer_orders = {order["item_id"]: order for order in request_payload["orders"]}
    updated_amount = 0
    for index, order in enumerate(existing_customer["orders"]):
        if order["item_id"] in item_ids:
            updated_count = int(customer_orders[order["item_id"]]["quantity"]) + int(order["quantity"])
            updated_amount = updated_amount + (
                    customer_orders[order["item_id"]]["Price"] *
                    customer_orders[order["item_id"]]["quantity"])
            query = {"customer_id": customer_id}
            param = {"$set": {f"orders.{index}.quantity": updated_count,
                              "Amount to be paid": int(existing_customer["Amount to be paid"]) + updated_amount},
                     }
            update_queries.append({"query": query, "params": param})
    for order in request_payload["orders"]:
        if order["item_id"] not in existing_item_id and order["item_id"] in existing_items_id:
            updated_amount = updated_amount + (order["Price"]) * int(order["quantity"])
            query = {"cutomer_id": customer_id}
            param = {"$set": {"Amount to be paid": int(existing_customer["Amount to be paid"]) + updated_amount},
                     "$push": {"orders": order}}
            update_queries.append({"query": query, "params": param})


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
