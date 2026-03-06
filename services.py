from models import Product, Category, Supplier


class InventoryService:
    def __init__(self, products=None,categories=None,suppliers=None):
        self.products = products if products else []
        self.categories = categories if categories else []
        self.suppliers = suppliers if suppliers else []

    # -------- Product Management --------

    def add_product(self, product):
        if not self.is_sku_unique(product.sku):
            raise ValueError("SKU must be unique.")
        self.products.append(product)

    def delete_product(self, sku):
        self.products = [p for p in self.products if p.sku != sku]

    def find_by_sku(self, sku):
        for product in self.products:
            if product.sku == sku:
                return product
        return None

    def find_by_name(self, name):
        return [
            p for p in self.products
            if name.lower() in p.name.lower()
        ]

    def is_sku_unique(self, sku):
        return all(p.sku != sku for p in self.products)
    
    #------category management-------

    def is_category_id_unique(self, category_id):
        return all(c.category_id != category_id for c in self.categories)

    def add_category(self, category):
        if not self.is_category_id_unique(category.category_id):
            raise ValueError("Category_id must be unique.")
        self.categories.append(category)

    def delete_category(self, category_id):
        self.categories = [c for c in self.categories if c.category_id != category_id]

    def find_category_by_id(self, category_id):
        for category in self.categories:
            if category.category_id == category_id:
                return category
        return None
        
    def find_category_by_name(self, name):
        return[
            c for c in self.categories
            if name.lower() in c.name.lower()
        ]
    
    #---------supplier management-------

    def is_supplier_id_unique(self, supplier_id):
        return all(s.supplier_id != supplier_id for s in self.suppliers)
    
    def add_supplier(self, supplier):
        if not self.is_supplier_id_unique(supplier.supplier_id):
            raise ValueError("Supplier_id must be unique")
        self.suppliers.append(supplier)

    def delete_supplier(self, supplier_id):
        self.suppliers = [s for s in self.suppliers if s.supplier_id != supplier_id]

    def find_supplier_by_id(self, supplier_id):
        for supplier in self.suppliers:
            if supplier.supplier_id == supplier_id:
                return supplier
        return None
    
    def find_supplier_by_name(self, name):
        return[
            s for s in self.suppliers
            if name.lower() in s.name.lower()
        ]

    # -------- Stock Management --------

    def update_stock(self, sku, amount, operation):
        """
        operation: "increase" or "decrease"
        Finds product by SKU, then delegates to model method.
        """
        product = self.find_by_sku(sku)
        if not product:
            raise ValueError(f"No product found with SKU: {sku}")
        if operation == "increase":
            product.increase_stock(amount)
        elif operation == "decrease":
            product.decrease_stock(amount)
        else:
            raise ValueError("Operation must be 'increase' or 'decrease'.")

    # -------- Discount --------

    def apply_discount_to_product(self, sku, percentage):
        """
        Bridge method — finds product by SKU, calls model's apply_discount.
        """
        product = self.find_by_sku(sku)
        if not product:
            raise ValueError(f"No product found with SKU: {sku}")
        product.apply_discount(percentage)

    # -------- Aggregations --------

    def get_total_inventory_value(self):
        return sum(p.get_total_value() for p in self.products)

    def get_low_stock_products(self):
        return [p for p in self.products if p.is_low_stock()]

    # -------- Sorting --------

    def sort_products(self, sort_key):
        """
        Returns a sorted COPY — does not mutate the original list.
        sort_key: "name", "price", "stock", "sku"
        """
        if sort_key == "name":
            return sorted(self.products, key=lambda p: p.name.lower())
        elif sort_key == "price":
            return sorted(self.products, key=lambda p: p.price_per_unit)
        elif sort_key == "stock":
            return sorted(self.products, key=lambda p: p.stock)
        elif sort_key == "sku":
            return sorted(self.products, key=lambda p: p.sku)
        return self.products
    
        #SORT BY CATEGORY

    def get_products_by_category(self, category_id):
        return[
            p for p in self.products
            if p.category_id == category_id
        ]
    
           #SORT BY SUPPLIER

    def get_products_by_supplier(self, supplier_id):
        return[
            p for p in self.products
            if p.supplier_id == supplier_id
        ]
    
       #category value summary

    def get_category_value_summary(self):
        summary = {}
        for p in self.products:
            cat_id = p.category_id
            total = p.get_total_value()
            if cat_id in summary:
                summary[cat_id] += total
            else:
                summary[cat_id] = total
        return summary

