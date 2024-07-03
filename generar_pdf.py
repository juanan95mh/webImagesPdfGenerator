import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import os

# URL de la página web
url = "https://www.arcoguia.com/croquis-de-escalada-en-roca-de-las-hoces-de-vegacervera-leon/"

# Realizar la solicitud HTTP y obtener el contenido de la página
response = requests.get(url)
response.raise_for_status()

# Analizar el contenido HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Encontrar todas las imágenes en la página dentro de los elementos <a>
image_urls = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if 'wp-content/uploads' in href and (href.endswith('.jpg') or href.endswith('.png')):
        if not href.startswith('http'):
            href = os.path.join('http://www.arcoguia.com', href)
        image_urls.append(href)

print(f"Se encontraron {len(image_urls)} imágenes en {url}.")
print("URLs de las imágenes:")
for idx, img_url in enumerate(image_urls, 1):
    print(f"{idx}: {img_url}")

# Crear un PDF
pdf = FPDF()
pdf.set_auto_page_break(0)

# Descargar y agregar cada imagen al PDF
for idx, img_url in enumerate(image_urls, 1):
    try:
        img_response = requests.get(img_url)
        img_response.raise_for_status()
        
        img = Image.open(BytesIO(img_response.content))
        img_format = img.format
        img_path = f"temp_image_{idx}.{img_format.lower()}"
        img.save(img_path)
        
        pdf.add_page()
        
        # Mantener la proporción original de la imagen en el PDF
        pdf_w, pdf_h = pdf.w - 20, pdf.h - 20
        img_w, img_h = img.size
        if img_w > pdf_w or img_h > pdf_h:
            if img_w / pdf_w > img_h / pdf_h:
                new_w = pdf_w
                new_h = (pdf_w / img_w) * img_h
            else:
                new_h = pdf_h
                new_w = (pdf_h / img_h) * img_w
        else:
            new_w, new_h = img_w, img_h
        
        pdf.image(img_path, x=10, y=10, w=new_w, h=new_h)
        
        # Eliminar la imagen temporal después de agregarla al PDF
        os.remove(img_path)
    except Exception as e:
        print(f"Error al procesar la imagen {idx}: {e} - URL: {img_url}")

# Guardar el PDF
output_path = "output.pdf"
pdf.output(output_path)
print(f"PDF generado correctamente en: {output_path}")