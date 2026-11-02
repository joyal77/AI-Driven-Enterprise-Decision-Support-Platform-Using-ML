import os
import sys
import hashlib
import datetime
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.session import engine, SessionLocal, Base
from app.db.models import Customer, Product, Order, OrderItem, StoreUser, ChurnPrediction

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.strip().encode()).hexdigest()

SAMPLE_PRODUCTS = [
    # --- ELECTRONICS ---
    {
        "sku": "ELEC-ECH-001",
        "title": "Echo Dot (5th Gen) Smart Speaker with Alexa & Bigger Bass",
        "category": "Electronics",
        "price": 4499.0,
        "original_price": 5499.0,
        "stock_quantity": 85,
        "rating": 4.6,
        "rating_count": 18240,
        "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=600&auto=format&fit=crop&q=80",
        "description": "Our best sounding Echo Dot yet. Enjoy an improved audio experience compared to any previous Echo Dot with Alexa for clearer vocals and deeper bass in any room.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-FTV-002",
        "title": "Fire TV Stick 4K streaming device with Alexa Voice Remote (includes TV controls)",
        "category": "Electronics",
        "price": 3999.0,
        "original_price": 5999.0,
        "stock_quantity": 120,
        "rating": 4.5,
        "rating_count": 9420,
        "image_url": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600&auto=format&fit=crop&q=80",
        "description": "Cinematic experience: watch in vibrant 4K Ultra HD with support for Dolby Vision, HDR10+, and immersive Dolby Atmos audio.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-SNY-003",
        "title": "Sony WH-1000XM5 Wireless Industry Leading Active Noise Canceling Headphones",
        "category": "Electronics",
        "price": 26990.0,
        "original_price": 34990.0,
        "stock_quantity": 42,
        "rating": 4.8,
        "rating_count": 4820,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
        "description": "Magnificent sound, engineered to perfection with the Integrated Processor V1. Up to 30-hour battery life with quick charging.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-APL-004",
        "title": "Apple iPad (10th Generation): with A14 Bionic chip, 10.9-inch Liquid Retina Display",
        "category": "Electronics",
        "price": 34900.0,
        "original_price": 39900.0,
        "stock_quantity": 30,
        "rating": 4.7,
        "rating_count": 3120,
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&auto=format&fit=crop&q=80",
        "description": "Colorfully reimagined and more versatile than ever with an all-screen design, 10.9-inch Liquid Retina display, and fast A14 Bionic chip.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-SAM-005",
        "title": "Samsung Galaxy Watch 6 Bluetooth 44mm Smartwatch with Sapphire Crystal Glass",
        "category": "Electronics",
        "price": 18999.0,
        "original_price": 33999.0,
        "stock_quantity": 55,
        "rating": 4.4,
        "rating_count": 2180,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
        "description": "Advanced sleep coaching, heart rate tracking, personalized HR zones, and sleek stainless steel rotating bezel.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-LOG-006",
        "title": "Logitech MX Master 3S Wireless Performance Mouse with Quiet Clicks & 8K DPI Sensor",
        "category": "Electronics",
        "price": 8995.0,
        "original_price": 10995.0,
        "stock_quantity": 64,
        "rating": 4.7,
        "rating_count": 8700,
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
        "description": "Feel every moment of your workflow with even more precision, tactility, and performance, thanks to Quiet Clicks and an 8,000 DPI track-on-glass sensor.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-SND-007",
        "title": "SanDisk 128GB Ultra Dual Drive Luxe USB Type-C Flash Drive",
        "category": "Electronics",
        "price": 1299.0,
        "original_price": 2400.0,
        "stock_quantity": 210,
        "rating": 4.5,
        "rating_count": 42100,
        "image_url": "https://images.unsplash.com/photo-1618424181497-157f25b6ddd5?w=600&auto=format&fit=crop&q=80",
        "description": "The 2-in-1 all-metal flash drive with reversible USB Type-C and traditional Type-A connectors for seamless file transfer between smartphones and PCs.",
        "is_prime": 1
    },
    {
        "sku": "ELEC-BOT-008",
        "title": "boAt Airdopes 141 Bluetooth Truly Wireless in Ear Earbuds with 42H Playtime",
        "category": "Electronics",
        "price": 1199.0,
        "original_price": 4490.0,
        "stock_quantity": 140,
        "rating": 4.3,
        "rating_count": 78900,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
        "description": "Equipped with 8mm drivers, ENx environmental noise cancellation technology, and ASAP fast charging giving 75 min playtime in 5 mins.",
        "is_prime": 1
    },

    # --- FASHION ---
    {
        "sku": "FASH-LEV-009",
        "title": "Levi's Men's 511 Slim Fit Mid Rise Dark Indigo Stretchable Jeans",
        "category": "Fashion",
        "price": 2499.0,
        "original_price": 4199.0,
        "stock_quantity": 95,
        "rating": 4.4,
        "rating_count": 5420,
        "image_url": "https://images.unsplash.com/photo-1542272604-780c96856592?w=600&auto=format&fit=crop&q=80",
        "description": "Modern slim-fit jeans with room to move, upgraded with premium stretch denim for all-day comfort and athletic mobility.",
        "is_prime": 1
    },
    {
        "sku": "FASH-ALN-010",
        "title": "Allen Solly Men's Regular Fit Solid Polo Collar Premium Cotton T-Shirt",
        "category": "Fashion",
        "price": 899.0,
        "original_price": 1499.0,
        "stock_quantity": 180,
        "rating": 4.2,
        "rating_count": 16400,
        "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600&auto=format&fit=crop&q=80",
        "description": "Crafted from 100% combed cotton pique fabric, featuring classic ribbed collar, two-button placket, and signature embroidered logo.",
        "is_prime": 1
    },
    {
        "sku": "FASH-PUM-011",
        "title": "Puma Men's Tazon 6 Fracture Running & Training Shoes",
        "category": "Fashion",
        "price": 3299.0,
        "original_price": 5999.0,
        "stock_quantity": 60,
        "rating": 4.5,
        "rating_count": 8200,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        "description": "Sleek, streamlined silhouette with synthetic leather upper, midfoot saddle for maximum fit, and EVA heel pod for cushioning.",
        "is_prime": 1
    },
    {
        "sku": "FASH-BIB-012",
        "title": "Biba Women's Traditional Floral Printed Pure Cotton Anarkali Kurta Set",
        "category": "Fashion",
        "price": 2799.0,
        "original_price": 5500.0,
        "stock_quantity": 72,
        "rating": 4.6,
        "rating_count": 3900,
        "image_url": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop&q=80",
        "description": "Elegant flared cotton anarkali paired with matching churidar and dupatta with delicate golden gota patti accents.",
        "is_prime": 1
    },
    {
        "sku": "FASH-FOS-013",
        "title": "Fossil Grant Chronograph Navy Blue Dial Men's Leather Watch",
        "category": "Fashion",
        "price": 9495.0,
        "original_price": 14495.0,
        "stock_quantity": 38,
        "rating": 4.7,
        "rating_count": 7100,
        "image_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=600&auto=format&fit=crop&q=80",
        "description": "Modeled after vintage clocks, this timepiece has Roman numeral hour markers with a modern dark blue dial and rich brown leather strap.",
        "is_prime": 1
    },
    {
        "sku": "FASH-LAV-014",
        "title": "Lavie Women's Monisa Structured Faux Leather Satchel Handbag",
        "category": "Fashion",
        "price": 1499.0,
        "original_price": 3999.0,
        "stock_quantity": 88,
        "rating": 4.3,
        "rating_count": 4500,
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80",
        "description": "Premium saffiano-textured vegan leather, spacious multi-compartment design, dual top handles, and detachable adjustable shoulder strap.",
        "is_prime": 1
    },
    {
        "sku": "FASH-RAY-015",
        "title": "Ray-Ban Classic Polarized Green Classic G-15 Aviator Sunglasses",
        "category": "Fashion",
        "price": 8290.0,
        "original_price": 10590.0,
        "stock_quantity": 40,
        "rating": 4.7,
        "rating_count": 3100,
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=80",
        "description": "Iconic pilot shape, durable gold metal frame, and polarized crystal lenses that absorb 85% of visible light and block UV.",
        "is_prime": 1
    },
    {
        "sku": "FASH-FAS-016",
        "title": "Fastrack Limitless FS1 Pro Smartwatch with 1.96-inch Super AMOLED Arched Display",
        "category": "Fashion",
        "price": 2999.0,
        "original_price": 7995.0,
        "stock_quantity": 110,
        "rating": 4.2,
        "rating_count": 11200,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80",
        "description": "SingleSync Bluetooth calling, NitroFast charging, 110+ sports modes, and 200+ watch faces.",
        "is_prime": 1
    },

    # --- HOME & KITCHEN ---
    {
        "sku": "HOME-PHI-017",
        "title": "Philips Daily Collection HL7756/00 750W Mixer Grinder with 3 Stainless Steel Jars",
        "category": "Home & Kitchen",
        "price": 3299.0,
        "original_price": 5295.0,
        "stock_quantity": 65,
        "rating": 4.4,
        "rating_count": 34100,
        "image_url": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&auto=format&fit=crop&q=80",
        "description": "Tough 750W Turbo motor with advanced air ventilation system for rapid cooling and continuous grinding of hard ingredients like turmeric.",
        "is_prime": 1
    },
    {
        "sku": "HOME-INS-018",
        "title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker, Slow Cooker, Rice Cooker (6 Litre)",
        "category": "Home & Kitchen",
        "price": 8990.0,
        "original_price": 13990.0,
        "stock_quantity": 35,
        "rating": 4.7,
        "rating_count": 8900,
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=80",
        "description": "7 appliances in 1: pressure cook, slow cook, rice cooker, yogurt maker, steamer, sauté pan, and food warmer with 13 one-touch smart programs.",
        "is_prime": 1
    },
    {
        "sku": "HOME-PIG-019",
        "title": "Pigeon by Stovekraft Cruise 1800W Induction Cooktop with 7 Preset Indian Menus",
        "category": "Home & Kitchen",
        "price": 1699.0,
        "original_price": 3195.0,
        "stock_quantity": 90,
        "rating": 4.2,
        "rating_count": 52000,
        "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80",
        "description": "High-grade electrical that protects against short circuits, dual heat sensor technology, and smart LED display.",
        "is_prime": 1
    },
    {
        "sku": "HOME-DYS-020",
        "title": "Dyson V8 Absolute Cordless Vacuum Cleaner with De-tangling Technology",
        "category": "Home & Kitchen",
        "price": 29900.0,
        "original_price": 43900.0,
        "stock_quantity": 25,
        "rating": 4.8,
        "rating_count": 6700,
        "image_url": "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600&auto=format&fit=crop&q=80",
        "description": "Powerful, versatile, and low noise cordless cleaning with 40 minutes of fade-free suction and Motorbar cleaner head.",
        "is_prime": 1
    },
    {
        "sku": "HOME-MIL-021",
        "title": "Milton Thermosteel Flip Lid Vacuum Insulated Flask Water Bottle (1000 ml)",
        "category": "Home & Kitchen",
        "price": 949.0,
        "original_price": 1285.0,
        "stock_quantity": 150,
        "rating": 4.5,
        "rating_count": 68000,
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80",
        "description": "Double walled vacuum insulation maintains hot and cold beverage temperatures for 24 hours, crafted with 100% rust-free stainless steel.",
        "is_prime": 1
    },
    {
        "sku": "HOME-SOL-022",
        "title": "Amazon Brand - Solimo 100% Cotton 500 GSM 2-Piece Plush Bath Towel Set",
        "category": "Home & Kitchen",
        "price": 799.0,
        "original_price": 1400.0,
        "stock_quantity": 130,
        "rating": 4.3,
        "rating_count": 29000,
        "image_url": "https://images.unsplash.com/photo-1616627547584-bf28cee262db?w=600&auto=format&fit=crop&q=80",
        "description": "Extra soft, super absorbent combed cotton bath towels with double-stitched hems for high durability and fade-resistant color.",
        "is_prime": 1
    },
    {
        "sku": "HOME-SLE-023",
        "title": "SleepyCat Original 6-Inch Orthopedic Memory Foam Medium-Firm Mattress",
        "category": "Home & Kitchen",
        "price": 11499.0,
        "original_price": 16999.0,
        "stock_quantity": 28,
        "rating": 4.6,
        "rating_count": 4800,
        "image_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600&auto=format&fit=crop&q=80",
        "description": "Engineered for spinal alignment with open-cell memory foam and bamboo fabric zipper cover with machine washable ease.",
        "is_prime": 1
    },
    {
        "sku": "HOME-PRE-024",
        "title": "Prestige Iris Plus 750 Watt Mixer Grinder with 4 Multi-Utility Stainless Steel Jars",
        "category": "Home & Kitchen",
        "price": 2899.0,
        "original_price": 6295.0,
        "stock_quantity": 80,
        "rating": 4.2,
        "rating_count": 39500,
        "image_url": "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=600&auto=format&fit=crop&q=80",
        "description": "Equipped with heavy-duty motor, superior grade stainless steel jars, ergonomic handles, and transparent juice extractor jar.",
        "is_prime": 1
    },

    # --- GROCERY ---
    {
        "sku": "GROC-TAT-025",
        "title": "Tata Tea Gold Leaf Black Tea with Gently Rolled Aromatic Leaves (1 kg)",
        "category": "Grocery",
        "price": 549.0,
        "original_price": 660.0,
        "stock_quantity": 200,
        "rating": 4.6,
        "rating_count": 41200,
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80",
        "description": "An exquisite blend of premium Assam CTC teas with 15% gently rolled long leaves for an irresistible aroma and rich flavor.",
        "is_prime": 1
    },
    {
        "sku": "GROC-DAA-026",
        "title": "Daawat Rozana Super Basmati Rice with Rich Natural Aroma (5 kg)",
        "category": "Grocery",
        "price": 449.0,
        "original_price": 599.0,
        "stock_quantity": 175,
        "rating": 4.5,
        "rating_count": 32000,
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        "description": "Finest aged basmati grains with delicate aroma and fluffy texture, ideal for everyday biryani, pulao, and steam rice.",
        "is_prime": 1
    },
    {
        "sku": "GROC-FOR-027",
        "title": "Fortune Sunlite Refined Sunflower Oil Jar with Vitamin A & D (5 Litre)",
        "category": "Grocery",
        "price": 799.0,
        "original_price": 999.0,
        "stock_quantity": 110,
        "rating": 4.5,
        "rating_count": 28400,
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
        "description": "Light, healthy, and easy to digest refined sunflower oil packed with natural tocopherols to support heart wellness.",
        "is_prime": 1
    },
    {
        "sku": "GROC-FER-028",
        "title": "Ferrero Rocher Premium Crispy Hazelnut & Milk Chocolate Gift Box (16 Pieces)",
        "category": "Grocery",
        "price": 529.0,
        "original_price": 595.0,
        "stock_quantity": 90,
        "rating": 4.8,
        "rating_count": 19500,
        "image_url": "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=600&auto=format&fit=crop&q=80",
        "description": "A whole crunchy hazelnut wrapped in creamy filling, encased in crisp wafer, dipped in smooth milk chocolate and finely chopped hazelnuts.",
        "is_prime": 1
    },
    {
        "sku": "GROC-KEL-029",
        "title": "Kellogg's Corn Flakes Original High-Iron Breakfast Cereal (1.2 kg Value Pack)",
        "category": "Grocery",
        "price": 389.0,
        "original_price": 450.0,
        "stock_quantity": 140,
        "rating": 4.4,
        "rating_count": 21000,
        "image_url": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600&auto=format&fit=crop&q=80",
        "description": "Naturally cholesterol free crispy golden corn flakes enriched with essential B-group vitamins and iron for an energized start.",
        "is_prime": 1
    },
    {
        "sku": "GROC-NES-030",
        "title": "Nescafe Classic 100% Pure Instant Coffee Glass Jar (200 g)",
        "category": "Grocery",
        "price": 499.0,
        "original_price": 590.0,
        "stock_quantity": 160,
        "rating": 4.6,
        "rating_count": 36700,
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
        "description": "Crafted from fine Robusta and Arabica coffee beans, slow-roasted to deliver that unmistakably bold signature aroma.",
        "is_prime": 1
    },
    {
        "sku": "GROC-HAP-031",
        "title": "Happilo 100% Natural Premium California Raw Almonds (500 g Value Pack)",
        "category": "Grocery",
        "price": 429.0,
        "original_price": 695.0,
        "stock_quantity": 125,
        "rating": 4.5,
        "rating_count": 48900,
        "image_url": "https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=600&auto=format&fit=crop&q=80",
        "description": "Crisp, wholesome California badam packed with dietary fiber, plant protein, and healthy monounsaturated fatty acids.",
        "is_prime": 1
    },
    {
        "sku": "GROC-NUT-032",
        "title": "Nutella Creamy Hazelnut Spread with Cocoa (750 g Jar)",
        "category": "Grocery",
        "price": 649.0,
        "original_price": 750.0,
        "stock_quantity": 95,
        "rating": 4.8,
        "rating_count": 31000,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80",
        "description": "Iconic rich hazelnut spread made with quality skimmed milk and cocoa, perfect for breakfast toast, pancakes, and fruit.",
        "is_prime": 1
    },

    # --- BEAUTY ---
    {
        "sku": "BEAU-LOR-033",
        "title": "L'Oreal Paris Total Repair 5 Damaged Hair Repairing Shampoo (650 ml)",
        "category": "Beauty",
        "price": 499.0,
        "original_price": 799.0,
        "stock_quantity": 115,
        "rating": 4.4,
        "rating_count": 42000,
        "image_url": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=600&auto=format&fit=crop&q=80",
        "description": "Enriched with Ceramide-Cement technology to combat hair fall, dryness, roughness, dullness, and split ends.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-MIN-034",
        "title": "Minimalist 10% Niacinamide Face Serum with Zinc for Blemishes & Oil Balancing (30 ml)",
        "category": "Beauty",
        "price": 599.0,
        "original_price": 699.0,
        "stock_quantity": 95,
        "rating": 4.6,
        "rating_count": 27800,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80",
        "description": "Nourishing daily face serum packed with pure 10% Vitamin B3 and 1% Zinc PCA to visibly reduce acne marks and refine pore texture.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-MAY-035",
        "title": "Maybelline New York Colossal Bold Smudgeproof Kajal & Hypercurl Mascara Combo",
        "category": "Beauty",
        "price": 449.0,
        "original_price": 799.0,
        "stock_quantity": 130,
        "rating": 4.5,
        "rating_count": 39000,
        "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop&q=80",
        "description": "Up to 24-hour waterproof intense black eyeliner and lash curler combo for dramatic volume without clumping.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-CET-036",
        "title": "Cetaphil Gentle Skin Hydrating Cleanser for Dry to Sensitive Skin (250 ml)",
        "category": "Beauty",
        "price": 549.0,
        "original_price": 649.0,
        "stock_quantity": 85,
        "rating": 4.7,
        "rating_count": 33100,
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
        "description": "Dermatologist-recommended non-foaming hydrating formula infused with niacinamide, panthenol, and hydrating glycerin.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-DER-037",
        "title": "The Derma Co 1% Hyaluronic Sunscreen Aqua Gel with SPF 50 & PA++++ (50 g)",
        "category": "Beauty",
        "price": 449.0,
        "original_price": 499.0,
        "stock_quantity": 105,
        "rating": 4.5,
        "rating_count": 21400,
        "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&auto=format&fit=crop&q=80",
        "description": "Ultra-lightweight, non-greasy sunscreen with 1% hyaluronic acid, vitamin E, and broad-spectrum blue light protection.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-FOR-038",
        "title": "Forest Essentials Pure Rosewater Facial Tonic & Hydrating Body Mist (130 ml)",
        "category": "Beauty",
        "price": 1475.0,
        "original_price": 1650.0,
        "stock_quantity": 45,
        "rating": 4.7,
        "rating_count": 8900,
        "image_url": "https://images.unsplash.com/photo-1608248597359-54b38d6df4d5?w=600&auto=format&fit=crop&q=80",
        "description": "Steam distilled from fresh Kannauj roses to naturally hydrate, cool, and re-balance facial skin glow.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-NIV-039",
        "title": "Nivea Men Dark Spot Reduction Vitamin C Non-Greasy Moisturizer Cream (150 ml)",
        "category": "Beauty",
        "price": 279.0,
        "original_price": 399.0,
        "stock_quantity": 140,
        "rating": 4.4,
        "rating_count": 25400,
        "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=80",
        "description": "Light, fast-absorbing daily face cream with UV filters to protect against hyperpigmentation and oil buildup.",
        "is_prime": 1
    },
    {
        "sku": "BEAU-BIO-040",
        "title": "Biotique Bio Kelp Fresh Growth Protein Anti-Hairfall Shampoo (650 ml)",
        "category": "Beauty",
        "price": 399.0,
        "original_price": 630.0,
        "stock_quantity": 100,
        "rating": 4.3,
        "rating_count": 18700,
        "image_url": "https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=600&auto=format&fit=crop&q=80",
        "description": "Therapeutic blend of pure kelp, natural barks, peppermint oil, and mint extract to gently cleanse and invigorate hair follicles.",
        "is_prime": 1
    }
]

