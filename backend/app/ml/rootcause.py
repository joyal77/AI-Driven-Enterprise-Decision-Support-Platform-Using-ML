def analyze_root_cause(customer):
    reasons = []

    # Extract ratings & attributes gracefully
    cust_type = getattr(customer, "customer_type", "Loyal Customer") or "Loyal Customer"
    travel_type = getattr(customer, "type_of_travel", "Business travel") or "Business travel"
    cabin = getattr(customer, "contract_length", "Business") or "Business"

    boarding = getattr(customer, "online_boarding", 4) or 4
    comfort = getattr(customer, "seat_comfort", 4) or 4
    entertainment = getattr(customer, "inflight_entertainment", 4) or 4
    food = getattr(customer, "food_and_drink", 4) or 4
    legroom = getattr(customer, "leg_room_service", 4) or 4
    onboard = getattr(customer, "on_board_service", 4) or 4
    cleanliness = getattr(customer, "cleanliness", 4) or 4
    dep_delay = getattr(customer, "departure_delay_in_minutes", 0) or 0
    arr_delay = getattr(customer, "arrival_delay_in_minutes", 0) or 0

    # Friction checks
    if arr_delay > 20 or dep_delay > 20:
        reasons.append(f"Flight schedule delay encountered (Departure: {dep_delay}m, Arrival: {arr_delay}m)")
    
    if comfort <= 3:
        reasons.append("Low seat comfort experience creating cabin ergonomics friction")
    
    if boarding <= 3:
        reasons.append("Online boarding & digital check-in friction")
        
    if entertainment <= 3:
        reasons.append("Dissatisfaction with inflight entertainment service")
        
    if food <= 3:
        reasons.append("Dissatisfaction with food & beverage options")
        
    if legroom <= 3:
        reasons.append("Dissatisfaction with leg room service")

    if cleanliness <= 3:
        reasons.append("Cabin cleanliness issues flagged by passenger")

    if "disloyal" in cust_type.lower():
        reasons.append("First-time / Disloyal customer profile with low brand attachment")

    if "personal" in travel_type.lower():
        reasons.append("Leisure travel passenger profile with higher price sensitivity")

    # Dynamic personalized highlights for satisfied passengers
    if len(reasons) == 0:
        top_services = []
        if boarding >= 4: top_services.append("Online Boarding")
        if comfort >= 4: top_services.append("Seat Comfort")
        if legroom >= 4: top_services.append("Legroom")
        if cleanliness >= 4: top_services.append("Cleanliness")
        if onboard >= 4: top_services.append("On-Board Service")

        services_str = ", ".join(top_services[:3]) if top_services else "inflight amenities"
        reasons.append(f"Outstanding passenger satisfaction in {services_str}")
        reasons.append(f"Favorable {cust_type} profile flying {cabin} class with 0 flight delays")

    return reasons
