from flask import Flask, render_template, request
import sqlite3
import uuid
import smtplib
from email.mime.text import MIMEText
import os


app = Flask(__name__)

# ==============================
# CONFIGURAÇÕES
# ==============================

SEU_EMAIL = os.environ.get("EMAIL_USER")
SENHA_EMAIL = os.environ.get("EMAIL_PASS")


# ==============================
# LISTA DE CONVIDADOS
# ==============================

CONVIDADOS_INICIAIS = [
    "Artur Mendes",
    "Julia Souza",
    "Carlos Silva",
]

# ==============================
# BANCO DE DADOS
# ==============================

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS convidados (
            id TEXT PRIMARY KEY,
            nome TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()


def cadastrar_convidados_iniciais():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    for nome in CONVIDADOS_INICIAIS:
        try:
            cursor.execute(
                "INSERT INTO convidados (id, nome) VALUES (?, ?)",
                (str(uuid.uuid4()), nome)
            )
        except:
            pass  # ignora se já existir

    conn.commit()
    conn.close()

# ==============================
# EMAIL
# ==============================

def enviar_email(nome):
    corpo = f"""
Nova confirmação!

Convidado confirmado: {nome}
"""

    msg = MIMEText(corpo)
    msg["Subject"] = "Nova confirmação - Festa 18"
    msg["From"] = SEU_EMAIL
    msg["To"] = SEU_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SEU_EMAIL, SENHA_EMAIL)
        server.send_message(msg)

# ==============================
# ROTA PRINCIPAL
# ==============================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome_digitado = request.form["nome"].strip()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Busca ignorando maiúsculas/minúsculas
        cursor.execute(
            "SELECT nome FROM convidados WHERE LOWER(nome) LIKE LOWER(?)",
            (nome_digitado + "%",)
        )

        resultados = cursor.fetchall()
        conn.close()

        if len(resultados) == 1:
            nome_oficial = resultados[0][0]
            enviar_email(nome_oficial)
            return render_template(
                "index.html",
                sucesso="Presença confirmada com sucesso!"
            )

        elif len(resultados) > 1:
            return render_template(
                "index.html",
                erro="Digite nome e sobrenome para confirmar."
            )

        else:
            return render_template(
                "index.html",
                erro="Seu nome não está na lista de convidados."
            )

    return render_template("index.html")

# ==============================
# START
# ==============================

# ==============================
# INICIALIZAÇÃO (IMPORTANTE PARA RENDER)
# ==============================

init_db()
cadastrar_convidados_iniciais()

# ==============================
# START LOCAL
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

