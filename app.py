from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import os
import json

app = Flask(__name__)
app.secret_key = 'medicare_ai_secret_key_2024'

class MediCareAI:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect('medicare.db')
        c = conn.cursor()
        
        # Tabla de usuarios
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nombre TEXT NOT NULL,
                     edad INTEGER,
                     condiciones_medicas TEXT,
                     alergias TEXT,
                     fecha_registro DATE)''')
        
        # Tabla de medicamentos
        c.execute('''CREATE TABLE IF NOT EXISTS medicamentos
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     usuario_id INTEGER,
                     nombre TEXT NOT NULL,
                     dosis TEXT,
                     horarios TEXT,
                     fecha_inicio DATE,
                     fecha_fin DATE,
                     FOREIGN KEY (usuario_id) REFERENCES usuarios (id))''')
        
        # Tabla de consultas
        c.execute('''CREATE TABLE IF NOT EXISTS consultas
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     usuario_id INTEGER,
                     sintomas TEXT,
                     respuesta_ia TEXT,
                     fecha_consulta DATETIME,
                     urgencia TEXT,
                     FOREIGN KEY (usuario_id) REFERENCES usuarios (id))''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    
    def generar_respuesta_medica(self, sintomas, historial=None):
        """Generar respuesta médica usando IA (simulada por ahora)"""
        
        # Simulación de IA - Respuestas inteligentes basadas en palabras clave
        respuestas_base = {
            "dolor de cabeza": {
                "respuesta": "El dolor de cabeza puede tener múltiples causas. Te recomiendo: 1) Descansar en un lugar tranquilo y oscuro, 2) Aplicar compresas frías en la frente, 3) Mantenerte bien hidratado, 4) Evitar ruidos fuertes. Si el dolor persiste más de 24 horas o es muy intenso, consulta a un médico.",
                "urgencia": "baja"
            },
            "fiebre": {
                "respuesta": "La fiebre es una respuesta natural del cuerpo a infecciones. Recomendaciones: 1) Mantente bien hidratado con líquidos, 2) Descansa en cama, 3) Usa ropa ligera, 4) Aplica compresas tibias si es necesario. Si la fiebre supera 38.5°C o dura más de 3 días, busca atención médica.",
                "urgencia": "media"
            },
            "dolor de pecho": {
                "respuesta": "⚠️ El dolor de pecho puede ser serio y requiere atención médica inmediata. Por favor: 1) Busca atención médica urgente AHORA, 2) No conduzcas, pide que te lleven al hospital, 3) Mantente calmado, 4) Si tienes medicamentos cardíacos prescritos, tómalos según las indicaciones de tu médico.",
                "urgencia": "alta"
            },
            "mareo": {
                "respuesta": "Los mareos pueden ser causados por varias razones. Te sugiero: 1) Siéntate o acuéstate inmediatamente, 2) Mantente hidratado, 3) Evita movimientos bruscos, 4) Verifica si has comido recientemente. Si los mareos son frecuentes o severos, consulta con tu médico.",
                "urgencia": "baja"
            },
            "dificultad respirar": {
                "respuesta": "⚠️ La dificultad para respirar puede ser seria. Acciones inmediatas: 1) Busca atención médica urgente, 2) Siéntate en posición erguida, 3) Mantente calmado, 4) Si tienes inhalador, úsalo según prescripción. No esperes, busca ayuda médica ahora.",
                "urgencia": "alta"
            }
        }
        
        # Buscar síntomas clave en el texto
        sintomas_lower = sintomas.lower()
        for clave, info in respuestas_base.items():
            if clave in sintomas_lower:
                return info
        
        # Respuesta por defecto para síntomas no específicos
        return {
            "respuesta": f"Gracias por consultarme sobre: '{sintomas}'. Basándome en lo que describes, te recomiendo: 1) Monitorear cuidadosamente tu estado, 2) Descansar adecuadamente, 3) Mantener una buena hidratación, 4) Anotar cualquier cambio en los síntomas. Si los síntomas empeoran, persisten por más de 24 horas, o te causan preocupación, no dudes en consultar con un profesional médico. Recuerda que esta es una orientación general y no reemplaza el diagnóstico médico profesional.",
            "urgencia": "baja"
        }
    
    def agregar_medicamento(self, usuario_id, nombre, dosis, horarios):
        """Agregar medicamento al sistema"""
        conn = sqlite3.connect('medicare.db')
        c = conn.cursor()
        c.execute("INSERT INTO medicamentos (usuario_id, nombre, dosis, horarios, fecha_inicio) VALUES (?, ?, ?, ?, ?)",
                 (usuario_id, nombre, dosis, json.dumps(horarios), datetime.now().date()))
        conn.commit()
        conn.close()
        print(f"✅ Medicamento '{nombre}' agregado correctamente")
    
    def obtener_medicamentos(self, usuario_id):
        """Obtener medicamentos del usuario"""
        conn = sqlite3.connect('medicare.db')
        c = conn.cursor()
        c.execute("SELECT * FROM medicamentos WHERE usuario_id = ?", (usuario_id,))
        medicamentos = c.fetchall()
        conn.close()
        return medicamentos

# Instancia global
medicare_ai = MediCareAI()

