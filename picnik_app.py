import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os
from io import StringIO
import sys

# Configuración de matplotlib para Streamlit
plt.style.use('default')
st.set_page_config(page_title="pICNIK - Análisis Isoconversional", layout="wide")

# Intentar importar pICNIK
try:
    import picnik as pnk
    PICNIK_AVAILABLE = True
except ImportError:
    PICNIK_AVAILABLE = False
    st.error("⚠️ La librería pICNIK no está instalada. Por favor, instálala con: pip install picnik")

st.title("🔬 pICNIK - Análisis Isoconversional")

if not PICNIK_AVAILABLE:
    st.stop()

# Inicializar estados de sesión
def initialize_session_state():
    session_vars = {
        'data_files': [],
        'B': None,
        'T0': None,
        'xtr': None,
        'Iso_Tables': None,
        'ace': None,
        'calculated_energies': {},
        'conversion_done': False,
        'isoconversion_done': False,
        't_min': 420.0,
        't_max': 820.0,
        'uploaded_files': None
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

initialize_session_state()

# Función para mostrar gráficos de matplotlib
def show_matplotlib_plot():
    """Captura y muestra gráficos de matplotlib en Streamlit"""
    fig = plt.gcf()
    if fig.get_axes():  # Solo mostrar si hay contenido
        st.pyplot(fig)
    plt.close(fig)

# Sidebar para navegación
st.sidebar.title("📋 Módulos de Análisis")
module = st.sidebar.selectbox(
    "Seleccionar módulo:",
    [
        "1. Carga de Datos y Resumen Gráfico",
        "2. Rango de Temperatura para Conversión", 
        "3. Cálculo de Valores de Conversión",
        "4. Tablas Isoconversionales",
        "5. Cálculo de Energía de Activación",
        "6. Predicción Model-free"
    ]
)

# Estado del progreso en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Estado del Análisis:**")
st.sidebar.write(f"🔧 Datos cargados: {'✅' if st.session_state.B is not None else '❌'}")
st.sidebar.write(f"📈 Conversión calculada: {'✅' if st.session_state.conversion_done else '❌'}")
st.sidebar.write(f"📋 Tablas isoconversionales: {'✅' if st.session_state.Iso_Tables is not None else '❌'}")
st.sidebar.write(f"⚡ Energías calculadas: {len(st.session_state.calculated_energies)}")

# ==================== MÓDULO 1 ====================
if module == "1. Carga de Datos y Resumen Gráfico":
    st.header("📁 Módulo 1: Carga de Datos y Resumen Gráfico")
    
    uploaded_files = st.file_uploader(
        "Cargar archivos CSV de datos térmicos", 
        type=['csv'], 
        accept_multiple_files=True,
        help="Sube múltiples archivos CSV con datos de TGA/DSC"
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        
        # Mostrar archivos cargados
        st.subheader("📂 Archivos cargados:")
        for i, file in enumerate(uploaded_files):
            st.write(f"**{i}**: {file.name}")
        
        # Interfaz para ordenar archivos
        st.subheader("🔄 Ordenar archivos para análisis")
        st.info("Especifica el orden de los archivos usando índices separados por comas (ej: 0,1,2)")
        
        order_input = st.text_input(
            "Orden de archivos:",
            value=",".join(str(i) for i in range(len(uploaded_files))),
            placeholder="0,1,2,3..."
        )
        
        if st.button("🚀 Procesar archivos", type="primary"):
            try:
                # Validar orden
                order_indices = [int(idx.strip()) for idx in order_input.split(',')]
                if len(order_indices) != len(uploaded_files) or set(order_indices) != set(range(len(uploaded_files))):
                    st.error("❌ Error: Los índices deben ser una permutación completa de 0 a n-1")
                else:
                    # Crear archivos temporales
                    with tempfile.TemporaryDirectory() as temp_dir:
                        file_paths = []
                        ordered_files = [uploaded_files[i] for i in order_indices]
                        
                        for file in ordered_files:
                            file_path = os.path.join(temp_dir, file.name)
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            file_paths.append(file_path)
                        
                        ################################################################ Funciones de pICNIK
                        with st.spinner("Procesando archivos..."):
                            st.session_state.xtr = pnk.DataExtraction()
                            st.session_state.B, st.session_state.T0 = st.session_state.xtr.read_files(file_paths)
                        ################################################################

                        st.success("✅ Archivos procesados exitosamente")
                        
                        # Mostrar información
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("🌡️ **Velocidades de calentamiento (K/min):**")
                            st.write(st.session_state.B)
                        with col2:
                            st.write("🌡️ **Temperaturas iniciales (K):**")
                            st.write(st.session_state.T0)
                        
                        # Mostrar gráfico de resumen
                        st.subheader("📊 Resumen gráfico de datos")
                        show_matplotlib_plot()
                        
            except ValueError:
                st.error("❌ Error: Por favor ingrese números válidos separados por comas")
            except Exception as e:
                st.error(f"❌ Error al procesar archivos: {str(e)}")

# ==================== MÓDULO 2 ====================
elif module == "2. Rango de Temperatura para Conversión":
    st.header("🌡️ Módulo 2: Determinación del Rango de Temperatura")
    
    ############################################################# Warning picnik related
    if st.session_state.xtr is None:
        st.warning("⚠️ Primero debe cargar los datos en el Módulo 1")
    #############################################################
    else:
        st.subheader("📊 Visualización de datos")
        
        # Configuración del gráfico
        col1, col2 = st.columns(2)
        with col1:
            x_data = st.selectbox("Datos para eje X:", ["temperature", "time"])
            x_units = st.selectbox("Unidades X:", ["K", "°C", "min", "s"])
        
        with col2:
            y_data = st.selectbox("Datos para eje Y:", ["TG", "DTG", "DSC"])
            y_units = st.selectbox("Unidades Y:", ["%", "mg", "W/g", "mW/mg"])
        
        if st.button("📈 Generar gráfico"):
            try:
                ################################################################ funciones de picnik
                st.session_state.xtr.plot_data(x_data=x_data, y_data=y_data, x_units=x_units, y_units=y_units)
                show_matplotlib_plot()
                st.success("✅ Gráfico generado exitosamente")
            except Exception as e:
                st.error(f"❌ Error al generar gráfico: {str(e)}")
        
        # Configuración del rango de temperatura
        st.subheader("🎯 Configurar rango de temperatura")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.t_min = st.number_input(
                "Temperatura mínima (K):", 
                value=float(st.session_state.t_min), 
                min_value=0.0
            )
        with col2:
            st.session_state.t_max = st.number_input(
                "Temperatura máxima (K):", 
                value=float(st.session_state.t_max), 
                min_value=0.0
            )
        
        st.info(f"🎯 Rango seleccionado: {st.session_state.t_min:.1f} - {st.session_state.t_max:.1f} K")

# ==================== MÓDULO 3 ====================
elif module == "3. Cálculo de Valores de Conversión":
    st.header("🔄 Módulo 3: Cálculo de Valores de Conversión")
    
    if st.session_state.xtr is None:
        st.warning("⚠️ Primero debe cargar los datos en el Módulo 1")
    else:
        st.subheader("🌡️ Rango de temperatura configurado")
        st.info(f"Rango: {st.session_state.t_min:.1f} - {st.session_state.t_max:.1f} K")
        
        # Modificar rango si es necesario
        col1, col2 = st.columns(2)
        with col1:
            temp_min = st.number_input("Temperatura mínima (K):", value=st.session_state.t_min)
        with col2:
            temp_max = st.number_input("Temperatura máxima (K):", value=st.session_state.t_max)
        
        if st.button("🔄 Calcular conversión", type="primary"):
            try:
                with st.spinner("Calculando conversión..."):
                    ################################################################ funciones de picnik
                    st.session_state.xtr.Conversion(temp_min, temp_max)
                    st.session_state.conversion_done = True
                    st.session_state.t_min = temp_min
                    st.session_state.t_max = temp_max
                
                st.success("✅ Conversión calculada exitosamente")
                
                # Mostrar gráfico
                st.subheader("📊 Gráfico de conversión vs temperatura")
                show_matplotlib_plot()
                
            except Exception as e:
                st.error(f"❌ Error al calcular conversión: {str(e)}")
        
        if st.session_state.conversion_done:
            st.success("✅ Conversión ya calculada para el rango actual")

# ==================== MÓDULO 4 ====================
elif module == "4. Tablas Isoconversionales":
    st.header("📋 Módulo 4: Tablas Isoconversionales")
    
    if st.session_state.xtr is None:
        st.warning("⚠️ Primero debe cargar los datos en el Módulo 1")
    elif not st.session_state.conversion_done:
        st.warning("⚠️ Primero debe calcular la conversión en el Módulo 3")
    else:
        st.subheader("⚙️ Configuración de tablas isoconversionales")
        
        d_a = st.number_input(
            "Diferencia entre valores de conversión (d_a):", 
            value=0.005, 
            min_value=0.001, 
            max_value=0.1, 
            step=0.001,
            help="Incremento de conversión para generar las tablas isoconversionales"
        )
        
        if st.button("📊 Generar tablas isoconversionales", type="primary"):
            try:
                with st.spinner("Generando tablas isoconversionales..."):
                    st.session_state.Iso_Tables = st.session_state.xtr.Isoconversion(d_a=d_a)
                    st.session_state.isoconversion_done = True
                
                st.success("✅ Tablas isoconversionales generadas exitosamente")
                
            except Exception as e:
                st.error(f"❌ Error al generar tablas: {str(e)}")
        
        # Mostrar tablas si están disponibles
        if st.session_state.Iso_Tables is not None:
            st.subheader("📋 Tabla de Temperaturas Isoconversionales")
            
            # Mostrar la primera tabla (temperaturas)
            if len(st.session_state.Iso_Tables) > 0:
                df_temp = pd.DataFrame(st.session_state.Iso_Tables[0])
                st.dataframe(df_temp, use_container_width=True)
                
                # Botón de descarga
                csv_data = df_temp.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar tabla de temperaturas",
                    data=csv_data,
                    file_name="temperaturas_isoconversionales.csv",
                    mime="text/csv"
                )
            
            # Mostrar la segunda tabla si existe (tiempos)
            if len(st.session_state.Iso_Tables) > 1:
                st.subheader("📋 Tabla de Tiempos Isoconversionales")
                df_time = pd.DataFrame(st.session_state.Iso_Tables[1])
                st.dataframe(df_time, use_container_width=True)
                
                csv_data_time = df_time.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar tabla de tiempos",
                    data=csv_data_time,
                    file_name="tiempos_isoconversionales.csv",
                    mime="text/csv"
                )

