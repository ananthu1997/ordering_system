from unittest import mock
from src.client.app import *
from copy import deepcopy
import requests

customer_details = {
    "_id": 1,
    "customer_id": 1,
    "customer_name": "Ananthu",
    "customer_address": "Bangalore",
    "orders": [
        {
            "item_id": 1,
            "order_name": "Laptop",
            "quantity": 2,
            "Price": 10000
        },
        {
            "item_id": 2,
            "order_name": "Mobile",
            "quantity": 2,
            "Price": 1000
        }
    ],
    "Amount to be paid": 22000,
    "Status": "Transaction has been completed and order is confirmed",
    "order_id": "KAJmj7O2TGhoJ1dE"
}

item_details = {
    "item_info": [
        {
            "item_id": 1,
            "item_name": "Laptop",
            "item_price": "20000",
            "total_quantity": 1000
        },
        {
            "item_id": 2,
            "item_name": "Mobile",
            "item_price": "10000",
            "total_quantity": 1000
        }
    ]
}

request_payload = {
    "order_details": {
        "customer_info": {
            "customer_id": 1,
            "customer_address": "bangalore",
            "customer_name": "Ananthu",
            "orders": [
                {
                    "item_id": 1,
                    "order_name": "laptop",
                    "quantity": 2,
                    "Price": 10000
                },
                {
                    "item_id": 2,
                    "order_name": "mobile_phone",
                    "quantity": 1,
                    "Price": 1000
                }
            ]
        }
    }
}

request_payload_1 = {
    "order_details": {
        "customer_info": {
            "customer_id": 2,
            "customer_address": "Bangalore",
            "customer_name": "Ajayan",
            "orders": [
                {
                    "item_id": 1,
                    "order_name": "laptop",
                    "quantity": 2,
                    "Price": 10000
                },
                {
                    "item_id": 2,
                    "order_name": "mobile_phone",
                    "quantity": 1,
                    "Price": 1000
                }
            ]
        }
    }
}

request_payload_delete = {
    "customer_id": 1,
    "orders": [
        {
            "item_id": 1,
            "order_name": "laptop",
            "quantity": 2,
            "Price": 10000
        },
        {
            "item_id": 2,
            "order_name": "mobile_phone",
            "quantity": 1,
            "Price": 1000
        }
    ]
}

success_response_code = 200


@mock.patch("pymongo.collection.Collection.find")
def test_get_all_customer_info_success(mock_find):
    """
    Testcase for success scenario for fetching customer info
    """
    mock_find.return_value = [customer_details]
    with app.app_context():
        customer = get_all_customer_info()
        assert success_response_code == customer.status_code


@mock.patch("pymongo.collection.Collection.find")
def test_get_all_customer_info_failure(mock_find):
    """
    Testcase for negative scenario for fetching customer info
    """
    mock_find.return_value = []
    with app.app_context():
        customer, status = get_all_customer_info()
        assert success_response_code == status


def test_add_customer():
    """
    TC to check whether new customer is added
    """
    response = requests.post("http://127.0.0.1:5000/addCustomer", json=request_payload)
    assert response.status_code == 200


def test_add_customer_case1():
    """
    TC to check whether new customer is added
    """
    response = requests.post("http://127.0.0.1:5000/addCustomer", json=request_payload_1)
    assert response.status_code == 200


def test_delete_orders():
    """
    TC to check whether existing customer is deleted
    """
    response = requests.delete("http://127.0.0.1:5000/deleteOrders", json=request_payload_delete)
    assert response.text == "Successfully deleted the items for customerId 1"
    assert response.status_code == 200


def test_delete_orders_case_1():
    """
    TC to check whether the failure response is return when invalid customer Id is given
    """
    request_payload_delete_error = deepcopy(request_payload_delete)
    request_payload_delete_error["customer_id"] = 3
    response = requests.delete("http://127.0.0.1:5000/deleteOrders", json=request_payload_delete_error)
    assert response.status_code == 400
    assert response.text == "Failed to delete the items for customerId 3"


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_customer_id_success(mock_find):
    """
    Testcase for success scenario for fetching individual customer info
    """
    mock_find.return_value = customer_details
    with app.app_context():
        message, status = get_customer_id(1)
        assert success_response_code == status


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_customer_id_failure(mock_find):
    """
    Testcase for negative scenario for fetching individual customer info
    """
    mock_find.return_value = {}
    expected_message = "Customer Id 1 not found"
    with app.app_context():
        message, status = get_customer_id(1)
        assert expected_message == message
        assert success_response_code == status
