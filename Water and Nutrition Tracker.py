# Nutrition_and_water_tracker
from nicegui import ui
import pandas as pd
import json
import datetime
import math
from pathlib import Path
from typing import Any, Dict

# ---------- Config ----------
MENU_CSV = "toddler_menu_500.csv"
LOG_FILE = "daily_log.json"
TODAY = datetime.date.today().isoformat()

# ---------- Load menu ----------
menu = pd.read_csv(MENU_CSV)
menu = menu.rename(columns={
    'Calories_kcal': 'Calories',
    'Protein_g': 'Protein',
    'Fat_g': 'Fat',
    'Carbs_g': 'Carbs'
})

# ---------- Load logs ----------
logs: Dict[str, Dict[str, Any]] = {}  # logs will store all meal/water entries for each day

try:
    log_path = Path(LOG_FILE)
    # Check if the log file already exists (e.g., daily_log.json)
    if log_path.exists():
        with log_path.open("r", encoding="utf-8") as f:
            # Load the JSON contents into the logs dictionary
            logs = json.load(f)
# Handle two possible errors:
# 1. json.JSONDecodeError → if the JSON file is corrupted or not valid JSON
# 2. OSError → if the file can’t be opened (permissions, disk problem, etc.)
except (json.JSONDecodeError, OSError) as e:
    print(f"Warning: Could not read log file: {e}")
    # Fall back to an empty log so the app can still run
    logs = {}

# Ensure today's entry exists
if TODAY not in logs:
    logs[TODAY] = {
        'mode': 'Toddler',
        'requirements': {},
        'meals': [],
        'water_ml': 0.0
    }

# ---------- Totals ----------
tot_cal = tot_pro = tot_fat = tot_carb = water_total = 0.0


def recompute_totals():
    global tot_cal, tot_pro, tot_fat, tot_carb, water_total
    meals = logs[TODAY].get('meals', [])
    tot_cal = sum(m.get('calories', 0) for m in meals)
    tot_pro = sum(m.get('protein', 0) for m in meals)
    tot_fat = sum(m.get('fat', 0) for m in meals)
    tot_carb = sum(m.get('carbs', 0) for m in meals)
    water_total = logs[TODAY].get('water_ml', 0.0)


recompute_totals()


# ---------- Calculation functions ----------
def mifflin_st_jeor_bmr(weight, height, age, sex):
    if sex == 'Male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def toddler_calories(weight, activity):
    return weight * {'Low': 28, 'Medium': 32, 'High': 36}[activity]


def activity_multiplier(activity):
    return {'Low': 1.2, 'Medium': 1.5, 'High': 1.75}.get(activity, 1.2)


def calculate_requirements(mode, weight, height, age, sex, activity):
    if mode == 'Adult':
        bmr = mifflin_st_jeor_bmr(weight, height, age, sex)
        calories = bmr * activity_multiplier(activity)
        protein = weight * 1.6
        fat = weight * 0.9
        water_ml = weight * 30
    else:
        calories = toddler_calories(weight, activity)
        protein = weight * 1.2
        fat = weight * 0.8
        water_ml = weight * 30
    carbs = max((calories - (protein * 4 + fat * 9)) / 4, 0)
    return round(calories, 2), round(protein, 2), round(fat, 2), round(carbs, 2), round(water_ml, 2)


