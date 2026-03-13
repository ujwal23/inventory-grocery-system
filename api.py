from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from storage import (
    load_products, save_products,
    load_categories, save_categories,
    load_suppliers, save_suppliers
)
from services import InventoryService
from models import Product, Category, Supplier
from util import generate_next_sku, generate_next_category_id, generate_next_supplier_id

app = FastAPI()

# -------------------------
# PYDANTIC SCHEMAS
# -------------------------

class ProductInput(BaseModel):
    name: str
    price_per_unit: float
    stock: int
    min_stock: int
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None

class ProductUpdate(BaseModel):
    price_per_unit: Optional[float] = None
    min_stock: Optional[int] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None

class StockUpdate(BaseModel):
    amount: int
    operation: str  # "increase" or "decrease"

class CategoryInput(BaseModel):
    name: str

class SupplierInput(BaseModel):
    name: str
    contact: str
    lead_time: int

# -------------------------
# HELPER
# -------------------------

def get_inventory():
    products = load_products()
    categories = load_categories()
    suppliers = load_suppliers()
    return InventoryService(products, categories, suppliers)

# -------------------------
# ROOT
# -------------------------

@app.get("/")
def root():
    return {"message": "Inventory API is running"}

# -------------------------
# PRODUCT ENDPOINTS
# -------------------------

@app.get("/products")
def get_products():
    inventory = get_inventory()
    return [p.to_dict() for p in inventory.products]

@app.get("/products/low-stock")
def get_low_stock():
    inventory = get_inventory()
    low = inventory.get_low_stock_products()
    return [p.to_dict() for p in low]

@app.get("/products/{sku}")
def get_product(sku: str):
    inventory = get_inventory()
    product = inventory.find_by_sku(sku.upper())
    if not product:
        return {"error": "Product not found"}
    return product.to_dict()

@app.post("/products")
def add_product(data: ProductInput):
    inventory = get_inventory()
    sku = generate_next_sku(inventory.products)
    product = Product(
        sku,
        data.name.strip().lower(),
        data.price_per_unit,
        data.stock,
        data.min_stock,
        data.category_id,
        data.supplier_id
    )
    inventory.add_product(product)
    save_products(inventory.products)
    return {"message": "Product added", "sku": sku}

@app.patch("/products/{sku}")
def update_product(sku: str, data: ProductUpdate):
    inventory = get_inventory()
    product = inventory.find_by_sku(sku.upper())
    if not product:
        return {"error": "Product not found"}

    if data.price_per_unit is not None:
        product.price_per_unit = data.price_per_unit
    if data.min_stock is not None:
        product.min_stock = data.min_stock
    if data.category_id is not None:
        product.category_id = data.category_id
    if data.supplier_id is not None:
        product.supplier_id = data.supplier_id

    save_products(inventory.products)
    return {"message": "Product updated", "product": product.to_dict()}

@app.patch("/products/{sku}/stock")
def update_stock(sku: str, data: StockUpdate):
    inventory = get_inventory()
    try:
        inventory.update_stock(sku.upper(), data.amount, data.operation)
        save_products(inventory.products)
        product = inventory.find_by_sku(sku.upper())
        return {"message": "Stock updated", "new_stock": product.stock}
    except ValueError as e:
        return {"error": str(e)}

@app.delete("/products/{sku}")
def delete_product(sku: str):
    inventory = get_inventory()
    product = inventory.find_by_sku(sku.upper())
    if not product:
        return {"error": "Product not found"}
    inventory.delete_product(sku.upper())
    save_products(inventory.products)
    return {"message": f"Product {sku} deleted"}

# -------------------------
# CATEGORY ENDPOINTS
# -------------------------

@app.get("/categories")
def get_categories():
    inventory = get_inventory()
    return [c.to_dict() for c in inventory.categories]

@app.post("/categories")
def add_category(data: CategoryInput):
    inventory = get_inventory()
    if inventory.find_category_by_name(data.name):
        return {"error": "Category already exists"}
    category_id = generate_next_category_id(inventory.categories)
    category = Category(category_id, data.name.strip().lower())
    inventory.add_category(category)
    save_categories(inventory.categories)
    return {"message": "Category added", "category_id": category_id}

@app.delete("/categories/{category_id}")
def delete_category(category_id: str):
    inventory = get_inventory()
    category = inventory.find_category_by_id(category_id.upper())
    if not category:
        return {"error": "Category not found"}
    inventory.delete_category(category_id.upper())
    save_categories(inventory.categories)
    return {"message": f"Category {category_id} deleted"}

# -------------------------
# SUPPLIER ENDPOINTS
# -------------------------

@app.get("/suppliers")
def get_suppliers():
    inventory = get_inventory()
    return [s.to_dict() for s in inventory.suppliers]

@app.post("/suppliers")
def add_supplier(data: SupplierInput):
    inventory = get_inventory()
    if inventory.find_supplier_by_name(data.name):
        return {"error": "Supplier already exists"}
    supplier_id = generate_next_supplier_id(inventory.suppliers)
    supplier = Supplier(supplier_id, data.name.strip().lower(), data.contact, data.lead_time)
    inventory.add_supplier(supplier)
    save_suppliers(inventory.suppliers)
    return {"message": "Supplier added", "supplier_id": supplier_id}

@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: str):
    inventory = get_inventory()
    supplier = inventory.find_supplier_by_id(supplier_id.upper())
    if not supplier:
        return {"error": "Supplier not found"}
    inventory.delete_supplier(supplier_id.upper())
    save_suppliers(inventory.suppliers)
    return {"message": f"Supplier {supplier_id} deleted"}