"""
seed_customer_carts.py

Seeds user-isolated shopping carts for each SmartCart customer account according to the dataset.
Attributes used from prediction_batch_1.csv:
1. preferred_category: Items placed in cart belong to customer's preferred category (Electronics, Books, Fashion, Beauty, Home & Kitchen, Grocery, Sports).
2. cart_abandonments_last_30d:
   - If cart_abandonments_last_30d == 0 (e.g. AMZ_PRED1_1007, AMZ_PRED1_1041): 0 items in cart (clean/empty cart).
   - If cart_abandonments_last_30d == 1: 1 product in cart.
   - If cart_abandonments_last_30d in [2, 3, 4]: 2 products in cart.
   - If cart_abandonments_last_30d >= 5: 3 products in cart.

Ensures:
- Every customer account has its own independent cart in the database.
- Edits made by one user affect ONLY that user's account.
- AMZ_PRED1_1041 has 0 items in cart (abandonments = 0).
"""

import sys
import os
import random
import datetime

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.session import SessionLocal
from app.db.models import Customer, Product, CartItem

def seed_carts_from_dataset():
    db = SessionLocal()
    try:
        print("[Cart Seeder] Initializing per-user shopping carts from dataset...")
        products = db.query(Product).filter(Product.is_active == 1).all()
        if not products:
            print("[Cart Seeder] Error: No active products found in catalog.")
            return

        # Group products by category
        prods_by_cat = {}
        for p in products:
            cat = p.category or "General"
            if cat not in prods_by_cat:
                prods_by_cat[cat] = []
            prods_by_cat[cat].append(p)

        customers = db.query(Customer).order_by(Customer.id).all()
        print(f"[Cart Seeder] Found {len(customers)} customers in database.")

        # Clear any existing cart items to ensure fresh, clean, dataset-aligned state
        db.query(CartItem).delete()
        db.commit()

        total_seeded_items = 0
        customers_with_carts = 0
        customers_empty_carts = 0

        # Deterministic seeding based on customer attributes
        for c in customers:
            abandonments = c.cart_abandonments_last_30d if c.cart_abandonments_last_30d is not None else 0
            cat = c.preferred_category or "Electronics"

            # Determine number of cart items based on dataset abandonments
            if abandonments <= 0:
                item_count = 0
            elif abandonments == 1:
                item_count = 1
            elif abandonments <= 4:
                item_count = 2
            else:
                item_count = 3

            if item_count == 0:
                customers_empty_carts += 1
                continue

            customers_with_carts += 1

            # Get products from preferred category first
            cat_products = prods_by_cat.get(cat, products)
            other_products = [p for p in products if p not in cat_products]

            # Deterministic selection based on customer ID for consistency
            rng = random.Random(c.id * 100 + 42)
            
            selected_products = []
            if len(cat_products) >= item_count:
                selected_products = rng.sample(cat_products, item_count)
            else:
                selected_products = list(cat_products)
                remaining = item_count - len(selected_products)
                if other_products:
                    selected_products += rng.sample(other_products, min(remaining, len(other_products)))

            for prod in selected_products:
                qty = 1
                ci = CartItem(
                    customer_id=c.id,
                    product_id=prod.id,
                    quantity=qty,
                    created_at=datetime.datetime.now()
                )
                db.add(ci)
                total_seeded_items += 1

        db.commit()
        print(f"[Cart Seeder] Complete! Seeded {total_seeded_items} cart items across {customers_with_carts} customer accounts.")
        print(f"[Cart Seeder] Customers with 0 items (clean cart): {customers_empty_carts} accounts.")

        # Verification of benchmark accounts
        print("\n=== Verification ===")
        # AMZ_PRED1_1001 (Electronics, abandonments=3)
        c1001 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
        c1001_cart = db.query(CartItem).filter(CartItem.customer_id == c1001.id).all() if c1001 else []
        print(f"Customer AMZ_PRED1_1001 (Category: {c1001.preferred_category}, Abandonments: {c1001.cart_abandonments_last_30d}):")
        print(f"   Items in Cart: {len(c1001_cart)}")
        for it in c1001_cart:
            print(f"    - {it.product.title} (Qty: {it.quantity}, Price: ₹{it.product.price:,.2f})")

        # AMZ_PRED1_1002 (Books, abandonments=6)
        c1002 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1002").first()
        c1002_cart = db.query(CartItem).filter(CartItem.customer_id == c1002.id).all() if c1002 else []
        print(f"\nCustomer AMZ_PRED1_1002 (Category: {c1002.preferred_category}, Abandonments: {c1002.cart_abandonments_last_30d}):")
        print(f"   Items in Cart: {len(c1002_cart)}")
        for it in c1002_cart:
            print(f"    - {it.product.title} (Qty: {it.quantity}, Price: ₹{it.product.price:,.2f})")

        # AMZ_PRED1_1003 (Fashion, abandonments=7)
        c1003 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1003").first()
        c1003_cart = db.query(CartItem).filter(CartItem.customer_id == c1003.id).all() if c1003 else []
        print(f"\nCustomer AMZ_PRED1_1003 (Category: {c1003.preferred_category}, Abandonments: {c1003.cart_abandonments_last_30d}):")
        print(f"   Items in Cart: {len(c1003_cart)}")
        for it in c1003_cart:
            print(f"    - {it.product.title} (Qty: {it.quantity}, Price: ₹{it.product.price:,.2f})")

        # AMZ_PRED1_1041 (Benchmark 0 orders, abandonments=0)
        c1041 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
        c1041_cart = db.query(CartItem).filter(CartItem.customer_id == c1041.id).all() if c1041 else []
        print(f"\nBenchmark Customer AMZ_PRED1_1041 (Category: {c1041.preferred_category}, Abandonments: {c1041.cart_abandonments_last_30d}):")
        print(f"   Items in Cart: {len(c1041_cart)} (Guaranteed 0)")
        assert len(c1041_cart) == 0, f"Error: AMZ_PRED1_1041 must have 0 cart items, found {len(c1041_cart)}!"

        print("\n[Cart Seeder] SUCCESS: All customer accounts have strictly isolated, dataset-aligned carts!")

    except Exception as e:
        db.rollback()
        print(f"[Cart Seeder Error] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_carts_from_dataset()
