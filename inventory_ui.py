import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"
CURRENCY = "₹"

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(page_title="Inventory Manager", page_icon="📦", layout="wide")

# -------------------------
# API HELPERS
# -------------------------

def get_products():
    try:
        return requests.get(f"{BASE_URL}/products").json()
    except:
        return []

def get_categories():
    try:
        return requests.get(f"{BASE_URL}/categories").json()
    except:
        return []

def get_suppliers():
    try:
        return requests.get(f"{BASE_URL}/suppliers").json()
    except:
        return []

def get_low_stock():
    try:
        return requests.get(f"{BASE_URL}/products/low-stock").json()
    except:
        return []

def is_api_available():
    try:
        requests.get(f"{BASE_URL}/")
        return True
    except:
        return False

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("📦 Inventory Manager")
page = st.sidebar.radio("Navigate", ["Products", "Categories", "Suppliers", "Reports"])

if is_api_available():
    st.sidebar.success("✅ API connected")
else:
    st.sidebar.error("❌ API not available")
    st.error("Inventory API is not running. Start it with: uvicorn api:app --reload")
    st.stop()

# -------------------------
# PAGE 1 — PRODUCTS
# -------------------------

if page == "Products":
    st.title("Products")

    # ---- Add Product Form ----
    with st.expander("➕ Add New Product"):
        categories = get_categories()
        suppliers = get_suppliers()

        cat_options = {c["name"].title(): c["category_id"] for c in categories}
        sup_options = {s["name"].title(): s["supplier_id"] for s in suppliers}

        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name")
                price = st.number_input("Price per unit", min_value=0.0, step=0.5, value=None, placeholder="0")
                stock = st.number_input("Stock", min_value=0, step=1, value=None, placeholder="0")
            with col2:
                min_stock = st.number_input("Min Stock", min_value=0, step=1, value=None, placeholder="0")
                category = st.selectbox("Category (optional)", ["None"] + list(cat_options.keys()))
                supplier = st.selectbox("Supplier (optional)", ["None"] + list(sup_options.keys()))

            submitted = st.form_submit_button("Add Product", type="primary")
            if submitted:
                if not name.strip():
                    st.error("Product name cannot be empty.")
                elif price is None or stock is None or min_stock is None:
                    st.error("Please fill in price, stock and min stock.")
                else:
                    payload = {
                        "name": name.strip().lower(),
                        "price_per_unit": float(price),
                        "stock": int(stock),
                        "min_stock": int(min_stock),
                        "category_id": cat_options.get(category) if category != "None" else None,
                        "supplier_id": sup_options.get(supplier) if supplier != "None" else None
                    }
                    result = requests.post(f"{BASE_URL}/products", json=payload).json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"Product added! SKU: {result['sku']}")
                        st.rerun()

    st.markdown("---")

    # ---- Sort Options ----
    products = get_products()

    if not products:
        st.info("No products found.")
    else:
        col_sort, col_count = st.columns([3, 1])
        with col_sort:
            sort_option = st.selectbox("Sort by", [
                "Name (A-Z)",
                "Price (Low to High)",
                "Price (High to Low)",
                "Stock (Low to High)",
                "Category"
            ])
        with col_count:
            st.markdown(f"<br>**{len(products)} products**", unsafe_allow_html=True)

        if sort_option == "Name (A-Z)":
            products = sorted(products, key=lambda p: p["name"])
        elif sort_option == "Price (Low to High)":
            products = sorted(products, key=lambda p: p["price_per_unit"])
        elif sort_option == "Price (High to Low)":
            products = sorted(products, key=lambda p: p["price_per_unit"], reverse=True)
        elif sort_option == "Stock (Low to High)":
            products = sorted(products, key=lambda p: p["stock"])
        elif sort_option == "Category":
            products = sorted(products, key=lambda p: p.get("category_id") or "")

        st.markdown("---")

        categories = get_categories()
        suppliers = get_suppliers()
        cat_options = {c["name"].title(): c["category_id"] for c in categories}
        sup_options = {s["name"].title(): s["supplier_id"] for s in suppliers}
        cat_id_to_name = {c["category_id"]: c["name"].title() for c in categories}
        sup_id_to_name = {s["supplier_id"]: s["name"].title() for s in suppliers}

        # ---- Product List ----
        for product in products:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                st.markdown(f"**{product['name'].title()}**")
                st.caption(f"SKU: {product['sku']}")
                cat_name = cat_id_to_name.get(product.get("category_id"), "—")
                sup_name = sup_id_to_name.get(product.get("supplier_id"), "—")
                st.caption(f"Category: {cat_name} | Supplier: {sup_name}")

            with col2:
                st.markdown(f"{CURRENCY}{product['price_per_unit']}")
                if product["stock"] <= product["min_stock"]:
                    st.warning(f"⚠️ Stock: {product['stock']}")
                else:
                    st.markdown(f"Stock: {product['stock']}")

            with col3:
                update_amount = st.number_input(
                    "Amount",
                    min_value=1,
                    step=1,
                    key=f"amt_{product['sku']}"
                )
                col3a, col3b = st.columns(2)
                with col3a:
                    if st.button("➕", key=f"inc_{product['sku']}"):
                        result = requests.patch(
                            f"{BASE_URL}/products/{product['sku']}/stock",
                            json={"amount": update_amount, "operation": "increase"}
                        ).json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"Stock: {result['new_stock']}")
                            st.rerun()
                with col3b:
                    if st.button("➖", key=f"dec_{product['sku']}"):
                        result = requests.patch(
                            f"{BASE_URL}/products/{product['sku']}/stock",
                            json={"amount": update_amount, "operation": "decrease"}
                        ).json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"Stock: {result['new_stock']}")
                            st.rerun()

            with col4:
                if st.button("🗑️ Delete", key=f"del_{product['sku']}"):
                    result = requests.delete(f"{BASE_URL}/products/{product['sku']}").json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"{product['name'].title()} deleted.")
                        st.rerun()

            # ---- Edit Form per product ----
            with st.expander(f"✏️ Edit {product['name'].title()}"):
                with st.form(f"edit_form_{product['sku']}"):
                    st.caption("Leave fields unchanged to keep current values.")
                    ecol1, ecol2 = st.columns(2)

                    with ecol1:
                        current_cat = cat_id_to_name.get(product.get("category_id"), "None")
                        current_sup = sup_id_to_name.get(product.get("supplier_id"), "None")

                        new_price = st.number_input(
                            f"Price (current: {CURRENCY}{product['price_per_unit']})",
                            min_value=0.0,
                            step=0.5,
                            value=None,
                            placeholder=str(product['price_per_unit'])
                        )
                        new_min_stock = st.number_input(
                            f"Min Stock (current: {product['min_stock']})",
                            min_value=0,
                            step=1,
                            value=None,
                            placeholder=str(product['min_stock'])
                        )

                    with ecol2:
                        new_category = st.selectbox(
                            f"Category (current: {current_cat})",
                            ["Keep current"] + list(cat_options.keys()),
                            key=f"ecat_{product['sku']}"
                        )
                        new_supplier = st.selectbox(
                            f"Supplier (current: {current_sup})",
                            ["Keep current"] + list(sup_options.keys()),
                            key=f"esup_{product['sku']}"
                        )

                    edit_submitted = st.form_submit_button("Save Changes", type="primary")
                    if edit_submitted:
                        payload = {}
                        changes = []

                        if new_price is not None:
                            payload["price_per_unit"] = float(new_price)
                            changes.append(f"Price updated to {CURRENCY}{new_price}")
                        if new_min_stock is not None:
                            payload["min_stock"] = int(new_min_stock)
                            changes.append(f"Min stock updated to {int(new_min_stock)}")
                        if new_category != "Keep current":
                            payload["category_id"] = cat_options[new_category]
                            changes.append(f"Category updated to {new_category}")
                        if new_supplier != "Keep current":
                            payload["supplier_id"] = sup_options[new_supplier]
                            changes.append(f"Supplier updated to {new_supplier}")

                        if not payload:
                            st.info("No changes made.")
                        else:
                            result = requests.patch(
                                f"{BASE_URL}/products/{product['sku']}",
                                json=payload
                            ).json()
                            if "error" in result:
                                st.error(result["error"])
                            else:
                                for change in changes:
                                    st.success(f"✅ {product['name'].title()} — {change}")
                                st.rerun()

            st.divider()

