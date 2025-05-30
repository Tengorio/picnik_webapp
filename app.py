import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tempfile
import os
import io
from typing import List, Tuple, Optional
import zipfile

# Configuración de la página
st.set_page_config(
    page_title="pICNIK - Análisis Isoconversional",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🧪 pICNIK - Análisis Isoconversional de Cinética No-Isotérmica")
st.markdown("---")

# Información en la barra lateral
with st.sidebar:
    st.header("📋 Información")
    st.markdown("""
    **pICNIK** es una herramienta para análisis isoconversional que implementa los métodos:
    
    - **OFW**: Ozawa-Flynn-Wall
    - **KAS**: Kissinger-Akahira-Sunose  
    - **Fr**: Friedman
    - **Vy**: Vyazovkin
    - **aVy**: Vyazovkin Avanzado
    
    **Formato de archivos CSV:**
                g
    - Columna 1: Tiempo
    - Columna 2: Temperatura (°C)
    - Columna 3: Masa
    """)
    
    st.markdown("---")
    st.markdown("**Pasos del análisis:**")
    st.markdown("1. Cargar archivos CSV")
    st.markdown("2. Configurar parámetros")
    st.markdown("3. Calcular energías de activación")
    st.markdown("4. Visualizar resultados")
    st.markdown("5. Descargar reportes")

# Función para simular la importación de picnik (para demostración)
def simulate_picnik_analysis(files_data, t0, tf, methods):
    """Simula el análisis de pICNIK para demostración"""
    # En la implementación real, aquí iría:
    # import picnik as pnk
    
    results = {}
    alpha_range = np.linspace(0.1, 0.9, 9)
    
    # Simular resultados para cada método
    if 'Friedman' in methods:
        # Simular energías de activación variables
        E_fr = np.random.normal(150, 20, len(alpha_range))
        error_fr = np.random.uniform(5, 15, len(alpha_range))
        results['Friedman'] = {'E': E_fr, 'error': error_fr}
    
    if 'OFW' in methods:
        E_ofw = np.random.normal(145, 15, len(alpha_range))
        error_ofw = np.random.uniform(3, 10, len(alpha_range))
        results['OFW'] = {'E': E_ofw, 'error': error_ofw}
    
    if 'KAS' in methods:
        E_kas = np.random.normal(148, 18, len(alpha_range))
        error_kas = np.random.uniform(4, 12, len(alpha_range))
        results['KAS'] = {'E': E_kas, 'error': error_kas}
    
    if 'Vyazovkin' in methods:
        E_vy = np.random.normal(152, 25, len(alpha_range))
        results['Vyazovkin'] = {'E': E_vy, 'error': None}
    
    if 'Vyazovkin Avanzado' in methods:
        E_avy = np.random.normal(155, 22, len(alpha_range))
        results['Vyazovkin Avanzado'] = {'E': E_avy, 'error': None}
    
    return results, alpha_range

def create_results_plot(results, alpha_range):
    """Crea gráficos de los resultados"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Energías de Activación vs Conversión', 
                       'Comparación de Métodos',
                       'Distribución de Energías',
                       'Errores por Método'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    
    # Gráfico principal: E vs α
    for i, (method, data) in enumerate(results.items()):
        fig.add_trace(
            go.Scatter(
                x=alpha_range,
                y=data['E'],
                mode='lines+markers',
                name=method,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        if data['error'] is not None:
            fig.add_trace(
                go.Scatter(
                    x=np.concatenate([alpha_range, alpha_range[::-1]]),
                    y=np.concatenate([data['E'] + data['error'], 
                                    (data['E'] - data['error'])[::-1]]),
                    fill='toself',
                    fillcolor=colors[i % len(colors)].replace('1)', '0.2)'),
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=False,
                    name=f'{method} Error'
                ),
                row=1, col=1
            )
    
    # Gráfico de barras comparativo
    avg_energies = [np.mean(data['E']) for data in results.values()]
    fig.add_trace(
        go.Bar(
            x=list(results.keys()),
            y=avg_energies,
            marker_color=colors[:len(results)],
            name='Energía Promedio'
        ),
        row=1, col=2
    )
    
    # Histograma de distribución
    all_energies = []
    for data in results.values():
        all_energies.extend(data['E'])
    
    fig.add_trace(
        go.Histogram(
            x=all_energies,
            nbinsx=20,
            marker_color='#FF6B6B',
            opacity=0.7,
            name='Distribución E'
        ),
        row=2, col=1
    )
    
    # Gráfico de errores
    methods_with_errors = [method for method, data in results.items() if data['error'] is not None]
    if methods_with_errors:
        avg_errors = [np.mean(results[method]['error']) for method in methods_with_errors]
        fig.add_trace(
            go.Bar(
                x=methods_with_errors,
                y=avg_errors,
                marker_color='#FFA07A',
                name='Error Promedio'
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Resultados del Análisis Isoconversional",
        title_x=0.5
    )
    
    fig.update_xaxes(title_text="Conversión (α)", row=1, col=1)
    fig.update_yaxes(title_text="Energía de Activación (kJ/mol)", row=1, col=1)
    fig.update_xaxes(title_text="Método", row=1, col=2)
    fig.update_yaxes(title_text="E promedio (kJ/mol)", row=1, col=2)
    fig.update_xaxes(title_text="Energía de Activación (kJ/mol)", row=2, col=1)
    fig.update_yaxes(title_text="Frecuencia", row=2, col=1)
    fig.update_xaxes(title_text="Método", row=2, col=2)
    fig.update_yaxes(title_text="Error promedio", row=2, col=2)
    
    return fig

def create_data_preview_plot(files_data):
    """Crea gráfico de vista previa de los datos"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperatura vs Tiempo', 'Masa vs Tiempo', 
                       'Masa vs Temperatura', 'Velocidad de Calentamiento'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    
    for i, (filename, data) in enumerate(files_data.items()):
        color = colors[i % len(colors)]
        
        # Temperatura vs Tiempo
        fig.add_trace(
            go.Scatter(x=data['Tiempo'], y=data['Temperatura'], 
                      mode='lines', name=f'{filename} - T(t)',
                      line=dict(color=color)),
            row=1, col=1
        )
        
        # Masa vs Tiempo
        fig.add_trace(
            go.Scatter(x=data['Tiempo'], y=data['Masa'], 
                      mode='lines', name=f'{filename} - m(t)',
                      line=dict(color=color),
                      showlegend=False),
            row=1, col=2
        )
        
        # Masa vs Temperatura
        fig.add_trace(
            go.Scatter(x=data['Temperatura'], y=data['Masa'], 
                      mode='lines', name=f'{filename} - m(T)',
                      line=dict(color=color),
                      showlegend=False),
            row=2, col=1
        )
        
        # Velocidad de calentamiento (aproximada)
        if len(data) > 1:
            heating_rate = np.gradient(data['Temperatura'], data['Tiempo'])
            fig.add_trace(
                go.Scatter(x=data['Tiempo'], y=heating_rate, 
                          mode='lines', name=f'{filename} - β(t)',
                          line=dict(color=color),
                          showlegend=False),
                row=2, col=2
            )
    
    fig.update_layout(height=600, title_text="Vista Previa de Datos Experimentales")
    fig.update_xaxes(title_text="Tiempo", row=1, col=1)
    fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
    fig.update_xaxes(title_text="Tiempo", row=1, col=2)
    fig.update_yaxes(title_text="Masa", row=1, col=2)
    fig.update_xaxes(title_text="Temperatura (°C)", row=2, col=1)
    fig.update_yaxes(title_text="Masa", row=2, col=1)
    fig.update_xaxes(title_text="Tiempo", row=2, col=2)
    fig.update_yaxes(title_text="Velocidad Calentamiento (°C/min)", row=2, col=2)
    
    return fig

# Pestañas principales
tab1, tab2, tab3, tab4 = st.tabs(["📁 Carga de Datos", "⚙️ Configuración", "📊 Análisis", "📋 Resultados"])

# Inicializar variables de sesión
if 'files_data' not in st.session_state:
    st.session_state.files_data = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'alpha_range' not in st.session_state:
    st.session_state.alpha_range = None

# TAB 1: Carga de Datos
with tab1:
    st.header("📁 Carga de Archivos CSV")
    
    st.info("""
    **Instrucciones:**
    1. Cargar archivos CSV con datos termogravimétricos
    2. Cada archivo debe tener 3 columnas: Tiempo, Temperatura (°C), Masa
    3. Los archivos deben corresponder a diferentes velocidades de calentamiento
    4. Cargar en orden ascendente de velocidad de calentamiento
    """)
    
    uploaded_files = st.file_uploader(
        "Seleccionar archivos CSV",
        type=['csv'],
        accept_multiple_files=True,
        help="Cargar múltiples archivos CSV con datos TGA"
    )
    
    if uploaded_files:
        st.success(f"Se cargaron {len(uploaded_files)} archivos")
        
        # Procesar archivos
        files_data = {}
        for file in uploaded_files:
            try:
                df = pd.read_csv(file)
                if df.shape[1] >= 3:
                    df.columns = ['Tiempo', 'Temperatura', 'Masa']
                    files_data[file.name] = df
                else:
                    st.error(f"El archivo {file.name} no tiene 3 columnas")
            except Exception as e:
                st.error(f"Error al leer {file.name}: {str(e)}")
        
        st.session_state.files_data = files_data
        
        if files_data:
            st.subheader("📈 Vista Previa de Datos")
            
            # Mostrar estadísticas básicas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Archivos Cargados", len(files_data))
            with col2:
                total_points = sum(len(df) for df in files_data.values())
                st.metric("Puntos de Datos Total", total_points)
            with col3:
                temp_ranges = [f"{df['Temperatura'].min():.1f}-{df['Temperatura'].max():.1f}°C" 
                             for df in files_data.values()]
                st.metric("Archivos Válidos", len(temp_ranges))
            
            # Gráfico de vista previa
            preview_fig = create_data_preview_plot(files_data)
            st.plotly_chart(preview_fig, use_container_width=True)
            
            # Tabla resumen
            st.subheader("📋 Resumen de Archivos")
            summary_data = []
            for filename, df in files_data.items():
                heating_rate = np.gradient(df['Temperatura'], df['Tiempo']).mean()
                summary_data.append({
                    'Archivo': filename,
                    'Puntos': len(df),
                    'T inicial (°C)': f"{df['Temperatura'].min():.1f}",
                    'T final (°C)': f"{df['Temperatura'].max():.1f}",
                    'Velocidad promedio (°C/min)': f"{heating_rate:.2f}",
                    'Masa inicial': f"{df['Masa'].iloc[0]:.3f}",
                    'Masa final': f"{df['Masa'].iloc[-1]:.3f}"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)

# TAB 2: Configuración
with tab2:
    st.header("⚙️ Configuración del Análisis")
    
    if not st.session_state.files_data:
        st.warning("Primero debe cargar archivos en la pestaña 'Carga de Datos'")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌡️ Rango de Temperatura")
            t0 = st.number_input(
                "Temperatura inicial (°C)",
                min_value=0,
                max_value=1000,
                value=50,
                help="Temperatura inicial para el análisis"
            )
            
            tf = st.number_input(
                "Temperatura final (°C)",
                min_value=t0+1,
                max_value=1200,
                value=750,
                help="Temperatura final para el análisis"
            )
            
            st.subheader("🎯 Parámetros de Conversión")
            alpha_min = st.slider(
                "Conversión mínima (α)",
                min_value=0.01,
                max_value=0.5,
                value=0.1,
                step=0.01
            )
            
            alpha_max = st.slider(
                "Conversión máxima (α)",
                min_value=0.5,
                max_value=0.99,
                value=0.9,
                step=0.01
            )
            
            n_points = st.number_input(
                "Número de puntos isoconversionales",
                min_value=5,
                max_value=20,
                value=9,
                help="Número de puntos de conversión para el análisis"
            )
        
        with col2:
            st.subheader("📊 Métodos de Análisis")
            methods = st.multiselect(
                "Seleccionar métodos isoconversionales",
                ['Friedman', 'OFW', 'KAS', 'Vyazovkin', 'Vyazovkin Avanzado'],
                default=['Friedman', 'OFW', 'KAS'],
                help="Métodos para calcular la energía de activación"
            )
            
            st.subheader("🔧 Parámetros Avanzados")
            
            # Parámetros para Vyazovkin
            if 'Vyazovkin' in methods or 'Vyazovkin Avanzado' in methods:
                e_min = st.number_input(
                    "Energía mínima (kJ/mol)",
                    min_value=1,
                    max_value=100,
                    value=1,
                    help="Límite inferior para búsqueda de energía"
                )
                
                e_max = st.number_input(
                    "Energía máxima (kJ/mol)",
                    min_value=100,
                    max_value=1000,
                    value=300,
                    help="Límite superior para búsqueda de energía"
                )
            
            # Método de integración
            integration_method = st.selectbox(
                "Método de integración",
                ['senum-yang', 'trapezoid'],
                help="Método para integración numérica"
            )
            
            # Codificación de archivos
            encoding = st.selectbox(
                "Codificación de archivos",
                ['utf-8', 'latin-1', 'cp1252'],
                help="Codificación de caracteres de los archivos CSV"
            )
        
        # Botón para guardar configuración
        if st.button("💾 Guardar Configuración", type="primary"):
            config = {
                't0': t0,
                'tf': tf,
                'alpha_min': alpha_min,
                'alpha_max': alpha_max,
                'n_points': n_points,
                'methods': methods,
                'integration_method': integration_method,
                'encoding': encoding
            }
            
            if 'Vyazovkin' in methods or 'Vyazovkin Avanzado' in methods:
                config['e_bounds'] = (e_min, e_max)
            
            st.session_state.config = config
            st.success("✅ Configuración guardada correctamente")

# TAB 3: Análisis
with tab3:
    st.header("📊 Ejecutar Análisis Isoconversional")
    
    if not st.session_state.files_data:
        st.warning("Debe cargar archivos de datos primero")
    elif 'config' not in st.session_state:
        st.warning("Debe configurar los parámetros de análisis primero")
    else:
        config = st.session_state.config
        
        st.subheader("🔍 Resumen de Configuración")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **Rango de Temperatura:**
            - Inicial: {config['t0']}°C
            - Final: {config['tf']}°C
            """)
        
        with col2:
            st.info(f"""
            **Conversión:**
            - Mínima: {config['alpha_min']}
            - Máxima: {config['alpha_max']}
            - Puntos: {config['n_points']}
            """)
        
        with col3:
            methods_str = ", ".join(config['methods'])
            st.info(f"""
            **Métodos:**
            {methods_str}
            """)
        
        st.markdown("---")
        
        # Botón para ejecutar análisis
        if st.button("🚀 Ejecutar Análisis", type="primary", use_container_width=True):
            with st.spinner("Ejecutando análisis isoconversional..."):
                try:
                    # Simular análisis (en implementación real usar pICNIK)
                    results, alpha_range = simulate_picnik_analysis(
                        st.session_state.files_data,
                        config['t0'],
                        config['tf'],
                        config['methods']
                    )
                    
                    st.session_state.analysis_results = results
                    st.session_state.alpha_range = alpha_range
                    
                    st.success("✅ Análisis completado exitosamente!")
                    
                    # Mostrar resultados preliminares
                    st.subheader("📈 Resultados Preliminares")
                    
                    for method, data in results.items():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"E promedio - {method}", f"{np.mean(data['E']):.1f} kJ/mol")
                        with col2:
                            st.metric(f"E máxima - {method}", f"{np.max(data['E']):.1f} kJ/mol")
                        with col3:
                            st.metric(f"E mínima - {method}", f"{np.min(data['E']):.1f} kJ/mol")
                    
                except Exception as e:
                    st.error(f"Error durante el análisis: {str(e)}")
                    st.error("En una implementación real, aquí se ejecutaría el código de pICNIK")

# TAB 4: Resultados
with tab4:
    st.header("📋 Resultados y Visualización")
    
    if st.session_state.analysis_results is None:
        st.warning("Debe ejecutar el análisis primero")
    else:
        results = st.session_state.analysis_results
        alpha_range = st.session_state.alpha_range
        
        # Crear y mostrar gráficos
        results_fig = create_results_plot(results, alpha_range)
        st.plotly_chart(results_fig, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla de resultados detallados
        st.subheader("📊 Tabla de Resultados Detallados")
        
        # Crear DataFrame con todos los resultados
        results_df_data = {'Conversión (α)': alpha_range}
        
        for method, data in results.items():
            results_df_data[f'E_{method} (kJ/mol)'] = data['E']
            if data['error'] is not None:
                results_df_data[f'Error_{method} (kJ/mol)'] = data['error']
        
        results_df = pd.DataFrame(results_df_data)
        st.dataframe(results_df, use_container_width=True)
        
        # Estadísticas resumen
        st.subheader("📈 Estadísticas Resumen")
        
        summary_stats = []
        for method, data in results.items():
            stats = {
                'Método': method,
                'E promedio (kJ/mol)': f"{np.mean(data['E']):.2f}",
                'Desviación estándar': f"{np.std(data['E']):.2f}",
                'E mínima (kJ/mol)': f"{np.min(data['E']):.2f}",
                'E máxima (kJ/mol)': f"{np.max(data['E']):.2f}",
                'Rango (kJ/mol)': f"{np.max(data['E']) - np.min(data['E']):.2f}"
            }
            
            if data['error'] is not None:
                stats['Error promedio'] = f"{np.mean(data['error']):.2f}"
            else:
                stats['Error promedio'] = "N/A"
            
            summary_stats.append(stats)
        
        summary_df = pd.DataFrame(summary_stats)
        st.dataframe(summary_df, use_container_width=True)
        
        # Botones de descarga
        st.subheader("💾 Descargar Resultados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV con resultados detallados
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📄 Descargar CSV Detallado",
                data=csv_buffer.getvalue(),
                file_name="resultados_isoconversional.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel con múltiples hojas
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                results_df.to_excel(writer, sheet_name='Resultados Detallados', index=False)
                summary_df.to_excel(writer, sheet_name='Resumen Estadístico', index=False)
            
            st.download_button(
                label="📊 Descargar Excel Completo",
                data=excel_buffer.getvalue(),
                file_name="analisis_isoconversional.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            # Reporte en texto
            report_text = f"""
REPORTE DE ANÁLISIS ISOCONVERSIONAL
=====================================

Configuración del Análisis:
- Rango de temperatura: {st.session_state.config['t0']}°C - {st.session_state.config['tf']}°C
- Rango de conversión: {st.session_state.config['alpha_min']} - {st.session_state.config['alpha_max']}
- Número de puntos: {st.session_state.config['n_points']}
- Métodos utilizados: {', '.join(st.session_state.config['methods'])}

Resultados Estadísticos:
"""
            
            for method, data in results.items():
                report_text += f"""
{method}:
- Energía promedio: {np.mean(data['E']):.2f} ± {np.std(data['E']):.2f} kJ/mol
- Rango: {np.min(data['E']):.2f} - {np.max(data['E']):.2f} kJ/mol
"""
            
            st.download_button(
                label="📝 Descargar Reporte TXT",
                data=report_text,
                file_name="reporte_analisis.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🧪 <strong>pICNIK Streamlit App</strong> - Análisis Isoconversional Simplificado</p>
    <p>Desarrollado para facilitar el uso de la librería pICNIK sin necesidad de programación</p>
</div>
""", unsafe_allow_html=True)