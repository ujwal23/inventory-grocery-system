from models import Product, Category, Supplier
from services import InventoryService
from storage import (
    save_products, load_products,
    save_categories, load_categories,
    save_suppliers, load_suppliers
)
from util import (
    generate_next_sku,
    generate_next_category_id,
    generate_next_supplier_id,
    get_valid_int,
    get_valid_float,
    print_product,
)


# -------------------------
# STARTUP
# -------------------------

def check_low_stock_on_startup(inventory):
    low = inventory.get_low_stock_products()
    if low:
        print("\n⚠️  LOW STOCK ALERT — the following products need attention:")
        for p in low:
            print(f"   {p.sku} | {p.name} — Stock: {p.stock} (Min: {p.min_stock})")


# -------------------------
# PRINT MENUS
# -------------------------

def print_main_menu():
    print("\n------- Inventory App -------")
    print("1. Products")
    print("2. Categories")
    print("3. Suppliers")
    print("4. Reports")
    print("5. Exit")


def print_products_menu():
    print("\n--- Products ---")
    print("1. Add Product")
    print("2. View All")
    print("3. Search")
    print("4. Update Stock")
    print("5. Apply Discount")
    print("6. Delete Product")
    print("7. View Low Stock")
    print("8. Back")
    print("9. Exit")


def print_categories_menu():
    print("\n--- Categories ---")
    print("1. Add Category")
    print("2. Delete Category")
    print("3. View Categories")
    print("4. Back")
    print("5. Exit")


def print_suppliers_menu():
    print("\n--- Suppliers ---")
    print("1. Add Supplier")
    print("2. Delete Supplier")
    print("3. View Suppliers")
    print("4. Back")
    print("5. Exit")


def print_reports_menu():
    print("\n--- Reports ---")
    print("1. Products by Category")
    print("2. Products by Supplier")
    print("3. Category Value Summary")
    print("4. Total Inventory Value")
    print("5. Back")
    print("6. Exit")


# -------------------------
# PRODUCT ACTIONS
# -------------------------

