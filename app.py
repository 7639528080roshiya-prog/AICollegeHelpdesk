import os
import copy
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    session,
    url_for
)

from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "gct_smartdesk_secret_key_2026"
)

app.config["SESSION_PERMANENT"] = True

os.makedirs("staff_files", exist_ok=True)


# =========================================================
# MONGODB CONNECTION
# =========================================================

MONGO_URI = os.getenv("MONGO_URI")

client = None
db = None
collection = None
users_collection = None


if MONGO_URI:

    try:

        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        client.admin.command("ping")

        db = client["AICollegeHelpdesk"]

        collection = db["college_data"]

        users_collection = db["users"]

        print("======================================")
        print("MongoDB Atlas connected successfully!")
        print("Database: AICollegeHelpdesk")
        print("Collection: college_data")
        print("======================================")

    except Exception as e:

        print("MongoDB connection error:", e)

else:

    print("WARNING: MONGO_URI not found in .env")


# =========================================================
# COLLEGE DATA
# =========================================================

DATA = {

    "college_name":
        "Government College of Technology",

    "short_name":
        "GCT",

    "location":
        "Thadagam Road, Coimbatore",

    "contact":
        "0422-2432221",

    "principal":
        "Dr. K. Manonmani, M.E., Ph.D",

    "about":
        "GCT - Govt College since 1945.",

    "timing":
        "8:30 AM - 4:30 PM",

    "ug_courses": [

        "B.E Computer Science and Engineering",

        "B.E Electronics and Communication Engineering",

        "B.E Mechanical Engineering",

        "B.E Civil Engineering",

        "B.E Electrical and Electronics Engineering"

    ],

    "pg_courses": [

        "M.E Computer Science and Engineering",

        "MBA",

        "MCA"

    ],

    "facilities": [

        "Library",

        "Hostel",

        "Laboratories"

    ],

    "hostel":
        "Hostel facility is available."
}


# =========================================================
# DEFAULT STAFF DATA
# =========================================================

DEFAULT_STAFF_DATA = {

    "_id":
        "main_data",

    "admission":
        (
            "UG Admission 2026 is open. "
            "Contact 0422-2432221."
        ),

    "naan_mudhalvan":
        (
            "Naan Mudhalvan skill development programme "
            "is available for eligible students."
        ),

    "exam_fees": {

        "UG":
            "Rs.1500 per semester",

        "PG":
            "Rs.2000 per semester"

    },

    "announcement":
        (
            "Welcome to GCT SmartDesk. "
            "Check the portal regularly for latest announcements."
        ),

    "hostel":
        (
            "Separate hostel facilities are available for students."
        ),

    "library_timing":
        "Library timing: 8:30 AM - 5:30 PM",

    "students":
        [],

    "results": [

        {

            "roll_no":
                "C24UG223CSC028",

            "name":
                "Demo Student",

            "course":
                "B.E CSE",

            "semester":
                "VI",

            "result":
                "PASS"

        }

    ],

    "staff_list": [

        {

            "name":
                "Dr. K. Manonmani",

            "designation":
                "Principal",

            "department":
                "Administration"

        }

    ],

    "hod_list": [

        {

            "name":
                "Computer Science HOD",

            "department":
                "CSE"

        },

        {

            "name":
                "ECE HOD",

            "department":
                "ECE"

        },

        {

            "name":
                "Mechanical HOD",

            "department":
                "Mechanical"

        }

    ],

    "library_books": [

        {

            "book_id":
                "CSE001",

            "title":
                "Python Programming",

            "department":
                "CSE",

            "status":
                "Available"

        },

        {

            "book_id":
                "ECE002",

            "title":
                "Digital Electronics",

            "department":
                "ECE",

            "status":
                "Available"

        },

        {

            "book_id":
                "MECH01",

            "title":
                "Thermodynamics",

            "department":
                "Mechanical",

            "status":
                "Available"

        }

    ],

    "game_results": [

        {

            "game":
                "Cricket",

            "team":
                "GCT Team",

            "college":
                "GCT",

            "position":
                "1st Prize"

        },

        {

            "game":
                "Football",

            "team":
                "GCT Team",

            "college":
                "GCT",

            "position":
                "1st Prize"

        }

    ],

    "attendance":
        [],

    "fees_paid":
        [],

    "complaints":
        [],

    "placements": [

        {

            "company":
                "TCS",

            "status":
                "Upcoming"

        },

        {

            "company":
                "Infosys",

            "status":
                "Upcoming"

        }

    ],

    "events": [

        {

            "event":
                "College Annual Day",

            "date":
                "2026"

        },

        {

            "event":
                "Sports Day",

            "date":
                "2026"

        }

    ]

}


# =========================================================
# LOAD DATA FROM MONGODB
# =========================================================

