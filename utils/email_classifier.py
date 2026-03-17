def categorize_email(email: dict) -> str:
    """
    Categorize an email based on sender, subject, and preview text.
    
    Categories:
    - Important
    - Work / Jobs
    - Social
    - Notifications
    - Promotions
    - Other
    """
    subject = email.get("subject", "").lower()
    sender = email.get("from", "").lower()
    preview = email.get("preview", "").lower()

    # 1. Important
    important_keywords = ["security", "alert", "verification", "password"]
    if any(kw in subject for kw in important_keywords) or any(kw in sender for kw in important_keywords):
        return "Important"

    # 2. Work / Jobs
    job_keywords = ["job", "interview", "career", "hiring", "opportunity"]
    job_platforms = ["indeed", "jobright", "linkedin", "glassdoor"]
    if any(kw in subject for kw in job_keywords) or any(kw in sender for kw in job_platforms):
        return "Work / Jobs"

    # 3. Social
    social_platforms = ["linkedin.com", "twitter.com", "facebook.com", "instagram.com"]
    if any(kw in sender for kw in social_platforms):
        return "Social"

    # 4. Notifications
    notif_keywords = ["notification", "update", "activity"]
    if any(kw in subject for kw in notif_keywords):
        return "Notifications"

    # 5. Promotions
    promo_keywords = ["sale", "offer", "discount", "deal", "promotion"]
    if any(kw in subject for kw in promo_keywords):
        return "Promotions"

    # Default
    return "Other"
