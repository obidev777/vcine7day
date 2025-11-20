import os
import sys
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import filedialog, messagebox

class AndroidIconGenerator:
    def __init__(self):
        self.sizes = {
            # Mipmap para launcher icons
            'mipmap-hdpi': 72,
            'mipmap-mdpi': 48,
            'mipmap-xhdpi': 96,
            'mipmap-xxhdpi': 144,
            'mipmap-xxxhdpi': 192,
            
            # Mipmap para adaptive icons (foreground)
            'mipmap-hdpi-foreground': 108,
            'mipmap-mdpi-foreground': 72,
            'mipmap-xhdpi-foreground': 144,
            'mipmap-xxhdpi-foreground': 216,
            'mipmap-xxxhdpi-foreground': 288,
            
            # Mipmap para adaptive icons (background) - opcional
            'mipmap-hdpi-background': 108,
            'mipmap-mdpi-background': 72,
            'mipmap-xhdpi-background': 144,
            'mipmap-xxhdpi-background': 216,
            'mipmap-xxxhdpi-background': 288,
            
            # Play Store
            'play-store': 512,
        }
        
    def select_image(self):
        """Selecciona una imagen del sistema de archivos"""
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal
        
        file_path = filedialog.askopenfilename(
            title="Selecciona la imagen para el icono",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        return file_path
    
    def create_rounded_icon(self, image, size):
        """Crea un icono redondeado"""
        # Crear una máscara circular
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Redimensionar la imagen
        img_resized = image.resize((size, size), Image.Resampling.LANCZOS)
        
        # Aplicar la máscara circular
        result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        result.putalpha(mask)
        result.paste(img_resized, (0, 0), img_resized)
        
        return result
    
    def create_adaptive_icon_foreground(self, image, size):
        """Crea el foreground para adaptive icons (mantiene la imagen completa)"""
        return image.resize((size, size), Image.Resampling.LANCZOS)
    
    def create_adaptive_icon_background(self, size, color=(0, 0, 0, 0)):
        """Crea un background simple para adaptive icons (transparente por defecto)"""
        bg = Image.new('RGBA', (size, size), color)
        return bg
    
    def generate_icons(self, input_path, output_dir="android_icons"):
        """Genera todos los iconos necesarios"""
        try:
            # Crear directorio de salida
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Abrir y procesar la imagen original
            original_image = Image.open(input_path).convert('RGBA')
            
            # Generar iconos para cada densidad
            for folder, size in self.sizes.items():
                # Crear subdirectorio
                folder_path = os.path.join(output_dir, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                if 'foreground' in folder:
                    # Generar foreground para adaptive icons
                    icon = self.create_adaptive_icon_foreground(original_image, size)
                    icon.save(os.path.join(folder_path, 'ic_launcher_foreground.png'))
                    
                elif 'background' in folder:
                    # Generar background para adaptive icons (transparente)
                    icon = self.create_adaptive_icon_background(size)
                    icon.save(os.path.join(folder_path, 'ic_launcher_background.png'))
                    
                elif 'play-store' in folder:
                    # Icono para Play Store
                    icon = self.create_rounded_icon(original_image, size)
                    icon.save(os.path.join(folder_path, 'ic_launcher_play_store.png'))
                    
                else:
                    # Iconos tradicionales redondeados
                    icon = self.create_rounded_icon(original_image, size)
                    icon.save(os.path.join(folder_path, 'ic_launcher.png'))
            
            return True, output_dir
            
        except Exception as e:
            return False, str(e)
    
    def show_instructions(self, output_dir):
        """Muestra instrucciones para usar los iconos generados"""
        instructions = f"""
✅ Iconos generados exitosamente en: {output_dir}

📁 ESTRUCTURA DE CARPETAS CREADA:

{output_dir}/
├── mipmap-hdpi/ic_launcher.png
├── mipmap-mdpi/ic_launcher.png
├── mipmap-xhdpi/ic_launcher.png
├── mipmap-xxhdpi/ic_launcher.png
├── mipmap-xxxhdpi/ic_launcher.png
├── mipmap-hdpi-foreground/ic_launcher_foreground.png
├── mipmap-mdpi-foreground/ic_launcher_foreground.png
├── mipmap-xhdpi-foreground/ic_launcher_foreground.png
├── mipmap-xxhdpi-foreground/ic_launcher_foreground.png
├── mipmap-xxxhdpi-foreground/ic_launcher_foreground.png
├── mipmap-hdpi-background/ic_launcher_background.png
├── mipmap-mdpi-background/ic_launcher_background.png
├── mipmap-xhdpi-background/ic_launcher_background.png
├── mipmap-xxhdpi-background/ic_launcher_background.png
└── mipmap-xxxhdpi-background/ic_launcher_background.png
└── play-store/ic_launcher_play_store.png

📋 INSTRUCCIONES PARA ANDROID STUDIO:

1. Copia las carpetas mipmap-* a tu proyecto:
   - Ve a: app/src/main/res/
   - Pega las carpetas mipmap-* aquí

2. En tu archivo AndroidManifest.xml, asegúrate de que apunte al icono:
   android:icon="@mipmap/ic_launcher"

3. Para Adaptive Icons (Android 8.0+), configura en res/mipmap-anydpi-v26/:
   - Crea un archivo ic_launcher.xml con:
   
   <?xml version="1.0" encoding="utf-8"?>
   <adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
       <background android:drawable="@mipmap/ic_launcher_background"/>
       <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
   </adaptive-icon>

4. El icono de Play Store está en la carpeta play-store/
"""
        return instructions

def main():
    """Función principal"""
    print("🚀 Generador de Iconos para Android")
    print("=" * 40)
    
    generator = AndroidIconGenerator()
    
    # Seleccionar imagen
    print("📷 Selecciona una imagen para generar los iconos...")
    image_path = generator.select_image()
    
    if not image_path:
        print("❌ No se seleccionó ninguna imagen.")
        return
    
    print(f"📁 Imagen seleccionada: {image_path}")
    
    # Especificar directorio de salida
    output_dir = input("📂 Ingresa el nombre del directorio de salida (presiona Enter para 'android_icons'): ").strip()
    if not output_dir:
        output_dir = "android_icons"
    
    # Generar iconos
    print("🔄 Generando iconos...")
    success, result = generator.generate_icons(image_path, output_dir)
    
    if success:
        print("✅ ¡Iconos generados exitosamente!")
        instructions = generator.show_instructions(result)
        print(instructions)
        
        # Guardar instrucciones en un archivo
        with open(os.path.join(result, "INSTRUCCIONES.txt"), "w", encoding="utf-8") as f:
            f.write(instructions)
        
        print(f"📝 Las instrucciones también se guardaron en: {os.path.join(result, 'INSTRUCCIONES.txt')}")
        
    else:
        print(f"❌ Error al generar iconos: {result}")

if __name__ == "__main__":
    # Verificar dependencias
    try:
        from PIL import Image
        main()
    except ImportError:
        print("❌ Se requiere la biblioteca Pillow.")
        print("📦 Instálala con: pip install pillow")
        
        # Instalación automática
        install = input("¿Quieres instalar Pillow automáticamente? (s/n): ").lower()
        if install == 's':
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("✅ Pillow instalado. Ejecuta el script nuevamente.")