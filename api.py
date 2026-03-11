from fastapi import FastAPI
from pydantic import BaseModel
from storage import load_products, save_products, load_categories, load_suppliers
from services import InventoryService
from models import Product
from util import generate_next_sku

app = FastAPI()

# -------- Pydantic Schemas --------

class ProductInput(BaseModel):
    name: str
    price_per_unit: float
    stock: int
    min_stock: int
    category_id: str = None
    supplier_id: str = None

class StockUpdate(BaseModel):
    amount: int
    operation: str  # "increase" or "decrease"

# -------- Helper --------

def get_inventory():
    products = load_products()
    categories = load_categories()
    suppliers = load_suppliers()
    return InventoryService(products, categories, suppliers)

# -------- Endpoints --------

@app.get("/")
def root():
    return {"message": "Inventory API is running"}

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
        data.name,
        data.price_per_unit,
        data.stock,
        data.min_stock,
        data.category_id,
        data.supplier_id
    )
    inventory.add_product(product)
    save_products(inventory.products)
    return {"message": "Product added", "sku": sku}

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