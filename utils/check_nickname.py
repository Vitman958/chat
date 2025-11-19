def check_nickname(nick_name):
    has_letter = nick_name.isdigit()

    all_valid = all(char.isalpha() or char.isdigit() or char in ['_', '-'] for char in nick_name)

    if has_letter:
        return False, f"Никнейм не может состоять только из цифр"
    
    if not all_valid:
        return False, f"Недопустимые символы"
    
    if len(nick_name) < 3 or len(nick_name) > 16:
        return False, f"Недопустимая длина никнейма"

    return True, ""
    