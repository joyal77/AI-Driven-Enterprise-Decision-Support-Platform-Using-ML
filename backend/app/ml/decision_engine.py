"""
decision_engine.py

Generates transparent, rule-based e-commerce retention recommendations,
explainable AI (xAI) root-cause diagnostics, and actionable countermeasures
to overcome churn friction drivers.
"""

from typing import List, Dict, Any

def extract_detailed_root_causes(customer_obj, risk_category: str = "High Risk") -> List[Dict[str, Any]]:
    """
    xAI Root Cause Diagnostics:
    Extracts individual customer friction drivers, severity tiers, observed metrics,
    analytical descriptions, and precise 'How to Overcome' prescriptive countermeasures.
    """
    tickets = getattr(customer_obj, 'customer_service_tickets', 0) or 0
    days_since_purchase = getattr(customer_obj, 'days_since_last_purchase', None)
    membership = str(getattr(customer_obj, 'membership_status', '') or '').lower()
    cart_abandonments = getattr(customer_obj, 'cart_abandonments_last_30d', 0) or 0
    total_orders = getattr(customer_obj, 'total_orders_lifetime', 0) or 0
    sessions = getattr(customer_obj, 'sessions_last_30d', 0) or 0
    late_deliveries = getattr(customer_obj, 'late_deliveries_count', 0) or 0
    returns = getattr(customer_obj, 'return_count', 0) or 0
    return_rate = getattr(customer_obj, 'return_rate', 0.0) or 0.0
    cancellations = getattr(customer_obj, 'cancellations_count', 0) or 0
    rating = getattr(customer_obj, 'avg_rating_given', 0) or 0.0
    category = getattr(customer_obj, 'preferred_category', 'General') or 'General'
    aov = getattr(customer_obj, 'avg_order_value', 500.0) or 500.0
    signup_date = getattr(customer_obj, 'signup_date', None)

    # Low Risk accounts: Healthy standing with optimal metrics. Do not trigger emergency friction interventions.
    if risk_category == "Low Risk":
        return [{
            "id": "low_risk_healthy_standing",
            "title": "Healthy Engagement & Category Affinity",
            "metric": f"Consistent shopping activity in {category}",
            "severity": "Low",
            "weight": 1.0,
            "description": f"Customer maintains steady purchasing habits and positive sentiment in {category}. Churn probability is low with no critical friction drivers.",
            "how_to_overcome": f"Maintain routine brand presence with simple targeted Sponsored Product Ads and seasonal {category} category promotions."
        }]

    detailed_causes = []

    # 1. Zero Lifetime Orders (New Registered Account Unactivated)
    if total_orders == 0:
        date_str = str(signup_date) if signup_date else "recently"
        detailed_causes.append({
            "id": "zero_orders_unactivated",
            "title": "New Account Onboarding & Activation Gap",
            "metric": "0 lifetime orders placed (Account Unactivated)",
            "severity": "High" if risk_category == "High Risk" else "Medium",
            "weight": 8.0,
            "description": f"Customer registered on {date_str} but has not yet completed their initial purchase. High attrition risk without targeted first-order onboarding incentives.",
            "how_to_overcome": f"Deploy automated First-Order Welcome Onboarding series with a 10% welcome discount coupon (Code: WELCOME10) and Free Delivery on {category} items."
        })

    # 2. Support Ticket Grievances
    if tickets >= 3:
        detailed_causes.append({
            "id": "customer_support_high",
            "title": "Customer Service & Grievance Overload",
            "metric": f"{tickets} support tickets filed",
            "severity": "High",
            "weight": float(tickets) * 2.5,
            "description": "Repeated customer inquiries and dissatisfaction tickets indicate unsolved platform friction or order dissatisfaction.",
            "how_to_overcome": "Assign a dedicated Tier-2 VIP Support Concierge to execute an immediate resolution callback within 4 hours, resolve open tickets, and grant an exclusive 10% grievance resolution voucher (Code: CARE10)."
        })
    elif tickets >= 1:
        detailed_causes.append({
            "id": "customer_support_med",
            "title": "Open Inquiries & Service Friction",
            "metric": f"{tickets} support ticket{'s' if tickets > 1 else ''} filed",
            "severity": "Medium",
            "weight": float(tickets) * 1.5,
            "description": "Customer has active inquiries requiring resolution to maintain shopping confidence.",
            "how_to_overcome": "Initiate proactive customer care ticket review with a 5% courtesy coupon to ensure satisfactory ticket closure within 24 hours."
        })

    # 3. High Cart Abandonment
    if cart_abandonments >= 3:
        detailed_causes.append({
            "id": "cart_abandonment_high",
            "title": "High Cart Abandonment Friction",
            "metric": f"{cart_abandonments} carts abandoned (last 30d)",
            "severity": "High" if cart_abandonments >= 5 else "Medium",
            "weight": float(cart_abandonments) * 1.6,
            "description": "Customer repeatedly adds merchandise to cart but exits before completing checkout, indicating price sensitivity or shipping cost barriers.",
            "how_to_overcome": "Send automated customer recovery message within 2 hours offering an instant 10% discount coupon (Code: RECOVER10), Free Delivery, and 1-click checkout recovery."
        })
    elif cart_abandonments >= 1 and total_orders > 0:
        detailed_causes.append({
            "id": "cart_abandonment_med",
            "title": "Pending Cart Hesitation",
            "metric": f"{cart_abandonments} abandoned cart{'s' if cart_abandonments > 1 else ''} (last 30d)",
            "severity": "Low",
            "weight": float(cart_abandonments) * 0.8,
            "description": "Customer left items in shopping cart. A gentle reminder can convert pending interest into completed orders.",
            "how_to_overcome": "Send timely in-app reminder offering 5% discount and limited-time Free Delivery on cart items."
        })

    # 4. Fulfillment & Late Deliveries
    if late_deliveries >= 1:
        detailed_causes.append({
            "id": "late_delivery",
            "title": "Fulfillment Friction (Late Deliveries)",
            "metric": f"{late_deliveries} late deliver{'ies' if late_deliveries > 1 else 'y'} recorded",
            "severity": "High" if late_deliveries >= 2 else "Medium",
            "weight": float(late_deliveries) * 2.0,
            "description": "Delayed shipments directly erode customer trust and prompt buyers to look for faster competing e-commerce alternatives.",
            "how_to_overcome": "Permanently route all future orders through SmartCart Express Air Priority Logistics (Free ₹0 Shipping) and grant an instant 5% delay apology discount coupon (Code: SPEED5)."
        })

    # 5. Inactivity & Purchase Recency (Only for customers with past purchases)
    if total_orders > 0 and days_since_purchase is not None:
        if days_since_purchase > 90:
            detailed_causes.append({
                "id": "recency_dormancy_high",
                "title": "Extended Dormancy & Lapsed Purchasing Rhythms",
                "metric": f"{int(days_since_purchase)} days since last purchase",
                "severity": "High",
                "weight": float(days_since_purchase) / 15.0,
                "description": "Purchase lapsed significantly beyond expected reorder cycles; customer is at imminent risk of moving to competitors.",
                "how_to_overcome": f"Deploy AI-driven win-back re-engagement email sequence showcasing top-rated new arrivals in {category} with an exclusive 15% 'Welcome Back' voucher."
            })
        elif days_since_purchase > 45:
            detailed_causes.append({
                "id": "recency_dormancy_med",
                "title": "Purchase Interval Slowdown",
                "metric": f"{int(days_since_purchase)} days since last purchase",
                "severity": "Medium",
                "weight": float(days_since_purchase) / 25.0,
                "description": "Slight slowdown in purchase rhythm compared to historical baseline.",
                "how_to_overcome": f"Deliver personalized seasonal showcase in {category} to stimulate re-order interest."
            })

    # 6. Frequent Returns & Replacements
    if returns >= 2 or (total_orders > 0 and return_rate >= 0.25):
        rate_pct = f"{(return_rate * 100):.1f}%" if return_rate else "elevated"
        detailed_causes.append({
            "id": "returns_friction",
            "title": "High Return & Replacement Frequency",
            "metric": f"{returns} items returned ({rate_pct} return rate)",
            "severity": "Medium",
            "weight": float(returns) * 1.4,
            "description": "Customer has experienced multiple product mismatches or satisfaction issues, increasing platform fatigue.",
            "how_to_overcome": "Provide detailed specifications before checkout and offer VIP doorstep exchange with instant quality verification."
        })

    # 7. Order Cancellations
    if cancellations >= 2:
        detailed_causes.append({
            "id": "cancellations_friction",
            "title": "Frequent Order Cancellations",
            "metric": f"{cancellations} orders cancelled",
            "severity": "High",
            "weight": float(cancellations) * 2.2,
            "description": "Buyer remorse or delivery timeframe dissatisfaction leading to cancelled transactions post-order placement.",
            "how_to_overcome": "Offer pre-checkout delivery confirmation times and immediate order modification features instead of forced full order cancellations."
        })

    # 8. Unfavorable Review Rating
    if 0 < rating <= 3.0:
        detailed_causes.append({
            "id": "low_rating",
            "title": "Negative Customer Sentiment & Low Ratings",
            "metric": f"{rating:.1f} / 5.0 average stars given",
            "severity": "High" if rating <= 2.0 else "Medium",
            "weight": (5.0 - rating) * 2.0,
            "description": "Customer expressed dissatisfaction with past product quality or packaging condition.",
            "how_to_overcome": "Customer Experience Director outreach via email with personalized apology and replacement product guarantee."
        })

    # 9. Low Browsing Frequency (Only if total_orders > 0)
    if total_orders > 0 and sessions <= 2:
        detailed_causes.append({
            "id": "low_sessions",
            "title": "Low Storefront Browsing Engagement",
            "metric": f"{sessions} app sessions in last 30d",
            "severity": "Low",
            "weight": 2.0,
            "description": "Minimal engagement with storefront apps or website, signaling slipping mindshare.",
            "how_to_overcome": "Deliver personalized app push notifications during peak browsing windows highlighting flash deals and trending products."
        })

    # 10. Membership Inactivity
    if membership in ['none', 'expired', 'standard', ''] and total_orders >= 1:
        detailed_causes.append({
            "id": "membership_tier",
            "title": "Standard / Non-Prime Membership Status",
            "metric": "No active Prime membership",
            "severity": "Low",
            "weight": 1.5,
            "description": "Lack of Prime membership increases shipping friction and lowers lifetime buying frequency.",
            "how_to_overcome": "Offer a complimentary 30-day SmartCart Prime trial featuring Free One-Day Delivery and exclusive early-access festival sales."
        })

    # Sort descending by severity weight
    detailed_causes.sort(key=lambda x: x["weight"], reverse=True)

    # Fallback for accounts with no detected friction points
    if not detailed_causes:
        if total_orders == 0:
            detailed_causes.append({
                "id": "unactivated_account",
                "title": "New Account Awaiting Activation",
                "metric": "0 orders placed",
                "severity": "Medium",
                "weight": 2.0,
                "description": "Account created but no purchases recorded yet. Welcome campaign recommended.",
                "how_to_overcome": f"Send welcome onboarding coupon for initial checkout in {category}."
            })
        elif risk_category == "High Risk":
            detailed_causes.append({
                "id": "general_risk",
                "title": "Multi-Factor Behavioral Anomaly",
                "metric": "Elevated churn risk score",
                "severity": "High",
                "weight": 4.0,
                "description": "Cross-dimensional feature combination indicates elevated risk of churn.",
                "how_to_overcome": "Dispatch VIP personalized concierge survey and exclusive 15% customer loyalty appreciation discount coupon (Code: VIP15)."
            })
        elif risk_category == "Medium Risk":
            detailed_causes.append({
                "id": "general_moderate",
                "title": "Moderate Behavioral Activity Decline",
                "metric": "Borderline risk metrics",
                "severity": "Medium",
                "weight": 2.0,
                "description": "Slight slowdown in purchase rhythm compared to historical baseline.",
                "how_to_overcome": f"Enroll in seasonal retention campaigns and {category} category promotional events."
            })
        else:
            detailed_causes.append({
                "id": "low_risk_standing",
                "title": "Healthy Customer Standing",
                "metric": "Optimal engagement metrics",
                "severity": "Low",
                "weight": 1.0,
                "description": "Strong customer lifetime value, steady order frequency, and positive sentiment.",
                "how_to_overcome": "Maintain engagement with VIP customer rewards, milestone loyalty badges, and personalized cross-sell recommendations."
            })

    return detailed_causes

