from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import sqlite3
import hashlib

auth = Blueprint('auth', __name__)


@auth.route('register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        login = request.form['login']
        password1 = request.form['password1']
        password2 = request.form['password2']
        conn  = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user_credentials WHERE login = ?", (login,))
        user = c.fetchone()
        if user:
            flash('This login already exists. Please use a different one.', category='error')
        elif len(login)<1:
            flash('Please enter your login and password.', category='error')
        elif len(password1) < 7 or len(password1) > 21:
            flash('Password must have from 8 to 20 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'t match.', category='error')
        else:
            c.execute("INSERT INTO user_credentials (login, password) VALUES (?, ?)",
                      (login, hashlib.sha256(password1.encode()).hexdigest()))
            conn.commit()
            flash('Sucessfull registration! Account created. Please log in now.', category='success')
            return redirect(url_for('views.home'))
        conn.close()


    return render_template("register.html")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        login = request.form['login']
        password1 = request.form['password']
        c.execute("SELECT * FROM user_credentials WHERE login = ?", (login,))
        user = c.fetchone()
        if user:
            if user[2] == hashlib.sha256(password1.encode()).hexdigest():
                flash('Login sucessfull!', category='success')
                session["user_session"] = user[0]
                return redirect(url_for('auth.personal'))
            else:
                flash('Wrong password.', category = 'error')
        else:
            flash('Please register account before logging in.', category='error')

        conn.close()

    return render_template("login.html")


@auth.route('logout')
def logout():
    if "user_session" in session:
        session.pop("user_session", None)
        return redirect(url_for('views.home'))
    else:
        flash("You have to log in first.", category='error')
        return redirect(url_for('auth.login'))


@auth.route('personal', methods=['GET', 'POST'])
def personal():
    if request.method == 'POST':
        user_session = session.get('user_session')
        age = request.form.get('age')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')
        activity = request.form.get('activity')
        goal = request.form.get('goal')
        train_day_per_week = request.form.get('train_day_per_week')
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        if age != "" and sex != "" and height != "" and weight != "" and goal != "" and train_day_per_week != "":
            c.execute("INSERT INTO personal_data (age, sex, height, weight, activity, goal, train_day_per_week, id_user) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (age, sex, height, weight, activity, goal, train_day_per_week, user_session,))
            conn.commit()
            c.execute("SELECT * FROM personal_data WHERE id_user = (?)", (user_session,))
            personal_all = c.fetchone()
            calories_goal_m = 0
            calories_goal_w = 0
            if personal_all[2] == 0:
                calories_goal_m = calories_goal_m + (personal_all[4] * 13.5 + personal_all[3] * 4.8 - personal_all[1] * 5.7 + 240 + 100*personal_all[5])
            if personal_all[2] == 1:
                calories_goal_w = calories_goal_m + (personal_all[4] * 9.2 + personal_all[3] * 3.1 - personal_all[1] * 4.3 + 477 + 70*personal_all[5])
            if personal_all[7] == 1:
                calories_goal_m = round(calories_goal_m) + 80
                calories_goal_w = round(calories_goal_w) + 60
            if personal_all[7] == 2:
                calories_goal_m = round(calories_goal_m) + 80 * 1.1
                calories_goal_w = round(calories_goal_w) + 60 * 1.1
            if personal_all[7] == 3:
                calories_goal_m = round(calories_goal_m) + 80 * 1.2
                calories_goal_w = round(calories_goal_w) + 60 * 1.2
            if personal_all[7] == 4:
                calories_goal_m = round(calories_goal_m) + 80 * 1.4
                calories_goal_w = round(calories_goal_w) + 60 * 1.4
            if personal_all[7] == 5:
                calories_goal_m = round(calories_goal_m) + 80 * 1.5
                calories_goal_w = round(calories_goal_w) + 60 * 1.5
            if personal_all[7] == 6:
                calories_goal_m = round(calories_goal_m) + 80 * 1.6
                calories_goal_w = round(calories_goal_w) + 60 * 1.6
            if personal_all[7] == 7:
                calories_goal_m = round(calories_goal_m) + 80 * 1.7
                calories_goal_w = round(calories_goal_w) + 60 * 1.7
            if personal_all[6] == 1:
                calories_goal_m = round(calories_goal_m) - 300
                calories_goal_w = round(calories_goal_w) - 200
            if personal_all[6] == 3:
                calories_goal_m = round(calories_goal_m) + 300
                calories_goal_w = round(calories_goal_w) + 200
            if personal_all[2] == 0:
                c.execute("SELECT id_user FROM user_credentials WHERE id_user = (?)", (user_session,))
                id_user = c.fetchone()
                c.execute("INSERT INTO calories_goal (calories_goal, id_personal) VALUES (?, ?)", (calories_goal_m, id_user[0]))
                conn.commit()
            if personal_all[2] == 1:
                c.execute("SELECT id_user FROM user_credentials WHERE id_user = (?)", (user_session,))
                id_user = c.fetchone()
                c.execute("INSERT INTO calories_goal (calories_goal, id_personal) VALUES (?, ?)", (calories_goal_w, id_user[0]))
                conn.commit()
            c.execute("SELECT u.login, p.age, p.sex, p.height, p.weight, p.activity, p.goal, p.train_day_per_week, c.calories_goal FROM personal_data p inner join user_credentials u on p.id_user = u.id_user \
                                inner join calories_goal c on  c.id_personal = p.id_personal WHERE u.id_user = (?)",
                      (user_session,))
            calories_all = c.fetchone()
            conn.close()
            return render_template("personal.html", calories_all=calories_all)
        else:
            flash("Please insert your personal data!", category='error')
            c.execute("SELECT u.login, p.age, p.sex, p.height, p.weight, p.activity, p.goal, p.train_day_per_week, c.calories_goal FROM personal_data p inner join user_credentials u on p.id_user = u.id_user \
                                            inner join calories_goal c on  c.id_personal = p.id_user WHERE u.id_user = (?)",
                      (user_session,))
            calories_all = c.fetchone()
            conn.close()
            return render_template("personal.html", calories_all=calories_all)
    else:
        user_session = session.get('user_session')
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        c.execute("SELECT u.login, p.age, p.sex, p.height, p.weight, p.activity, p.goal, p.train_day_per_week, c.calories_goal FROM personal_data p inner join user_credentials u on p.id_user = u.id_user \
                    inner join calories_goal c on  c.id_personal = p.id_user WHERE u.id_user = (?)", (user_session,))
        calories_all = c.fetchone()
        conn.close()
        return render_template("personal.html", calories_all=calories_all)


@auth.route('progress', methods=['GET', 'POST'])
def progress():
    if request.method == 'POST':
        user_session = session.get('user_session')
        date = request.form.get('date')
        weight = request.form.get('weight')
        training = request.form.get('training')
        steps = request.form.get('steps')
        notes = request.form.get('notes')
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        if date != "" and weight != "" and steps != "":
            c.execute("INSERT INTO progress (date_progress, current_weight, training, steps, notes, id_user) VALUES (?, ?, ?, ?, ?, ?)", (date, weight, training, steps, notes, user_session,))
            conn.commit()
            c.execute("SELECT * FROM progress WHERE id_user = (?)", (user_session,))
            progress_all = c.fetchall()
            conn.commit()
            conn.close()
            return render_template("progress.html", progress_all=progress_all)
        else:
            flash("Please insert your data", category='error')
            c.execute("SELECT * FROM progress WHERE id_user = (?)", (user_session,))
            progress_all = c.fetchall()
            conn.commit()
            conn.close()
            return render_template("progress.html", progress_all=progress_all)
    else:
        user_session = session.get('user_session')
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        c.execute("SELECT * FROM progress WHERE id_user = (?)", (user_session,))
        progress_all = c.fetchall()
        conn.commit()
        conn.close()
        return render_template("progress.html", progress_all=progress_all)


@auth.route('diet', methods=['GET', 'POST'])
def diet():
    if request.method == 'POST':
        user_session = session.get('user_session')
        date = request.form.get('date', False)
        calories = request.form.get('calories', False)
        proteins = request.form.get('proteins', False)
        carbohydrates = request.form.get('carbohydrates', False)
        fats = request.form.get('fats', False)
        liquids = request.form.get('liquids', False)
        notes = request.form.get('notes', False)
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        if date != "" and calories != "" and proteins != "" and carbohydrates != "" and fats != "" and liquids != "":
            c.execute("INSERT INTO diet (date_diet, calories_eaten, proteins_eaten,carbs_eaten, fats_eaten, liquids_drunk, notes, id_user) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (date, calories, proteins, carbohydrates, fats, liquids, notes, user_session),)
            conn.commit()
            c.execute("SELECT * FROM diet WHERE id_user = (?)", (user_session,))
            diet_all = c.fetchall()
            conn.commit()
            conn.close()
            return render_template("diet.html", diet_all=diet_all, proteins=proteins, carbohydrates=carbohydrates, fats=fats)
        else:
            flash("Please insert your data", category='error')
            c.execute("SELECT * FROM diet WHERE id_user = (?)", (user_session,))
            diet_all = c.fetchall()
            conn.commit()
            conn.close()
            return render_template("diet.html", diet_all=diet_all, proteins=proteins, carbohydrates=carbohydrates, fats=fats)
    else:
        user_session = session.get('user_session')
        conn = sqlite3.connect('progressapp.db')
        c = conn.cursor()
        c.execute("SELECT * FROM diet WHERE id_user = (?)", (user_session,))
        diet_all = c.fetchall()
        conn.commit()
        conn.close()
        return render_template("diet.html", diet_all=diet_all)