import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import datetime
import os


# -----------------------------
# File for saving data
# -----------------------------
DATA_FILE = "health_data.json"

# -----------------------------
# Global Variables
# -----------------------------
current_intake = 0
daily_water_goal = 0
meal_list = []
total_calories = 0
total_protein = 0
total_carbs = 0
total_fat = 0
daily_calorie_goal = 2000

today = datetime.date.today().isoformat()

# -----------------------------
# Food Chart with Macros
# -----------------------------
food_chart = {
    "Oatmeal": {"calories": 250, "protein": 5, "carbs": 45, "fat": 4},
    "Banana": {"calories": 100, "protein": 1, "carbs": 27, "fat": 0.3},
    "Apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
    "Chicken Breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "Salad": {"calories": 150, "protein": 3, "carbs": 10, "fat": 10},
    "Rice (1 cup)": {"calories": 200, "protein": 4, "carbs": 45, "fat": 0.5},
    "Egg": {"calories": 78, "protein": 6, "carbs": 0.6, "fat": 5},
    "Bread Slice": {"calories": 70, "protein": 3, "carbs": 13, "fat": 1},
    "Milk (1 cup)": {"calories": 120, "protein": 8, "carbs": 12, "fat": 5},
    "Yogurt": {"calories": 100, "protein": 5, "carbs": 12, "fat": 2}
}

categories = ["Breakfast", "Lunch", "Dinner", "Snack"]
activity_levels = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]

# -----------------------------
# Save/Load Functions
# -----------------------------


def save_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            all_data = json.load(f)
    else:
        all_data = {}
    all_data[today] = {
        "current_intake": current_intake,
        "daily_water_goal": daily_water_goal,
        "meal_list": meal_list,
        "daily_calorie_goal": daily_calorie_goal
    }
    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=4)


def load_data():
    global current_intake, daily_water_goal, meal_list, total_calories, total_protein, total_carbs, total_fat, daily_calorie_goal
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            all_data = json.load(f)
        # Initialize today's data if missing
        if today not in all_data:
            all_data[today] = {
                "current_intake": 0,
                "daily_water_goal": 0,
                "meal_list": [],
                "daily_calorie_goal": 2000
            }
        today_data = all_data[today]
        # Fix for old format (list)
        if isinstance(today_data, list):
            today_data = {"meal_list": today_data, "current_intake":0, "daily_water_goal":0, "daily_calorie_goal":2000}
        current_intake = today_data.get("current_intake", 0)
        daily_water_goal = today_data.get("daily_water_goal", 0)
        meal_list = today_data.get("meal_list", [])
        daily_calorie_goal = today_data.get("daily_calorie_goal", 2000)
        total_calories = sum(m.get("calories",0) for m in meal_list)
        total_protein = sum(m.get("protein",0) for m in meal_list)
        total_carbs = sum(m.get("carbs",0) for m in meal_list)
        total_fat = sum(m.get("fat",0) for m in meal_list)
    else:
        # No file, start fresh
        current_intake = daily_water_goal = total_calories = total_protein = total_carbs = total_fat = 0
        meal_list.clear()
        daily_calorie_goal = 2000

# -----------------------------
# Water Tracker Functions
# -----------------------------


def set_water_goal():
    global daily_water_goal
    try:
        weight = float(weight_entry.get())
        daily_water_goal = weight * 35
        update_water_display()
    except ValueError:
        messagebox.showerror("Error", "Enter a valid weight.")


def log_water():
    global current_intake
    try:
        amount = float(intake_entry.get())
        if amount <= 0: raise ValueError
        current_intake = min(current_intake + amount, daily_water_goal)
        update_water_display()
        if current_intake >= daily_water_goal:
            messagebox.showinfo("Congrats!", "You reached your daily water goal! 💧")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid positive number")


def update_water_display():
    goal_label.config(text=f"Daily Water Goal: {int(daily_water_goal)} ml")
    intake_label.config(text=f"Water Consumed: {int(current_intake)} ml")
    water_progress['value'] = (current_intake / daily_water_goal) * 100 if daily_water_goal else 0


def remind_water():
    messagebox.showinfo("Reminder", "Time to drink water! 💧")
    root.after(3600000, remind_water)

# -----------------------------
# Meal Planner Functions
# -----------------------------