def ring_svg(percent, size=100, stroke=12, color='#4CAF50'):  # stroke: thickness of the ring line
    pct = max(0, min(100, percent))
    radius = (size - stroke) / 2
    circ = 2 * math.pi * radius
    dash = circ * pct / 100
    gap = circ - dash
    svg = f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <g transform="translate({size / 2},{size / 2})">
        <circle r="{radius}" stroke="#e6e6e6" stroke-width="{stroke}" fill="none"/>
        <circle r="{radius}" stroke="{color}" stroke-width="{stroke}" stroke-dasharray="{dash} {gap}" 
        stroke-line cap="round" transform="rotate(-90)" fill="none"/>
        <text x="0" y="6" text-anchor="middle" font-size="{size * 0.22}" font-weight="600">{pct:.0f}%</text>
      </g>
    </svg>
    '''
    return svg


# ---------- UI ----------
with ui.row().style('max-width:1200px;margin:auto;gap:30px'):
    # LEFT Column
    with ui.column().style('width:48%;gap:12px'):
        ui.markdown('## Water and Nutrition Tracker').style('font-weight:700')
        # Mode Select
        mode_select = ui.select(['Toddler', 'Adult'], value=logs[TODAY].get('mode', 'Toddler'), label='Mode')
        # --- Inputs that should hide/show ---
        with ui.row().style('gap:20px'):
            weight_input = ui.input('Weight (kg)').props('type=number outlined')

        # Group height + age + sex in a container, so we can hide/show it
        with ui.column() as adult_fields:
            with ui.row():
                height_input = ui.input('Height (cm)').props('type=number outlined')
                age_input = ui.input('Age (yrs)').props('type=number outlined')
            sex_select = ui.select(['Male', 'Female'], value='Female', label='Sex')

        activity_select = ui.select(['Low', 'Medium', 'High'], value='Low', label='Activity')
        requirement_label = ui.label('Daily Requirement → Not set').style('font-weight:700;color:#0b79d0')

        # --- Mode change logic ---
        # The original function remains unchanged and clean.
        def update_field_visibility():
            if mode_select.value == 'Toddler':
                adult_fields.visible = False
            else:
                adult_fields.visible = True


        adult_fields.bind_visibility_from(mode_select, 'value', backward=lambda v: v != 'Toddler')
        # Initial state setup works as-is.
        update_field_visibility()

        # Set requirements
        def set_requirements():
            global req_cal, req_pro, req_fat, req_carb, req_water
            if not weight_input.value:
                ui.notify('Enter weight', color='negative')
                return
            if mode_select.value == 'Adult' and (not height_input.value or not age_input.value):
                ui.notify('Enter height & age', color='negative')
                return
            req_cal, req_pro, req_fat, req_carb, req_water = calculate_requirements(
                mode_select.value,
                float(weight_input.value),
                float(height_input.value or 0),
                float(age_input.value or 0),
                sex_select.value,
                activity_select.value
            )
            logs[TODAY]['mode'] = mode_select.value
            logs[TODAY]['requirements'] = {'calories': req_cal, 'protein': req_pro, 'fat': req_fat, 'carbs': req_carb,
                                           'water_ml': req_water}
            json.dump(logs, open(LOG_FILE, 'w'), indent=2)
            requirement_label.set_text(
                f"Daily Requirement → Calories: {req_cal:.1f} kcal | Protein: {req_pro:.1f} g | Fat: {req_fat:.1f} g | "
                f"Carbs: {req_carb:.1f} g | Water: {req_water:.0f} ml")
            recompute_totals()
            update_progress_bars()
            update_visuals()
            ui.notify('Requirements set!', color='positive')


        ui.button('Set Requirements', on_click=set_requirements)

        # Meal logging
        ui.markdown('### Meal Tracker')
        food_select = ui.select(list(menu['Food']), label='Food')
        log_box = ui.html('# Meal Log<br>', sanitize=False).style(
            'height:180px;overflow:auto;border:1px solid #ddd;padding:8px;')


        def log_meal():
            if not food_select.value:
                ui.notify('Select food', color='negative')
                return
            row = menu[menu['Food'] == food_select.value].iloc[0]
            entry = {'time': datetime.datetime.now().isoformat(), 'food': row['Food'],
                     'calories': float(row['Calories']), 'protein': float(row['Protein']), 'fat': float(row['Fat']),
                     'carbs': float(row['Carbs'])}
            logs[TODAY].setdefault('meals', []).append(entry)
            json.dump(logs, open(LOG_FILE, 'w'), indent=2)
            recompute_totals()
            log_box.set_content(
                log_box.content + f"- {entry['time'][:19]} {entry['food']} → C:{entry['calories']:.1f} "
                                  f"P:{entry['protein']:.1f} F:{entry['fat']:.1f} Cr:{entry['carbs']:.1f}<br>")
            update_progress_bars()
            update_visuals()
            ui.notify('Meal logged', color='positive')


        ui.button('Log Meal', on_click=log_meal)

        # Water logging
        ui.markdown('### Water Tracker')
        water_input = ui.input('Water (ml)').props('type=number outlined')


        def add_water():
            try:
                amt = float(water_input.value)
            except ValueError:
                ui.notify('Enter valid water', color='negative')
                return
            logs[TODAY]['water_ml'] = logs[TODAY].get('water_ml', 0.0) + amt
            json.dump(logs, open(LOG_FILE, 'w'), indent=2)
            recompute_totals()
            log_box.set_content(
                log_box.content + f"- {datetime.datetime.now().strftime('%H:%M:%S')} Water: {amt:.0f} ml<br>")
            water_input.value = ''
            update_progress_bars()
            update_visuals()
            if water_total >= req_water > 0:
                ui.notify('Reached water goal!', color='positive')


        ui.button('Add Water', on_click=add_water)

        # RIGHT column
    with ui.column().style('width:48%;gap:12px'):
        ui.label('Calories Progress:')
        calorie_progress = ui.html('', sanitize=False).style('width:100%')
        ui.label('Water Progress:')
        water_progress = ui.html('', sanitize=False).style('width:100%')
        with ui.row().style('gap:20px;align-items:center'):
            calorie_ring = ui.html('', sanitize=False).style('width:120px;height:120px')
            water_ring = ui.html('', sanitize=False).style('width:120px;height:120px')
            pie_image = ui.image().style('width:220px;height:220px;object-fit:contain')


def update_progress_bars():
    cal_pct = (tot_cal / req_cal * 100) if req_cal else 0
    water_pct = (water_total / req_water * 100) if req_water else 0
    cal_display = max(0, min(100, cal_pct))
    water_display = max(0, min(100, water_pct))
    cal_color = '#FF9800' if tot_cal <= req_cal else '#f44336'
    water_color = '#4CAF50' if water_total <= req_water else '#2196F3'

    calorie_progress.set_content(f'''
    <div style="width:100%;height:36px;background:#eee;border-radius:10px;position:relative;">
      <div style="width:{cal_display}%;height:100%;background:{cal_color};border-radius:10px;"></div>
      <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:700;">
        {cal_pct:.1f}%
      </div>
    </div>
    ''')
    water_progress.set_content(f'''
    <div style="width:100%;height:36px;background:#eee;border-radius:10px;position:relative;">
      <div style="width:{water_display}%;height:100%;background:{water_color};border-radius:10px;"></div>
      <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:700;">
        {water_pct:.1f}%
      </div>
    </div>
    ''')


def update_visuals():
    calorie_ring.set_content(ring_svg((tot_cal / req_cal * 100) if req_cal else 0, size=120, stroke=14))
    water_ring.set_content(
        ring_svg((water_total / req_water * 100) if req_water else 0, size=120, stroke=14, color='#4CAF50'))


def clear_today():
    logs[TODAY] = {
        'mode': logs[TODAY].get('mode', 'Toddler'),
        'requirements': logs[TODAY].get('requirements', {}),
        'meals': [],
        'water_ml': 0.0
    }
    json.dump(logs, open(LOG_FILE, 'w'), indent=2)

    recompute_totals()
    update_progress_bars()
    update_visuals()

    log_box.set_content("#### Log<br>")
    ui.notify("Today's data cleared!", color='positive')


ui.button('Clear Today’s Data', color='negative', on_click=clear_today)

# ---------- Initial population ----------
reqs = logs[TODAY].get('requirements', {})
req_cal = reqs.get('calories', 0.0)
req_pro = reqs.get('protein', 0.0)
req_fat = reqs.get('fat', 0.0)
req_carb = reqs.get('carbs', 0.0)
req_water = reqs.get('water_ml', 0.0)
recompute_totals()
update_progress_bars()
update_visuals()

# ---------- Run ----------
ui.run(title='Water and Nutrition Tracker')
