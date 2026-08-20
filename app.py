"""Aplicação principal do sistema de biblioteca escolar."""
import os
from flask import Flask, send_from_directory
from database import init_db
from routes import api
from auth import auth

app = Flask(__name__, static_folder="html", static_url_path="")
app.config["JSON_SORT_KEYS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "toschibook-dev-secret-2026")

init_db()
app.register_blueprint(api)
app.register_blueprint(auth)


@app.after_request
def adicionar_cors(resposta):
    """Permite que o front aberto pelo Live Server acesse a API Flask."""
    resposta.headers["Access-Control-Allow-Origin"] = "*"
    resposta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resposta.headers["Access-Control-Allow-Credentials"] = "true"
    return resposta


@app.get("/")
def index():
    return send_from_directory("html", "index.html")


@app.get("/html/<path:nome_arquivo>")
def servir_html(nome_arquivo):
    """Serve as páginas HTML também pelo caminho /html/."""
    return send_from_directory("html", nome_arquivo)


@app.get("/css/<path:nome_arquivo>")
def servir_css(nome_arquivo):
    """Serve os arquivos de estilo da pasta css/."""
    return send_from_directory("css", nome_arquivo)


@app.get("/javascript/<path:nome_arquivo>")
def servir_javascript(nome_arquivo):
    """Serve os arquivos JavaScript da pasta javascript/."""
    return send_from_directory("javascript", nome_arquivo)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