# ==================== MÓDULO 5 ====================
elif module == "5. Cálculo de Energía de Activación":
    st.header("⚡ Módulo 5: Cálculo de Energía de Activación")
    
    if st.session_state.Iso_Tables is None:
        st.warning("⚠️ Primero debe generar las tablas isoconversionales en el Módulo 4")
    else:
        ################################################################ ActivationEergy class
        # Crear objeto ActivationEnergy si no existe
        if st.session_state.ace is None:
            st.session_state.ace = pnk.ActivationEnergy(
                st.session_state.B, 
                st.session_state.T0, 
                st.session_state.Iso_Tables
            )
        
        st.subheader("🔬 Seleccionar método de cálculo")
        
        methods = {
            "Friedman": "Fr",
            "Kissinger-Akahira-Sunose": "KAS", 
            "Ozawa-Flynn-Wall": "OFW",
            "Vyazovkin": "Vy",
            "Vyazovkin Avanzado": "aVy"
        }
        
        selected_method = st.selectbox("Método de cálculo:", list(methods.keys()))
        method_code = methods[selected_method]
        
        # Parámetros adicionales para aVy
        if selected_method == "Vyazovkin Avanzado":
            col1, col2 = st.columns(2)
            with col1:
                param1 = st.number_input("Parámetro 1:", value=5, min_value=1)
            with col2:
                param2 = st.number_input("Parámetro 2:", value=180, min_value=1)
        ################################################################ Aquí se definen los casos para los métodos en el cálculo de la energía
        if st.button("⚡ Calcular energía de activación", type="primary"):
            try:
                with st.spinner(f"Calculando energía con método {selected_method}..."):
                    if selected_method == "Vyazovkin Avanzado":
                        result = st.session_state.ace.aVy((param1, param2))
                    elif selected_method == "Friedman":
                        result = st.session_state.ace.Fr()
                    elif selected_method == "Kissinger-Akahira-Sunose":
                        result = st.session_state.ace.KAS()
                    elif selected_method == "Ozawa-Flynn-Wall":
                        result = st.session_state.ace.OFW()
                    elif selected_method == "Vyazovkin":
                        result = st.session_state.ace.Vy()
                
                st.session_state.calculated_energies[method_code] = result
                st.success(f"✅ Energía de activación calculada con método {selected_method}")
                
            except Exception as e:
                st.error(f"❌ Error al calcular energía: {str(e)}")
        
        # Mostrar energías calculadas
        if st.session_state.calculated_energies:
            st.subheader("📊 Energías de activación calculadas")
            
            for method, energy in st.session_state.calculated_energies.items():
                st.write(f"**{method}**: ✅ Calculada")
            
            # Mostrar gráfico
            if st.button("📈 Mostrar gráfico de energías"):
                try:
                    ################################################################ funcion de picnik
                    st.session_state.ace.Ea_plot(ylim=(50, 95))
                    show_matplotlib_plot()
                except Exception as e:
                    st.error(f"❌ Error al mostrar gráfico: {str(e)}")
            
            # Exportar resultados
            if st.button("📥 Exportar resultados"):
                try:
                    # Capturar salida de export_Ea
                    buffer = StringIO()
                    old_stdout = sys.stdout
                    sys.stdout = buffer
                    
                    ################################################################ función de picnik
                    st.session_state.ace.export_Ea()
                    
                    sys.stdout = old_stdout
                    output = buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Descargar resultados de energía",
                        data=output,
                        file_name="energia_activacion.csv",
                        mime="text/csv"
                    )
                    st.success("✅ Resultados exportados")
                except Exception as e:
                    st.error(f"❌ Error al exportar: {str(e)}")

