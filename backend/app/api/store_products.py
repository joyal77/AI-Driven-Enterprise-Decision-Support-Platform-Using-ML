import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db.session import get_db
from ..db.models import Product

router = APIRouter(prefix="/store/products", tags=["SmartCart Storefront Products"])

class ProductCreateUpdate(BaseModel):
    title: str
    category: str
    price: float
    original_price: Optional[float] = None
    stock_quantity: int = 100
    image_url: Optional[str] = None
    description: Optional[str] = None
    is_prime: int = 1
    sku: Optional[str] = None

@router.get("")
def list_store_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    prime_only: bool = False,
    sort: Optional[str] = "popular", # 'popular' | 'price_asc' | 'price_desc' | 'rating'
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == 1)

    if category and category.lower() != "all":
        query = query.filter(Product.category.ilike(category.strip()))

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Product.title.like(search_fmt)) |
            (Product.category.like(search_fmt)) |
            (Product.description.like(search_fmt))
        )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if prime_only:
        query = query.filter(Product.is_prime == 1)

    # Sorting
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    else: # popular / default
        query = query.order_by(Product.rating_count.desc(), Product.id.asc())

    total_count = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit,
        "products": [
            {
                "id": p.id,
                "sku": p.sku,
                "title": p.title,
                "category": p.category,
                "price": p.price,
                "original_price": p.original_price or round(p.price * 1.25, 2),
                "discount_pct": round(((p.original_price - p.price) / p.original_price * 100)) if p.original_price and p.original_price > p.price else 20,
                "stock_quantity": p.stock_quantity,
                "in_stock": p.stock_quantity > 0,
                "rating": p.rating,
                "rating_count": p.rating_count,
                "image_url": p.image_url,
                "description": p.description,
                "is_prime": bool(p.is_prime)
            }
            for p in products
        ]
    }

@router.get("/categories")
def get_store_categories(db: Session = Depends(get_db)):
    rows = db.query(
        Product.category,
        func.count(Product.id).label("count")
    ).filter(Product.is_active == 1).group_by(Product.category).all()

    return [
        {"category": r[0], "count": r[1]}
        for r in rows
    ]