def seed_database():
    print("[Seed Store] Refreshing store-specific tables...")
    try:
        OrderItem.__table__.drop(bind=engine, checkfirst=True)
        Order.__table__.drop(bind=engine, checkfirst=True)
        Product.__table__.drop(bind=engine, checkfirst=True)
        StoreUser.__table__.drop(bind=engine, checkfirst=True)
    except Exception as e:
        print(f"[Seed Store] Note on table drop: {e}")

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # 1. Seed or Update Products
        print(f"[Seed Store] Checking {len(SAMPLE_PRODUCTS)} catalog products...")
        added_products = 0
        updated_products = 0

        for item in SAMPLE_PRODUCTS:
            prod = db.query(Product).filter((Product.sku == item["sku"]) | (Product.title == item["title"])).first()
            if not prod:
                new_p = Product(
                    sku=item["sku"],
                    title=item["title"],
                    product_name=item["title"],
                    category=item["category"],
                    price=item["price"],
                    original_price=item["original_price"],
                    stock_quantity=item["stock_quantity"],
                    rating=item["rating"],
                    rating_count=item["rating_count"],
                    image_url=item["image_url"],
                    description=item["description"],
                    is_prime=item["is_prime"],
                    is_active=1
                )
                db.add(new_p)
                added_products += 1
            else:
                prod.sku = item["sku"]
                prod.title = item["title"]
                prod.product_name = item["title"]
                prod.category = item["category"]
                prod.price = item["price"]
                prod.original_price = item["original_price"]
                prod.stock_quantity = item["stock_quantity"]
                prod.rating = item["rating"]
                prod.rating_count = item["rating_count"]
                prod.image_url = item["image_url"]
                prod.description = item["description"]
                prod.is_prime = item["is_prime"]
                prod.is_active = 1
                updated_products += 1

        db.commit()
        print(f"[Seed Store] Products: {added_products} created, {updated_products} updated.")

        # 2. Seed Store User Accounts
        # A. Admin Account
        admin_pw = hash_pw("admin123")
        admin_user = db.query(StoreUser).filter(StoreUser.username == "admin@smartcart.com").first()
        if not admin_user:
            db.add(StoreUser(
                username="admin@smartcart.com",
                password_hash=admin_pw,
                role="admin",
                full_name="SmartCart Platform Administrator"
            ))
            # Also create alias 'admin'
            db.add(StoreUser(
                username="admin",
                password_hash=admin_pw,
                role="admin",
                full_name="Administrator"
            ))
            print("[Seed Store] Admin accounts created (admin@smartcart.com / admin123 and admin / admin123).")

        # B. Product Manager Account
        pm_pw = hash_pw("manager123")
        pm_user = db.query(StoreUser).filter(StoreUser.username == "pm@smartcart.com").first()
        if not pm_user:
            db.add(StoreUser(
                username="pm@smartcart.com",
                password_hash=pm_pw,
                role="product_manager",
                full_name="SmartCart Product Manager"
            ))
            # Also create alias 'manager'
            db.add(StoreUser(
                username="manager",
                password_hash=pm_pw,
                role="product_manager",
                full_name="Catalog Manager"
            ))
            print("[Seed Store] Product Manager accounts created (pm@smartcart.com / manager123 and manager / manager123).")

        # C. Customer Accounts (Unique customer_id as username, customer123 as password)
        customers = db.query(Customer).all()
        print(f"[Seed Store] Found {len(customers)} customers in database to provision store credentials for...")
        cust_pw = hash_pw("customer123")
        cust_created = 0

        for c in customers:
            uname = str(c.source_customer_id).strip()
            existing_user = db.query(StoreUser).filter(StoreUser.username == uname).first()
            if not existing_user:
                new_u = StoreUser(
                    username=uname,
                    password_hash=cust_pw,
                    role="customer",
                    customer_id=c.id,
                    full_name=f"Customer {uname}"
                )
                db.add(new_u)
                cust_created += 1
            else:
                existing_user.password_hash = cust_pw
                existing_user.customer_id = c.id
                existing_user.role = "customer"

        db.commit()
        print(f"[Seed Store] Customer store credentials: {cust_created} new accounts provisioned with password 'customer123'.")

        total_users = db.query(StoreUser).count()
        total_products = db.query(Product).count()
        print(f"[Seed Store] Complete! Total Store Products: {total_products}, Total Store Users: {total_users}")

    except Exception as e:
        db.rollback()
        print(f"[Seed Store Error] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
