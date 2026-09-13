import os

from flask import Flask, render_template, request, redirect, jsonify, session
from pymongo import MongoClient
from dotenv import load_dotenv


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "gct_final_both_pass"

os.makedirs("staff_files", exist_ok=True)


# ============================================================
# LOAD .ENV
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# ============================================================
# MONGODB ATLAS CONNECTION
# ============================================================

MONGO_URI = os.getenv("MONGO_URI")

client = None
db = None
collection = None

try:

    if not MONGO_URI:
        raise ValueError("MONGO_URI not found in .env file")

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    client.admin.command("ping")

    db = client["AICollegeHelpdesk"]
    collection = db["college_data"]

    print("======================================")
    print("MongoDB Atlas connected successfully!")
    print("Database: AICollegeHelpdesk")
    print("Collection: college_data")
    print("======================================")

except Exception as e:

    print("======================================")
    print("MongoDB connection error:", e)
    print("======================================")

    client = None
    db = None
    collection = None


# ============================================================
# COLLEGE STATIC DATA
# ============================================================

DATA = {

    "college name":
        "Government College of Technology, Coimbatore",

    "principal":
        "Dr. K. Manonmani, M.E., Ph.D",

    "contact":
        "0422-2432221",

    "location":
        "Thadagam Road, Coimbatore",

    "about":
        "GCT - Govt College since 1945.",

    "ug_courses":
        "B.E CSE, ECE, Mechanical, Civil, EEE",

    "pg_courses":
        "M.E CSE, MBA, MCA",

    "timing":
        "8:30 AM to 4:30 PM",

    "facilities":
        "Library, Hostel, Labs",

    "hostel":
        "Hostel available"
}


# ============================================================
# DEFAULT STAFF DATA
# ============================================================

DEFAULT_STAFF_DATA = {

    "_id": "main_data",

    "admission":
        "UG Admission 2026 open",

    "naan_mudhalvan":
        "Naan Mudhalvan Scheme - Skill Training",

    "exam_fees":
        "UG Rs.1500/sem, PG Rs.2000/sem",

    "announcement":
        "Welcome!",

    "students": {},

    "results": {},

    "staff_list": {},

    "hod_list": {},

    "library_books": {

        "CSE001": {
            "title": "Python Programming",
            "author": "Guido",
            "dept": "CSE",
            "total": 10,
            "available": 10
        },

        "ECE002": {
            "title": "Digital Electronics",
            "author": "Morris Mano",
            "dept": "ECE",
            "total": 5,
            "available": 5
        },

        "MECH01": {
            "title": "Thermodynamics",
            "author": "Cengel",
            "dept": "Mechanical",
            "total": 8,
            "available": 8
        }
    },

    "game_results": [],

    "attendance": {},

    "fees_paid": {},

    "complaints": [],

    "placements": [],

    "events": []
}


# ============================================================
# LOAD DATA FROM MONGODB
# ============================================================

def load_data():

    if collection is None:

        print("MongoDB unavailable. Using default data.")

        return DEFAULT_STAFF_DATA.copy()

    try:

        data = collection.find_one({
            "_id": "main_data"
        })

        if data:

            print("College data loaded from MongoDB.")

            return data

        else:

            collection.insert_one(
                DEFAULT_STAFF_DATA.copy()
            )

            print("Default college data saved to MongoDB.")

            return DEFAULT_STAFF_DATA.copy()

    except Exception as e:

        print("MongoDB load error:", e)

        return DEFAULT_STAFF_DATA.copy()


# ============================================================
# SAVE DATA TO MONGODB
# ============================================================

def save_to_db(data):

    if collection is None:

        print(
            "MongoDB unavailable. "
            "Document was not saved."
        )

        return False

    try:

        collection.update_one(

            {"_id": "main_data"},

            {"$set": data},

            upsert=True

        )

        print("Data saved to MongoDB successfully.")

        return True

    except Exception as e:

        print("MongoDB save error:", e)

        return False


# ============================================================
# LOAD INITIAL STAFF DATA
# ============================================================

STAFF_DATA = load_data()


# ============================================================
# LOGIN PASSWORDS
# ============================================================

STAFF_PASS = "staff123"

PRINCIPAL_PASS = "gct123"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(

        "home.html",

        username=session.get(
            "user",
            "Guest"
        ),

        data=DATA,

        staff_data=STAFF_DATA
    )


# ============================================================
# STUDENT
# ============================================================