def load_data():

    global collection

    if collection is not None:

        try:

            saved_data = collection.find_one(
                {"_id": "main_data"}
            )

            if saved_data:

                # Missing keys add
                for key, value in DEFAULT_STAFF_DATA.items():

                    if key not in saved_data:

                        saved_data[key] = copy.deepcopy(value)


                # =================================================
                # IMPORTANT TYPE FIXES
                # =================================================

                # exam_fees dictionary ஆக இருக்க வேண்டும்
                if not isinstance(
                    saved_data.get("exam_fees"),
                    dict
                ):

                    saved_data["exam_fees"] = copy.deepcopy(
                        DEFAULT_STAFF_DATA["exam_fees"]
                    )


                # library_books list ஆக இருக்க வேண்டும்
                if not isinstance(
                    saved_data.get("library_books"),
                    list
                ):

                    saved_data["library_books"] = copy.deepcopy(
                        DEFAULT_STAFF_DATA["library_books"]
                    )


                # placements list ஆக இருக்க வேண்டும்
                if not isinstance(
                    saved_data.get("placements"),
                    list
                ):

                    saved_data["placements"] = copy.deepcopy(
                        DEFAULT_STAFF_DATA["placements"]
                    )


                # results list ஆக இருக்க வேண்டும்
                if not isinstance(
                    saved_data.get("results"),
                    list
                ):

                    saved_data["results"] = copy.deepcopy(
                        DEFAULT_STAFF_DATA["results"]
                    )


                # game_results list ஆக இருக்க வேண்டும்
                if not isinstance(
                    saved_data.get("game_results"),
                    list
                ):

                    saved_data["game_results"] = copy.deepcopy(
                        DEFAULT_STAFF_DATA["game_results"]
                    )


                # events list ஆக இருக்க வேண்டும்
                if not isinstance(
                    saved_data.get("events"),
                    list
                ):

                    saved_data["events"] = copy.deepcopy(
                        DEFAULT_STAFF_DATA["events"]
                    )


                # attendance list
                if not isinstance(
                    saved_data.get("attendance"),
                    list
                ):

                    saved_data["attendance"] = []


                # fees_paid list
                if not isinstance(
                    saved_data.get("fees_paid"),
                    list
                ):

                    saved_data["fees_paid"] = []


                # complaints list
                if not isinstance(
                    saved_data.get("complaints"),
                    list
                ):

                    saved_data["complaints"] = []


                print(
                    "College data loaded from MongoDB."
                )

                return saved_data


            # No data found
            default_data = copy.deepcopy(
                DEFAULT_STAFF_DATA
            )

            collection.insert_one(
                default_data
            )

            print(
                "Default college data inserted."
            )

            return default_data


        except Exception as e:

            print(
                "Error loading MongoDB data:",
                e
            )


    print(
        "Using default local data."
    )

    return copy.deepcopy(
        DEFAULT_STAFF_DATA
    )


STAFF_DATA = load_data()


# =========================================================
# SAVE DATA TO MONGODB
# =========================================================

def save_to_db():

    global collection

    if collection is None:

        return False

    try:

        data_to_save = copy.deepcopy(
            STAFF_DATA
        )

        data_to_save["_id"] = "main_data"

        collection.replace_one(

            {"_id": "main_data"},

            data_to_save,

            upsert=True

        )

        return True

    except Exception as e:

        print(
            "MongoDB save error:",
            e
        )

        return False


# =========================================================
# LOGIN CHECK
# =========================================================

def is_logged_in():

    return (

        "user" in session

        and

        session.get(
            "logged_in"
        ) is True

    )


# =========================================================
# MAIN HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template(

        "home.html",

        username=session.get(
            "user",
            "Guest"
        ),

        role=session.get(
            "role",
            "guest"
        ),

        data=DATA,

        staff_data=STAFF_DATA

    )


# =========================================================
# HOME
# =========================================================

@app.route("/home")
def home():

    return render_template(

        "home.html",

        username=session.get(
            "user",
            "Guest"
        ),

        role=session.get(
            "role",
            "guest"
        ),

        data=DATA,

        staff_data=STAFF_DATA

    )


# =========================================================
# LIVE CHAT PAGE
# =========================================================

