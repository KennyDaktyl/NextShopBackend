import json
import os
from django import forms
import openai
from web.models.images import Photo, Thumbnail
from web.models.prices import ProductPrice
from web.models.products import Product


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'meta_title', 
            'meta_description', 
            'h1_tag', 
            'name', 
            'slug', 
            'qty', 
            'description', 
            'category',  
            'oryg_image', 
            'image_alt', 
            'image_title', 
            'is_active'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Dodaj klasę CSS Bootstrap 5 do każdego pola
            field.widget.attrs['class'] = 'form-control'

    def generate_seo_data(self, name, image_url, category):
        # Konfiguracja OpenAI
        openai.api_key = os.getenv('OPEN_AI_SECRET')

        # Prompt dla ChatGPT
        prompt = (
             f"Generuj dane SEO dla produktu '{name}' ze zdjęciem: {image_url} z kategorii {category}. "
            "Zwróć wynik w formacie JSON: "
            "{'meta_title': '...', 'meta_description': '...', 'description': '...', 'seo_text': '<section>...</section>', 'alt': '...', 'title': '...'}."
            " Zwróć tylko poprawny JSON."
        )

        # Nowa metoda OpenAI ChatCompletion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Możesz użyć "gpt-4" w zależności od dostępności
            messages=[
                {"role": "system", "content": "Jesteś asystentem generującym dane SEO dla e-commerce."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )

        # Parsowanie odpowiedzi
        raw_content = response['choices'][0]['message']['content']
        cleaned_content = raw_content.strip()
        try:
            seo_data = json.loads(raw_content)
            seo_data = json.loads(cleaned_content)
            print(seo_data)
            return seo_data  # Zwraca dane jako obiekt Python (słownik)
        except Exception as e:
            print("Niekompletna odpowiedź. Próbuję naprawić...")
            raw_content += "}"  # Dodaj brakujący nawias, jeśli JSON został obcięty
            try:
                seo_data = json.loads(raw_content)
            except json.JSONDecodeError as e:
                print(f"Błąd parsowania JSON po poprawce: {e}")
                seo_data = None
        

class ProductPriceForm(forms.ModelForm):
    class Meta:
        model = ProductPrice
        fields = ['price']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'price': 'Nowa cena',
        }
        

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['name', 'oryg_image', 'image_alt', 'image_title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
            
class ThumbnailForm(forms.ModelForm):
    class Meta:
        model = Thumbnail
        fields = ['order', 'alt', 'title']