@app.route("/student")
def student():

    return render_template(

        "student.html",

        data=DATA,

        staff_data=STAFF_DATA
    )


# ============================================================
# STAFF LOGIN
# ============================================================

@app.route(
    "/staff",
    methods=["GET", "POST"]
)
def staff():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        ).strip()

        if password == STAFF_PASS:

            session["is_staff"] = True

            return redirect("/staff")

        else:

            return (
                "<h3>Wrong Password</h3>"
                "<a href='/staff'>Try Again</a>"
            )

    if (
        not session.get("is_staff")
        and not session.get("is_principal")
    ):

        return """
        <body style="
        text-align:center;
        padding:50px;
        background:#e8f5e9">

        <h2>👨‍🏫 Staff Login</h2>

        <form method="POST">

        <input
        type="password"
        name="password"
        placeholder="Password"
        style="padding:12px;width:260px"
        required>

        <br><br>

        <button
        style="
        padding:12px 30px;
        background:#4CAF50;
        color:white;
        border:none;
        border-radius:8px">

        Login

        </button>

        </form>

        <p>Password:
        <b>staff123</b></p>

        <a href="/">Home</a>

        </body>
        """

    return render_template(

        "staff.html",

        data=DATA,

        staff_data=STAFF_DATA
    )


# ============================================================
# PRINCIPAL LOGIN
# ============================================================

@app.route(
    "/principal",
    methods=["GET", "POST"]
)
def principal():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        ).strip()

        if password == PRINCIPAL_PASS:

            session["is_principal"] = True
            session["is_staff"] = True

            return redirect("/principal")

        else:

            return (
                "<h3>Wrong Password</h3>"
                "<a href='/principal'>Try Again</a>"
            )

    if not session.get("is_principal"):

        return """
        <body style="
        text-align:center;
        padding:50px;
        background:#ffebee">

        <h2>🔐 Principal Login</h2>

        <form method="POST">

        <input
        type="password"
        name="password"
        placeholder="Password"
        style="padding:12px;width:260px"
        required>

        <br><br>

        <button
        style="
        padding:12px 30px;
        background:#d32f2f;
        color:white;
        border:none;
        border-radius:8px">

        Login

        </button>

        </form>

        <p>Password:
        <b>gct123</b></p>

        <a href="/">Home</a>

        </body>
        """

    return render_template(

        "principal.html",

        data=DATA,

        staff_data=STAFF_DATA
    )


# ============================================================
# LIBRARY
# ============================================================

@app.route("/library")
def library():

    return render_template(

        "library.html",

        data=DATA,

        staff_data=STAFF_DATA
    )


# ============================================================
# GAMES
# ============================================================

@app.route("/games")
def games():

    return render_template(

        "games.html",

        data=DATA,

        staff_data=STAFF_DATA
    )


# ============================================================
# SAVE GAME RESULT
# ============================================================

@app.route(
    "/games/save",
    methods=["POST"]
)
def save_game_result():

    if (
        not session.get("is_staff")
        and not session.get("is_principal")
    ):

        return "Staff Only"

    STAFF_DATA["game_results"].append({

        "game":
            request.form.get(
                "game",
                ""
            ),

        "winner":
            request.form.get(
                "winner",
                ""
            ),

        "dept":
            request.form.get(
                "dept",
                "CSE"
            ),

        "prize":
            request.form.get(
                "prize",
                "1st Prize"
            )
    })

    save_to_db(STAFF_DATA)

    if session.get("is_principal"):

        return redirect("/principal")

    return redirect("/staff")


# ============================================================
# SAVE ATTENDANCE
# ============================================================

@app.route(
    "/attendance/save",
    methods=["POST"]
)
def save_attendance():

    if (
        not session.get("is_staff")
        and not session.get("is_principal")
    ):

        return "Staff Only"

    roll = request.form.get(
        "roll",
        ""
    ).upper().strip()

    STAFF_DATA["attendance"][roll] = request.form.get(
        "percent",
        "0"
    )

    save_to_db(STAFF_DATA)

    if session.get("is_principal"):

        return redirect("/principal")

    return redirect("/staff")


# ============================================================
# SAVE FEES
# ============================================================