def generate_rich_specs_and_features(product: Product):
    title = product.title or ""
    cat = product.category or "General"
    brand = title.split()[0] if title else "SmartCart"
    
    specs = {
        "Brand": brand,
        "Category": cat,
        "Model / SKU": product.sku or f"SKU-{product.id:04d}",
        "Stock Status": f"In Stock ({product.stock_quantity} units available)" if product.stock_quantity > 0 else "Currently Unavailable",
        "Fast Delivery": "FREE Delivery by Tomorrow 11 AM with Prime" if product.is_prime else "Standard 2-3 Business Days Delivery",
        "Warranty": "1 Year Comprehensive Manufacturer Brand Warranty",
        "Replacement Policy": "7 Days Returnable / Replacement Policy",
        "Accepted Payments": "UPI, Credit/Debit Card, Net Banking, Cash on Delivery",
        "Fulfillment": "SmartCart Certified Warehouse Hub"
    }

    if "Electronic" in cat:
        features = [
            "Engineered with cutting-edge internal micro-architecture for high performance, clarity, and reliability.",
            "Broad multi-platform compatibility across iOS, Android, macOS, and Windows operating systems.",
            "Optimized power efficiency featuring quick-charge support and adaptive heat dissipation.",
            "Sleek ergonomic build with durable matte tactile finish for heavy-duty daily use.",
            "Certified authentic hardware covered by official 1-year brand warranty."
        ]
    elif "Fashion" in cat:
        features = [
            "Woven from high-thread-count breathable fabric offering superior comfort in all climates.",
            "Precision tailoring with reinforced dual-needle stitching for lasting shape retention.",
            "Versatile modern aesthetic suitable for professional casual wear and everyday leisure.",
            "Pre-shrunk fabric ensures consistent fit and color vibrancy after repeated machine washes.",
            "Lightweight, wrinkle-resistant construction with premium hardware trims."
        ]
    elif "Home" in cat or "Kitchen" in cat:
        features = [
            "Designed to elevate everyday culinary convenience and enhance contemporary kitchen aesthetics.",
            "Fabricated from 100% food-grade, BPA-free, and corrosion-resistant materials.",
            "High-torque motor and advanced heating coils engineered for swift daily household tasks.",
            "Ergonomic stay-cool handles and auto-cutoff safety protection for peace of mind.",
            "Detachable dishwasher-safe components facilitate fast, hassle-free cleanup."
        ]
    elif "Beauty" in cat or "Care" in cat:
        features = [
            "Dermatologically tested clean formulation enriched with nourishing botanical bio-actives.",
            "Free from parabens, sulfates, and harsh synthetic additives; 100% cruelty-free.",
            "Ultra-lightweight, non-greasy absorption that delivers intense long-lasting hydration.",
            "Noticeably smoother and healthier appearance observed within 10 to 14 days of routine use.",
            "Housed in UV-protective airless pump container to retain active ingredient freshness."
        ]
    elif "Book" in cat:
        features = [
            "Globally recognized international bestseller packed with actionable wisdom and behavioral research.",
            "High-opacity cream pages with eye-friendly typography for fatigue-free reading sessions.",
            "Includes comprehensive chapter summaries, practical diagrams, and real-world case studies.",
            "Highly acclaimed by business leaders, educators, and personal development practitioners.",
            "Sturdy library-grade binding with gold foil-accented embossed cover."
        ]
    elif "Grocery" in cat:
        features = [
            "100% authentic, hygienically sourced, and rigorously lab-tested for peak freshness.",
            "Rich authentic aroma and taste with essential natural nutrient profiles preserved.",
            "Triple-layer nitrogen-sealed pouch ensures optimal shelf life and crisp flavor retention.",
            "FSSAI certified and produced under stringent international food hygiene protocols.",
            "Essential dietary staple for nutritious everyday family meals."
        ]
    else:
        features = [
            "High-impact resistant construction engineered for active daily workouts and recreation.",
            "Textured non-slip grip delivers exceptional stability, safety, and hand comfort.",
            "Compact, balanced form factor makes it convenient to store or transport anywhere.",
            "Meets all international consumer product safety and non-toxic standards.",
            "Backed by SmartCart Purchase Protection and manufacturer customer assistance."
        ]

    reviews = [
        {
            "id": 1,
            "author": "Rahul Sharma, Bengaluru",
            "rating": 5,
            "date": "16 October 2026",
            "verified": True,
            "title": "Superb quality and delivered in less than 24 hours!",
            "comment": f"I purchased this {product.title[:45]} and it works like a charm. Packaging was immaculate with brand seal intact. Highly satisfied with SmartCart!"
        },
        {
            "id": 2,
            "author": "Ananya Sen, Kolkata",
            "rating": 5,
            "date": "10 October 2026",
            "verified": True,
            "title": "Authentic product at an unbeatable price",
            "comment": f"Compared with other marketplaces and SmartCart had the best price. The build quality feels sturdy and genuine. Recommend without hesitation."
        },
        {
            "id": 3,
            "author": "Vikram Malhotra, Mumbai",
            "rating": 4,
            "date": "02 October 2026",
            "verified": True,
            "title": "Very practical and reliable daily driver",
            "comment": "Works exactly as specified in the product description. The delivery executive was polite and the item is performing great so far."
        }
    ]

    return specs, features, reviews

