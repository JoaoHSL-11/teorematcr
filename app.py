from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def check_primo_par_a_par(modulos):
    return all(gcd(a, b) == 1 for a, b in combinations(modulos, 2))

def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def normalize_congruence(a, b, m):
    inv = mod_inverse(a, m)
    if inv is None:
        return None
    return (b * inv) % m

def chinese_remainder_theorem(congruences):
    modulos = []
    for c in congruences:
        modulos.append(c['m'])

    if not check_primo_par_a_par(modulos):
        return None

    M = 1
    for x in modulos:
        M *= x

    x = 0
    for c in congruences:
        Mi = M // c['m']
        inv = mod_inverse(Mi, c['m'])
        if inv is None:
            return None
        x += c['b'] * Mi * inv

    return {'x': x % M, 'mod': M}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resolver', methods=['POST'])
def resolver():
    data = request.get_json()
    raw_congruences = data.get('congruences', [])

    processed = []
    for c in raw_congruences:
        a, b, m = c.get('a'), c.get('b'), c.get('m')
        if any(x is None for x in [a, b, m]):
            return jsonify({'error': 'Dados incompletos'}), 400
        try:
            b_normalized = normalize_congruence(a, b, m)
            processed.append({'b': b_normalized, 'm': m})
        except Exception:
            return jsonify({'error': f'Não foi possível normalizar: {a}x ≡ {b} (mod {m})'}), 400

    result = chinese_remainder_theorem(processed)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Sistema inválido.'}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
