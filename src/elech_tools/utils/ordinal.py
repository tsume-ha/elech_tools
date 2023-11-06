def ordinal(n: int) -> str:
    """
    Convert integer to ordinal.
    1 -> 1st
    2 -> 2nd
    3 -> 3rd
    4 -> 4th

    -----------
    Parameters:
        n: int
    Returns:
        string: ortinal
    """
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix
