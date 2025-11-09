import string
import hashlib
import requests
from zxcvbn import zxcvbn
import time

def print_animated_banner():
    banner = r"""
          _____                    _____                    _____                    _____                    _____          
         /\    \                  /\    \                  /\    \                  /\    \                  /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\                /::\    \        
       /::::\    \              /::::\    \              /::::\    \              /:::/    /               /::::\    \       
      /::::::\    \            /::::::\    \            /::::::\    \            /:::/    /               /::::::\    \      
     /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \          /:::/    /               /:::/\:::\    \     
    /:::/__\:::\    \        /:::/__\:::\    \        /:::/  \:::\    \        /:::/    /               /:::/__\:::\    \    
   /::::\   \:::\    \      /::::\   \:::\    \      /:::/    \:::\    \      /:::/    /                \:::\   \:::\    \   
  /::::::\   \:::\    \    /::::::\   \:::\    \    /:::/    / \:::\    \    /:::/    /      _____    ___\:::\   \:::\    \  
 /:::/\:::\   \:::\    \  /:::/\:::\   \:::\____\  /:::/    /   \:::\ ___\  /:::/____/      /\    \  /\   \:::\   \:::\    \ 
/:::/  \:::\   \:::\____\/:::/  \:::\   \:::|    |/:::/____/  ___\:::|    ||:::|    /      /::\____\/::\   \:::\   \:::\____\
\::/    \:::\  /:::/    /\::/   |::::\  /:::|____|\:::\    \ /\  /:::|____||:::|____\     /:::/    /\:::\   \:::\   \::/    /
 \/____/ \:::\/:::/    /  \/____|:::::\/:::/    /  \:::\    /::\ \::/    /  \:::\    \   /:::/    /  \:::\   \:::\   \/____/ 
          \::::::/    /         |:::::::::/    /    \:::\   \:::\ \/____/    \:::\    \ /:::/    /    \:::\   \:::\    \     
           \::::/    /          |::|\::::/    /      \:::\   \:::\____\       \:::\    /:::/    /      \:::\   \:::\____\    
           /:::/    /           |::| \::/____/        \:::\  /:::/    /        \:::\__/:::/    /        \:::\  /:::/    /    
          /:::/    /            |::|  ~|               \:::\/:::/    /          \::::::::/    /          \:::\/:::/    /     
         /:::/    /             |::|   |                \::::::/    /            \::::::/    /            \::::::/    /      
        /:::/    /              \::|   |                 \::::/    /              \::::/    /              \::::/    /       
        \::/    /                \:|   |                  \::/____/                \::/____/                \::/    /        
         \/____/                  \|___|                                            ~~                       \/____/                                 
"""
    green_color = "\033[92m"
    reset_color = "\033[0m"

    for line in banner.splitlines():
        print(green_color + line + reset_color)
        time.sleep(0.1)

print_animated_banner()

common_patterns = [
    "password", "123456", "123456789", "qwerty", "abc123", "111111", "123123",
    "admin", "letmein", "welcome", "monkey", "login", "princess", "solo",
    "passw0rd", "starwars", "dragon", "football", "baseball", "shadow",
    "master", "hello", "freedom", "whatever", "qazwsx", "trustno1", "1234",
    "12345", "password1", "iloveyou", "sunshine", "flower", "hottie",
    "loveme", "zaq1zaq1", "batman", "superman", "pokemon"
]

#функция проверки утечек
def check_pwned(password: str) -> int:
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except requests.RequestException:
        return 0
    hashes = (line.split(':') for line in res.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return int(count)
    return 0

#функция для визуальной шкалы
def print_strength_bar(points, max_points=12):
    bar_length = 12
    filled_length = int(bar_length * points / max_points)
    empty_length = bar_length - filled_length

    #цвета ANSI для консоли
    if points <= 4:
        color = "\033[91m"  #красный
        label = "Слабый"
    elif points <= 8:
        color = "\033[93m"  #жёлтый
        label = "Средний"
    else:
        color = "\033[92m"  #зелёный
        label = "Сильный"

    reset = "\033[0m"
    bar = color + "█" * filled_length + "-" * empty_length + reset
    print(f"{bar} {label}")

print("Эта программа создана для оценки безопасности ваших паролей.")

while True:
    password = input("\nВведите пароль (или 'exit' для выхода): ")
    if password.lower() == "exit":
        break

    result = zxcvbn(password)
    password_point = result["score"]

    #длина
    length = len(password)
    for limit in [5, 7, 11, 15]:
        if length > limit:
            password_point += 1

    #разные типы символов
    if any(ch.isupper() for ch in password):
        password_point += 1
    if any(ch.islower() for ch in password):
        password_point += 1
    if any(ch.isdigit() for ch in password):
        password_point += 1
    if any(ch in string.punctuation for ch in password):
        password_point += 1

    #распространённые слова
    if any(word in password.lower() for word in common_patterns):
        password_point -= 2
        print("⚠️ Пароль содержит распространённое слово/шаблон.")

    #пробелы
    if " " in password:
        print("⚠️ Пароль не может содержать пробелы.")
        continue

    #проверка утечек
    leaks = check_pwned(password)
    if leaks > 0:
        print(f"⚠️ Этот пароль встречался в утечках {leaks} раз(а)!")
        password_point = max(password_point - 2, 0)

    #щкала сложности
    print_strength_bar(password_point)


