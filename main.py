from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "API de simulação web rodando na nuvem!"})

@app.route('/executar', methods=['POST'])
def executar():
    dados = request.json

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # roda sem interface
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(dados.get("url", "https://instagram.com"))

    titulo = driver.title
    driver.quit()

    return jsonify({"mensagem": "Página carregada com sucesso!", "titulo": titulo})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
