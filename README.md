# ordering_system
Retail Ordering System Back-end implementation

This is a Retail ordering System for the users to place the order depending upon on the item availability 
and post the transaction for the selected orders. It is developed using python with flask as the framework
and MongoDB as the database the store the order info for each users


FILES

src/client/app.py - Allows users to place the order based on the item availability in stock, they can also update or delete any orders to the current order details.
after placing the order it also enables the customer to complete the transaction and view the status of there order.

src/admin/app.py - Allows admin to add items to the item List, updates it and also delete the items which are not there in the stock. Admins can also view the 
items available in the stock . It allows the users to view the items in the stock

src/delivery/app.py - Allows admin to update the logistics data along with delivery status for each orders ,admins can also view all the delivery status pending. 
It allows the users to view their delivery details based on the customer ids

tests/client/app.py - Testcase for src/client/app.py

tests/admin/app.py - Testcase for src/admin/app.py

tests/delivery/app.py - Testcase for src/delivery/app.py

UML

![uml](https://user-images.githubusercontent.com/31721523/194814300-07601290-01a3-49f0-b28d-7dffafce9663.png)