def add_meal():
    global total_calories, total_protein, total_carbs, total_fat
    food_name = food_var.get()
    category = category_var.get()
    if food_name not in food_chart:
        messagebox.showinfo("Error", "Food not in chart.")
        return
    data = food_chart[food_name]
    meal_entry = {
        "food": food_name,
        "category": category,
        "calories": data["calories"],
        "protein": data["protein"],
        "carbs": data["carbs"],
        "fat": data["fat"]
    }
    meal_list.append(meal_entry)
    total_calories += data["calories"]
    total_protein += data["protein"]
    total_carbs += data["carbs"]
    total_fat += data["fat"]
    update_meal_display()
    if total_calories >= daily_calorie_goal:
        messagebox.showinfo("Goal Reached!", "You reached your daily calorie goal! 🍽️")


def update_meal_display():
    meal_display.delete(0, tk.END)
    for m in meal_list:
        meal_display.insert(tk.END, f"{m['category']}: {m['food']} - {m['calories']} kcal | P:{m['protein']} C:{m['carbs']} F:{m['fat']}")
    calories_label.config(text=f"Total Calories: {total_calories} kcal")
    macros_label.config(text=f"Protein: {total_protein}g | Carbs: {total_carbs}g | Fat: {total_fat}g")
    calorie_progress['value'] = (total_calories / daily_calorie_goal) * 100 if daily_calorie_goal else 0
    goal_label_meal.config(text=f"Daily Calorie Goal: {daily_calorie_goal} kcal")


def calculate_daily_goal():
    global daily_calorie_goal
    try:
        weight = float(weight_goal_entry.get())
        height = float(height_entry.get())
        age = int(age_entry.get())
        gender = gender_var.get()
        activity = activity_var.get()
        if gender.lower() == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Extra Active": 1.9
        }
        tdee = bmr * activity_multipliers.get(activity, 1.2)
        daily_calorie_goal = int(tdee)
        update_meal_display()
        messagebox.showinfo("Success", f"Daily calorie goal calculated: {daily_calorie_goal} kcal")
    except ValueError:
        messagebox.showerror("Error", "Enter valid numeric values for weight, height, age.")

# -----------------------------
# History Functions
# -----------------------------


def show_history():
    selected_date = history_date_var.get()
    if not selected_date or not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE) as f:
        all_data = json.load(f)
        data = all_data.get(selected_date, {})
        if isinstance(data, list):
            data = {"meal_list": data, "current_intake":0, "daily_water_goal":0, "daily_calorie_goal":2000}
        history_display.delete(0, tk.END)
        for m in data.get("meal_list", []):
            history_display.insert(tk.END, f"{m['category']}: {m['food']} - {m['calories']} kcal | P:{m['protein']} C:{m['carbs']} F:{m['fat']}")
        water = data.get("current_intake", 0)
        water_goal = data.get("daily_water_goal", 0)
        calorie_goal = data.get("daily_calorie_goal", 2000)
        total_cal = sum(m.get("calories",0) for m in data.get("meal_list",[]))
        water_history_label.config(text=f"Water: {water} / {water_goal} ml")
        calorie_history_label.config(text=f"Calories: {total_cal} / {calorie_goal} kcal")
        water_history_progress['value'] = (water / water_goal) * 100 if water_goal else 0
        calories_history_progress['value'] = (total_cal / calorie_goal) * 100 if calorie_goal else 0


def reset_today():
    global current_intake, daily_water_goal, meal_list, total_calories, total_protein, total_carbs, total_fat
    current_intake = daily_water_goal = total_calories = total_protein = total_carbs = total_fat = 0
    meal_list.clear()
    update_water_display()
    update_meal_display()
    save_data()

# -----------------------------
# GUI
# -----------------------------


root = tk.Tk()
root.title("💪 Health Management App")
root.geometry("700x800")
root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))

load_data()

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# -- Water Tracker Tab --
water_tab = ttk.Frame(notebook)
notebook.add(water_tab, text="💧 Water Tracker")
tk.Label(water_tab, text="Enter your weight (kg):").pack(pady=5)
weight_entry = tk.Entry(water_tab); weight_entry.pack()
tk.Button(water_tab, text="Set Water Goal", command=set_water_goal).pack(pady=5)
goal_label = tk.Label(water_tab, text=f"Daily Water Goal: {daily_water_goal} ml"); goal_label.pack(pady=5)
tk.Label(water_tab, text="Enter water amount drank (ml):").pack(pady=5)
intake_entry = tk.Entry(water_tab); intake_entry.pack()
tk.Button(water_tab, text="Log Water", command=log_water).pack(pady=5)
water_progress = ttk.Progressbar(water_tab, length=400); water_progress.pack(pady=10)
intake_label = tk.Label(water_tab, text=f"Water Consumed: {current_intake} ml"); intake_label.pack(pady=5)
update_water_display()
root.after(3600000, remind_water)

