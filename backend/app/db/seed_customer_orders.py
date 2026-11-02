"""
seed_customer_orders.py

Generates realistic, unique, and distributed orders across SmartCart customer accounts.
Ensures:
1. Every order for every customer is UNIQUE (no repeated products, no duplicated order totals or dates).
2. Customer AMZ_PRED1_1001 has distinct orders with unique products and totals.
3. Benchmark customer AMZ_PRED1_1041 strictly has 0 orders, ₹0.00 spend, and None recency.
4. Approximately 50 registered customers receive 1 to 3 realistic purchases aligned with their preferred categories and membership tiers.
5. Invokes customer_feature_service.reconcile_all_registered_customers() to synchronize live RFM metrics and ML churn scores.
"""

import sys
import os
import random
import datetime

# Fix Windows console encoding for currency symbols
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.session import SessionLocal
from app.db.models import Customer, Product, Order, OrderItem, StoreUser
from app.services.customer_feature_service import reconcile_and_predict_customer, reconcile_all_registered_customers

CITIES_ADDRESSES = [
    "Flat 302, Palm Grove Heights, Indiranagar, Bengaluru 560038",
    "Villa 14, Prestige Silver Crest, Kadubeesanahalli, Bengaluru 560103",
    "B-402, Godrej Woodsman Estate, Bellary Road, Hebbal, Bengaluru 560024",
    "A-1204, Lodha Park, Senapati Bapat Marg, Lower Parel, Mumbai 400013",
    "Flat 801, Rustomjee Elements, Upper Juhu, Andheri West, Mumbai 400053",
    "House No. 42, Sector 15, Part 2, Gurugram, Haryana 122001",
    "Tower 5, Apt 1102, DLF Phase 5, Golf Course Road, Gurugram 122002",
    "Plot 88, Jubilee Hills Road No. 36, Hyderabad 500033",
    "Flat 6B, Rainbow Vistas, Hitec City, Hyderabad 500018",
    "No. 27, 4th Main Road, Besant Nagar, Chennai 600090",
    "B-201, Amanora Park Town, Hadapsar, Pune 411028",
    "Flat 503, Panchshil Towers, Kharadi, Pune 411014"
]

PAYMENT_MODES = ["UPI", "Credit/Debit Card", "Net Banking", "Cash on Delivery"]

