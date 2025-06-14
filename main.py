from flask import Flask
import taa_monthly

app = Flask(__name__)

@app.route("/")
def home():
    return "API activa"

@app.route("/ejecutar")
def ejecutar():
    tu_script.main()
    return "Script ejecutado correctamente"
