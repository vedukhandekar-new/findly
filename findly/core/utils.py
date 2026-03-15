from math import radians, cos, sin, asin, sqrt


def _haversine(lat1, lon1, lat2, lon2):
    """Returns distance in km between two GPS coordinates."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return R * 2 * asin(sqrt(a))


def _text_similarity(text1, text2):
    """Simple word-overlap score 0–100. Swap with AI model in production."""
    w1 = set(text1.lower().split())
    w2 = set(text2.lower().split())
    if not w1 or not w2:
        return 0.0
    return round(len(w1 & w2) / max(len(w1), len(w2)) * 100, 2)


def run_matching_algorithm(new_item, radius_km=5):
    """
    Called after every new Lost or Found report.
    Finds candidates by category + GPS proximity, creates Match records,
    and notifies both users.
    """
    # Import here to avoid circular imports
    from .models import Item, Match
    from .utils import send_notification

    opposite_type = 'Found' if new_item.report_type == 'Lost' else 'Lost'
    candidates    = Item.objects.filter(
        report_type=opposite_type,
        category=new_item.category,
        status='Active'
    )

    for candidate in candidates:
        dist = _haversine(
            new_item.latitude,  new_item.longitude,
            candidate.latitude, candidate.longitude
        )
        if dist > radius_km:
            continue

        confidence = _text_similarity(new_item.description, candidate.description)

        lost_item  = new_item   if new_item.report_type  == 'Lost'  else candidate
        found_item = new_item   if new_item.report_type  == 'Found' else candidate

        # Skip if match already exists
        if Match.objects.filter(lost_item=lost_item, found_item=found_item).exists():
            continue

        match = Match.objects.create(
            lost_item=lost_item,
            found_item=found_item,
            ai_confidence=confidence,
            match_status='Pending'
        )

        # Update both items to Matching
        lost_item.status  = 'Matching'
        found_item.status = 'Matching'
        lost_item.save()
        found_item.save()

        # Notify both users
        send_notification(
            lost_item.reporter,
            f"Good news! A potential match was found for your lost {lost_item.category}. Check your matches."
        )
        send_notification(
            found_item.reporter,
            f"The {found_item.category} you found may belong to someone. Check your matches."
        )


def send_notification(user, message_text):
    """Creates a Notification record for the given user."""
    from .models import Notification
    Notification.objects.create(recipient=user, message=message_text)