@app.route(
    "/fees/save",
    methods=["POST"]
)
def save_fees():

    if (
        not session.get("is_staff")
        and not session.get("is_principal")
    ):

        return "Staff Only"

    roll = request.form.get(
        "roll",
        ""
    ).upper().strip()

    STAFF_DATA["fees_paid"][roll] = {

        "amount":
            request.form.get(
                "amount",
                ""
            ),

        "status":
            request.form.get(
                "status",
                "Paid"
            )
    }

    save_to_db(STAFF_DATA)

    if session.get("is_principal"):

        return redirect("/principal")

    return redirect("/staff")


# ============================================================
# COMPLAINT
# ============================================================

@app.route(
    "/complaint",
    methods=["GET", "POST"]
)
def complaint():

    if request.method == "POST":

        STAFF_DATA["complaints"].append({

            "roll":
                request.form.get(
                    "roll",
                    "Anonymous"
                ),

            "msg":
                request.form.get(
                    "msg",
                    ""
                )
        })

        save_to_db(STAFF_DATA)

        return (
            "<h3>Complaint Sent! ✅ "
            "<a href='/'>Home</a></h3>"
        )

    return render_template(

        "complaint.html",

        staff_data=STAFF_DATA
    )


# ============================================================
# PLACEMENT
# ============================================================

@app.route(
    "/placement",
    methods=["GET", "POST"]
)
def placement():

    if request.method == "POST":

        if (
            not session.get("is_staff")
            and not session.get("is_principal")
        ):

            return "Staff Only"

        STAFF_DATA["placements"].append({

            "company":
                request.form.get(
                    "company",
                    ""
                ),

            "package":
                request.form.get(
                    "package",
                    ""
                ),

            "students":
                request.form.get(
                    "students",
                    ""
                )
        })

        save_to_db(STAFF_DATA)

        return redirect("/placement")

    return render_template(

        "placement.html",

        staff_data=STAFF_DATA,

        data=DATA
    )


# ============================================================
# EVENTS
# ============================================================

