from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import csv
from flask_socketio import SocketIO, emit
import base64
import io
from PIL import Image
import os

app = Flask(__name__)
socketio = SocketIO(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["SECRET_KEY"] = "secret_key_here"

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
rto_state_codes = [
    "AP",  # Andhra Pradesh
    "AR",  # Arunachal Pradesh
    "AS",  # Assam
    "BR",  # Bihar
    "CG",  # Chhattisgarh
    "GA",  # Goa
    "GJ",  # Gujarat
    "HR",  # Haryana
    "HP",  # Himachal Pradesh
    "JH",  # Jharkhand
    "KA",  # Karnataka
    "KL",  # Kerala
    "MP",  # Madhya Pradesh
    "MH",  # Maharashtra
    "MN",  # Manipur
    "ML",  # Meghalaya
    "MZ",  # Mizoram
    "NL",  # Nagaland
    "OD",  # Odisha
    "PB",  # Punjab
    "RJ",  # Rajasthan
    "SK",  # Sikkim
    "TN",  # Tamil Nadu
    "TS",  # Telangana
    "TR",  # Tripura
    "UP",  # Uttar Pradesh
    "UK",  # Uttarakhand
    "WB",  # West Bengal
    "AN",  # Andaman and Nicobar Islands
    "CH",  # Chandigarh
    "DD",  # Dadra and Nagar Haveli and Daman and Diu
    "LD",  # Lakshadweep
    "DL",  # Delhi
    "PY",  # Puducherry
    "LA",  # Ladakh
    "JK"   # Jammu and Kashmir
]

# Define a simple User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def check_password(self, password):
        return self.password == password

# Create some sample users
users = [User(1, "admin", "admin"), User(2, "user2", "password2")]

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for user in users:
            if user.username == username and user.check_password(password):
                login_user(user)
                return redirect(url_for("data"))
    return render_template("index.html")

@app.route("/protected")
@login_required
def protected():
    return f"Hello, {current_user.username}!"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/data")
@login_required
def data():
    data = []
    with open("Data/data.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # print(row[0][0:2])
            if row[0][0:2].upper() in rto_state_codes:
                # Assuming the image files are stored in a 'images' directory
                image_path = f"{row[0]}_original.jpg"
                data.append([row[0], image_path,row[2],row[3]])
            elif row[0][0:2].isdigit():
                image_path = f"{row[0]}_original.jpg"
                data.append([row[0], image_path,row[2],row[3]])
    data.reverse()
    return render_template("data.html", data=data)


@socketio.on('image')
def handle_image(data):
    # Decode the base64 image data
    image_data = base64.b64decode(data['image'])
    fileName = data['fileName']
    numberPlate = data['numberPlate']
    time = data['time']
    colorCode = data['colorCode']
    image = Image.open(io.BytesIO(image_data))
    with open('Data/data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([numberPlate, fileName,  time, colorCode])
    # Process the image (e.g., save it, display it, etc.)
    image.save(f'./uploads/fileName.png')
    print("Image received and saved as 'received_image.png'")

    # Optionally, emit a response back to the client
    emit('image_response', {'status': 'Number plate scan successfully'})

if __name__ == "__main__":
    socketio.run(app, debug=True)