# -- Meal Planner Tab --
meal_tab = ttk.Frame(notebook)
notebook.add(meal_tab, text="🍽️ Meal Planner")
tk.Label(meal_tab, text="Enter info to calculate daily calorie goal:").pack(pady=5)
tk.Label(meal_tab, text="Weight (kg):").pack(); weight_goal_entry = tk.Entry(meal_tab); weight_goal_entry.pack()
tk.Label(meal_tab, text="Height (cm):").pack(); height_entry = tk.Entry(meal_tab); height_entry.pack()
tk.Label(meal_tab, text="Age:").pack(); age_entry = tk.Entry(meal_tab); age_entry.pack()
tk.Label(meal_tab, text="Gender:").pack()
gender_var = tk.StringVar(); gender_dropdown = ttk.Combobox(meal_tab, values=["Male","Female"], textvariable=gender_var); gender_dropdown.current(0); gender_dropdown.pack()
tk.Label(meal_tab, text="Activity Level:").pack()
activity_var = tk.StringVar(); activity_dropdown = ttk.Combobox(meal_tab, values=activity_levels, textvariable=activity_var); activity_dropdown.current(0); activity_dropdown.pack()
tk.Button(meal_tab, text="Calculate Daily Calorie Goal", command=calculate_daily_goal).pack(pady=5)
goal_label_meal = tk.Label(meal_tab, text=f"Daily Calorie Goal: {daily_calorie_goal} kcal"); goal_label_meal.pack(pady=5)
tk.Label(meal_tab, text="Select Meal Category:").pack(pady=5)
category_var = tk.StringVar(); category_dropdown = ttk.Combobox(meal_tab, values=categories, textvariable=category_var); category_dropdown.current(0); category_dropdown.pack()
tk.Label(meal_tab, text="Select Food:").pack(pady=5)
food_var = tk.StringVar(); food_dropdown = ttk.Combobox(meal_tab, values=list(food_chart.keys()), textvariable=food_var); food_dropdown.current(0); food_dropdown.pack()
tk.Button(meal_tab, text="Add Meal", command=add_meal).pack(pady=10)
tk.Button(meal_tab, text="Reset Today", command=reset_today).pack(pady=5)
meal_display = tk.Listbox(meal_tab, width=75); meal_display.pack(pady=10)
calories_label = tk.Label(meal_tab, text=f"Total Calories: {total_calories} kcal"); calories_label.pack(pady=5)
macros_label = tk.Label(meal_tab, text=f"Protein: {total_protein}g | Carbs: {total_carbs}g | Fat: {total_fat}g"); macros_label.pack(pady=5)
calorie_progress = ttk.Progressbar(meal_tab, length=400); calorie_progress.pack(pady=10)
update_meal_display()

# -- History Tab --
history_tab = ttk.Frame(notebook)
notebook.add(history_tab, text="📊 History")
tk.Label(history_tab, text="Select Date:").pack(pady=5)
if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        all_data = json.load(f)
        available_dates = [d for d in all_data.keys() if d != today]
else:
    available_dates = []
history_date_var = tk.StringVar()
history_dropdown = ttk.Combobox(history_tab, values=available_dates, textvariable=history_date_var)
if available_dates:
    history_dropdown.current(0)
history_dropdown.pack(pady=5)
tk.Button(history_tab, text="Show History", command=show_history).pack(pady=10)
history_display = tk.Listbox(history_tab, width=80); history_display.pack(pady=10)
water_history_label = tk.Label(history_tab, text=""); water_history_label.pack(pady=5)
calorie_history_label = tk.Label(history_tab, text=""); calorie_history_label.pack(pady=5)
calories_history_progress = ttk.Progressbar(history_tab, length=400); calories_history_progress.pack(pady=5)
water_history_progress = ttk.Progressbar(history_tab, length=400); water_history_progress.pack(pady=5)

root.mainloop()
