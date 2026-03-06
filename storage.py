import json
import os
from models import Product, Category, Supplier

#products

PRODUCT_NAME = "inventory.json"


def save_products(products):
    with open(PRODUCT_NAME, "w") as file:
        json.dump([p.to_dict() for p in products], file, indent=4)


def load_products():
    if not os.path.exists(PRODUCT_NAME):
        return []

    try:
        with open(PRODUCT_NAME, "r") as file:
            data = json.load(file)
        return [Product.from_dict(item) for item in data]

    except (json.JSONDecodeError, KeyError):
        print("Warning: inventory data file is corrupted. Starting fresh.")
        return []
    
#category

CATEGORY_NAME = "category.json"


def save_categories(categories):
    with open(CATEGORY_NAME, "w") as file:
        json.dump([c.to_dict() for c in categories], file, indent=4)


def load_categories():
    if not os.path.exists(CATEGORY_NAME):
        return []

    try:
        with open(CATEGORY_NAME, "r") as file:
            data = json.load(file)
        return [Category.from_dict(item) for item in data]

    except (json.JSONDecodeError, KeyError):
        print("Warning: category data file is corrupted. Starting fresh.")
        return []
    
#Supplier 

SUPPLIER_NAME = "supplier.json"


def save_suppliers(suppliers):
    with open(SUPPLIER_NAME, "w") as file:
        json.dump([s.to_dict() for s in suppliers], file, indent=4)


def load_suppliers():
    if not os.path.exists(SUPPLIER_NAME):
        return []

    try:
        with open(SUPPLIER_NAME, "r") as file:
            data = json.load(file)
        return [Supplier.from_dict(item) for item in data]

    except (json.JSONDecodeError, KeyError):
        print("Warning: supplier data file is corrupted. Starting fresh.")
        return []