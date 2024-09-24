import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

def modificar_columna():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if not file_path:
        return
    
    try:
        # Leer el CSV con todas las columnas como strings
        df = pd.read_csv(file_path, encoding='ISO-8859-1', sep=';', on_bad_lines='skip', dtype=str)
        
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
                    margen =  1 + (float(row[margen_pvp_index]) / 10000)
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
            df.to_csv(save_path, index=False, sep=';', quoting=0)  # quoting=0 para no usar comillas
            messagebox.showinfo("Éxito", "El archivo ha sido guardado correctamente.")
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

def on_enter(event):
    event.widget.config(bg='lightblue')

def on_leave(event):
    event.widget.config(bg='gray')

# Crear la ventana principal
root = tk.Tk()
root.title("Redondeo de PVP masivo")
root.geometry("650x350")  # Aumentamos un poco la altura para acomodar el nuevo checkbox

# Cambiar el color de fondo de la ventana principal
root.configure(bg='black')

# Crear variables Tkinter
valor_iva = tk.DoubleVar(value=1.21)  # Valor predeterminado de IVA
valor_margen = tk.DoubleVar(value=1.25)  # Valor predeterminado de Margen
usar_margen_pvp = tk.BooleanVar(value=False)  # Variable para el checkbox

# Crear un título
titulo = tk.Label(root, text="Redondeo de Costo", font=("Arial", 22, "bold"), fg='white', bg='black')
titulo.pack(pady=10)

# Crear una descripción
descripcion = tk.Label(root, text="Seleccione el CSV y calculará el costo para obtener un pvp redondeado", fg='white', bg='black')
descripcion.pack(pady=5)

# Crear campos de entrada para IVA y Margen en el mismo renglón
frame_inputs = tk.Frame(root, bg='black')
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="IVA:", fg='white', bg='black').grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
entrada_iva = tk.Entry(frame_inputs, textvariable=valor_iva)
entrada_iva.grid(row=0, column=1, padx=1, pady=5)

tk.Label(frame_inputs, text="Margen:", fg='white', bg='black').grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
entrada_margen = tk.Entry(frame_inputs, textvariable=valor_margen)
entrada_margen.grid(row=0, column=3, padx=7, pady=5)

# Agregar el checkbox para usar margenPVP
checkbox_margen_pvp = tk.Checkbutton(root, text="Usar margenPVP del CSV", variable=usar_margen_pvp, 
                                     fg='white', bg='black', selectcolor='black', activebackground='black')
checkbox_margen_pvp.pack(pady=5)

# Crear botones en el mismo renglón con estilo
frame_buttons = tk.Frame(root, bg='black')
frame_buttons.pack(pady=10)

btn_modificar = tk.Button(frame_buttons, text="Redondear Costo", command=modificar_columna, bg='gray', fg='white', relief=tk.RAISED, borderwidth=2)
btn_modificar.grid(row=0, column=0, padx=10, pady=10)
btn_modificar.bind("<Enter>", on_enter)
btn_modificar.bind("<Leave>", on_leave)

btn_descargar_encabezado = tk.Button(frame_buttons, text="Formato ejemplo", command=generar_csv_encabezado, bg='gray', fg='white', relief=tk.RAISED, borderwidth=2)
btn_descargar_encabezado.grid(row=0, column=1, padx=10, pady=10)
btn_descargar_encabezado.bind("<Enter>", on_enter)
btn_descargar_encabezado.bind("<Leave>", on_leave)

# Iniciar el bucle principal de Tkinter
root.mainloop()