def generate_structured_retention_plan(customer_obj, risk_category: str = "High Risk", churn_probability: float = 0.0, detailed_causes: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Constructs a rich, cohesive Amazon Seller Central Retention Campaign Plan
    directly aligned with the customer's actual behavioral root causes.
    """
    category = getattr(customer_obj, 'preferred_category', 'General') or 'General'

    # Low Risk accounts: Simple lightweight targeted sponsored product ads retention plan only
    if risk_category == "Low Risk":
        return [
            {
                "id": "camp_sponsored_ads_retention",
                "title": f"Targeted Sponsored Product Ads & Category Showcase ({category})",
                "channel": "Digital Ads (In-App Sponsored Placements & Search Ads)",
                "priority": "Low Touch",
                "status": "Ready for Review",
                "root_cause_driver": f"Low Risk Engagement & {category} Category Affinity",
                "perk_type": "sponsored_ads",
                "perk_value": 0.0,
                "coupon_code": None,
                "perk_display": f"Targeted {category} Sponsored Product Ads & In-App Discovery Banners",
                "objective": f"Serve lightweight sponsored product ads and featured bestsellers in {category} to maintain top-of-mind brand presence without unnecessary promotional cost.",
                "action_summary": f"Sponsored Product Ads: Targeted digital ad placements showcasing trending {category} products."
            }
        ]

    if detailed_causes is None:
        detailed_causes = extract_detailed_root_causes(customer_obj, risk_category)

    membership = str(getattr(customer_obj, 'membership_status', '') or '').lower()
    total_orders = getattr(customer_obj, 'total_orders_lifetime', 0) or 0
    aov = getattr(customer_obj, 'avg_order_value', 500.0) or 500.0

    plan = []
    seen_strategies = set()

    # Map each identified root cause directly to an operational campaign action
    for rc in detailed_causes:
        cid = rc.get("id", "")
        driver_str = f"{rc.get('title', 'Risk Factor')} ({rc.get('metric', 'Observed Friction')})"

        if cid in ["customer_support_high", "customer_support_med"] and "support" not in seen_strategies:
            seen_strategies.add("support")
            plan.append({
                "id": "camp_support_vip",
                "title": "Priority VIP Support Concierge Callback & 10% Resolution Coupon",
                "channel": "VIP Concierge (Phone / Priority Callback)",
                "priority": "Critical" if rc.get("severity") == "High" else "High Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "discount_voucher",
                "perk_value": 10.0,
                "coupon_code": "CARE10",
                "free_shipping": False,
                "perk_display": "10% Grievance Resolution Voucher (Code: CARE10) + Dedicated VIP Concierge",
                "objective": f"Direct outreach within 4 hours to resolve {rc.get('metric')} and grant an exclusive 10% resolution voucher (Code: CARE10) on next checkout.",
                "action_summary": "Support Concierge Callback: Resolve open tickets and issue 10% discount voucher (CARE10)."
            })

        elif cid in ["cart_abandonment_high", "cart_abandonment_med"] and "cart" not in seen_strategies:
            seen_strategies.add("cart")
            plan.append({
                "id": "camp_cart_recovery",
                "title": "Automated Cart Recovery with Free Delivery",
                "channel": "Customer Account Messages",
                "priority": "High Priority" if rc.get("severity") == "High" else "Medium Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "discount_voucher",
                "perk_value": 10.0,
                "coupon_code": "RECOVER10",
                "free_shipping": True,
                "perk_display": "10% Off Cart Voucher (Code: RECOVER10) + Free Express Air Shipping",
                "objective": f"Recover {rc.get('metric')} via instant customer account message offering Free Shipping and 10% checkout discount.",
                "action_summary": "Cart Recovery Message: Send 10% coupon (RECOVER10) & Free Delivery to customer account messages."
            })

        elif cid == "late_delivery" and "logistics" not in seen_strategies:
            seen_strategies.add("logistics")
            plan.append({
                "id": "camp_logistics_guarantee",
                "title": "Free Express Air Priority Delivery & 5% Delay Apology Coupon",
                "channel": "Express Air Logistics & Apology Coupon",
                "priority": "High Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "express_shipping",
                "perk_value": 5.0,
                "coupon_code": "SPEED5",
                "free_shipping": True,
                "perk_display": "Free Express Air Priority Delivery (₹0 Shipping) + 5% Delay Apology Coupon (Code: SPEED5)",
                "objective": f"Compensate for {rc.get('metric')} with permanent Express Air Free Delivery (₹0 Shipping) and an instant 5% apology discount coupon.",
                "action_summary": "Fulfillment Guarantee: Permanent Express Air Free Delivery upgrade & 5% apology coupon (SPEED5)."
            })

        elif cid in ["recency_dormancy_high", "recency_dormancy_med"] and "dormancy" not in seen_strategies:
            seen_strategies.add("dormancy")
            plan.append({
                "id": "camp_winback_email",
                "title": f"Targeted Win-Back Re-engagement Campaign ({category})",
                "channel": "Email & Personalized Storefront Digest",
                "priority": "High Priority" if rc.get("severity") == "High" else "Medium Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "discount_voucher",
                "perk_value": 15.0,
                "coupon_code": "WINBACK15",
                "free_shipping": True,
                "perk_display": "15% Win-Back Discount Voucher (Code: WINBACK15) + Free Delivery",
                "objective": f"Lapsed purchase re-engagement showcasing curated top-rated bestsellers in {category} with an exclusive 15% discount and Free Delivery.",
                "action_summary": f"Win-Back Campaign: Curated {category} showcase with 15% 'Welcome Back' voucher (WINBACK15)."
            })

        elif cid in ["zero_orders_unactivated", "unactivated_account"] and "activation" not in seen_strategies:
            seen_strategies.add("activation")
            plan.append({
                "id": "camp_welcome_activation",
                "title": f"First-Order Welcome Activation Series ({category})",
                "channel": "Email & In-App Welcome Banner",
                "priority": "High Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "discount_voucher",
                "perk_value": 10.0,
                "coupon_code": "WELCOME10",
                "free_shipping": True,
                "perk_display": "10% First-Order Welcome Voucher (Code: WELCOME10) + Free Delivery",
                "objective": f"Convert registered non-buyer with 10% welcome coupon (WELCOME10) and Free Delivery on first order in {category}.",
                "action_summary": f"Welcome Onboarding: Offer 10% instant discount (WELCOME10) + Free Delivery on initial order in {category}."
            })

        elif cid == "returns_friction" and "returns" not in seen_strategies:
            seen_strategies.add("returns")
            plan.append({
                "id": "camp_doorstep_exchange",
                "title": "VIP Doorstep Hassle-Free Exchange & 5% Courtesy Coupon",
                "channel": "Customer Care & Courier Logistics",
                "priority": "Medium Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "discount_voucher",
                "perk_value": 5.0,
                "coupon_code": "EASY5",
                "free_shipping": False,
                "perk_display": "5% Courtesy Coupon (Code: EASY5) + VIP Doorstep Exchange Privilege",
                "objective": "Mitigate return fatigue by offering instant doorstep verification and a 5% courtesy coupon.",
                "action_summary": "Doorstep VIP Exchange: Seamless product swap without return processing delays + 5% coupon (EASY5)."
            })

        elif cid == "cancellations_friction" and "cancellations" not in seen_strategies:
            seen_strategies.add("cancellations")
            plan.append({
                "id": "camp_order_modification",
                "title": "Flexible Pre-Dispatch Order Modification & Free Delivery Guarantee",
                "channel": "Storefront Order Management",
                "priority": "High Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "express_shipping",
                "perk_value": 0.0,
                "coupon_code": "FLEXFREE",
                "free_shipping": True,
                "perk_display": "Free Express Priority Delivery (Code: FLEXFREE) & 1-Click Order Edits",
                "objective": "Allow customers to modify delivery timeframes and items rather than cancelling orders outright, with free delivery guaranteed.",
                "action_summary": "Order Flexibility: Offer 1-click delivery rescheduling & free delivery to prevent order cancellations."
            })

        elif cid == "low_rating" and "sentiment" not in seen_strategies:
            seen_strategies.add("sentiment")
            plan.append({
                "id": "camp_sentiment_recovery",
                "title": "Customer Experience Director Direct Apology & 10% Courtesy Coupon",
                "channel": "Executive Email Outreach",
                "priority": "High Priority",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "discount_voucher",
                "perk_value": 10.0,
                "coupon_code": "CARE10",
                "free_shipping": False,
                "perk_display": "10% Courtesy Discount Voucher (Code: CARE10) + Executive Care Outreach",
                "objective": "Direct personalized outreach addressing dissatisfaction with an exclusive 10% courtesy coupon and satisfaction guarantee.",
                "action_summary": "Executive Sentiment Care: Personalized apology email with 10% courtesy coupon (CARE10)."
            })

        elif cid == "membership_tier" and "membership" not in seen_strategies:
            seen_strategies.add("membership")
            plan.append({
                "id": "camp_prime_trial",
                "title": "Complimentary 30-Day SmartCart Prime Trial & Free Delivery",
                "channel": "In-App Push & Email Offer",
                "priority": "Standard",
                "status": "Ready for Review",
                "root_cause_driver": driver_str,
                "perk_type": "prime_trial",
                "perk_value": 0.0,
                "coupon_code": "FREEPRIME30",
                "free_shipping": True,
                "perk_display": "30-Day Free SmartCart Prime Membership (Unlimited Free Delivery)",
                "objective": "Eliminate delivery fee barriers by providing 30 days of Free One-Day Delivery and festival sale perks.",
                "action_summary": "Prime Trial Incentive: 30-day Free Delivery trial to boost checkout frequency."
            })

    # If customer is Prime member with healthy orders, add Loyalty Appreciation
    if membership in ['prime', 'plus', 'prime_active'] and total_orders >= 5 and "loyalty" not in seen_strategies:
        plan.append({
            "id": "camp_prime_vip_rewards",
            "title": "Prime VIP Milestone Appreciation & Early Access",
            "channel": "VIP In-App Dashboard & Push",
            "priority": "Standard",
            "status": "Ready for Review",
            "root_cause_driver": "High-Value Prime Loyalty Recognition",
            "perk_type": "discount_voucher",
            "perk_value": 15.0,
            "coupon_code": "VIP15",
            "perk_display": "15% Exclusive Prime VIP Voucher (Code: VIP15) + Early Access Deals",
            "objective": f"Reward loyal Prime customer with exclusive early access to upcoming {category} deals.",
            "action_summary": f"Loyalty Appreciation: Early-access invite and 15% VIP discount coupon (VIP15)."
        })

    # Fallback if no specific campaigns were added
    if not plan:
        if total_orders >= 10:
            plan.append({
                "id": "camp_vip_platinum",
                "title": "High-Value Account Platinum Concierge & 15% VIP Voucher",
                "channel": "Personalized VIP Account Service",
                "priority": "Standard",
                "status": "Ready for Review",
                "root_cause_driver": "Platinum Customer Retention & High Lifetime Value",
                "perk_type": "discount_voucher",
                "perk_value": 15.0,
                "coupon_code": "VIP15",
                "perk_display": "15% Platinum VIP Voucher (Code: VIP15) + Free Express Delivery",
                "objective": "Maintain long-term retention of top-tier spending customer with 15% VIP discount and priority fulfillment.",
                "action_summary": "VIP Rewards Program: Dedicated account manager and 15% VIP voucher (VIP15)."
            })
        else:
            plan.append({
                "id": "camp_seasonal_nurture",
                "title": f"Seasonal Merchandise Discovery & Cross-Sell ({category})",
                "channel": "Storefront Digest & Deals Feed",
                "priority": "Standard",
                "status": "Ready for Review",
                "root_cause_driver": f"Category Mindshare Nurture ({category})",
                "perk_type": "discount_voucher",
                "perk_value": 10.0,
                "coupon_code": "DISCOVER10",
                "perk_display": f"10% Off {category} Voucher (Code: DISCOVER10)",
                "objective": f"Keep brand top of mind with tailored recommendations in {category}.",
                "action_summary": f"Promotional Nurture: Weekly curated product digest tailored to {category}."
            })

    return plan

def generate_recommendation(risk_category: str, churn_probability: float, customer_obj) -> List[str]:
    """
    Generates concise string summaries of retention recommendations
    for database storage and PDF export.
    """
    detailed_causes = extract_detailed_root_causes(customer_obj, risk_category)
    structured_plan = generate_structured_retention_plan(customer_obj, risk_category, churn_probability, detailed_causes)
    return [p["action_summary"] for p in structured_plan]

def extract_root_causes(customer_obj, risk_category: str = "High Risk") -> list:
    """Legacy helper returning string summaries."""
    detailed = extract_detailed_root_causes(customer_obj, risk_category)
    return [f"{d['title']} ({d['metric']})" for d in detailed]


def generate_simple_explanation(churn_probability: float, risk_category: str, shap_explanation: list) -> str:
    """
    Generates a concise 2-4 sentence plain English explanation for non-technical business administrators.
    Mentions the 2-3 most relevant factors and whether they increase or reduce the customer's risk of leaving.
    Avoids technical terms like SHAP, feature importance, model weights, Random Forest.
    """
    if not shap_explanation or len(shap_explanation) == 0:
        return (
            "The exact reason for this customer's risk profile cannot be determined from the available data. "
            "Additional shopping or interaction history is required to identify specific behavioral drivers."
        )

    prob = float(churn_probability or 0.0)
    if not risk_category:
        if prob >= 65.0:
            risk_category = "High Risk"
        elif prob >= 35.0:
            risk_category = "Medium Risk"
        else:
            risk_category = "Low Risk"

    risk_lower = risk_category.lower()
    is_high = "high" in risk_lower
    is_med = "medium" in risk_lower or "moderate" in risk_lower
    is_low = "low" in risk_lower

    if is_high:
        s1 = "This customer has a high predicted risk of leaving."
    elif is_med:
        s1 = "This customer has a moderate predicted risk of leaving."
    else:
        s1 = "This customer has a low predicted risk of leaving."

    # Filter to top 2-3 most relevant factors
    top_items = shap_explanation[:3]
    if len(top_items) > 2 and top_items[2].get("importance", 0) < 0.005 and top_items[2].get("contribution_val", 0) < 5.0:
        top_items = top_items[:2]

    def describe_feature(item):
        feat = (item.get("feature") or "").lower()
        lbl = (item.get("label") or feat).lower()
        val = str(item.get("value") or "").strip()
        
        # Support Tickets
        if "ticket" in feat or "ticket" in lbl or "service" in feat:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None:
                if num == 0:
                    return {"full": "having no customer support complaints", "short": "a clean support record"}
                elif num == 1:
                    return {"full": "one customer support ticket", "short": "one support ticket"}
                else:
                    return {"full": f"{num} customer support tickets", "short": f"{num} support tickets"}
            return {"full": f"customer support ticket history ({val})", "short": "support tickets"}

        # App Sessions
        if "session" in feat or "session" in lbl:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None:
                if num == 0:
                    return {"full": "no app visits in the past month", "short": "lack of app visits"}
                else:
                    return {"full": f"recent app activity ({num} visits in the last 30 days)", "short": "recent app activity"}
            return {"full": f"app engagement levels ({val})", "short": "recent app activity"}

        # Recency / Days Since Last Purchase
        if "days_since" in feat or ("purchase" in feat and "last" in feat) or "recency" in feat:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None:
                if num <= 7:
                    return {"full": "a very recent purchase", "short": "recent purchase history"}
                else:
                    return {"full": f"their last purchase being {num} days ago", "short": "purchase history"}
            return {"full": f"purchase recency ({val})", "short": "purchase history"}

        # Cart Abandonment
        if "abandon" in feat or "abandon" in lbl:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None and num > 0:
                if num == 1:
                    return {"full": "one abandoned shopping cart", "short": "an abandoned cart"}
                return {"full": f"leaving items behind in {num} shopping carts", "short": f"{num} cart abandonments"}
            return {"full": "cart abandonment patterns", "short": "cart abandonment"}

        # Late Deliveries
        if "late" in feat or "delivery" in feat:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None and num > 0:
                return {"full": f"experiencing {num} delayed delivery package{'s' if num > 1 else ''}", "short": "delivery delays"}
            return {"full": "shipping delivery times", "short": "delivery timing"}

        # Returns
        if "return" in feat:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None and num > 0:
                return {"full": f"returning {num} item{'s' if num > 1 else ''}", "short": "product returns"}
            return {"full": "product return frequency", "short": "product returns"}

        # Cancellations
        if "cancel" in feat:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None and num > 0:
                return {"full": f"canceling {num} order{'s' if num > 1 else ''}", "short": "order cancellations"}
            return {"full": "order cancellations", "short": "order cancellations"}

        # Orders Lifetime
        if "lifetime" in feat or ("total_orders" in feat and "30d" not in feat):
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None:
                if num == 0:
                    return {"full": "having zero completed orders to date", "short": "an unactivated order history"}
                return {"full": f"a lifetime total of {num} orders", "short": "lifetime order history"}
            return {"full": "lifetime order volume", "short": "lifetime order history"}

        # Orders last 30d
        if "orders_last_30d" in feat:
            digits = "".join(c for c in val if c.isdigit())
            num = int(digits) if digits else None
            if num is not None:
                if num == 0:
                    return {"full": "placing no orders in the last month", "short": "a lack of recent orders"}
                return {"full": f"placing {num} order{'s' if num > 1 else ''} in the last 30 days", "short": "recent order frequency"}
            return {"full": "recent order frequency", "short": "recent orders"}

        # Membership
        if "membership" in feat or "prime" in feat or "tier" in feat:
            return {"full": f"their {val} membership status", "short": "membership status"}

        # Average Order Value / Spend
        if "spend" in feat or "aov" in feat or "order_value" in feat:
            return {"full": f"their average spend level ({val})", "short": "average spend"}

        clean_title = (item.get("label") or feat.replace("_", " ")).strip()
        return {"full": f"{clean_title.lower()} ({val})", "short": clean_title.lower()}

    risk_factors = []
    protective_factors = []

    for item in top_items:
        impact_str = (item.get("impact") or "").lower()
        direction = (item.get("direction") or "").lower()
        desc = describe_feature(item)

        if "increase" in impact_str or direction == "positive":
            risk_factors.append(desc)
        elif "protect" in impact_str or direction == "negative":
            protective_factors.append(desc)
        else:
            s_val = item.get("shap_value", 0.0)
            if s_val > 0:
                risk_factors.append(desc)
            else:
                protective_factors.append(desc)

    sentences = [s1]

    if risk_factors and protective_factors:
        if len(risk_factors) == 1 and len(protective_factors) >= 1:
            rf = risk_factors[0]
            pf_list = " and ".join(p["short"] for p in protective_factors)
            rf_phrase = rf["full"]
            rf_cap = rf_phrase[0].upper() + rf_phrase[1:]
            
            if is_low:
                s2 = f"{rf_cap} is the main factor highlighted as increasing concern, while {pf_list} help explain the prediction."
                s3 = "The customer has not shown enough evidence to suggest a high likelihood of leaving."
                sentences.extend([s2, s3])
            elif is_high:
                s2 = f"{rf_cap} is a primary factor increasing their likelihood of leaving, though {pf_list} offer some account stability."
                s3 = "However, the risk signals remain dominant and require attention."
                sentences.extend([s2, s3])
            else:
                s2 = f"{rf_cap} is contributing to increased attrition risk, while {pf_list} help offset some of this concern."
                s3 = "Proactive retention outreach can help keep this account engaged."
                sentences.extend([s2, s3])
        elif len(risk_factors) >= 2 and len(protective_factors) >= 1:
            rf_combined = f"{risk_factors[0]['full']} and {risk_factors[1]['short']}"
            rf_cap = rf_combined[0].upper() + rf_combined[1:]
            pf_short = protective_factors[0]["short"]
            
            s2 = f"{rf_cap} are the primary factors driving their elevated risk of leaving."
            s3 = f"Although {pf_short} provides some positive balance, these friction points currently outweigh the account's strengths."
            sentences.extend([s2, s3])
        else:
            rf_str = " and ".join(r["short"] for r in risk_factors)
            pf_str = " and ".join(p["short"] for p in protective_factors)
            s2 = f"Issues such as {rf_str} are increasing the risk of departure, while {pf_str} help reduce it."
            sentences.append(s2)

    elif risk_factors and not protective_factors:
        if len(risk_factors) == 1:
            rf = risk_factors[0]["full"]
            s2 = f"{rf[0].upper() + rf[1:]} is the main driver increasing this customer's risk of leaving."
            s3 = "Addressing this friction point should be the primary focus to preserve the relationship."
            sentences.extend([s2, s3])
        elif len(risk_factors) == 2:
            rf1 = risk_factors[0]["full"]
            rf2 = risk_factors[1]["short"]
            s2 = f"{rf1[0].upper() + rf1[1:]} and {rf2} are the main factors increasing their likelihood of leaving."
            s3 = "These friction points indicate growing dissatisfaction and require proactive attention."
            sentences.extend([s2, s3])
        else:
            rf1 = risk_factors[0]["full"]
            rf2 = risk_factors[1]["short"]
            rf3 = risk_factors[2]["short"]
            s2 = f"{rf1[0].upper() + rf1[1:]}, {rf2}, and {rf3} are the main factors increasing their likelihood of leaving."
            s3 = "Multiple customer service or order friction points are contributing to this elevated risk."
            sentences.extend([s2, s3])

    elif protective_factors and not risk_factors:
        if len(protective_factors) == 1:
            pf = protective_factors[0]["full"]
            s2 = f"{pf[0].upper() + pf[1:]} is strongly helping to reduce the risk of departure."
            s3 = "The customer continues to demonstrate healthy engagement with the platform."
            sentences.extend([s2, s3])
        else:
            pf1 = protective_factors[0]["full"]
            pf2 = protective_factors[1]["short"]
            s2 = f"{pf1[0].upper() + pf1[1:]} and {pf2} are the primary factors reducing their likelihood of leaving."
            s3 = "The customer has not shown evidence to suggest an immediate likelihood of departure."
            sentences.extend([s2, s3])

    else:
        sentences.append("Key behavioral factors remain balanced between risk drivers and protective habits.")

    return " ".join(sentences)

