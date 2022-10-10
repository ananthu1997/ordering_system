from unittest import mock
from src.delivery.app import *
from unittest.mock import patch
import requests

success_response_code = 200
negative_response_code = 400

delivery_details = {
    "_id": 1,
    "customer_id": 1,
    "order_id": "3LLmjGnaYu254qPe",
    "orders": [
        {
            "item_id": 1,
            "order_name": "Laptop",
            "quantity": 2,
            "Price": 10000
        }
    ],
    "status": "Your Order for 3LLmjGnaYu254qPe has been placed in the queue"
}

request_payload = {
    "logistic_info": [
        {
            "customer_id": 1,
            "order_id": "WBYC9umlEP0yZiSf",
            "location": "bangalore",
            "expected_date": "Oct-10-2022"
        }
    ]
}

request_payload_1 = {
    "logistic_info": [
        {
            "customer_id": 3,
            "order_id": "WBYC9umlEP0yZiSf",
            "location": "bangalore",
            "expected_date": "Oct-10-2022"
        }
    ]
}

request_payload_2 = {
    "delivery_info": [
        {
            "customer_id": 1,
            "order_id": "WBYC9umlEP0yZiSf",
            "location": "bangalore",
            "expected_date": "Oct-19-2022"
        }
    ]
}

request_payload_3 = {
    "delivery_info": [
        {
            "customer_id": 3,
            "order_id": "WBYC9umlEP0yZiSf",
            "location": "bangalore",
            "expected_date": "Oct-19-2022"
        }
    ]
}


@mock.patch("pymongo.collection.Collection.find")
def test_get_all_items_info_success(mock_find):
    """
    Testcase for success scenario for fetching delivery Item status
    """
    mock_find.return_value = [delivery_details]
    with app.app_context():
        customer = get_delivery_status()
        assert success_response_code == customer.status_code


@mock.patch("pymongo.collection.Collection.find")
def test_get_all_items_info_failure(mock_find):
    """
    Testcase for negative scenario for fetching delivery Item status
    """
    mock_find.return_value = {}
    with app.app_context():
        customer, status = get_delivery_status()
        assert success_response_code == status
        assert customer == "There is no delivery status to be pending for any orders"


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_delivery_status_by_id_success(mock_find):
    """
    Testcase for success scenario for fetching individual order status
    """
    mock_find.return_value = delivery_details
    with app.app_context():
        customer = get_delivery_status()
        assert success_response_code == customer.status_code


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_delivery_status_by_id_failure(mock_find):
    """
    Testcase for negative scenario for fetching individual order status
    """
    mock_find.return_value = {}
    with app.app_context():
        customer = get_delivery_status()
        assert success_response_code == customer.status_code


def test_update_logistics_data():
    """
    TC to check whether logistic data is updated
    """
    response = requests.post("http://127.0.0.1:5002/updateLogisticData", json=request_payload)
    assert response.status_code == 200
    assert response.text == "Successfully updated the Logistic data for orders"


def test_update_logistics_data_case_1():
    """
    TC to check whether logistic data is not updated when invalid customer Id is given
    """
    response = requests.post("http://127.0.0.1:5002/updateLogisticData", json=request_payload_1)
    assert response.status_code == 200
    assert response.text == "There is no customerId 3 present in the logistic data"


def test_update_delivery_status():
    """
    TC to check whether delivery status data is updated
    """
    response = requests.post("http://127.0.0.1:5002/updateDeliveryStatus", json=request_payload_2)
    assert response.status_code == 200
    assert response.text == "Successfully updated the Delivery Status for orders"


def test_update_delivery_status_case_1():
    """
    TC to check whether delivery status data is not updated when invalid customer Id is given
    """
    response = requests.post("http://127.0.0.1:5002/updateDeliveryStatus", json=request_payload_3)
    assert response.status_code == 200
    assert response.text == "There is no customerId 3 present in the Delivery Data"