def add_product(inventory):
    name = input("Enter name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    price = get_valid_float("Enter price: ")
    stock = get_valid_int("Enter stock: ")
    min_stock = get_valid_int("Enter minimum stock: ")

    category_id = None
    if inventory.categories:
        print("\nAvailable Categories:")
        for c in inventory.categories:
            print(f"  {c.category_id} — {c.name}")
        choice = input("Enter category ID (or press Enter to skip): ").strip().upper()
        if choice and inventory.find_category_by_id(choice):
            category_id = choice
        elif choice:
            print("Category not found. Leaving unassigned.")

    supplier_id = None
    if inventory.suppliers:
        print("\nAvailable Suppliers:")
        for s in inventory.suppliers:
            print(f"  {s.supplier_id} — {s.name}")
        choice = input("Enter supplier ID (or press Enter to skip): ").strip().upper()
        if choice and inventory.find_supplier_by_id(choice):
            supplier_id = choice
        elif choice:
            print("Supplier not found. Leaving unassigned.")

    sku = generate_next_sku(inventory.products)

    try:
        product = Product(sku, name, price, stock, min_stock, category_id, supplier_id)
        inventory.add_product(product)
        save_products(inventory.products)
        print(f"Product added successfully. SKU: {sku}")
    except ValueError as e:
        print("Error:", e)


def view_all(inventory):
    if not inventory.products:
        print("No products in inventory.")
        return
    print(f"\n--- All Products ({len(inventory.products)} total) ---")
    for p in inventory.products:
        print_product(p)


def search_product(inventory):
    print("\nSearch by:")
    print("1. Name")
    print("2. SKU")
    choice = input("Choose option: ").strip()

    if choice == "1":
        keyword = input("Enter name keyword: ").strip()
        results = inventory.find_by_name(keyword)
        if not results:
            print("No matching products found.")
            return
        for p in results:
            print_product(p)
    elif choice == "2":
        sku = input("Enter SKU: ").strip().upper()
        product = inventory.find_by_sku(sku)
        if not product:
            print("No product found with that SKU.")
            return
        print_product(product)
    else:
        print("Invalid choice.")


def update_stock(inventory):
    sku = input("Enter SKU: ").strip().upper()
    product = inventory.find_by_sku(sku)
    if not product:
        print("No product found with that SKU.")
        return

    print(f"\n{product.name} — Current stock: {product.stock}")
    print("1. Increase stock")
    print("2. Decrease stock")
    choice = input("Choose option: ").strip()

    if choice not in ("1", "2"):
        print("Invalid choice.")
        return

    amount = get_valid_int("Enter amount: ")
    operation = "increase" if choice == "1" else "decrease"

    try:
        inventory.update_stock(sku, amount, operation)
        save_products(inventory.products)
        print(f"Stock updated. New stock: {product.stock}")
    except ValueError as e:
        print("Error:", e)


def apply_discount(inventory):
    sku = input("Enter SKU: ").strip().upper()
    product = inventory.find_by_sku(sku)
    if not product:
        print("No product found with that SKU.")
        return

    print(f"\n{product.name} — Current price: ₹{product.price_per_unit:.2f}")
    percentage = get_valid_float("Enter discount percentage (0-100): ")

    try:
        inventory.apply_discount_to_product(sku, percentage)
        save_products(inventory.products)
        print(f"Discount applied. New price: ₹{product.price_per_unit:.2f}")
    except ValueError as e:
        print("Error:", e)


def delete_product(inventory):
    sku = input("Enter SKU to delete: ").strip().upper()
    product = inventory.find_by_sku(sku)
    if not product:
        print("No product found with that SKU.")
        return

    confirm = input(f"Delete '{product.name}'? (y/n): ").strip().lower()
    if confirm == "y":
        inventory.delete_product(sku)
        save_products(inventory.products)
        print("Product deleted.")
    else:
        print("Cancelled.")


def view_low_stock(inventory):
    low = inventory.get_low_stock_products()
    if not low:
        print("All products are sufficiently stocked.")
        return
    print(f"\n⚠️  Low Stock Products ({len(low)} found):")
    for p in low:
        print_product(p)


# -------------------------
# CATEGORY ACTIONS
# -------------------------

def add_category(inventory):
    name = input("Enter category name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    category_id = generate_next_category_id(inventory.categories)
    try:
        category = Category(category_id, name)
        inventory.add_category(category)
        save_categories(inventory.categories)
        print(f"Category added. ID: {category_id}")
    except ValueError as e:
        print("Error:", e)


def delete_category(inventory):
    if not inventory.categories:
        print("No categories found.")
        return

    view_categories(inventory)
    category_id = input("Enter category ID to delete: ").strip().upper()
    category = inventory.find_category_by_id(category_id)
    if not category:
        print("Category not found.")
        return

    confirm = input(f"Delete '{category.name}'? (y/n): ").strip().lower()
    if confirm == "y":
        inventory.delete_category(category_id)
        save_categories(inventory.categories)
        print("Category deleted.")
    else:
        print("Cancelled.")


def view_categories(inventory):
    if not inventory.categories:
        print("No categories found.")
        return
    print(f"\n--- Categories ({len(inventory.categories)} total) ---")
    for c in inventory.categories:
        print(f"  {c.category_id} — {c.name}")


# -------------------------
# SUPPLIER ACTIONS
# -------------------------

def add_supplier(inventory):
    name = input("Enter supplier name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    contact = input("Enter contact info: ").strip()
    if not contact:
        print("Contact cannot be empty.")
        return

    lead_time = get_valid_int("Enter lead time (days): ")
    supplier_id = generate_next_supplier_id(inventory.suppliers)

    try:
        supplier = Supplier(supplier_id, name, contact, lead_time)
        inventory.add_supplier(supplier)
        save_suppliers(inventory.suppliers)
        fast = "⚡ Fast supplier" if supplier.is_fast_supplier() else "🐢 Slow supplier"
        print(f"Supplier added. ID: {supplier_id} — {fast}")
    except ValueError as e:
        print("Error:", e)


def delete_supplier(inventory):
    if not inventory.suppliers:
        print("No suppliers found.")
        return

    view_suppliers(inventory)
    supplier_id = input("Enter supplier ID to delete: ").strip().upper()
    supplier = inventory.find_supplier_by_id(supplier_id)
    if not supplier:
        print("Supplier not found.")
        return

    confirm = input(f"Delete '{supplier.name}'? (y/n): ").strip().lower()
    if confirm == "y":
        inventory.delete_supplier(supplier_id)
        save_suppliers(inventory.suppliers)
        print("Supplier deleted.")
    else:
        print("Cancelled.")


def view_suppliers(inventory):
    if not inventory.suppliers:
        print("No suppliers found.")
        return
    print(f"\n--- Suppliers ({len(inventory.suppliers)} total) ---")
    for s in inventory.suppliers:
        fast = "⚡ Fast" if s.is_fast_supplier() else "🐢 Slow"
        print(f"  {s.supplier_id} — {s.name} | Contact: {s.contact} | Lead time: {s.lead_time} days | {fast}")


# -------------------------
# REPORT ACTIONS
# -------------------------

def view_products_by_category(inventory):
    if not inventory.categories:
        print("No categories found.")
        return
    view_categories(inventory)
    category_id = input("Enter category ID: ").strip().upper()
    results = inventory.get_products_by_category(category_id)
    if not results:
        print("No products found in this category.")
        return
    print(f"\n--- Products in category {category_id} ---")
    for p in results:
        print_product(p)


def view_products_by_supplier(inventory):
    if not inventory.suppliers:
        print("No suppliers found.")
        return
    view_suppliers(inventory)
    supplier_id = input("Enter supplier ID: ").strip().upper()
    results = inventory.get_products_by_supplier(supplier_id)
    if not results:
        print("No products found for this supplier.")
        return
    print(f"\n--- Products from supplier {supplier_id} ---")
    for p in results:
        print_product(p)


def view_category_value_summary(inventory):
    summary = inventory.get_category_value_summary()
    if not summary:
        print("No data available.")
        return
    print("\n--- Category Value Summary ---")
    for cat_id, total in summary.items():
        category = inventory.find_category_by_id(cat_id)
        name = category.name if category else cat_id
        print(f"  {name}: ₹{total:.2f}")


def total_value(inventory):
    total = inventory.get_total_inventory_value()
    print(f"\nTotal Inventory Value: ₹{total:.2f}")


# -------------------------
# SUBMENUS
# -------------------------

def products_menu(inventory):
    while True:
        print_products_menu()
        choice = input("Choose option: ").strip()

        if choice == "1":
            add_product(inventory)
        elif choice == "2":
            view_all(inventory)
        elif choice == "3":
            search_product(inventory)
        elif choice == "4":
            update_stock(inventory)
        elif choice == "5":
            apply_discount(inventory)
        elif choice == "6":
            delete_product(inventory)
        elif choice == "7":
            view_low_stock(inventory)
        elif choice == "8":
            break
        elif choice == "9":
            return "exit"
        else:
            print("Invalid option.")


def categories_menu(inventory):
    while True:
        print_categories_menu()
        choice = input("Choose option: ").strip()

        if choice == "1":
            add_category(inventory)
        elif choice == "2":
            delete_category(inventory)
        elif choice == "3":
            view_categories(inventory)
        elif choice == "4":
            break
        elif choice == "5":
            return "exit"
        else:
            print("Invalid option.")


def suppliers_menu(inventory):
    while True:
        print_suppliers_menu()
        choice = input("Choose option: ").strip()

        if choice == "1":
            add_supplier(inventory)
        elif choice == "2":
            delete_supplier(inventory)
        elif choice == "3":
            view_suppliers(inventory)
        elif choice == "4":
            break
        elif choice == "5":
            return "exit"
        else:
            print("Invalid option.")


def reports_menu(inventory):
    while True:
        print_reports_menu()
        choice = input("Choose option: ").strip()

        if choice == "1":
            view_products_by_category(inventory)
        elif choice == "2":
            view_products_by_supplier(inventory)
        elif choice == "3":
            view_category_value_summary(inventory)
        elif choice == "4":
            total_value(inventory)
        elif choice == "5":
            break
        elif choice == "6":
            return "exit"
        else:
            print("Invalid option.")


# -------------------------
# MAIN LOOP
# -------------------------

def main():
    products = load_products()
    categories = load_categories()
    suppliers = load_suppliers()
    inventory = InventoryService(products, categories, suppliers)

    check_low_stock_on_startup(inventory)

    while True:
        print_main_menu()
        choice = input("Choose option: ").strip()

        if choice == "1":
            result = products_menu(inventory)
            if result == "exit":
                break
        elif choice == "2":
            result = categories_menu(inventory)
            if result == "exit":
                break
        elif choice == "3":
            result = suppliers_menu(inventory)
            if result == "exit":
                break
        elif choice == "4":
            result = reports_menu(inventory)
            if result == "exit":
                break
        elif choice == "5":
            break
        else:
            print("Invalid option.")

    save_products(inventory.products)
    save_categories(inventory.categories)
    save_suppliers(inventory.suppliers)
    print("Goodbye!")


if __name__ == "__main__":
    main()