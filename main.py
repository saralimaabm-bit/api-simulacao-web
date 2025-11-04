from flask import Flask, jsonify, request
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "API rodando com Selenium na nuvem!"})

@app.route('/executar', methods=['POST'])
def executar():
    dados = request.json

    # Garante que o ChromeDriver esteja instalado
    chromedriver_autoinstaller.install()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(dados.get("url", "https://example.com"))
    titulo = driver.title
    driver.quit()

    return jsonify({"mensagem": "Página carregada!", "titulo": titulo})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