# -------------------------
# PAGE 2 — CATEGORIES
# -------------------------

elif page == "Categories":
    st.title("Categories")

    with st.expander("➕ Add New Category"):
        with st.form("add_category_form"):
            cat_name = st.text_input("Category Name")
            submitted = st.form_submit_button("Add Category", type="primary")
            if submitted:
                if not cat_name.strip():
                    st.error("Category name cannot be empty.")
                else:
                    result = requests.post(f"{BASE_URL}/categories", json={"name": cat_name.strip()}).json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"Category added! ID: {result['category_id']}")
                        st.rerun()

    st.markdown("---")

    categories = get_categories()

    if not categories:
        st.info("No categories found.")
    else:
        st.markdown(f"**{len(categories)} categories**")
        for cat in categories:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{cat['name'].title()}**")
                st.caption(f"ID: {cat['category_id']}")
            with col2:
                if st.button("🗑️ Delete", key=f"del_cat_{cat['category_id']}"):
                    result = requests.delete(f"{BASE_URL}/categories/{cat['category_id']}").json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"{cat['name'].title()} deleted.")
                        st.rerun()
            st.divider()

# -------------------------
# PAGE 3 — SUPPLIERS
# -------------------------

elif page == "Suppliers":
    st.title("Suppliers")

    with st.expander("➕ Add New Supplier"):
        with st.form("add_supplier_form"):
            col1, col2 = st.columns(2)
            with col1:
                sup_name = st.text_input("Supplier Name")
                sup_contact = st.text_input("Contact (phone or email)")
            with col2:
                sup_lead = st.number_input("Lead Time (days)", min_value=1, step=1, value=None, placeholder="0")

            submitted = st.form_submit_button("Add Supplier", type="primary")
            if submitted:
                if not sup_name.strip() or not sup_contact.strip():
                    st.error("Name and contact cannot be empty.")
                elif sup_lead is None:
                    st.error("Please enter lead time.")
                else:
                    result = requests.post(f"{BASE_URL}/suppliers", json={
                        "name": sup_name.strip(),
                        "contact": sup_contact.strip(),
                        "lead_time": int(sup_lead)
                    }).json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"Supplier added! ID: {result['supplier_id']}")
                        st.rerun()

    st.markdown("---")

    suppliers = get_suppliers()

    if not suppliers:
        st.info("No suppliers found.")
    else:
        st.markdown(f"**{len(suppliers)} suppliers**")
        for sup in suppliers:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{sup['name'].title()}**")
                st.caption(f"ID: {sup['supplier_id']} | Contact: {sup['contact']} | Lead time: {sup['lead_time']} days")
                if sup["lead_time"] <= 7:
                    st.success("⚡ Fast supplier")
            with col2:
                if st.button("🗑️ Delete", key=f"del_sup_{sup['supplier_id']}"):
                    result = requests.delete(f"{BASE_URL}/suppliers/{sup['supplier_id']}").json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"{sup['name'].title()} deleted.")
                        st.rerun()
            st.divider()

