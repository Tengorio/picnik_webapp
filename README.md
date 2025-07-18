# 🔬 pICNIK Web App - Análisis Isoconversional

Una aplicación web interactiva desarrollada con Streamlit para realizar análisis isoconversional de cinética térmica utilizando la librería pICNIK.

## 📋 Características de la Interfaz

- **Sidebar de navegación**: Navegación paso a paso a través de 6 módulos especializados
- **Indicadores de estado**: Seguimiento visual del progreso del análisis
- **Gráficos interactivos**: Visualización en tiempo real
- **Múltiples métodos**: Soporte para Friedman, KAS, OFW, Vyazovkin y Vyazovkin Avanzado
- **Exportación fácil**: Botones de descarga en cada módulo
- **Validación de datos**: Mensajes de error y advertencias claros

## 🌐 Aplicación Online (gratis)

Puedes acceder y usar la aplicación web en [https://picnik.streamlit.app/](https://picnik.streamlit.app/)

## 🛠️ Instalación en local 

### Clonación del repositorio
```bash
git clone https://github.com/tengorio/picnik_webapp.git
cd picnik_webapp
```

### Instala Requisitos previos
```bash
pip install requirements.txt
```

### Ejecutar la aplicación
```bash
streamlit run picnik_app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 🧩 Descripción de los Módulos

### 1. ⬆️ Carga de Datos y 📊 Resumen Gráfico
- Carga múltiples archivos CSV de datos térmicos (TGA/DSC)
- Ordenamiento personalizable de archivos
- Visualización automática de datos cargados

### 2. 🌡️ Rango de Temperatura para Conversión
- Configuración interactiva de rangos de temperatura
- Visualización personalizable (temperatura/tiempo vs TG/DTG/DSC)
- Selección de unidades

### 3. 🔄 Cálculo de Valores de Conversión
- Cálculo automático de valores de conversión
- Validación del rango de temperatura
- Visualización de curvas de conversión

### 4. 📋 Tablas Isoconversionales
- Generación de tablas isoconversionales
- Configuración del incremento de conversión (d_a)
- Exportación de tablas de temperaturas y tiempos

### 5. ⚡ Cálculo de Energía de Activación
- **Métodos disponibles:**
  - Friedman
  - Kissinger-Akahira-Sunose (KAS)
  - Ozawa-Flynn-Wall (OFW)
  - Vyazovkin
  - Vyazovkin Avanzado
- Visualización comparativa de energías
- Exportación de resultados

### 6. 🔮 Predicción Model-free
- **Programas de temperatura:**
  - Isotérmico
  - Calentamiento lineal
  - Programa mixto
- Predicciones basadas en energías calculadas
- Exportación de curvas de predicción

## 🧑‍💻 Uso

### Flujo de trabajo recomendado

1. **Preparar datos**: Asegúrate de tener archivos CSV con datos de TGA/DSC
2. **Cargar datos** (Módulo 1): Sube y ordena tus archivos
3. **Configurar rango** (Módulo 2): Define el rango de temperatura de análisis
4. **Calcular conversión** (Módulo 3): Genera las curvas de conversión
5. **Crear tablas** (Módulo 4): Genera tablas isoconversionales
6. **Calcular energía** (Módulo 5): Aplica métodos de cálculo de energía de activación
7. **Hacer predicciones** (Módulo 6): Genera predicciones model-free

#### 📊 Formato de Datos

Los archivos CSV deben contener columnas para:
- Temperatura (K o °C)
- Tiempo (min o s)
- Datos termogravimétricos (TG, DTG)
- Datos de DSC (opcional)

#### Exportación de resultados
- Tablas isoconversionales → CSV
- Energías de activación → CSV
- Predicciones model-free → CSV

## 🤝 Contribución

Las contribuciones son bienvenidas. 

1. Fork el repositorio
2. Crea una rama para tu feature 
3. Commit tus cambios 
4. Push a la rama 
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🐛 Reporte de Bugs

Si encuentras algún error, por favor crea un issue en GitHub incluyendo:
- Descripción del error
- Pasos para reproducirlo
- Información del sistema
- Archivos de ejemplo o capturas de pantalla (si es posible)

## 📚 Documentación Adicional

- [Tesis: pICNIK: Implementaci ́on enpython de c ́alculos deisoconversi ́on para cin ́eticaanisot ́ermica ](https://tesiunamdocumentos.dgb.unam.mx/ptd2022/febrero/0822031/Index.html)
- [Documentación de pICNIK](https://picnik.readthedocs.io/)
- [Documentación de Streamlit](https://docs.streamlit.io/)

## 👥 Autor

- **Javier Tenorio** - *Desarrollo de la interfaz* - [Tengorio](https://github.com/tengorio) 

## 🙏 Agradecimientos

- **Erick Ramirez** - *Desarrollador de pICNIK* - [ErickErock](https://github.com/ErickErock) 
- Comunidad de Streamlit

---

**Si este proyecto te resulta útil, considera darle una estrella ⭐**