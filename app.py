from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from math import gcd
from itertools import combinations
import os

app = Flask(__name__)
CORS(app)  # Permitir requisições externas (útil se o front estiver separado)

# Verifica se os módulos são primos entre si
def check_primo_par_a_par(modulos):
    return all(gcd(a, b) == 1 for a, b in combinations(modulos, 2))

# Calcula o inverso modular usando o algoritmo extendido de Euclides
def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

# Normaliza a congruência do tipo ax ≡ b (mod m) para x ≡ b' (mod m)
def normalize_congruence(a, b, m):
    inv = mod_inverse(a, m)
    if inv is None:
        return None
    return (b * inv) % m

# Resolve sistema de congruências usando o Teorema Chinês dos Restos
def chinese_remainder_theorem(congruences):
    modulos = [c['m'] for c in congruences]

    if not check_primo_par_a_par(modulos):
        return None

    M = 1
    for m in modulos:
        M *= m

    x = 0
    for c in congruences:
        Mi = M // c['m']
        inv = mod_inverse(Mi, c['m'])
        if inv is None:
            return None
        x += c['b'] * Mi * inv

    return {'x': x % M, 'mod': M}

# Rota principal que renderiza o HTML
@app.route('/')
def home():
    return render_template('index.html')  # Certifique-se de que index.html está em /templates

# Rota para resolver sistema de congruências
@app.route('/resolver', methods=['POST'])
def resolver():
    data = request.get_json()
    raw_congruences = data.get('congruences', [])

    processed = []
    for c in raw_congruences:
        a = c.get('a')
        b = c.get('b')
        m = c.get('m')

        if None in [a, b, m]:
            return jsonify({'error': 'Dados incompletos'}), 400

        try:
            b_normalized = normalize_congruence(a, b, m)
            if b_normalized is None:
                raise Exception("Sem inverso")
            processed.append({'b': b_normalized, 'm': m})
        except Exception:
            return jsonify({'error': f'Não foi possível normalizar: {a}x ≡ {b} (mod {m})'}), 400

    result = chinese_remainder_theorem(processed)
    if result:
        return jsonify(result)

    return jsonify({'error': 'Sistema inválido. Os módulos devem ser primos entre si.'}), 400

# Início da aplicação
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