@app.route(
    "/events",
    methods=["GET", "POST"]
)
def events():

    if request.method == "POST":

        if not session.get("is_principal"):

            return "Principal Only"

        STAFF_DATA["events"].append({

            "title":
                request.form.get(
                    "title",
                    ""
                ),

            "date":
                request.form.get(
                    "date",
                    ""
                ),

            "dept":
                request.form.get(
                    "dept",
                    ""
                )
        })

        save_to_db(STAFF_DATA)

        return redirect("/principal")

    return render_template(

        "events.html",

        staff_data=STAFF_DATA,

        data=DATA
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/principal/logout")
def principal_logout():

    session.clear()

    return redirect("/")


@app.route("/staff/logout")
def staff_logout():

    session.clear()

    return redirect("/")


# ============================================================
# STAFF UPLOAD / UPDATE DATA
# ============================================================

@app.route(
    "/staff/upload",
    methods=["POST"]
)
def staff_upload():

    typ = request.form.get("type")

    if typ in [
        "admission",
        "naan_mudhalvan",
        "exam_fees",
        "exam_result"
    ]:

        if (
            not session.get("is_staff")
            and not session.get("is_principal")
        ):

            return "Access Denied"

    else:

        if not session.get("is_principal"):

            return (
                "<h3>Principal ku mattum! "
                "<a href='/principal'>Login</a></h3>"
            )

    # Admission
    if typ == "admission":

        STAFF_DATA["admission"] = request.form.get(
            "text",
            ""
        )

    # Naan Mudhalvan
    elif typ == "naan_mudhalvan":

        STAFF_DATA["naan_mudhalvan"] = request.form.get(
            "text",
            ""
        )

    # Exam Fees
    elif typ == "exam_fees":

        STAFF_DATA["exam_fees"] = request.form.get(
            "text",
            ""
        )

    # Exam Result
    elif typ == "exam_result":

        roll = request.form.get(
            "roll",
            ""
        ).strip().upper()

        STAFF_DATA["results"][roll] = {

            "cgpa":
                request.form.get(
                    "cgpa",
                    ""
                ),

            "result":
                request.form.get(
                    "result",
                    ""
                ),

            "dept":
                request.form.get(
                    "dept",
                    "CSE"
                )
        }

    # Staff Details
    elif typ == "staff_details":

        sid = request.form.get(
            "staff_id",
            ""
        ).strip().upper()

        STAFF_DATA["staff_list"][sid] = {

            "name":
                request.form.get(
                    "name",
                    ""
                ),

            "dept":
                request.form.get(
                    "dept",
                    "CSE"
                ),

            "designation":
                request.form.get(
                    "designation",
                    ""
                )
        }

    # HOD Details
    elif typ == "hod_details":

        dept = request.form.get(
            "dept",
            "CSE"
        )

        STAFF_DATA["hod_list"][dept] = {

            "name":
                request.form.get(
                    "name",
                    ""
                ),

            "exp":
                request.form.get(
                    "exp",
                    ""
                ),

            "contact":
                request.form.get(
                    "contact",
                    ""
                )
        }

    # Student Details
    elif typ == "student_details":

        roll = request.form.get(
            "roll",
            ""
        ).strip().upper()

        STAFF_DATA["students"][roll] = {

            "name":
                request.form.get(
                    "name",
                    ""
                ),

            "dept":
                request.form.get(
                    "dept",
                    "CSE"
                ),

            "year":
                request.form.get(
                    "year",
                    ""
                )
        }

    save_to_db(STAFF_DATA)

    if session.get("is_principal"):

        return redirect("/principal")

    return redirect("/staff")


# ============================================================
# GET STUDENT RESULT
# ============================================================

@app.route(
    "/get_result",
    methods=["POST"]
)
def get_result():

    roll = request.form.get(
        "roll",
        ""
    ).strip().upper()

    res = STAFF_DATA["results"].get(roll)

    if res:

        return jsonify({

            "found": True,

            "roll": roll,

            "data": res,

            "student":
                STAFF_DATA["students"].get(
                    roll
                )
        })

    return jsonify({

        "found": False
    })


# ============================================================
# CHATBOT PAGE
# ============================================================

@app.route("/chatbot")
def chatbot():

    return render_template(
        "index.html",
        username="admin"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login")
def login():

    return redirect("/")


# ============================================================
# LANGUAGE
# ============================================================

@app.route(
    "/language",
    methods=["GET", "POST"]
)
def language():

    return render_template(
        "language.html"
    )


# ============================================================
# CHATBOT API
# ============================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json(
        silent=True
    ) or {}

    user_msg = data.get(
        "message",
        ""
    ).lower().strip()

    # ========================================================
    # DEFAULT REPLY
    # ========================================================

    reply = (
        "Theriyala da, vera maathiri kelu - "
        "Admission, Fees, Library, Games, "
        "Placement, Contact nu kelu da!"
    )

    # ========================================================
    # PRINCIPAL
    # ========================================================

    if (
        "principal" in user_msg
        or "முதல்வர்" in user_msg
        or "பிரின்சிபல்" in user_msg
    ):

        reply = (
            f"Principal: "
            f"{DATA['principal']} da"
        )

    # ========================================================
    # ADMISSION
    # ========================================================

    elif (
        "admission" in user_msg
        or "admissions" in user_msg
        or "admission status" in user_msg
        or "admission எப்போது" in user_msg
        or "சேர்க்கை" in user_msg
        or "சேர்க்கை எப்போது" in user_msg
        or "அட்மிஷன்" in user_msg
    ):

        reply = (
            f"{STAFF_DATA['admission']} "
            f"- Contact {DATA['contact']}"
        )

    # ========================================================
    # FEES
    # ========================================================

    elif (
        "fees" in user_msg
        or "fee" in user_msg
        or "exam fees" in user_msg
        or "exam fee" in user_msg
        or "fee details" in user_msg
        or "exam fee details" in user_msg
        or "தேர்வு கட்டணம்" in user_msg
        or "கட்டணம்" in user_msg
        or "தேர்வு கட்டணம் எவ்வளவு" in user_msg
        or "கட்டணம் எவ்வளவு" in user_msg
        or "ஃபீஸ்" in user_msg
        or "பணம்" in user_msg
    ):

        reply = (
            f"Fees Details: "
            f"{STAFF_DATA['exam_fees']} da"
        )

    # ========================================================
    # LIBRARY
    # ========================================================

    elif (
        "library" in user_msg
        or "book" in user_msg
        or "books" in user_msg
        or "நூலகம்" in user_msg
        or "புத்தகம்" in user_msg
    ):

        reply = (
            f"Library la "
            f"{len(STAFF_DATA['library_books'])} "
            f"books irukku! "
            f"/library poi full list paaru da!"
        )

    # ========================================================
    # GAMES / SPORTS
    # ========================================================

    elif (
        "game" in user_msg
        or "games" in user_msg
        or "sports" in user_msg
        or "விளையாட்டு" in user_msg
        or "விளையாட்டுகள்" in user_msg
    ):

        reply = (
            f"Sports la "
            f"{len(STAFF_DATA['game_results'])} "
            f"results saved! "
            f"Winner lam /games la paaru da!"
        )

    # ========================================================
    # PLACEMENT
    # ========================================================

    elif (
        "placement" in user_msg
        or "placements" in user_msg
        or "வேலைவாய்ப்பு" in user_msg
        or "பிளேஸ்மென்ட்" in user_msg
    ):

        reply = (
            f"Placement la "
            f"{len(STAFF_DATA['placements'])} "
            f"company vanthirukku - "
            f"/placement la paaru da!"
        )

    # ========================================================
    # ATTENDANCE
    # ========================================================

    elif (
        "attendance" in user_msg
        or "present" in user_msg
        or "வருகை" in user_msg
        or "வருகை பதிவு" in user_msg
    ):

        reply = (
            "Attendance staff / principal "
            "than save pannuvanga da"
        )

    # ========================================================
    # CONTACT
    # ========================================================

    elif (
        "contact" in user_msg
        or "phone" in user_msg
        or "mobile" in user_msg
        or "number" in user_msg
        or "தொடர்பு" in user_msg
        or "தொலைபேசி" in user_msg
        or "போன்" in user_msg
        or "எண்" in user_msg
    ):

        reply = (
            f"Contact: {DATA['contact']} - "
            f"{DATA['location']} da"
        )

    # ========================================================
    # COURSE / DEPARTMENT
    # ========================================================

    elif (
        "course" in user_msg
        or "courses" in user_msg
        or "dept" in user_msg
        or "department" in user_msg
        or "departments" in user_msg
        or "பாடநெறி" in user_msg
        or "படிப்பு" in user_msg
        or "துறை" in user_msg
    ):

        reply = (
            f"UG: {DATA['ug_courses']} | "
            f"PG: {DATA['pg_courses']}"
        )

    # ========================================================
    # HOSTEL
    # ========================================================

    elif (
        "hostel" in user_msg
        or "ஹாஸ்டல்" in user_msg
        or "விடுதி" in user_msg
    ):

        reply = DATA["hostel"]

    # ========================================================
    # NAAN MUDHALVAN
    # ========================================================

    elif (
        "naan mudhalvan" in user_msg
        or "naan mudhalvan scheme" in user_msg
        or "நான் முதல்வன்" in user_msg
        or "நான் முதல்வன் திட்டம்" in user_msg
    ):

        reply = (
            f"{STAFF_DATA['naan_mudhalvan']} da"
        )

    # ========================================================
    # TIMING
    # IMPORTANT: TIMING MUST COME BEFORE ABOUT COLLEGE
    # ========================================================

    elif (
        "timing" in user_msg
        or "time" in user_msg
        or "college timing" in user_msg
        or "நேரம்" in user_msg
        or "கல்லூரி நேரம்" in user_msg
    ):

        reply = (
            f"College timing: "
            f"{DATA['timing']} da"
        )

    # ========================================================
    # FACILITIES
    # ========================================================

    elif (
        "facility" in user_msg
        or "facilities" in user_msg
        or "வசதி" in user_msg
        or "வசதிகள்" in user_msg
    ):

        reply = (
            f"College facilities: "
            f"{DATA['facilities']} da"
        )

    # ========================================================
    # ABOUT COLLEGE
    # IMPORTANT: BROAD COLLEGE KEYWORD IS LAST
    # ========================================================

    elif (
        "about college" in user_msg
        or "college பற்றி" in user_msg
        or "கல்லூரி பற்றி" in user_msg
        or "கல்லூரியை பற்றி" in user_msg
        or "கல்லூரி குறித்த" in user_msg
    ):

        reply = (
            f"{DATA['college name']} - "
            f"{DATA['about']} da"
        )

    # ========================================================
    # GREETING
    # ========================================================

    elif (
        user_msg in [
            "hi",
            "hello",
            "hey",
            "vanakkam"
        ]
        or "வணக்கம்" in user_msg
    ):

        reply = (
            "Vanakkam da! 🙏 "
            "Naan GCT Live Chatbot da! "
            "Admission, Fees, Library, Games, "
            "Placement ethu venalum kelu!"
        )

    # ========================================================
    # RETURN JSON
    # ========================================================

    return jsonify({
        "reply": reply
    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )