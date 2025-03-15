from flask import Flask, render_template, request, send_file
import pytesseract
from PIL import Image
import pandas as pd
import re
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_ticket():
    if 'image' not in request.files:
        return "No se cargó ninguna imagen", 400
    
    file = request.files['image']
    img = Image.open(file)
    
    # Extraer texto con OCR
    text = pytesseract.image_to_string(img, lang='spa')
    
    # Procesar el texto para extraer productos y precios
    # (Se necesita adaptar segun formato de tickets)
    lines = text.split('\n')
    products = []
    prices = []
    
    for line in lines:
        # Buscar patrones de precio (ejemplo: $123.45)
        price_match = re.search(r'\$?\s*(\d+[.,]\d+)', line)
        if price_match:
            price = price_match.group(1)
            # El producto es el texto antes del precio
            product = line[:price_match.start()].strip()
            if product:  # Si hay un nombre de producto
                products.append(product)
                prices.append(price)
    
    # Crear DataFrame
    df = pd.DataFrame({'Producto': products, 'Precio': prices})
    
    # Exportar a Excel
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    return send_file(excel_file, 
                     download_name='ticket_data.xlsx',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
