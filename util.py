def get_valid_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid whole number.")


def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def print_product(product):
    low = " ⚠️  LOW STOCK" if product.is_low_stock() else ""
    print(f"\n  SKU      : {product.sku}")
    print(f"  Name     : {product.name}")
    print(f"  Price    : ₹{product.price_per_unit:.2f}")
    print(f"  Stock    : {product.stock} (Min: {product.min_stock}){low}")
    print(f"  Value    : ₹{product.get_total_value():.2f}")
    print(f"  Category : {product.category_id or 'Unassigned'}")
    print(f"  Supplier : {product.supplier_id or 'Unassigned'}")
    print(f"  Updated  : {product.updated_at}")


def print_menu():
    print("\n------- Inventory Menu -------")
    print(" 1.  Add Product")
    print(" 2.  View All Products")
    print(" 3.  Search Product")
    print(" 4.  Update Stock")
    print(" 5.  Apply Discount")
    print(" 6.  Delete Product")
    print(" 7.  View Low Stock")
    print(" 8.  Sort Products")
    print(" 9.  Total Inventory Value")
    print("--- Categories ---")
    print("10.  Add Category")
    print("11.  Delete Category")
    print("12.  View Categories")
    print("--- Suppliers ---")
    print("13.  Add Supplier")
    print("14.  Delete Supplier")
    print("15.  View Suppliers")
    print("--- Reports ---")
    print("16.  Products by Category")
    print("17.  Products by Supplier")
    print("18.  Category Value Summary")
    print("19.  Exit")


def print_sort_menu():
    print("\nSort by:")
    print("1. Name (A-Z)")
    print("2. Price (Low to High)")
    print("3. Stock (Low to High)")
    print("4. SKU")


# -------------------------
# SKU HELPERS
# -------------------------

def format_sku(number):
    return f"PRD-{number:05d}"


def generate_next_sku(products):
    if not products:
        return format_sku(1)
    numbers = [int(p.sku.split("-")[1]) for p in products]
    return format_sku(max(numbers) + 1)


# -------------------------
# CATEGORY HELPERS
# -------------------------

def format_category_id(number):
    return f"CAT-{number:05d}"


def generate_next_category_id(categories):
    if not categories:
        return format_category_id(1)
    numbers = [int(c.category_id.split("-")[1]) for c in categories]
    return format_category_id(max(numbers) + 1)


# -------------------------
# SUPPLIER HELPERS
# -------------------------

def format_supplier_id(number):
    return f"SUP-{number:05d}"


def generate_next_supplier_id(suppliers):
    if not suppliers:
        return format_supplier_id(1)
    numbers = [int(s.supplier_id.split("-")[1]) for s in suppliers]
    return format_supplier_id(max(numbers) + 1)