@router.get("/{product_id}")
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    """Fetch rich product specifications, features, reviews, and related items."""
    clean_id = str(product_id).strip()
    
    if clean_id.isdigit():
        product = db.query(Product).filter(Product.id == int(clean_id), Product.is_active == 1).first()
    else:
        product = db.query(Product).filter(
            (Product.sku == clean_id) | (Product.title.ilike(f"%{clean_id}%")),
            Product.is_active == 1
        ).first()

    if not product and clean_id.isdigit():
        product = db.query(Product).filter(Product.id == int(clean_id)).first()

    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{clean_id}' not found in catalog.")

    specs, features, reviews = generate_rich_specs_and_features(product)

    # Fetch 4-6 related products from the same category or top catalog items
    related_rows = db.query(Product).filter(
        Product.category == product.category,
        Product.id != product.id,
        Product.is_active == 1
    ).order_by(Product.rating_count.desc()).limit(6).all()

    if len(related_rows) < 4:
        existing_ids = [r.id for r in related_rows] + [product.id]
        supplement = db.query(Product).filter(
            ~Product.id.in_(existing_ids),
            Product.is_active == 1
        ).order_by(Product.rating.desc()).limit(6 - len(related_rows)).all()
        related_rows.extend(supplement)

    related_items = [
        {
            "id": r.id,
            "sku": r.sku,
            "title": r.title,
            "category": r.category,
            "price": r.price,
            "original_price": r.original_price or round(r.price * 1.25, 2),
            "discount_pct": round(((r.original_price - r.price) / r.original_price * 100)) if r.original_price and r.original_price > r.price else 20,
            "rating": r.rating,
            "rating_count": r.rating_count,
            "image_url": r.image_url,
            "is_prime": bool(r.is_prime),
            "in_stock": r.stock_quantity > 0
        }
        for r in related_rows
    ]

    return {
        "id": product.id,
        "sku": product.sku,
        "title": product.title,
        "category": product.category,
        "price": product.price,
        "original_price": product.original_price or round(product.price * 1.25, 2),
        "discount_pct": round(((product.original_price - product.price) / product.original_price * 100)) if product.original_price and product.original_price > product.price else 20,
        "stock_quantity": product.stock_quantity,
        "in_stock": product.stock_quantity > 0,
        "rating": product.rating,
        "rating_count": product.rating_count,
        "image_url": product.image_url,
        "description": product.description,
        "is_prime": bool(product.is_prime),
        "specifications": specs,
        "features": features,
        "reviews": reviews,
        "related_products": related_items
    }

@router.get("/{product_id}/related")
def get_related_products(product_id: str, db: Session = Depends(get_db)):
    """Fetch related products for recommendations carousel."""
    detail = get_product_detail(product_id=product_id, db=db)
    return detail.get("related_products", [])

@router.post("")
def create_store_product(payload: ProductCreateUpdate, db: Session = Depends(get_db)):
    """Product Manager / Admin endpoint to create a new catalog item."""
    generated_sku = payload.sku or f"{payload.category[:4].upper()}-{int(datetime.datetime.now().timestamp()) % 100000}"
    
    new_prod = Product(
        sku=generated_sku,
        title=payload.title,
        product_name=payload.title,
        category=payload.category,
        price=payload.price,
        original_price=payload.original_price or round(payload.price * 1.3, 2),
        stock_quantity=payload.stock_quantity,
        image_url=payload.image_url or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
        description=payload.description or "High quality item available on SmartCart.",
        is_prime=payload.is_prime,
        rating=4.5,
        rating_count=1,
        is_active=1
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)

    return {
        "success": True,
        "message": "Product successfully added to SmartCart catalog.",
        "product": {
            "id": new_prod.id,
            "sku": new_prod.sku,
            "title": new_prod.title,
            "price": new_prod.price,
            "stock_quantity": new_prod.stock_quantity
        }
    }

@router.put("/{product_id}")
def update_store_product(product_id: int, payload: ProductCreateUpdate, db: Session = Depends(get_db)):
    """Product Manager / Admin endpoint to edit stock, price, or details."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found.")

    prod.title = payload.title
    prod.product_name = payload.title
    prod.category = payload.category
    prod.price = payload.price
    if payload.original_price is not None:
        prod.original_price = payload.original_price
    prod.stock_quantity = payload.stock_quantity
    if payload.image_url:
        prod.image_url = payload.image_url
    if payload.description:
        prod.description = payload.description
    prod.is_prime = payload.is_prime
    prod.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(prod)

    return {
        "success": True,
        "message": f"Product '{prod.title}' updated successfully.",
        "product": {
            "id": prod.id,
            "title": prod.title,
            "price": prod.price,
            "stock_quantity": prod.stock_quantity
        }
    }

@router.delete("/{product_id}")
def delete_store_product(product_id: int, db: Session = Depends(get_db)):
    """Product Manager / Admin endpoint to deactivate a product."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found.")

    prod.is_active = 0
    db.commit()
    return {"success": True, "message": "Product removed from active storefront catalog."}
