import string
import hashlib
import requests
from zxcvbn import zxcvbn

common_patterns = ["password", "qwerty", "admin", "123", "letmein"]

print("Эта программа создана для оценки безопасности ваших паролей.")

def check_pwned(password: str) -> int:
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except requests.RequestException:
        print("⚠️ Ошибка при проверке утечек. Пропускаем проверку.")
        return 0

    hashes = (line.split(':') for line in res.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return int(count)
    return 0

while True:
    password = input("\nВведите ваш пароль (или 'exit' для выхода): ")
    if password.lower() == "exit":
        print("Выход из программы.")
        break

    result = zxcvbn(password)
    password_point = 0
    password_point += result["score"]

    #проверка распространённых слов
    if any(word in password.lower() for word in common_patterns):
        password_point -= 2
        print("⚠️ Пароль содержит распространённое слово или шаблон.")

    #длина пароля
    length = len(password)
    if length <= 5:
        print("Слишком короткий пароль.")
        continue
    else:
        for limit in [5, 7, 11, 15]:
            if length > limit:
                password_point += 1

    # разные типы символов
    if any(ch.isupper() for ch in password):
        password_point += 1
    if any(ch.islower() for ch in password):
        password_point += 1
    if any(ch.isdigit() for ch in password):
        password_point += 1
    if any(ch in string.punctuation for ch in password):
        password_point += 1

    #пробелы
    if " " in password:
        print("Пароль не может содержать пробелы.")
        continue

    #проверка утечек
    leaks = check_pwned(password)
    if leaks > 0:
        print(f"⚠️ Этот пароль встречался в утечках {leaks} раз(а)! Не используйте его.")
        password_point = max(password_point - 2, 0)

    print(f"Итоговая оценка пароля: {password_point}")
