def stars(p_val):
    stars = ""
    if p_val<0.01:
        stars = "***"
    elif p_val < 0.05:
        stars = "**"
    elif p_val < 0.1:
        stars = "*"
    return stars