from datetime import datetime


class Product:
    def __init__(self, sku, name, price_per_unit, stock, min_stock, category_id=None, supplier_id=None):
        if not name.strip():
            raise ValueError("Product name cannot be empty.")
        if price_per_unit < 0:
            raise ValueError("Price cannot be negative.")
        if stock < 0:
            raise ValueError("Stock cannot be negative.")
        if min_stock < 0:
            raise ValueError("Minimum stock cannot be negative.")

        self.sku = sku
        self.name = name.strip().lower()
        self.price_per_unit = price_per_unit
        self.stock = stock
        self.min_stock = min_stock
        self.category_id = category_id
        self.supplier_id = supplier_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    # -------- Instance Methods --------

    def increase_stock(self, amount):
        if amount < 0:
            raise ValueError("Amount must be positive.")
        self.stock += amount
        self.updated_at = datetime.now().isoformat()

    def decrease_stock(self, amount):
        if amount > self.stock:
            raise ValueError("Cannot reduce stock below zero.")
        self.stock -= amount
        self.updated_at = datetime.now().isoformat()

    def is_low_stock(self):
        return self.stock <= self.min_stock

    def get_total_value(self):
        return self.stock * self.price_per_unit

    def apply_discount(self, percentage):
        if not (0 <= percentage <= 100):
            raise ValueError("Invalid discount percentage.")
        self.price_per_unit -= (percentage / 100) * self.price_per_unit
        self.updated_at = datetime.now().isoformat()

    # -------- Serialization --------

    def to_dict(self):
        return {
            "sku": self.sku,
            "name": self.name,
            "price_per_unit": self.price_per_unit,
            "stock": self.stock,
            "min_stock": self.min_stock,
            "category_id": self.category_id,
            "supplier_id": self.supplier_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        product = cls(
            data["sku"],
            data["name"],
            data["price_per_unit"],
            data["stock"],
            data["min_stock"],
            data.get("category_id"),
            data.get("supplier_id")
        )
        # Restore original timestamps — don't generate new ones
        product.created_at = data.get("created_at", product.created_at)
        product.updated_at = data.get("updated_at", product.updated_at)
        return product
    

class Category:
    def __init__(self, category_id, name):
        if not name.strip():
            raise ValueError("Category name cannot be empty.")
        self.category_id = category_id
        self.name = name

    def to_dict(self):
       return {
            "category_id": self.category_id,
            "name": self.name
        }

    @classmethod
    def from_dict(cls,data):
        return cls(
            data["category_id"],
            data["name"]
        )

class Supplier:
    def __init__(self, supplier_id, name, contact, lead_time):
        if not name.strip():
            raise ValueError("Supplier name cannot be empty.")
        if not contact:
            raise ValueError("Contact cannot be empty.")
        if lead_time < 0:
            raise ValueError("Lead time cannot be less than zero.")
        self.supplier_id = supplier_id
        self.name = name
        self.contact = contact
        self.lead_time = lead_time

    def is_fast_supplier(self):
        return self.lead_time <= 7
    
    def to_dict(self):
        return{
            "supplier_id" : self.supplier_id,
            "name" : self.name,
            "contact" : self.contact,
            "lead_time" : self.lead_time
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["suppiler_id"],
            data["name"],
            data["contact"],
            data["lead_time"]
        )
        