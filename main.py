import tkinter as tk
from PIL import Image, ImageTk
import math

# -------------------------
# PRESETY AUT
# -------------------------

CARS = {
    "malé": {
        "mass": 900,
        "img": "car_small.png",
        "size": 140
    },
    "normalní": {
        "mass": 1200,
        "img": "car.png",
        "size": 180
    },
    "velké": {
        "mass": 1800,
        "img": "car_big.png",
        "size": 240
    }
}

# -------------------------
# PRESETY BRZD
# -------------------------

BRAKES = {
    "slabé": 5.0,
    "střední": 9.0,
    "sportovní": 12.0
}

PERSON_MASS = 75

WIDTH = 900
HEIGHT = 500
GROUND_Y = 350
WALL_X = 700

DEFORMATION_ZONE = 0.8
REACTION_TIME = 1.0

# -------------------------
# FYZIKA
# -------------------------

def mass(base, people):
    return base + people * PERSON_MASS


def energy(m, v):
    return 0.5 * m * v * v


def acceleration(v, d):
    if d <= 0:
        return float("inf")
    return (v * v) / (2 * d)


def g_force(a):
    return a / 9.81


def impact_time(v, d):
    if v <= 0:
        return 0
    return (2 * d) / v


def impact_force(m, v, t):
    if t <= 0:
        return 0
    return (m * v) / t


def risk(g):
    if g < 5:
        return "Bezpečné"
    elif g < 12:
        return "Riziko zranění"
    elif g < 25:
        return "Vážné zranění"
    else:
        return "Smrtelné riziko"


# -------------------------
# SIMULACE
# -------------------------

running = False
car_obj = None
will_stop = False
STOP_X = 0


def start():

    global running
    global car_obj
    global will_stop
    global car_img
    global CAR_W
    global CAR_H
    global STOP_X

    if running:
        return

    try:
        v_kmh = float(speed_entry.get())
        people = int(people_entry.get())
        distance_when_notice = float(distance_entry.get())

        car_type = car_var.get()
        brake_type = brake_var.get()

    except:
        result_label.config(text="Chybné vstupy")
        return

    running = True

    canvas.delete("all")

    # -------------------------
    # AUTO
    # -------------------------

    car = CARS[car_type]

    base_mass = car["mass"]

    img = Image.open(car["img"]).convert("RGBA")

    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    CAR_W = car["size"]

    ratio = CAR_W / img.width
    CAR_H = int(img.height * ratio)

    img = img.resize((CAR_W, CAR_H), Image.Resampling.LANCZOS)

    car_img = ImageTk.PhotoImage(img)

    STOP_X = WALL_X - CAR_W

    # -------------------------
    # BRZDY
    # -------------------------

    MAX_DECEL = BRAKES[brake_type]

    # -------------------------
    # SCENA
    # -------------------------

    canvas.create_rectangle(
        0,
        GROUND_Y,
        WIDTH,
        HEIGHT,
        fill="green"
    )

    canvas.create_rectangle(
        WALL_X,
        180,
        WALL_X + 40,
        GROUND_Y,
        fill="gray"
    )

    m = mass(base_mass, people)
    v = v_kmh / 3.6

    d_reaction = v * REACTION_TIME
    d_braking = (v * v) / (2 * MAX_DECEL)

    d_needed = d_reaction + d_braking + DEFORMATION_ZONE

    diff = distance_when_notice - d_needed

    if diff >= 0:

        will_stop = True

        impact_speed = 0
        impact_energy = 0
        g = 0
        F = 0

        result_text = f"ZASTAVIL JSI {diff:.2f} m před zdí"

    else:

        will_stop = False

        braking_space = distance_when_notice - d_reaction

        if braking_space <= 0:
            impact_speed = v
        else:

            remaining = v * v - 2 * MAX_DECEL * braking_space

            if remaining > 0:
                impact_speed = math.sqrt(remaining)
            else:
                impact_speed = 0

        a = acceleration(impact_speed, DEFORMATION_ZONE)
        g = g_force(a)

        t = impact_time(impact_speed, DEFORMATION_ZONE)

        F = impact_force(m, impact_speed, t)

        impact_energy = energy(m, impact_speed)

        result_text = (
            f"NESTAČILO O {abs(diff):.2f} m\n"
            f"Rychlost při střetu: {impact_speed*3.6:.1f} km/h"
        )

    status = risk(g)

    result_label.config(

        text=

        f"Auto: {car_type}\n"
        f"Brzdy: {brake_type}\n\n"

        f"Rychlost: {v_kmh:.1f} km/h\n"
        f"Hmotnost: {m:.0f} kg\n\n"

        f"Reakcni draha: {d_reaction:.2f} m\n"
        f"Brzdna draha: {d_braking:.2f} m\n"
        f"Potrebna draha: {d_needed:.2f} m\n\n"

        f"Energie: {impact_energy:,.0f} J\n"
        f"Sila: {F:,.0f} N\n"
        f"G-force: {g:.1f}\n"
        f"Riziko: {status}\n\n"

        + result_text
    )

    car_obj = canvas.create_image(

        50,
        GROUND_Y - CAR_H,
        anchor="nw",
        image=car_img

    )

    move(6)


def move(speed):

    global running

    x, y = canvas.coords(car_obj)

    if will_stop:

        next_x = x + speed

        if next_x < STOP_X:

            canvas.move(car_obj, speed, 0)

            root.after(20, lambda: move(speed))

        else:

            canvas.coords(car_obj, STOP_X, y)

            running = False

    else:

        next_x = x + speed

        if next_x + CAR_W <= WALL_X:

            canvas.move(car_obj, speed, 0)

            root.after(20, lambda: move(speed))

        else:

            canvas.coords(car_obj, WALL_X - CAR_W, y)

            running = False


# -------------------------
# GUI
# -------------------------

root = tk.Tk()

root.title("Crash simulator")

tk.Label(root, text="Rychlost (km/h)").pack()

speed_entry = tk.Entry(root)
speed_entry.pack()
speed_entry.insert(0, "60")

tk.Label(root, text="Počet lidí").pack()

people_entry = tk.Entry(root)
people_entry.pack()
people_entry.insert(0, "4")

tk.Label(root, text="Kdy řidič zpozoruje překážku (m)").pack()

distance_entry = tk.Entry(root)
distance_entry.pack()
distance_entry.insert(0, "50")

tk.Label(root, text="Výběr auta").pack()

car_var = tk.StringVar(value="normalní")

tk.OptionMenu(
    root,
    car_var,
    *CARS.keys()
).pack()

tk.Label(root, text="Výber brzd").pack()

brake_var = tk.StringVar(value="střední")

tk.OptionMenu(
    root,
    brake_var,
    *BRAKES.keys()
).pack()

tk.Button(
    root,
    text="Spustit simulaci",
    command=start
).pack(pady=5)

result_label = tk.Label(
    root,
    text="",
    justify="left"
)

result_label.pack()

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="skyblue"
)

canvas.pack()

root.mainloop()