# -------------------------
# PAGE 4 — REPORTS
# -------------------------

elif page == "Reports":
    st.title("Reports")

    products = get_products()

    # ---- Total Inventory Value ----
    st.subheader("💰 Total Inventory Value")
    total_value = sum(p["price_per_unit"] * p["stock"] for p in products)
    st.metric("Total Value", f"{CURRENCY}{total_value:,.2f}")

    st.markdown("---")

    # ---- Low Stock Alert ----
    st.subheader("⚠️ Low Stock Products")
    low_stock = get_low_stock()
    if not low_stock:
        st.success("All products are sufficiently stocked.")
    else:
        for p in low_stock:
            st.warning(f"**{p['name'].title()}** — Stock: {p['stock']} (Min: {p['min_stock']})")

    st.markdown("---")

    # ---- Category Summary ----
    st.subheader("📊 Stock by Category")
    categories = get_categories()

    if not categories:
        st.info("No categories found.")
    else:
        cat_map = {c["category_id"]: c["name"] for c in categories}
        summary = {}
        for p in products:
            cat_id = p.get("category_id")
            cat_name = cat_map.get(cat_id, "Uncategorised").title()
            if cat_name not in summary:
                summary[cat_name] = {"count": 0, "value": 0}
            summary[cat_name]["count"] += 1
            summary[cat_name]["value"] += p["price_per_unit"] * p["stock"]

        for cat_name, data in summary.items():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{cat_name}** — {data['count']} products")
            with col2:
                st.markdown(f"Value: {CURRENCY}{data['value']:,.2f}")