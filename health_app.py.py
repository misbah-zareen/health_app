import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
import threading

# -----------------------------
# Global Variables
# -----------------------------
current_intake = 0  # ml
daily_goal = 0      # ml
meal_list = []      # list of meals (name, calories)
total_calories = 0

# -----------------------------
# Functions for Water Tracker
# -----------------------------
def calculate_water_goal():
    global daily_goal, current_intake
    try:
        weight = float(weight_entry.get())
        daily_goal = weight * 35  # daily water goal in ml
        goal_label.config(text=f"Daily Water Goal: {int(daily_goal)} ml")
        progress_bar['value'] = (current_intake / daily_goal) * 100 if daily_goal != 0 else 0
        intake_label.config(text=f"Water Consumed: {current_intake} ml")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for weight")

def log_water():
    global current_intake
    try:
        amount = float(intake_entry.get())
        if amount <= 0:
            raise ValueError
        current_intake += amount
        if current_intake > daily_goal:
            current_intake = daily_goal
            messagebox.showinfo("Congrats!", "You reached your daily water goal! 🎉")
        intake_label.config(text=f"Water Consumed: {int(current_intake)} ml")
        progress_bar['value'] = (current_intake / daily_goal) * 100 if daily_goal != 0 else 0
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid positive number")

def remind_user():
    messagebox.showinfo("Reminder", "Time to drink water! 💧")
    root.after(3600000, remind_user)  # 1 hour reminder

# -----------------------------
# Functions for Meal Planner
# -----------------------------
def add_meal():
    global meal_list, total_calories
    name = simpledialog.askstring("Meal Name", "Enter meal name:")
    if not name:
        return
    try:
        calories = float(simpledialog.askstring("Calories", "Enter calories for this meal:"))
        if calories < 0:
            raise ValueError
    except (ValueError, TypeError):
        messagebox.showerror("Error", "Please enter a valid calorie number")
        return
    meal_list.append((name, calories))
    total_calories += calories
    update_meal_display()

def update_meal_display():
    meal_display.delete(0, tk.END)
    for meal, cal in meal_list:
        meal_display.insert(tk.END, f"{meal}: {cal} kcal")
    calories_label.config(text=f"Total Calories: {total_calories} kcal")

# -----------------------------
# Build GUI
# -----------------------------
root = tk.Tk()
root.title("💪 Health Management App")
root.geometry("500x500")

# Notebook (Tabs)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# -----------------------------
# Tab 1: Water Tracker
# -----------------------------
water_tab = ttk.Frame(notebook)
notebook.add(water_tab, text="💧 Water Tracker")

tk.Label(water_tab, text="Enter your weight (kg):").pack(pady=5)
weight_entry = tk.Entry(water_tab)
weight_entry.pack()
tk.Button(water_tab, text="Set Water Goal", command=calculate_water_goal).pack(pady=5)

goal_label = tk.Label(water_tab, text="Daily Water Goal: 0 ml")
goal_label.pack(pady=5)

tk.Label(water_tab, text="Enter water amount drank (ml):").pack(pady=5)
intake_entry = tk.Entry(water_tab)
intake_entry.pack()
tk.Button(water_tab, text="Log Water", command=log_water).pack(pady=5)

progress_bar = ttk.Progressbar(water_tab, length=300)
progress_bar.pack(pady=10)

intake_label = tk.Label(water_tab, text="Water Consumed: 0 ml")
intake_label.pack(pady=5)

# Start reminders in background
root.after(3600000, remind_user)  # 1 hour first reminder

# -----------------------------
# Tab 2: Meal Planner
# -----------------------------
meal_tab = ttk.Frame(notebook)
notebook.add(meal_tab, text="🍽️ Meal Planner")

tk.Button(meal_tab, text="Add Meal", command=add_meal).pack(pady=10)
meal_display = tk.Listbox(meal_tab, width=50)
meal_display.pack(pady=10)

calories_label = tk.Label(meal_tab, text="Total Calories: 0 kcal")
calories_label.pack(pady=5)

# -----------------------------
# Run GUI
# -----------------------------
root.mainloop()
