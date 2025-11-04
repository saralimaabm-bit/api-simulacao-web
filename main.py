from flask import Flask, jsonify, request
import undetected_chromedriver as uc

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
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        driver = uc.Chrome(options=options)
        driver.get(url)
        titulo = driver.title
        driver.quit()

        return jsonify({"mensagem": "Página carregada!", "titulo": titulo})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
