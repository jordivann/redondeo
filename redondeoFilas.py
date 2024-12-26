import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
import numpy as np

def modificar_columna():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if not file_path:
        return
    
    try:
        # Leer el CSV con todas las columnas como strings
        df = pd.read_csv(file_path, encoding='ISO-8859-1', sep=';', on_bad_lines='skip', dtype=str, 
                         header=0 if usar_primera_fila_como_encabezado.get() else None)
        
        if not usar_primera_fila_como_encabezado.get():
            # Si no se usa la primera fila como encabezado, asignar nombres de columnas genéricos
            df.columns = [f'Column_{i}' for i in range(len(df.columns))]
        
        print("Columnas encontradas en el archivo CSV:")
        print(df.columns)
        
        # La columna objetivo es la décima (índice 9 en 0-basado)
        columna_objetivo = df.columns[9]
        
        # Obtener los valores ingresados por el usuario
        iva = valor_iva.get()
        margen_ingresado = valor_margen.get()
        usar_margen_pvp_valor = usar_margen_pvp.get()
        
        margen_pvp_index = 17
        
        # Aplicar la fórmula en la columna objetivo y formatear el resultado
        def aplicar_formula(row):
            valor = row[columna_objetivo]
            
            if pd.isna(valor) or valor == '':
                print("entro")
                return ''
            try:
                valor = float(valor)
                
                # Determinar qué margen usar    
                if usar_margen_pvp_valor:
                    # Convertir el margen del CSV (ej. 4000) a un factor (ej. 1.40)
                    margen =  1 + (float(row[df.columns[margen_pvp_index]]) / 10000)
                else:
                    margen = margen_ingresado if margen_ingresado != 1.25 else 1.25
                
                resultado = (valor / 100 * iva * margen)
                resultado = np.ceil(resultado / 10) * 10
                resultado = resultado / (iva * margen) * 100
                # Formatear el resultado con 3 decimales, sin separador de miles y con coma como separador decimal
                return f"{resultado:.3f}".replace('.', ',')
            except Exception as e:
                print(f"Error en aplicar fórmula: {e}")
                return ''
        
        df[columna_objetivo] = df.apply(aplicar_formula, axis=1)
        
        # Limpiar y convertir la columna 'codebar2' (suponiendo que es la segunda columna)
        columna_codebar2 = df.columns[1]
        
        def limpiar_columna(valor):
            if pd.isna(valor) or valor == '':
                return ''
            valor = str(valor).replace('.0', '')  # Eliminar ".0"
            try:
                if 'E' in valor or 'e' in valor:  # Manejar notación científica
                    valor = int(float(valor))
                else:
                    valor = int(valor)
                return valor
            except ValueError:
                return ''
        
        df[columna_codebar2] = df[columna_codebar2].apply(limpiar_columna)
        
        # Reemplazar NaN por cadenas vacías
        df.fillna('', inplace=True)
        
        print("Primeras filas del DataFrame modificado:")
        print(df.head())
        
        # Guardar el archivo asegurando el formato adecuado
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        
        if save_path:
            # Guardar sin índice y sin encabezados
            df.to_csv(save_path, index=False, header=False, sep=';', quoting=0)
            messagebox.showinfo("Éxito", "El archivo ha sido guardado correctamente sin títulos de columnas.")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {str(e)}")

def generar_csv_encabezado():
    # Definir las columnas que quieres en el CSV
    columnas = [
        "codigo","codebar", "codebar2", "codebar3", "codebar4",
        "producto", "presentacion", "rubro", "idSubRubro", "mp.precio*100", "m.IVA*100",
        "unidades", "importado", "margen", "activo", "gtin", "trazable",
        "margenPVP", "idLaboratorio", "Descripcion"
    ]
    
    # Crear un DataFrame con las columnas especificadas
    df = pd.DataFrame(columns=columnas)
    
    # Guardar el archivo CSV con las columnas especificadas
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    
    if save_path:
        df.to_csv(save_path, index=False, sep=';', quoting=1)  # quoting=1 para comillas dobles
        messagebox.showinfo("Éxito", "El archivo de encabezado ha sido guardado correctamente.")
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo para guardar.")