# ==================== MÓDULO 6 ====================
elif module == "6. Predicción Model-free":
    st.header("🔮 Módulo 6: Predicción Model-free")
    
    if not st.session_state.calculated_energies:
        st.warning("⚠️ Primero debe calcular la energía de activación en el Módulo 5")
    else:
        st.subheader("⚡ Seleccionar energía de activación")
        
        selected_energy = st.selectbox(
            "Energía a utilizar:",
            list(st.session_state.calculated_energies.keys())
        )
        
        st.subheader("🌡️ Programa de temperatura")
        
        temp_program = st.selectbox(
            "Tipo de programa:",
            ["Isotérmico", "Calentamiento Lineal", "Programa Mixto"]
        )
        
        # === PROGRAMA ISOTÉRMICO ===
        if temp_program == "Isotérmico":
            st.subheader("🔥 Configuración Isotérmica")
            
            col1, col2 = st.columns(2)
            with col1:
                isoT = st.number_input("Temperatura isotérmica (K):", value=575.0, min_value=0.0)
            with col2:
                alpha_max = st.number_input("Conversión máxima:", value=0.999, min_value=0.1, max_value=1.0)
            
            if st.button("🔮 Calcular predicción isotérmica", type="primary"):
                try:
                    ################################################################ funciones de picnik
                    with st.spinner("Calculando predicción isotérmica..."):
                        energy_data = st.session_state.calculated_energies[selected_energy]
                        ap, Tp, tp = st.session_state.ace.modelfree_prediction(
                            energy_data[2], B=0, isoT=isoT, alpha=alpha_max, bounds=(10, 10)
                        )
                    
                    st.success("✅ Predicción isotérmica calculada")
                    
                    # Mostrar resultados
                    results_df = pd.DataFrame({
                        'Tiempo (min)': tp,
                        'Temperatura (K)': Tp,
                        'Conversión': ap
                    })
                    
                    st.subheader("📊 Resultados de la predicción")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Descargar predicción
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar predicción isotérmica",
                        data=csv_data,
                        file_name="prediccion_isotermica.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error en predicción isotérmica: {str(e)}")
        
        # === CALENTAMIENTO LINEAL ===
        elif temp_program == "Calentamiento Lineal":
            st.subheader("📈 Configuración Calentamiento Lineal")
            
            col1, col2 = st.columns(2)
            with col1:
                B_rate = st.number_input("Velocidad de calentamiento (K/min):", value=10.0, min_value=0.1)
            with col2:
                alpha_max = st.number_input("Conversión máxima:", value=0.999, min_value=0.1, max_value=1.0)
            
            if st.button("🔮 Calcular predicción lineal", type="primary"):
                try:
                    with st.spinner("Calculando predicción lineal..."):
                        energy_data = st.session_state.calculated_energies[selected_energy]
                        ################################################################ función de picnik
                        ap, Tp, tp = st.session_state.ace.modelfree_prediction(
                            energy_data[2], B=B_rate, alpha=alpha_max, bounds=(10, 10)
                        )
                    
                    st.success("✅ Predicción lineal calculada")
                    
                    # Mostrar resultados
                    results_df = pd.DataFrame({
                        'Tiempo (min)': tp,
                        'Temperatura (K)': Tp,
                        'Conversión': ap
                    })
                    
                    st.subheader("📊 Resultados de la predicción")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Descargar predicción
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar predicción lineal",
                        data=csv_data,
                        file_name="prediccion_lineal.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error en predicción lineal: {str(e)}")
        
        # === PROGRAMA MIXTO ===
        elif temp_program == "Programa Mixto":
            st.subheader("🔄 Configuración Programa Mixto")
            
            col1, col2 = st.columns(2)
            with col1:
                heating_rate = st.number_input("Velocidad de calentamiento (K/min):", value=5.0, min_value=0.1)
                temp_initial = st.number_input("Temperatura inicial (K):", value=298.0, min_value=0.0)
            with col2:
                temp_isothermal = st.number_input("Temperatura isotérmica (K):", value=575.0, min_value=0.0)
                alpha_max = st.number_input("Conversión máxima:", value=0.999, min_value=0.1, max_value=1.0)
            
            if st.button("🔮 Calcular predicción mixta", type="primary"):
                try:
                    with st.spinner("Calculando predicción mixta..."):
                        def temp_program_func(t):
                            """Función de programa de temperatura mixto"""
                            heating_time = (temp_isothermal - temp_initial) / heating_rate
                            return np.array([
                                (temp_initial + heating_rate * time) if time <= heating_time 
                                else temp_isothermal 
                                for time in t
                            ])
                        
                        energy_data = st.session_state.calculated_energies[selected_energy]
                        ################################################################ función de picnik
                        ap, Tp, tp = st.session_state.ace.modelfree_prediction(
                            energy_data[2], B=10, T_func=temp_program_func, 
                            alpha=alpha_max, bounds=(10, 10)
                        )
                    
                    st.success("✅ Predicción mixta calculada")
                    
                    # Mostrar resultados
                    results_df = pd.DataFrame({
                        'Tiempo (min)': tp,
                        'Temperatura (K)': Tp,
                        'Conversión': ap
                    })
                    
                    st.subheader("📊 Resultados de la predicción")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Descargar predicción
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar predicción mixta",
                        data=csv_data,
                        file_name="prediccion_mixta.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error en predicción mixta: {str(e)}")

# Footer
st.markdown("---")
st.markdown("🔬 **pICNIK App** - Análisis Isoconversional para Cinética Térmica")
st.markdown("Desarrollado con Streamlit y la librería pICNIK")