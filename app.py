from flask import Flask, render_template, request, redirect
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            calories REAL,
            protein REAL,
            carbs REAL
        )
    """)
    conn.commit()
    conn.close()

def get_nutrition(food_name, quantity):
    nutrition_db = {
        "rice": {"calories": 130, "protein": 2.7, "carbs": 28},
        "chicken": {"calories": 165, "protein": 31, "carbs": 0},
        "egg": {"calories": 155, "protein": 13, "carbs": 1.1},
        "banana": {"calories": 89, "protein": 1.1, "carbs": 23},
        "bread": {"calories": 265, "protein": 9, "carbs": 49},
        "milk": {"calories": 42, "protein": 3.4, "carbs": 5},
        "apple": {"calories": 52, "protein": 0.3, "carbs": 14},
        "potato": {"calories": 77, "protein": 2, "carbs": 17},
        "oats": {"calories": 389, "protein": 17, "carbs": 66},
        "dal": {"calories": 116, "protein": 9, "carbs": 20},
        "chapati": {"calories": 297, "protein": 9, "carbs": 52},
        "paneer": {"calories": 265, "protein": 18, "carbs": 1.2},
        "fish": {"calories": 136, "protein": 20, "carbs": 0},
        "pasta": {"calories": 131, "protein": 5, "carbs": 25},
        "beans": {"calories": 347, "protein": 21, "carbs": 63},
        "fries": {"calories": 312, "protein": 3.4, "carbs": 41},
        "burger": {"calories": 295, "protein": 17, "carbs": 24},
        "pizza": {"calories": 266, "protein": 11, "carbs": 33},
        "salad": {"calories": 20, "protein": 1.8, "carbs": 3.3},
        "orange": {"calories": 47, "protein": 0.9, "carbs": 12},
        "mango": {"calories": 60, "protein": 0.8, "carbs": 15},
        "coffee": {"calories": 2, "protein": 0.3, "carbs": 0},
        "idli": {"calories": 39, "protein": 2, "carbs": 8},
        "dosa": {"calories": 168, "protein": 3.9, "carbs": 25},
        "yogurt": {"calories": 59, "protein": 10, "carbs": 3.6},
    }
    key = food_name.lower().strip()
    factor = int(quantity) / 100
    if key in nutrition_db:
        data = nutrition_db[key]
        return {
            "calories": round(data["calories"] * factor, 1),
            "protein": round(data["protein"] * factor, 1),
            "carbs": round(data["carbs"] * factor, 1)
        }
    return {"calories": 0, "protein": 0, "carbs": 0}

def generate_chart(entries):
    if not entries:
        return
    labels = [e[1] for e in entries]
    sizes = [e[3] for e in entries]
    sizes = [s if s > 0 else 1 for s in sizes]
    colors = ['#2ecc71','#3498db','#e74c3c','#f39c12','#9b59b6','#1abc9c','#e67e22']
    plt.figure(figsize=(7, 7))
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=None,
        colors=colors[:len(labels)],
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.75
    )
    plt.legend(
        wedges,
        labels,
        title="Foods",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    plt.title('Calories by Food', fontsize=16, pad=20)
    plt.tight_layout()
    chart_path = os.path.join('static', 'chart.png')
    os.makedirs('static', exist_ok=True)
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_food():
    food_name = request.form.get("food_name")
    quantity = request.form.get("quantity")
    nutrition = get_nutrition(food_name, quantity)
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO food_log (food_name, quantity, calories, protein, carbs)
        VALUES (?, ?, ?, ?, ?)
    """, (food_name, quantity, nutrition["calories"], nutrition["protein"], nutrition["carbs"]))
    conn.commit()
    conn.close()
    return redirect("/history")

@app.route("/history")
def history():
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM food_log")
    entries = cursor.fetchall()
    total_calories = sum(e[3] for e in entries)
    total_protein = sum(e[4] for e in entries)
    total_carbs = sum(e[5] for e in entries)
    generate_chart(entries)
    conn.close()
    return render_template("history.html",
        entries=entries,
        total_calories=round(total_calories, 1),
        total_protein=round(total_protein, 1),
        total_carbs=round(total_carbs, 1),
        show_chart=len(entries) > 0)

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_log WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/history")

init_db()
app.run(debug=True)