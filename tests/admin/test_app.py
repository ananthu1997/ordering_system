from unittest import mock
from src.admin.app import *
from unittest.mock import patch
import requests

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

request_payload_1 = {
    "item_info": [
        {
            "item_id": 3,
            "item_name": "Headset",
            "item_price": "9000",
            "total_quantity": 12000
        },
        {
            "item_id": 4,
            "item_name": "Earpods",
            "item_price": "1270",
            "total_quantity": 899
        }
    ]
}

request_payload_2 = {
    "item_info": [
        {
            "item_id": 5,
            "item_name": "TV",
            "item_price": "100000",
            "total_quantity": 100
        }
    ]
}

success_response_code = 200


@mock.patch("pymongo.collection.Collection.find")
def test_get_all_items_info_success(mock_find):
    """
    Testcase for success scenario for fetching Item info
    """
    mock_find.return_value = [item_details]
    with app.app_context():
        customer = get_items_info()
        assert success_response_code == customer.status_code


@mock.patch("pymongo.collection.Collection.find")
def test_get_all_items_info_failure(mock_find):
    """
    Testcase for negative scenario for fetching Item info
    """
    mock_find.return_value = []
    with app.app_context():
        customer, status = get_items_info()
        assert success_response_code == status
        assert customer == "No items in found in the Stock"


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_items_info_by_id_success(mock_find):
    """
    Testcase for success scenario for fetching individual Item info
    """
    mock_find.return_value = item_details
    with app.app_context():
        customer = get_items_info_by_id(1)
        assert success_response_code == customer.status_code


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_items_info_by_id_failure(mock_find):
    """
    Testcase for negative scenario for fetching individual Item info
    """
    mock_find.return_value = {}
    with app.app_context():
        customer = get_items_info_by_id(1)
        assert success_response_code == customer[1]
        assert customer[0] == "There is no Item with ItemId 1 in the Stock"


@mock.patch("pymongo.collection.Collection.find_one")
def test_get_items_info_by_id_failure_1(mock_find):
    """
    Testcase for negative scenario for fetching individual Item info
    """
    mock_find.return_value = item_details
    with app.app_context():
        customer = get_items_info_by_id(3)
        assert success_response_code == customer.status_code


def test_add_Items():
    """
    Testcase to check whether item is added to Item List
    """
    response = requests.post("http://127.0.0.1:5001/addItems", json=request_payload)
    assert response.status_code == 200
    assert response.text == "Successfully added items to the stock"


def test_add_Items_case_1():
    """
    Testcase to check whether item is updated to Item List
    """
    response = requests.post("http://127.0.0.1:5001/addItems", json=request_payload_1)
    assert response.status_code == 200
    assert response.text == "Successfully added items to the stock"


def test_delete_Items():
    """
    Testcase to check whether item is deleted from Item List
    """
    response = requests.delete("http://127.0.0.1:5001/deleteItems", json=request_payload)
    assert response.status_code == 200
    assert response.text == "Successfully Deleted items present in the stock"


def test_delete_Items_case_1():
    """
    Testcase to check whether failure response is occured when invalid itemId is given
    """
    response = requests.delete("http://127.0.0.1:5001/deleteItems", json=request_payload_2)
    assert response.status_code == 200
    assert response.text == "Item cannot be deleted since there was no itemId 5 in the stock"
