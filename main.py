from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "API rodando com Selenium na Render!"})

@app.route('/executar', methods=['POST'])
def executar():
    try:
        dados = request.json
        url = dados.get("url", "https://google.com")

        # Inicializa o Chrome headless via undetected-chromedriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Aponta para o Chrome instalado pelo apt
        chrome_options.binary_location = "/usr/bin/google-chrome-stable"

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        titulo = driver.title
        driver.quit()

        return jsonify({"mensagem": "Página carregada!", "titulo": titulo})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