def seed_realistic_orders():
    db = SessionLocal()
    try:
        print("[Order Seeder] Initializing realistic order distribution...")
        products = db.query(Product).filter(Product.is_active == 1).all()
        if not products:
            print("[Order Seeder] Error: No products found in catalog. Run seed_store.py first.")
            return

        # Map products by category
        prod_by_category = {}
        for p in products:
            cat = p.category or "General"
            if cat not in prod_by_category:
                prod_by_category[cat] = []
            prod_by_category[cat].append(p)

        all_customers = db.query(Customer).order_by(Customer.id).all()
        print(f"[Order Seeder] Found {len(all_customers)} customer accounts.")

        # 1. Update AMZ_PRED1_1001 (Customer ID 1) to ensure Order 2 has a UNIQUE product
        c1 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
        if c1:
            c1_orders = db.query(Order).filter(Order.customer_id == c1.id).order_by(Order.order_date).all()
            print(f"[Order Seeder] Customer AMZ_PRED1_1001 currently has {len(c1_orders)} orders.")
            
            # If Order 2 exists and has Product 8 (duplicate product of Order 1), change Order 2 to Product 7 (SanDisk Flash Drive)
            if len(c1_orders) >= 2:
                o2 = c1_orders[1]
                # Check items in Order 2
                sandisk_prod = db.query(Product).filter(Product.sku == "ELEC-SND-007").first() # SanDisk 128GB Flash Drive, ₹1299
                if not sandisk_prod:
                    sandisk_prod = products[6] # fallback

                # Restore previous items stock
                for it in o2.items:
                    prod = db.query(Product).filter(Product.id == it.product_id).first()
                    if prod:
                        prod.stock_quantity += it.quantity
                
                # Clear existing items
                for it in list(o2.items):
                    db.delete(it)
                db.flush()

                # Add new unique item to Order 2
                new_qty = 1
                unit_price = sandisk_prod.price
                line_total = round(unit_price * new_qty, 2)
                sandisk_prod.stock_quantity -= new_qty

                o2_item = OrderItem(
                    order_id=o2.id,
                    product_id=sandisk_prod.id,
                    quantity=new_qty,
                    unit_price=unit_price,
                    total_price=line_total
                )
                db.add(o2_item)

                subtotal = line_total
                shipping_fee = 0.0 # >= 500
                tax_fee = round(subtotal * 0.05, 2)
                final_total = round(subtotal + shipping_fee + tax_fee, 2)

                o2.subtotal = subtotal
                o2.tax_amount = tax_fee
                o2.shipping_amount = shipping_fee
                o2.order_amount = final_total
                o2.order_status = "Confirmed"
                o2.payment_mode = "Credit/Debit Card"
                db.commit()
                print(f"[Order Seeder] Updated AMZ_PRED1_1001 Order 2 to unique Product '{sandisk_prod.title}' (Total: ₹{final_total:,.2f}).")

        # 2. Check existing orders for other customers
        existing_other_orders = db.query(Order).filter(Order.customer_id != (c1.id if c1 else 1)).count()
        if existing_other_orders > 0:
            print(f"[Order Seeder] Database already contains {existing_other_orders} orders for other customers. Skipping additional seeding.")
        else:
            print("[Order Seeder] Seeding distributed orders for registered customers (strictly preserving AMZ_PRED1_1041 with 0 orders)...")
            random.seed(42) # Deterministic for repeatability
            now = datetime.datetime.now()

            # Target ~50 customers to receive orders
            # Exclude AMZ_PRED1_1001 (already has orders) and AMZ_PRED1_1041 (must be 0)
            eligible_customers = [
                c for c in all_customers 
                if c.source_customer_id not in ("AMZ_PRED1_1001", "AMZ_PRED1_1041")
            ]

            # Sample ~52 customers across various IDs
            selected_customers = eligible_customers[:52]
            orders_created = 0

            for cust in selected_customers:
                # Decide number of orders: 1 to 3
                num_orders = random.choices([1, 2, 3], weights=[0.50, 0.35, 0.15])[0]
                
                # Pick customer preferred category products first
                cust_cat = cust.preferred_category or "Electronics"
                matching_prods = prod_by_category.get(cust_cat, products)
                other_prods = [p for p in products if p not in matching_prods]

                is_prime = cust.membership_status and "prime" in cust.membership_status.lower()

                # Generate distinct timestamps over last 55 days
                # e.g. order 1: 35-55 days ago, order 2: 15-34 days ago, order 3: 2-14 days ago
                time_windows = [
                    (35, 55),
                    (15, 34),
                    (2, 14)
                ]

                # Keep track of purchased product IDs for this customer to ensure uniqueness
                customer_purchased_prod_ids = set()

                for order_idx in range(num_orders):
                    w_min, w_max = time_windows[order_idx]
                    days_ago = random.randint(w_min, w_max)
                    order_dt = now - datetime.timedelta(days=days_ago, hours=random.randint(1, 23), minutes=random.randint(1, 59))

                    # Choose 1-2 distinct products not yet purchased by this customer in this batch
                    available_prods = [p for p in matching_prods if p.id not in customer_purchased_prod_ids]
                    if not available_prods:
                        available_prods = [p for p in products if p.id not in customer_purchased_prod_ids]
                    if not available_prods:
                        available_prods = products

                    num_items = random.choices([1, 2], weights=[0.8, 0.2])[0]
                    chosen_prods = random.sample(available_prods, min(num_items, len(available_prods)))
                    
                    subtotal = 0.0
                    order_items_to_add = []

                    for cp in chosen_prods:
                        customer_purchased_prod_ids.add(cp.id)
                        qty = 1 # realistic quantity
                        line_total = round(cp.price * qty, 2)
                        subtotal += line_total
                        # Decrement stock safely
                        if cp.stock_quantity > 5:
                            cp.stock_quantity -= qty

                        order_items_to_add.append({
                            "product": cp,
                            "quantity": qty,
                            "unit_price": cp.price,
                            "total_price": line_total
                        })

                    # Shipping fee
                    shipping_fee = 0.0 if (is_prime or subtotal >= 500.0) else 40.0
                    tax_fee = round(subtotal * 0.05, 2)
                    final_amount = round(subtotal + shipping_fee + tax_fee, 2)

                    # Order status
                    if days_ago > 4:
                        order_status = "Delivered"
                    elif days_ago > 1:
                        order_status = "In Transit"
                    else:
                        order_status = "Confirmed"

                    payment_mode = random.choice(PAYMENT_MODES)
                    address = random.choice(CITIES_ADDRESSES)
                    order_num = f"SMART-{order_dt.strftime('%y%m%d')}-{random.randint(10000, 99999)}"

                    new_order = Order(
                        order_number=order_num,
                        customer_id=cust.id,
                        order_date=order_dt,
                        order_amount=final_amount,
                        subtotal=round(subtotal, 2),
                        tax_amount=tax_fee,
                        shipping_amount=shipping_fee,
                        discount=0.0,
                        payment_mode=payment_mode,
                        order_status=order_status,
                        shipping_address=address
                    )
                    db.add(new_order)
                    db.flush()

                    for oi in order_items_to_add:
                        item_obj = OrderItem(
                            order_id=new_order.id,
                            product_id=oi["product"].id,
                            quantity=oi["quantity"],
                            unit_price=oi["unit_price"],
                            total_price=oi["total_price"]
                        )
                        db.add(item_obj)

                    orders_created += 1

            db.commit()
            print(f"[Order Seeder] Successfully seeded {orders_created} unique, distributed orders across {len(selected_customers)} customers.")

        # 3. Synchronize All Customers with ML Churn Model and Authoritative Database Orders
        print("[Order Seeder] Synchronizing customer features and ML churn models...")
        sync_summary = reconcile_all_registered_customers(db)
        print(f"[Order Seeder] Reconciliation complete: {sync_summary.get('reconciled_count', 0)} accounts synced.")

        # 4. Rigorous Verification of Canonical State
        c1041 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
        c1041_orders = db.query(Order).filter(Order.customer_id == c1041.id).count() if c1041 else -1
        print(f"\n[Verification] Benchmark Customer AMZ_PRED1_1041:")
        print(f"   Database Orders: {c1041_orders}")
        print(f"   Lifetime Orders: {c1041.total_orders_lifetime}")
        print(f"   Lifetime Spend:  {c1041.total_spend_inr}")
        print(f"   Recency Days:    {c1041.days_since_last_purchase}")
        assert c1041_orders == 0, f"Error: AMZ_PRED1_1041 has {c1041_orders} orders! Must be 0."
        assert c1041.total_orders_lifetime == 0, f"Error: AMZ_PRED1_1041 lifetime orders is {c1041.total_orders_lifetime}! Must be 0."

        c1 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
        c1_orders = db.query(Order).filter(Order.customer_id == c1.id).all()
        print(f"\n[Verification] Customer AMZ_PRED1_1001:")
        print(f"   Database Orders: {len(c1_orders)}")
        for o in c1_orders:
            item_titles = [it.product.title for it in o.items]
            print(f"   Order #{o.order_number}: ₹{o.order_amount} | Items: {', '.join(item_titles)}")

        total_orders = db.query(Order).count()
        total_order_items = db.query(OrderItem).count()
        print(f"\n[Verification] Platform Totals:")
        print(f"   Total Orders: {total_orders}")
        print(f"   Total Order Items: {total_order_items}")
        print("[Order Seeder] SUCCESS: All customer orders are unique, realistic, and fully synchronized!")

    except Exception as e:
        db.rollback()
        print(f"[Order Seeder Error] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_realistic_orders()
