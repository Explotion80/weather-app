import os
import psycopg2
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

BASE_URL = "http://api.weatherapi.com/v1/current.json"
JEZYK = "pl"

app = Flask(__name__)

@app.route('/metrics')
def metric():
    return '', 200

# Inicjalizacja bazy danych
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            country VARCHAR(100),
            temperature FLOAT,
            condition TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Funkcja do zapisu danych pogodowych do bazy
def zapisz_do_bazy(city, country, temperature, condition):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO weather (city, country, temperature, condition)
            VALUES (%s, %s, %s, %s);
        """, (city, country, temperature, condition))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Błąd zapisu do bazy:", e)

# Funkcja do pobierania bieżącej pogody
def pobierz_biezaca_pogode(miasto):
    params = {"key": API_KEY, "q": miasto, "lang": JEZYK}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'current' in data:
                temp = data['current']['temp_c']
                condition = data['current']['condition']['text']
                country = data['location']['country']
                city = data['location']['name']

                zapisz_do_bazy(city, country, temp, condition)

                return f"Pogoda w {city}, {country}: {temp}°C, {condition}"
            else:
                return "Brak danych o bieżącej pogodzie."
        except ValueError:
            return "Błąd podczas przetwarzania odpowiedzi z API."
    else:
        return f"Błąd połączenia z API. Status kod: {response.status_code}"

# Strona główna
@app.route('/')
def index():
    return render_template('index.html')

# Strona z wynikami
@app.route('/wyniki', methods=['POST'])
def wyniki():
    miasto = request.form['miasto']
    wynik = pobierz_biezaca_pogode(miasto)
    return render_template('wyniki.html', wynik=wynik)

if __name__ == '__main__':
    init_db()  # <- Dodajemy inicjalizację bazy danych przy starcie
    app.run(debug=True, host='0.0.0.0', port=5000)
