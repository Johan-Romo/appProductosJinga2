from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .forms import ProductoForm
from django.http import HttpResponse
import csv
from django.contrib import messages
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render



def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'listar.html', {'productos': productos})

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'crear_producto.html', {'form': form})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'form': form})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('listar_productos')
    return render(request, 'eliminar_producto.html', {'producto': producto})


def exportar_productos(request):
    # Obtener todos los productos
    productos = Producto.objects.all()

    # Crear una respuesta HTTP con un archivo CSV adjunto
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="productos.csv"'

    # Crear un objeto writer para escribir los datos en el archivo CSV
    writer = csv.writer(response)

    # Escribir la fila de encabezados
    writer.writerow(['Nombre; Precio; Cantidad'])

    # Escribir los datos de los productos en el archivo CSV
    for producto in productos:
        writer.writerow([producto.nombre+';'+str(producto.precio)+';'+ str(producto.cantidad)])

    return response



def importar_productos(request):
    if request.method == 'POST' and 'archivo_csv' in request.FILES:
        archivo_csv = request.FILES['archivo_csv']

        if not archivo_csv.name.endswith('.csv'):
            messages.error(request, 'El archivo no es un CSV.')
            return redirect('importar_productos')  # Redirige para evitar el reenvío del formulario

        try:
            # Lee el contenido del archivo como texto
            texto_csv = archivo_csv.read().decode('utf-8').splitlines()

            csv_data = csv.reader(texto_csv, delimiter=';')  # Cambiar el delimitador a punto y coma
            for index, row in enumerate(csv_data):
                try:
                    nombre = row[0]
                    precio = Decimal(row[1])  # Convierte el valor a Decimal
                    cantidad = int(row[2])  # Convierte el valor a entero si es necesario

                    _, created = Producto.objects.update_or_create(
                        nombre=nombre,
                        defaults={'precio': precio, 'cantidad': cantidad}
                    )
                except (IndexError, ValueError, ValidationError, InvalidOperation) as e:
                    # Manejar errores de índice, valores no válidos, etc.
                    print(f"Error en la línea {index + 1}: {e}")
                    # Puedes agregar aquí un manejo específico para los valores problemáticos, como saltar la línea o registrar el error en algún archivo de registro
            messages.success(request, 'Productos importados exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {e}')
            return redirect('importar_productos')

        return redirect('importar_productos')  # Redirige después de procesar el archivo

    return render(request, 'importar_productos.html')


def graficar_productos(request):
    productos = Producto.objects.all()
    nombres = [producto.nombre for producto in productos]
    cantidades = [producto.cantidad for producto in productos]

    plt.figure(figsize=(10, 5))
    plt.bar(nombres, cantidades, color='skyblue')
    plt.xlabel('Producto')
    plt.ylabel('Cantidad')
    plt.title('Cantidad de cada Producto')
    plt.xticks(rotation=45, ha='right')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'listar.html', {'productos': productos, 'data': uri})
