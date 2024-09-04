import tkinter as tk
from tkinter import messagebox
import random
import mysql.connector
from tkcalendar import Calendar, DateEntry

def extraer_id(cadena):
    valores = cadena.split('||')
    for valor in valores:
        if "N° Seguimiento" in valor:
            numero_id = int(valor.split(':')[1].strip())
            return numero_id

class EnviosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inscripción de envíos")

        db_config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'database': 'semana 9 prog avanzada'
        }

        self.connection = mysql.connector.connect(**db_config)

        self.cursor = self.connection.cursor()

        # Creacion y configuracion de los elementos GUI

        self.label_seguimiento = tk.Label(root, text="N° de seguimiento:")
        self.entry_seguimiento = tk.Entry(root)

        self.label_origen = tk.Label(root, text="Origen:")
        self.entry_origen = tk.Entry(root)

        self.label_destino = tk.Label(root, text="Destino:")
        self.entry_destino = tk.Entry(root)

        self.label_entrega = tk.Label(root, text="Fecha de entrega prevista:")
        self.entry_entrega = DateEntry(root, width=12, bg="darkblue", fg="white", borderwidth=2)
        self.entry_entrega.delete(0, tk.END)

        self.label_estado = tk.Label(root, text="Estado de entrega:")
        categorias_envio = ["Seleccione una opción:", "En tránsito", "Entregado"]
        self.var_categoria_envio = tk.StringVar()
        self.var_categoria_envio.set(categorias_envio[0])

        self.btn_agregar = tk.Button(root, text="Agregar envio", command=self.agregar_envio)
        self.btn_mostrar = tk.Button(root, text="Mostrar envios", command=self.mostrar_envio)
        self.btn_limpiar = tk.Button(root, text="Limpiar lista", command=self.limpiar_datos)
        self.btn_actualizar = tk.Button(root, text="Actualizar envio", command=self.actualizar_envio)
        self.btn_borrar = tk.Button(root, text="Borrar envio", command=self.borrar_envio)
        self.btn_informe = tk.Button(root, text="Generar informe", command=self.escribir_informe)
        self.btn_generar = tk.Button(root, text="Generar N° seguimiento", command=self.generar_numero)
        self.numeros_generados = set()

        # Creacion de lista para seleccionar envios
        self.lista_envios = tk.Listbox(root, selectmode=tk.SINGLE, width=130)
        self.lista_envios.bind('<<ListboxSelect>>', self.cargar_datos)

        # Ubicación de los elementos GUI

        self.label_seguimiento.grid(row=1, column=0, padx=10, pady=10)
        self.entry_seguimiento.grid(row=1, column=1, padx=10, pady=10)
        self.btn_generar.grid(row=1, column=2, padx=4, pady=4)

        self.label_origen.grid(row=2, column=0, padx=10, pady=10)
        self.entry_origen.grid(row=2, column=1, padx=10, pady=10)

        self.label_destino.grid(row=3, column=0, padx=10, pady=10)
        self.entry_destino.grid(row=3, column=1, padx=10, pady=10)

        self.label_entrega.grid(row=4, column=0, padx=10, pady=10)
        self.entry_entrega.grid(row=4, column=1, padx=10, pady=10)

        self.label_estado.grid(row=5, column=0, padx=10, pady=10)
        menu_categoria_envio = tk.OptionMenu(root, self.var_categoria_envio, *categorias_envio)
        menu_categoria_envio["menu"].entryconfig(0, state="disabled")
        menu_categoria_envio.grid(row=5, column=1, padx=10, pady=10)

        self.lista_envios.grid(row=6, column=0, columnspan=2, pady=10)

        self.btn_agregar.grid(row=7, column=0, columnspan=1, pady=10)
        self.btn_mostrar.grid(row=7, column=1, columnspan=1, pady=10)
        self.btn_limpiar.grid(row=8, column=0, columnspan=1, pady=10)
        self.btn_actualizar.grid(row=8, column=1, columnspan=1, pady=10)
        self.btn_borrar.grid(row=9, column=0, columnspan=1, pady=10)
        self.btn_informe.grid(row=9, column=1, columnspan=1, pady=10)

    # FUNCIONES PARA PROGRAMA
    def generar_numero(self):
        numero_generado = random.randint(100000000, 999999999)
        while numero_generado in self.numeros_generados:
            numero_generado = random.randint(100000000, 999999999)
        self.numeros_generados.add(numero_generado)
        self.entry_seguimiento.delete(0, tk.END)
        self.entry_seguimiento.insert(0, numero_generado)

    def agregar_envio(self):
        seguimiento = self.entry_seguimiento.get()
        if self.entry_seguimiento.get() == "":
            messagebox.showerror("Error", "Debe agregar un número de seguimiento")
            return
        origen = self.entry_origen.get()
        if self.entry_origen.get() == "":
            messagebox.showerror("Error", "Debe agregar un número de seguimiento")
            return
        destino = self.entry_destino.get()
        if self.entry_destino.get() == "":
            messagebox.showerror("Error", "Debe agregar un número de seguimiento")
            return
        entrega = self.entry_entrega.get_date().strftime("%Y-%m-%d")
        estado = self.var_categoria_envio.get()

        try:
           # Insertar datos en tabla
            query = "INSERT INTO envios (NumeroSeguimiento, Origen, Destino, FechaEntregaPrevista, Estado) VALUES (%s, %s, %s, %s, %s)"
            values = (seguimiento, origen, destino, entrega, estado)
            self.cursor.execute(query, values)

           # Se confirma la transacción
            self.connection.commit()

            messagebox.showinfo("Éxito", "Envio agregado correctamente")
            self.limpiar_datos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar el envio: {str(e)}")

    def mostrar_envio(self):
        try:
            # Limpiar lista antes de mostrar
            self.lista_envios.delete(0, tk.END)

            # Consulta SELECT
            query = "SELECT * FROM envios"
            self.cursor.execute(query)

            # Obtener los resultados
            envios = self.cursor.fetchall()

            # Mostrar los resultados
            for envio in envios:
                self.lista_envios.insert(tk.END, f"N° Seguimiento: {envio[1]} || Origen: {envio[2]} || Destino: {envio[3]} || Fecha de entrega: {envio[4]} || Estado: {envio[5]}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar los envios: {str(e)}")

    def actualizar_envio(self):
        try:
            seleccion = self.lista_envios.curselection()

            # Obtener datos del envio
            seguimiento = self.entry_seguimiento.get()
            origen = self.entry_origen.get()
            destino = self.entry_destino.get()
            entrega = self.entry_entrega.get_date().strftime("%Y-%m-%d")
            estado = self.var_categoria_envio.get()

            # Actualizar envio en la DB
            query = "UPDATE envios SET Origen = %s, Destino = %s, FechaEntregaPrevista = %s, Estado = %s WHERE NumeroSeguimiento = %s"
            values = (origen, destino, entrega, estado, seguimiento)
            self.cursor.execute(query, values)

            # Confirmar la transacción
            self.connection.commit()

            messagebox.showinfo("Éxito", f"Envio con N° de seguimiento {seguimiento} actualizado correctamente")
            self.mostrar_envio()
            self.limpiar_datos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar especimen: {str(e)}")

    def cargar_datos(self, event):
        seleccion = self.lista_envios.curselection()
        if seleccion:
            envio_seleccionado = self.lista_envios.get(seleccion[0])

            NumeroSeguimiento = extraer_id(envio_seleccionado)

            # Obtener datos del envio
            query = "SELECT * FROM envios WHERE NumeroSeguimiento = %s"
            self.cursor.execute(query, (NumeroSeguimiento,))
            datos_envio = self.cursor.fetchone()

            # Cargar datos en los campos de entrada
            self.entry_seguimiento.delete(0, tk.END)
            self.entry_seguimiento.insert(0, NumeroSeguimiento)

            self.entry_origen.delete(0, tk.END)
            self.entry_origen.insert(0, datos_envio[2])

            self.entry_destino.delete(0, tk.END)
            self.entry_destino.insert(0, datos_envio[3])

            self.entry_entrega.set_date(datos_envio[4])

            self.var_categoria_envio.set(datos_envio[5])

    def limpiar_datos(self):
        self.entry_seguimiento.delete(0, tk.END)
        self.entry_origen.delete(0, tk.END)
        self.entry_destino.delete(0, tk.END)
        self.entry_entrega.delete(0, tk.END)
        self.var_categoria_envio.set("Seleccione una opción:")
        self.lista_envios.delete(0, tk.END)

    def escribir_informe(self):
        try:
            # Consulta SELECT
            query = "SELECT * FROM envios"
            self.cursor.execute(query)

            # Obtener los resultados
            envios = self.cursor.fetchall()

            # Generar los datos a escribir en el informe
            Informe = ""
            for envio in envios:
                Informe += (f"ID del envío: {envio[0]} || N° Seguimiento: {envio[1]} || Origen: {envio[2]} || Destino: {envio[3]} || Fecha de entrega: {envio[4]} || Estado: {envio[5]}\n")

            nombre_archivo = "Infome de envios.txt"
            with open(nombre_archivo, 'w') as archivo:
                archivo.write(Informe)

            messagebox.showinfo("Éxito", "Informe creado correctamente")
            self.limpiar_datos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar los envios: {str(e)}")

    def borrar_envio(self):
        try:
            seleccion = self.lista_envios.curselection()

            if seleccion:
                envio_seleccionado = self.lista_envios.get(seleccion[0])

                Seguimiento = extraer_id(envio_seleccionado)

                # Borrar envío de la DB
                query = "DELETE FROM envios WHERE NumeroSeguimiento = %s"
                self.cursor.execute(query, (Seguimiento,))

                # Confirmar transacción
                self.connection.commit()

                messagebox.showinfo("Éxito", f"Especimen con N° de seguimiento {Seguimiento} borrado correctamente")
                self.mostrar_envio()
                self.limpiar_datos()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar especimen: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnviosApp(root)
    root.mainloop()

    # Cerrar cursor y conexión
    app.cursor.close()
    app.connection.close()