# Configurar la apariencia de CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

# Crear la ventana principal
root = ctk.CTk()
root.title("Redondeo de PVP masivo")
root.geometry("800x700")  # Increased height for better spacing

# Crear variables Tkinter
valor_iva = ctk.DoubleVar(value=1.21)
valor_margen = ctk.DoubleVar(value=1.25)
usar_margen_pvp = ctk.BooleanVar(value=False)
usar_primera_fila_como_encabezado = ctk.BooleanVar(value=True)

# Crear un frame principal
main_frame = ctk.CTkFrame(root)
main_frame.pack(pady=30, padx=30, fill="both", expand=True)

# Crear un título
titulo = ctk.CTkLabel(main_frame, text="Redondeo de Costo", font=ctk.CTkFont(size=32, weight="bold"))
titulo.pack(pady=20)

# Crear una descripción
descripcion = ctk.CTkLabel(main_frame, text="Seleccione el CSV y calculará el costo para obtener un PVP redondeado", 
                           font=ctk.CTkFont(size=16), wraplength=600)
descripcion.pack(pady=15)

# Crear frame para los inputs
frame_inputs = ctk.CTkFrame(main_frame)
frame_inputs.pack(pady=25, padx=20, fill="x")

# IVA input
iva_frame = ctk.CTkFrame(frame_inputs)
iva_frame.pack(side="left", padx=(0, 10), fill="x", expand=True)
ctk.CTkLabel(iva_frame, text="IVA:", font=ctk.CTkFont(size=16)).pack(pady=(5, 0))
entrada_iva = ctk.CTkEntry(iva_frame, textvariable=valor_iva, width=140, height=40, font=ctk.CTkFont(size=16))
entrada_iva.pack(pady=10)

# Margen input
margen_frame = ctk.CTkFrame(frame_inputs)
margen_frame.pack(side="left", padx=(10, 0), fill="x", expand=True)
ctk.CTkLabel(margen_frame, text="Margen:", font=ctk.CTkFont(size=16)).pack(pady=(5, 0))
entrada_margen = ctk.CTkEntry(margen_frame, textvariable=valor_margen, width=140, height=40, font=ctk.CTkFont(size=16))
entrada_margen.pack(pady=10)

# Agregar los checkboxes
checkbox_frame = ctk.CTkFrame(main_frame)
checkbox_frame.pack(pady=20, fill="x")

checkbox_margen_pvp = ctk.CTkCheckBox(checkbox_frame, text="Usar margenPVP del CSV", 
                                      variable=usar_margen_pvp, font=ctk.CTkFont(size=16))
checkbox_margen_pvp.pack(pady=(0, 10))

checkbox_primera_fila = ctk.CTkCheckBox(checkbox_frame, text="Primera fila contiene títulos de columnas", 
                                        variable=usar_primera_fila_como_encabezado, font=ctk.CTkFont(size=16))
checkbox_primera_fila.pack(pady=(10, 0))

# Crear frame para los botones
frame_buttons = ctk.CTkFrame(main_frame)
frame_buttons.pack(pady=40)

btn_modificar = ctk.CTkButton(frame_buttons, text="Redondear Costo", command=modificar_columna, 
                              width=220, height=60, font=ctk.CTkFont(size=18, weight="bold"))
btn_modificar.pack(side="left", padx=(0, 15))

btn_descargar_encabezado = ctk.CTkButton(frame_buttons, text="Formato ejemplo", command=generar_csv_encabezado, 
                                         width=220, height=60, font=ctk.CTkFont(size=18, weight="bold"))
btn_descargar_encabezado.pack(side="left", padx=(15, 0))

# Iniciar el bucle principal de Tkinter
root.mainloop()