@app.route("/chatbot")
def chatbot():

    return render_template(

        "index.html",

        username=session.get(
            "user",
            "Guest"
        ),

        role=session.get(
            "role",
            "guest"
        ),

        data=DATA,

        staff_data=STAFF_DATA

    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    username = (

        request.form.get(
            "username"
        )

        or ""

    ).strip()


    email = (

        request.form.get(
            "email"
        )

        or ""

    ).strip()


    login_name = (

        username

        or email

        or "Student"

    )


    session.clear()


    session["user"] = login_name

    session["username"] = login_name

    session["email"] = (

        email

        if email

        else f"{login_name}@gct.ac.in"

    )

    session["role"] = "student"

    session["logged_in"] = True

    session.permanent = True


    return redirect(
        url_for("home")
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )


    name = (

        request.form.get(
            "name",
            ""
        )

        .strip()

    )


    email = (

        request.form.get(
            "email",
            ""
        )

        .strip()

        .lower()

    )


    password = request.form.get(
        "password",
        ""
    )


    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    if not name or not email or not password:

        return render_template(

            "register.html",

            error=(
                "Please fill all required fields."
            )

        )


    if "@" not in email:

        return render_template(

            "register.html",

            error=(
                "Please enter a valid email."
            )

        )


    if len(password) < 6:

        return render_template(

            "register.html",

            error=(
                "Password must contain "
                "at least 6 characters."
            )

        )


    if password != confirm_password:

        return render_template(

            "register.html",

            error=(
                "Passwords do not match."
            )

        )


    if users_collection is None:

        return render_template(

            "register.html",

            error=(
                "MongoDB is not connected."
            )

        )


    try:

        existing_user = users_collection.find_one(

            {
                "email": {

                    "$regex":
                        f"^{email}$",

                    "$options":
                        "i"

                }
            }

        )


        if existing_user:

            return render_template(

                "register.html",

                error=(
                    "Email already registered."
                )

            )


        hashed_password = generate_password_hash(
            password
        )


        new_user = {

            "name":
                name,

            "email":
                email,

            "password_hash":
                hashed_password,

            "role":
                "student",

            "created_at":
                datetime.utcnow()

        }


        users_collection.insert_one(
            new_user
        )


        return render_template(

            "login.html",

            message=(
                "Registration successful. "
                "Please login."
            )

        )


    except Exception as e:

        print(
            "Registration error:",
            e
        )

        return render_template(

            "register.html",

            error=(
                "Registration failed. "
                "Please try again."
            )

        )


# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/google-login")
def google_login():

    return render_template(

        "login.html",

        error=(
            "Google login is not configured yet."
        )

    )


# =========================================================
# STUDENT
# =========================================================

@app.route("/student")
def student():

    if not session.get(
        "student_verified"
    ):

        return render_template(

            "student_login.html",

            username=session.get(
                "user",
                "Student"
            )

        )


    return render_template(

        "student.html",

        username=session.get(
            "user",
            "Student"
        ),

        role="student",

        data=DATA,

        staff_data=STAFF_DATA,

        access_type="result_only"

    )


# =========================================================
# STUDENT VERIFY
# =========================================================

@app.route(
    "/student/verify",
    methods=["POST"]
)
def student_verify():

    dob = (

        request.form.get(
            "dob"
        )

        or ""

    ).strip()


    print(
        f"STUDENT DOB TRY: {dob}"
    )


    if not dob:

        return render_template(

            "student_login.html",

            username=session.get(
                "user",
                "Student"
            ),

            error=(
                "Date of Birth podu da!"
            )

        )


    valid = False


    for fmt in (

        "%Y-%m-%d",

        "%d-%m-%Y",

        "%d/%m/%Y",

        "%Y/%m/%d"

    ):

        try:

            datetime.strptime(
                dob,
                fmt
            )

            valid = True

            break

        except Exception:

            pass


    if not valid and len(dob) < 4:

        return render_template(

            "student_login.html",

            username=session.get(
                "user",
                "Student"
            ),

            error=(
                "Correct DOB podu da! "
                "Ex: 2005-05-15"
            )

        )


    session["student_verified"] = True

    session["student_dob"] = dob

    session["role"] = "student"

    session["user"] = session.get(
        "user",
        "Student"
    )

    session["logged_in"] = True


    print(
        f"STUDENT DOB VERIFIED: {dob}"
    )


    return redirect(
        url_for("student")
    )


# =========================================================
# STAFF
# =========================================================

@app.route("/staff")
def staff():

    if not session.get(
        "staff_verified"
    ):

        return render_template(

            "staff_login.html",

            username=session.get(
                "user",
                "Staff"
            )

        )


    return render_template(

        "staff.html",

        username=session.get(
            "user",
            "Staff"
        ),

        role="staff",

        data=DATA,

        staff_data=STAFF_DATA,

        access_type="staff"

    )


# =========================================================
# STAFF VERIFY
# =========================================================

@app.route(
    "/staff/verify",
    methods=["POST"]
)
def staff_verify():

    password = (

        request.form.get(
            "password"
        )

        or ""

    ).strip()


    print(
        f"STAFF PASSWORD TRY: {password}"
    )


    if password == "staff123":

        session["staff_verified"] = True

        session["role"] = "staff"

        session["user"] = session.get(
            "user",
            "Staff"
        )

        session["logged_in"] = True


        print(
            "STAFF ACCESS GRANTED"
        )


        return redirect(
            url_for("staff")
        )


    return render_template(

        "staff_login.html",

        username=session.get(
            "user",
            "Staff"
        ),

        error=(
            f"Invalid Password! "
            f"You typed: {password}"
        )

    )


# =========================================================
# PRINCIPAL
# =========================================================

@app.route("/principal")
def principal():

    if not session.get(
        "principal_verified"
    ):

        return render_template(

            "principal_login.html",

            username=session.get(
                "user",
                "Principal"
            )

        )


    return render_template(

        "principal.html",

        username=session.get(
            "user",
            "Principal"
        ),

        role="principal",

        data=DATA,

        staff_data=STAFF_DATA,

        access_type="full"

    )


# =========================================================
# PRINCIPAL VERIFY
# =========================================================

@app.route(
    "/principal/verify",
    methods=["POST"]
)
def principal_verify():

    password = (

        request.form.get(
            "password"
        )

        or ""

    ).strip()


    print(
        f"PRINCIPAL PASSWORD TRY: {password}"
    )


    if password == "gct123":

        session["principal_verified"] = True

        session["role"] = "principal"

        session["user"] = session.get(
            "user",
            "Principal"
        )

        session["logged_in"] = True


        print(
            "PRINCIPAL ACCESS GRANTED"
        )


        return redirect(
            url_for("principal")
        )


    return render_template(

        "principal_login.html",

        username=session.get(
            "user",
            "Principal"
        ),

        error=(
            f"Invalid Password! "
            f"You typed: {password}"
        )

    )


# =========================================================
# LIBRARY
# =========================================================

@app.route("/library")
def library():

    books = STAFF_DATA.get(
        "library_books",
        []
    )


    if not isinstance(books, list):

        books = []


    return render_template(

        "library.html",

        username=session.get(
            "user",
            "User"
        ),

        role=session.get(
            "role",
            "student"
        ),

        data=DATA,

        staff_data=STAFF_DATA,

        books=books

    )


# =========================================================
# GAMES
# =========================================================

@app.route("/games")
def games():

    game_results = STAFF_DATA.get(
        "game_results",
        []
    )


    if not isinstance(
        game_results,
        list
    ):

        game_results = []


    return render_template(

        "games.html",

        username=session.get(
            "user",
            "User"
        ),

        role=session.get(
            "role",
            "student"
        ),

        data=DATA,

        staff_data=STAFF_DATA,

        game_results=game_results

    )


# =========================================================
# SAVE GAME
# =========================================================

@app.route(
    "/games/save",
    methods=["POST"]
)
def save_game():

    game = (

        request.form.get(
            "game",
            ""
        )

        .strip()

    )


    team = (

        request.form.get(
            "team",
            ""
        )

        .strip()

    )


    college = (

        request.form.get(
            "college",
            "GCT"
        )

        .strip()

    )


    position = (

        request.form.get(
            "position",
            ""
        )

        .strip()

    )


    if not game:

        return jsonify({

            "success":
                False,

            "message":
                "Game name is required."

        }), 400


    if not isinstance(
        STAFF_DATA.get("game_results"),
        list
    ):

        STAFF_DATA["game_results"] = []


    new_game = {

        "game":
            game,

        "team":
            team,

        "college":
            college,

        "position":
            position

    }


    STAFF_DATA["game_results"].append(
        new_game
    )


    save_to_db()


    return jsonify({

        "success":
            True,

        "message":
            "Game result saved successfully.",

        "data":
            new_game

    })


# =========================================================
# ATTENDANCE SAVE
# =========================================================

@app.route(
    "/attendance/save",
    methods=["POST"]
)
def save_attendance():

    if not (

        session.get(
            "staff_verified"
        )

        or

        session.get(
            "principal_verified"
        )

    ):

        return jsonify({

            "success":
                False,

            "message":
                "Staff/Principal access only."

        }), 403


    roll_no = (

        request.form.get(
            "roll_no",
            ""
        )

        or

        request.form.get(
            "roll",
            ""
        )

    ).strip()


    attendance = (

        request.form.get(
            "attendance",
            ""
        )

        or

        request.form.get(
            "percentage",
            ""
        )

    ).strip()


    if not roll_no:

        return jsonify({

            "success":
                False,

            "message":
                "Roll number is required."

        }), 400


    if not isinstance(
        STAFF_DATA.get("attendance"),
        list
    ):

        STAFF_DATA["attendance"] = []


    record = {

        "roll_no":
            roll_no,

        "attendance":
            attendance,

        "updated_at":
            datetime.utcnow().isoformat()

    }


    STAFF_DATA["attendance"].append(
        record
    )


    save_to_db()


    return jsonify({

        "success":
            True,

        "message":
            "Attendance saved successfully.",

        "data":
            record

    })


# =========================================================
# FEES SAVE
# =========================================================

@app.route(
    "/fees/save",
    methods=["POST"]
)
def save_fees():

    if not (

        session.get(
            "staff_verified"
        )

        or

        session.get(
            "principal_verified"
        )

    ):

        return jsonify({

            "success":
                False,

            "message":
                "Staff/Principal access only."

        }), 403


    roll_no = (

        request.form.get(
            "roll_no",
            ""
        )

        or

        request.form.get(
            "roll",
            ""
        )

    ).strip()


    amount = (

        request.form.get(
            "amount",
            ""
        )

        .strip()

    )


    status = (

        request.form.get(
            "status",
            "Paid"
        )

        .strip()

    )


    if not roll_no:

        return jsonify({

            "success":
                False,

            "message":
                "Roll number is required."

        }), 400


    if not isinstance(
        STAFF_DATA.get("fees_paid"),
        list
    ):

        STAFF_DATA["fees_paid"] = []


    record = {

        "roll_no":
            roll_no,

        "amount":
            amount,

        "status":
            status,

        "updated_at":
            datetime.utcnow().isoformat()

    }


    STAFF_DATA["fees_paid"].append(
        record
    )


    save_to_db()


    return jsonify({

        "success":
            True,

        "message":
            "Fee details saved successfully.",

        "data":
            record

    })


# =========================================================
# MANAGE DATA
# =========================================================

@app.route(
    "/manage-data",
    methods=["GET", "POST"]
)
def manage_data():

    if not session.get(
        "principal_verified"
    ):

        return redirect(
            url_for("principal")
        )


    if request.method == "GET":

        return render_template(

            "manage_data.html",

            username=session.get(
                "user"
            ),

            role=session.get(
                "role"
            ),

            data=DATA,

            staff_data=STAFF_DATA

        )


    admission = request.form.get(
        "admission"
    )


    naan_mudhalvan = request.form.get(
        "naan_mudhalvan"
    )


    announcement = request.form.get(
        "announcement"
    )


    hostel = request.form.get(
        "hostel"
    )


    library_timing = request.form.get(
        "library_timing"
    )


    ug_fee = request.form.get(
        "ug_fee"
    )


    pg_fee = request.form.get(
        "pg_fee"
    )


    if admission:

        STAFF_DATA["admission"] = admission


    if naan_mudhalvan:

        STAFF_DATA["naan_mudhalvan"] = naan_mudhalvan


    if announcement:

        STAFF_DATA["announcement"] = announcement


    if hostel:

        STAFF_DATA["hostel"] = hostel


    if library_timing:

        STAFF_DATA["library_timing"] = library_timing


    # =====================================================
    # IMPORTANT EXAM FEE TYPE FIX
    # =====================================================

    if not isinstance(
        STAFF_DATA.get("exam_fees"),
        dict
    ):

        STAFF_DATA["exam_fees"] = copy.deepcopy(
            DEFAULT_STAFF_DATA["exam_fees"]
        )


    if ug_fee:

        STAFF_DATA["exam_fees"]["UG"] = ug_fee


    if pg_fee:

        STAFF_DATA["exam_fees"]["PG"] = pg_fee


    save_to_db()


    return redirect(
        url_for("home")
    )


# =========================================================
# COMPLAINT
# =========================================================

@app.route(
    "/complaint",
    methods=["GET", "POST"]
)
def complaint():

    if request.method == "POST":

        complaint_text = (

            request.form.get(
                "complaint",
                ""
            )

            or

            request.form.get(
                "message",
                ""
            )

        ).strip()


        if complaint_text:

            if not isinstance(
                STAFF_DATA.get("complaints"),
                list
            ):

                STAFF_DATA["complaints"] = []


            complaint_data = {

                "username":
                    session.get(
                        "user",
                        "User"
                    ),

                "email":
                    session.get(
                        "email",
                        "user@gct.ac.in"
                    ),

                "complaint":
                    complaint_text,

                "status":
                    "Pending",

                "created_at":
                    datetime.utcnow().isoformat()

            }


            STAFF_DATA["complaints"].append(
                complaint_data
            )


            save_to_db()


            return render_template(

                "complaint.html",

                username=session.get(
                    "user",
                    "User"
                ),

                role=session.get(
                    "role",
                    "student"
                ),

                message=(
                    "Complaint submitted successfully."
                )

            )


    return render_template(

        "complaint.html",

        username=session.get(
            "user",
            "User"
        ),

        role=session.get(
            "role",
            "student"
        )

    )


# =========================================================
# PLACEMENT
# =========================================================

@app.route(
    "/placement",
    methods=["GET", "POST"]
)
def placement():

    if request.method == "POST":

        if not session.get(
            "principal_verified"
        ):

            return jsonify({

                "success":
                    False,

                "message":
                    "Principal access only."

            }), 403


        company = (

            request.form.get(
                "company",
                ""
            )

            .strip()

        )


        status = (

            request.form.get(
                "status",
                "Upcoming"
            )

            .strip()

        )


        if not company:

            return jsonify({

                "success":
                    False,

                "message":
                    "Company name is required."

            }), 400


        if not isinstance(
            STAFF_DATA.get("placements"),
            list
        ):

            STAFF_DATA["placements"] = []


        placement_data = {

            "company":
                company,

            "status":
                status

        }


        STAFF_DATA["placements"].append(
            placement_data
        )


        save_to_db()


        return jsonify({

            "success":
                True,

            "message":
                "Placement saved successfully."

        })


    placements = STAFF_DATA.get(
        "placements",
        []
    )


    if not isinstance(
        placements,
        list
    ):

        placements = []


    return render_template(

        "placement.html",

        username=session.get(
            "user",
            "User"
        ),

        role=session.get(
            "role",
            "student"
        ),

        placements=placements

    )


# =========================================================
# EVENTS
# =========================================================

@app.route("/events")
def events():

    event_data = STAFF_DATA.get(
        "events",
        []
    )


    if not isinstance(
        event_data,
        list
    ):

        event_data = []


    return render_template(

        "events.html",

        username=session.get(
            "user",
            "User"
        ),

        role=session.get(
            "role",
            "student"
        ),

        events=event_data

    )


# =========================================================
# STAFF FILE UPLOAD
# =========================================================

@app.route(
    "/staff/upload",
    methods=["POST"]
)
def staff_upload():

    if not (

        session.get(
            "staff_verified"
        )

        or

        session.get(
            "principal_verified"
        )

    ):

        return jsonify({

            "success":
                False,

            "message":
                "Staff/Principal only."

        }), 403


    file = request.files.get(
        "file"
    )


    if not file or not file.filename:

        return jsonify({

            "success":
                False,

            "message":
                "No file selected."

        }), 400


    filename = os.path.basename(
        file.filename
    )


    filepath = os.path.join(
        "staff_files",
        filename
    )


    try:

        file.save(filepath)


        return jsonify({

            "success":
                True,

            "message":
                "File uploaded successfully.",

            "filename":
                filename

        })


    except Exception as e:

        print(
            "File upload error:",
            e
        )


        return jsonify({

            "success":
                False,

            "message":
                "File upload failed."

        }), 500


# =========================================================
# GET RESULT
# =========================================================

@app.route(
    "/get_result",
    methods=["GET", "POST"]
)
def get_result():

    roll_no = (

        request.values.get(
            "roll_no",
            ""
        )

        or

        request.values.get(
            "roll",
            ""
        )

    ).strip()


    if not roll_no:

        return jsonify({

            "success":
                False,

            "message":
                "Please enter register number."

        }), 400


    results = STAFF_DATA.get(
        "results",
        []
    )


    if not isinstance(
        results,
        list
    ):

        results = []


    for result in results:

        if not isinstance(
            result,
            dict
        ):

            continue


        stored_roll = str(

            result.get(
                "roll_no",
                ""
            )

        ).strip()


        if (

            stored_roll.lower()

            ==

            roll_no.lower()

        ):

            return jsonify({

                "success":
                    True,

                "result":
                    result

            })


    return jsonify({

        "success":
            False,

        "message":
            "Result not found."

    })


# =========================================================
# LANGUAGE PAGE
# =========================================================

@app.route(
    "/language",
    methods=["GET", "POST"]
)
def language():

    if request.method == "POST":

        selected_language = (

            request.form.get(
                "language"
            )

            or

            request.form.get(
                "lang"
            )

            or

            "English"

        )


        session["language"] = selected_language


        next_page = request.form.get(
            "next"
        )


        if next_page:

            return redirect(
                next_page
            )


        return redirect(
            url_for("home")
        )


    return render_template(

        "language.html",

        username=session.get(
            "user",
            "User"
        ),

        role=session.get(
            "role",
            "student"
        ),

        selected_language=session.get(
            "language",
            "English"
        )

    )


# =========================================================
# SET LANGUAGE
# =========================================================

@app.route(
    "/set_language",
    methods=["POST"]
)
def set_language():

    try:

        data = request.get_json(
            silent=True
        ) or {}


        language = data.get(
            "language",
            "en"
        )


        # English / Tamil only

        if language not in [
            "en",
            "ta"
        ]:

            language = "en"


        session["language"] = language


        print(
            "Chat language selected:",
            language
        )


        return jsonify({

            "success":
                True,

            "language":
                language

        })


    except Exception as e:

        print(
            "Language error:",
            e
        )


        return jsonify({

            "success":
                False,

            "language":
                "en"

        }), 500


# =========================================================
# CHAT API
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        # =====================================================
        # GET MESSAGE SAFELY
        # =====================================================

        if request.is_json:

            data = request.get_json(
                silent=True
            ) or {}


            user_message = data.get(
                "message",
                ""
            )

        else:

            user_message = request.form.get(
                "message",
                ""
            )


        user_message = (

            user_message

            or ""

        ).strip()


        if not user_message:

            return jsonify({

                "reply":
                    "Please type your question."

            })


        msg = user_message.lower()


        # =====================================================
        # LANGUAGE
        # =====================================================

        language = session.get(
            "language",
            "en"
        )


        # =====================================================
        # GREETING
        # =====================================================

        if (

            "hello" in msg

            or

            "hi" in msg

            or

            "hey" in msg

            or

            "வணக்கம்" in user_message

        ):

            if language == "ta":

                reply = (
                    "வணக்கம்! "
                    "நான் GCT College Helpdesk. "
                    "என்ன உதவி வேண்டும்?"
                )

            else:

                reply = (
                    "Vanakkam! "
                    "I am GCT College Helpdesk. "
                    "How can I help you?"
                )


        # =====================================================
        # PRINCIPAL
        # =====================================================

        elif (

            "principal" in msg

            or

            "முதல்வர்" in user_message

        ):

            if language == "ta":

                reply = (
                    "கல்லூரி முதல்வர்: "
                    + str(DATA["principal"])
                )

            else:

                reply = (
                    "Principal: "
                    + str(DATA["principal"])
                )


        # =====================================================
        # ADMISSION
        # =====================================================

        elif (

            "admission" in msg

            or

            "admissions" in msg

            or

            "சேர்க்கை" in user_message

        ):

            admission = STAFF_DATA.get(

                "admission",

                "UG Admission 2026 is open."

            )


            if language == "ta":

                reply = (
                    "சேர்க்கை தகவல்:\n"
                    + str(admission)
                )

            else:

                reply = str(admission)


        # =====================================================
        # FEES
        # IMPORTANT FIX
        # =====================================================

        elif (

            "fee" in msg

            or

            "fees" in msg

            or

            "exam fee" in msg

            or

            "exam fees" in msg

            or

            "கட்டணம்" in user_message

            or

            "தேர்வு கட்டணம்" in user_message

        ):

            fees = STAFF_DATA.get(

                "exam_fees",

                {}

            )


            # -------------------------------------------------
            # IMPORTANT:
            # MongoDB-la exam_fees string ஆக இருந்தாலும்
            # .get() error வராது
            # -------------------------------------------------

            if isinstance(
                fees,
                dict
            ):

                ug_fee = fees.get(

                    "UG",

                    "Rs.1500 per semester"

                )


                pg_fee = fees.get(

                    "PG",

                    "Rs.2000 per semester"

                )

            else:

                ug_fee = (
                    "Rs.1500 per semester"
                )

                pg_fee = (
                    "Rs.2000 per semester"
                )


            if language == "ta":

                reply = (

                    "தேர்வு கட்டணம்:\n"

                    f"UG - {ug_fee}\n"

                    f"PG - {pg_fee}"

                )

            else:

                reply = (

                    "Exam Fees:\n"

                    f"UG - {ug_fee}\n"

                    f"PG - {pg_fee}"

                )


        # =====================================================
        # LIBRARY
        # =====================================================

        elif (

            "library" in msg

            or

            "books" in msg

            or

            "புத்தகம்" in user_message

            or

            "நூலகம்" in user_message

        ):

            books = STAFF_DATA.get(

                "library_books",

                []

            )


            if isinstance(
                books,
                list
            ):

                book_count = len(
                    books
                )

            else:

                book_count = 0


            if language == "ta":

                reply = (

                    "நூலகத்தில் தற்போது "

                    f"{book_count} புத்தகங்கள் "
                    "உள்ளன."

                )

            else:

                reply = (

                    "Library has "

                    f"{book_count} books."

                )


        # =====================================================
        # PLACEMENT
        # =====================================================

        elif (

            "placement" in msg

            or

            "placements" in msg

            or

            "வேலைவாய்ப்பு" in user_message

        ):

            placements = STAFF_DATA.get(

                "placements",

                []

            )


            companies = []


            if isinstance(
                placements,
                list
            ):

                for item in placements:

                    if isinstance(
                        item,
                        dict
                    ):

                        company = item.get(
                            "company",
                            ""
                        )


                        if company:

                            companies.append(
                                str(company)
                            )


                    elif isinstance(
                        item,
                        str
                    ):

                        companies.append(
                            item
                        )


            if companies:

                company_text = ", ".join(
                    companies
                )

            else:

                company_text = (
                    "No placement data available."
                )


            if language == "ta":

                reply = (

                    "வேலைவாய்ப்பு நிறுவனங்கள்:\n"

                    + company_text

                )

            else:

                reply = (

                    "Placement Companies:\n"

                    + company_text

                )


        # =====================================================
        # HOSTEL
        # =====================================================

        elif (

            "hostel" in msg

            or

            "ஹாஸ்டல்" in user_message

        ):

            hostel = STAFF_DATA.get(

                "hostel",

                DATA["hostel"]

            )


            if language == "ta":

                reply = (

                    "ஹாஸ்டல் தகவல்:\n"

                    + str(hostel)

                )

            else:

                reply = str(hostel)


        # =====================================================
        # COURSES
        # =====================================================

        elif (

            "course" in msg

            or

            "courses" in msg

            or

            "department" in msg

            or

            "departments" in msg

            or

            "பாடநெறி" in user_message

            or

            "துறை" in user_message

        ):

            ug_courses = DATA.get(
                "ug_courses",
                []
            )


            pg_courses = DATA.get(
                "pg_courses",
                []
            )


            if isinstance(
                ug_courses,
                list
            ):

                ug_text = ", ".join(

                    str(x)

                    for x in ug_courses

                )

            else:

                ug_text = str(
                    ug_courses
                )


            if isinstance(
                pg_courses,
                list
            ):

                pg_text = ", ".join(

                    str(x)

                    for x in pg_courses

                )

            else:

                pg_text = str(
                    pg_courses
                )


            if language == "ta":

                reply = (

                    "UG பாடநெறிகள்:\n"

                    + ug_text

                    + "\n\n"

                    + "PG பாடநெறிகள்:\n"

                    + pg_text

                )

            else:

                reply = (

                    "UG Courses:\n"

                    + ug_text

                    + "\n\n"

                    + "PG Courses:\n"

                    + pg_text

                )


        # =====================================================
        # CONTACT
        # =====================================================

        elif (

            "contact" in msg

            or

            "phone" in msg

            or

            "mobile" in msg

            or

            "address" in msg

            or

            "தொடர்பு" in user_message

            or

            "முகவரி" in user_message

        ):

            if language == "ta":

                reply = (

                    "GCT தொடர்பு தகவல்:\n"

                    f"தொலைபேசி: {DATA['contact']}\n"

                    f"முகவரி: {DATA['location']}"

                )

            else:

                reply = (

                    "GCT Contact:\n"

                    f"Phone: {DATA['contact']}\n"

                    f"Location: {DATA['location']}"

                )


        # =====================================================
        # TIMING
        # =====================================================

        elif (

            "timing" in msg

            or

            "time" in msg

            or

            "open" in msg

            or

            "நேரம்" in user_message

        ):

            if language == "ta":

                reply = (

                    "கல்லூரி நேரம்: "

                    + str(DATA["timing"])

                )

            else:

                reply = (

                    "College Timing: "

                    + str(DATA["timing"])

                )


        # =====================================================
        # RESULTS
        # =====================================================

        elif (

            "result" in msg

            or

            "results" in msg

            or

            "முடிவு" in user_message

            or

            "தேர்வு முடிவு" in user_message

        ):

            if language == "ta":

                reply = (

                    "தேர்வு முடிவுகளை "

                    "Student Result பகுதியில் "
                    "பார்க்கலாம்."

                )

            else:

                reply = (

                    "You can check examination "
                    "results in the Student Result "
                    "section."

                )


        # =====================================================
        # GAMES
        # =====================================================

        elif (

            "game" in msg

            or

            "games" in msg

            or

            "sports" in msg

            or

            "விளையாட்டு" in user_message

        ):

            game_results = STAFF_DATA.get(

                "game_results",

                []

            )


            if isinstance(
                game_results,
                list
            ):

                game_count = len(
                    game_results
                )

            else:

                game_count = 0


            if language == "ta":

                reply = (

                    f"கல்லூரியில் {game_count} "

                    "விளையாட்டு பதிவுகள் உள்ளன."

                )

            else:

                reply = (

                    f"There are {game_count} "

                    "game records available."

                )


        # =====================================================
        # EVENTS
        # =====================================================

        elif (

            "event" in msg

            or

            "events" in msg

            or

            "நிகழ்ச்சி" in user_message

            or

            "நிகழ்வுகள்" in user_message

        ):

            event_data = STAFF_DATA.get(

                "events",

                []

            )


            if isinstance(
                event_data,
                list
            ):

                event_count = len(
                    event_data
                )

            else:

                event_count = 0


            if language == "ta":

                reply = (

                    f"கல்லூரியில் {event_count} "

                    "நிகழ்வு பதிவுகள் உள்ளன."

                )

            else:

                reply = (

                    f"There are {event_count} "

                    "college events available."

                )


        # =====================================================
        # ANNOUNCEMENT
        # =====================================================

        elif (

            "announcement" in msg

            or

            "announcements" in msg

            or

            "அறிவிப்பு" in user_message

        ):

            announcement = STAFF_DATA.get(

                "announcement",

                "No announcements available."

            )


            if language == "ta":

                reply = (

                    "அறிவிப்பு:\n"

                    + str(announcement)

                )

            else:

                reply = (

                    "Announcement:\n"

                    + str(announcement)

                )


        # =====================================================
        # NAAN MUDHALVAN
        # =====================================================

        elif (

            "naan mudhalvan" in msg

            or

            "நான் முதல்வன்" in user_message

        ):

            nm = STAFF_DATA.get(

                "naan_mudhalvan",

                "Naan Mudhalvan programme information is available."

            )


            if language == "ta":

                reply = (

                    "நான் முதல்வன்:\n"

                    + str(nm)

                )

            else:

                reply = str(nm)


        # =====================================================
        # FALLBACK
        # =====================================================

        else:

            if language == "ta":

                reply = (

                    "Admission, Fees, Library, "

                    "Placement, Hostel, Courses, "

                    "Results, Contact, Timing, "

                    "Games அல்லது Events பற்றி "
                    "கேளுங்கள்."

                )

            else:

                reply = (

                    "Ask about Admission, Fees, "

                    "Library, Placement, Hostel, "

                    "Courses, Results, Contact, "

                    "Timing, Games or Events."

                )


        # =====================================================
        # SEND RESPONSE
        # =====================================================

        return jsonify({

            "reply":
                reply

        })


    except Exception as e:

        print("======================================")

        print(
            "CHAT ERROR:",
            repr(e)
        )

        print("======================================")


        return jsonify({

            "reply": (
                "Sorry da! Server connection problem. "
                "Please try again."
            )

        }), 500


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# STAFF LOGOUT
# =========================================================

@app.route("/staff/logout")
def staff_logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# PRINCIPAL LOGOUT
# =========================================================

@app.route("/principal/logout")
def principal_logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "running",

        "mongodb":
            (
                "connected"

                if collection is not None

                else

                "not connected"
            ),

        "logged_in":
            is_logged_in(),

        "role":
            session.get(
                "role"
            ),

        "language":
            session.get(
                "language",
                "en"
            )

    })


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return (

        "<h2>404 - Page Not Found</h2>"

        "<a href='/'>Go to Home</a>"

    ), 404


# =========================================================
# 500 ERROR
# =========================================================

@app.errorhandler(500)
def internal_error(error):

    print(
        "INTERNAL SERVER ERROR:",
        error
    )


    return (

        "<h2>500 - Internal Server Error</h2>"

        "<a href='/'>Go to Home</a>"

    ), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("======================================")

    print(
        " GCT SMARTDESK"
    )

    print("======================================")

    print(
        " /        = HOME PAGE"
    )

    print(
        " /home    = HOME PAGE"
    )

    print(
        " /login   = LOGIN PAGE"
    )

    print(
        " /chatbot = LIVE CHAT"
    )

    print(
        " /chat    = CHAT API"
    )

    print(
        " Student  = DOB Verification"
    )

    print(
        " Staff    = staff123"
    )

    print(
        " Principal= gct123"
    )

    print("======================================")


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )