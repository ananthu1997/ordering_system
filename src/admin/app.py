from flask import Flask
from flask import request, jsonify
from pymongo import MongoClient, UpdateMany

cluster = MongoClient("mongodb+srv://ananthu:tlLaA4MvkMGFTnXA@cluster0.j1riy.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Retail"]
collection = db["online_ordering_system"]

db_1 = cluster["Admins"]
collection_1 = db_1["admin_system"]

app = Flask(__name__)


@app.route("/getItems", methods=["GET"])
def get_items_info():
    """
    Method to fetch all the items present in the Item list
    """
    all_items = list(collection_1.find({}))
    if all_items:
        return jsonify(all_items)
    else:
        return "No items in found in the Stock", 400


@app.route("/getItems/<int:item_id>", methods=["GET"])
def get_items_info_by_id(item_id):
    """
    Method to find individual item by its item_id
    """
    all_item = collection_1.find_one({"item_id": item_id})
    if all_item:
        return jsonify(all_item)
    return f"There is no Item with ItemId {item_id} in the Stock", 200


@app.route("/addItems", methods=["POST"])
def add_items():
    """
    Method to add items by the admins to update the Item List
    """
    request_payload = request.json
    items = request_payload["item_info"]
    existing_items = list(collection_1.find({}))
    insert_query = {"item_info": []}
    update_queries = []
    existing_item_ids = {item["item_id"]: item for item in existing_items if item}
    for item in items:
        if item["item_id"] in existing_item_ids:
            updated_count = int(item["total_quantity"]) + int(existing_item_ids[item["item_id"]]["total_quantity"])
            query = {"item_id": item["item_id"]}
            param = {"$set": {f"total_quantity": updated_count}}
            update_queries.append({"query": query, "params": param})
        else:
            item["_id"] = item["item_id"]
            insert_query["item_info"].append(item)
    if insert_query["item_info"]:
        collection_1.insert_many(insert_query["item_info"])
    if update_queries:
        update_queries = [
            UpdateMany(query["query"], query["params"], upsert=False) for query in update_queries
        ]
        # updates the items for the existing items
        collection_1.bulk_write(update_queries, ordered=False)
    if not insert_query["item_info"] and not update_queries:
        return "Addition to the items to the stock was failed", 200
    return "Successfully added items to the stock", 200


@app.route("/deleteItems", methods=["DELETE"])
def delete_items():
    """
    Method to delete items by the admins to update the Item List
    """
    request_payload = request.json
    items = request_payload["item_info"]
    existing_items = list(collection_1.find({}))
    update_queries = []
    if existing_items:
        existing_item_ids = {item["item_id"]: item for item in existing_items if item}
    else:
        return "There is no existing items present in the stock for deleting", 200
    for item in items:
        if item["item_id"] in existing_item_ids:
            updated_count = abs(int(item["total_quantity"]) - int(existing_item_ids[item["item_id"]]["total_quantity"]))
            query = {"item_id": item["item_id"]}
            param = {"$set": {f"total_quantity": updated_count}}
            update_queries.append({"query": query, "params": param})
        else:
            return f"Item cannot be deleted since there was no itemId {item['item_id']} in the stock", 200
    update_queries = [
        UpdateMany(query["query"], query["params"], upsert=False) for query in update_queries
    ]
    # updates the items for the existing items
    collection_1.bulk_write(update_queries, ordered=False)
    existing_items = list(collection_1.find({}))
    # delete the item in item DB when the total quantity is 0
    for item in existing_items:
        if item["total_quantity"] == 0:
            collection_1.delete_one({"item_id": item["item_id"]})
    return "Successfully Deleted items present in the stock", 200


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