@app.route('/')
def index():
    """Página principal"""
    print("📱 Acceso a página principal")
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Página de chat médico"""
    print("💬 Acceso a chat médico")
    return render_template('chat.html')

@app.route('/medicamentos')
def medicamentos():
    """Página de gestión de medicamentos"""
    print("💊 Acceso a gestión de medicamentos")
    return render_template('medicamentos.html')

@app.route('/historial')
def historial():
    """Página de historial médico"""
    print("📋 Acceso a historial médico")
    return render_template('historial.html')

@app.route('/api/consulta', methods=['POST'])
def consulta_medica():
    """API para consultas médicas con IA"""
    try:
        data = request.get_json()
        sintomas = data.get('sintomas', '')
        
        if not sintomas:
            return jsonify({'error': 'No se proporcionaron síntomas'}), 400
        
        print(f"🔍 Analizando síntomas: {sintomas}")
        
        # Generar respuesta con IA
        respuesta = medicare_ai.generar_respuesta_medica(sintomas)
        
        # Guardar consulta en base de datos
        conn = sqlite3.connect('medicare.db')
        c = conn.cursor()
        c.execute("INSERT INTO consultas (usuario_id, sintomas, respuesta_ia, fecha_consulta, urgencia) VALUES (?, ?, ?, ?, ?)",
                 (1, sintomas, respuesta['respuesta'], datetime.now(), respuesta['urgencia']))
        conn.commit()
        conn.close()
        
        print(f"✅ Consulta procesada - Urgencia: {respuesta['urgencia']}")
        
        return jsonify(respuesta)
        
    except Exception as e:
        print(f"❌ Error en consulta: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/medicamentos', methods=['POST'])
def agregar_medicamento_api():
    """API para agregar medicamentos"""
    try:
        data = request.get_json()
        
        medicare_ai.agregar_medicamento(
            usuario_id=1,
            nombre=data.get('nombre'),
            dosis=data.get('dosis'),
            horarios=data.get('horarios', [])
        )
        
        return jsonify({'status': 'success', 'message': 'Medicamento agregado correctamente'})
        
    except Exception as e:
        print(f"❌ Error agregando medicamento: {str(e)}")
        return jsonify({'error': 'Error al agregar medicamento'}), 500

@app.route('/api/recordatorios')
def obtener_recordatorios():
    """API para obtener recordatorios de medicamentos"""
    try:
        medicamentos = medicare_ai.obtener_medicamentos(usuario_id=1)
        
        recordatorios = []
        for med in medicamentos:
            horarios = json.loads(med[4]) if med[4] else []
            for horario in horarios:
                recordatorios.append({
                    'medicamento': med[2],
                    'dosis': med[3],
                    'hora': horario,
                    'id': med[0]
                })
        
        return jsonify(recordatorios)
        
    except Exception as e:
        print(f"❌ Error obteniendo recordatorios: {str(e)}")
        return jsonify({'error': 'Error al obtener recordatorios'}), 500

@app.route('/api/generar_reporte', methods=['POST'])
def generar_reporte():
    """API para generar reporte médico con IA"""
    try:
        data = request.get_json()
        periodo = data.get('periodo', '30')
        
        # Obtener historial del periodo
        conn = sqlite3.connect('medicare.db')
        c = conn.cursor()
        fecha_limite = datetime.now() - timedelta(days=int(periodo))
        c.execute("SELECT * FROM consultas WHERE usuario_id = ? AND fecha_consulta > ?", (1, fecha_limite))
        consultas = c.fetchall()
        conn.close()
        
        # Generar reporte con IA (simulado)
        if consultas:
            sintomas_frecuentes = [c[2] for c in consultas[:5]]  # Top 5
            consultas_urgentes = len([c for c in consultas if c[5] == 'alta'])
            
            reporte = f"""
REPORTE MÉDICO GENERADO POR IA
===============================
Período: Últimos {periodo} días
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Paciente: Usuario Demo

RESUMEN DE ACTIVIDAD:
• Total de consultas realizadas: {len(consultas)}
• Consultas de urgencia alta: {consultas_urgentes}
• Consultas de seguimiento regular: {len(consultas) - consultas_urgentes}

SÍNTOMAS MÁS CONSULTADOS:
{chr(10).join([f"• {sintoma[:50]}..." if len(sintoma) > 50 else f"• {sintoma}" for sintoma in sintomas_frecuentes[:3]])}

RECOMENDACIONES GENERALES:
1. Mantener seguimiento médico regular con su doctor de cabecera
2. Continuar con los medicamentos prescritos según indicaciones
3. Monitorear los síntomas recurrentes y reportar cambios
4. Mantener hábitos saludables de alimentación y ejercicio

PRÓXIMOS PASOS SUGERIDOS:
• Agendar cita de control con médico primario
• Revisar medicamentos actuales con farmacéutico
• Considerar evaluación especializada si síntomas persisten

NOTA IMPORTANTE: Este reporte es generado por Inteligencia Artificial y 
debe ser complementado con evaluación médica profesional. No reemplaza 
el criterio clínico de un profesional de la salud.

Generado por MediCare AI v1.0
            """
        else:
            reporte = f"""
REPORTE MÉDICO - PERÍODO SIN ACTIVIDAD
======================================
Período: Últimos {periodo} días
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

No se registraron consultas médicas en el período seleccionado.

RECOMENDACIONES:
• Recuerde que puede usar MediCare AI cuando tenga dudas sobre su salud
• Mantenga sus controles médicos regulares
• Registre sus medicamentos para mejores recordatorios

¡Su bienestar es nuestra prioridad!
            """
        
        return jsonify({'reporte': reporte})
        
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        return jsonify({'error': 'Error al generar reporte'}), 500

# Ruta de prueba para verificar que todo funciona
@app.route('/test')
def test():
    """Ruta de prueba"""
    return jsonify({
        'status': 'success', 
        'message': '🎉 MediCare AI funcionando correctamente!',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando MediCare AI...")
    print("📝 Configurando base de datos...")
    print("✅ ¡Aplicación lista!")
    print("🌐 Accede a: http://localhost:5000")
    app.run(debug=True, port=5000)