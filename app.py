from flask import Flask, render_template, request, jsonify
import requests
import xml.etree.ElementTree as ET
import threading
import time
from datetime import datetime
from typing import List, Dict
import urllib3

# Desabilita warnings de SSL não verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

XML_URL = 'https://alertadecheias.inea.rj.gov.br/alertadecheias/dados.xml'
data: List[Dict] = []
last_update: datetime = None
lock = threading.Lock()

def parse_xml(xml_content: str) -> List[Dict]:
    """Parse o XML e retorna uma lista de dicionários com os dados das estações"""
    try:
        root = ET.fromstring(xml_content)
        stations = []
        
        for estacao in root.findall('.//ESTACAO'):
            station_data = {
                'id': estacao.find('ID').text if estacao.find('ID') is not None else '',
                'nome_estacao': estacao.find('NOME_DA_ESTACAO').text if estacao.find('NOME_DA_ESTACAO') is not None else '',
                'nome_rio': estacao.find('NOME_RIO').text if estacao.find('NOME_RIO') is not None else '',
                'horario': estacao.find('HORARIO').text if estacao.find('HORARIO') is not None else '',
                'chuva_ultima': estacao.find('CHUVA_ULTIMA').text if estacao.find('CHUVA_ULTIMA') is not None else '0',
                'chuva_1h': estacao.find('CHUVA_1H').text if estacao.find('CHUVA_1H') is not None else '0',
                'chuva_4h': estacao.find('CHUVA_4H').text if estacao.find('CHUVA_4H') is not None else '0',
                'chuva_24h': estacao.find('CHUVA_24H').text if estacao.find('CHUVA_24H') is not None else '0',
                'chuva_96h': estacao.find('CHUVA_96H').text if estacao.find('CHUVA_96H') is not None else '0',
                'nivel_ultimo': estacao.find('NIVEL_ULTIMO').text if estacao.find('NIVEL_ULTIMO') is not None else '0',
                'nivel_15': estacao.find('NIVEL_15').text if estacao.find('NIVEL_15') is not None else '0',
                'nivel_30': estacao.find('NIVEL_30').text if estacao.find('NIVEL_30') is not None else '0',
                'nivel_45': estacao.find('NIVEL_45').text if estacao.find('NIVEL_45') is not None else '0',
                'latitude': estacao.find('LATITUDE').text if estacao.find('LATITUDE') is not None else '',
                'longitude': estacao.find('LONGITUDE').text if estacao.find('LONGITUDE') is not None else '',
                'municipio': estacao.find('MUNICIPIO').text if estacao.find('MUNICIPIO') is not None else '',
            }
            stations.append(station_data)
        
        return stations
    except Exception as e:
        print(f"Erro ao fazer parse do XML: {e}")
        return []

def fetch_data():
    """Busca os dados do XML e atualiza a variável global data"""
    global data, last_update
    
    while True:
        try:
            # Desabilita verificação SSL para contornar problemas de certificado
            response = requests.get(XML_URL, timeout=10, verify=False)
            if response.status_code == 200:
                new_data = parse_xml(response.content)
                with lock:
                    data = new_data
                    last_update = datetime.now()
                print(f"Dados atualizados às {last_update.strftime('%H:%M:%S')} - {len(data)} estações")
            else:
                print(f"Erro ao buscar XML: Status {response.status_code}")
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
        
        # Aguarda 5 minutos (300 segundos)
        time.sleep(300)

@app.route('/')
def index():
    """Página principal com tabela e filtro"""
    cidade_filtro = request.args.get('cidade', '').strip()
    
    with lock:
        current_data = data.copy()
        current_update = last_update
    
    # Filtra por cidade (município) se fornecido
    if cidade_filtro:
        filtered_data = [
            d for d in current_data 
            if cidade_filtro.lower() in d['municipio'].lower().replace('_', ' ')
        ]
    else:
        filtered_data = current_data
    
    # Obtém lista única de municípios para o select
    municipios = sorted(set(
        d['municipio'].replace('_', ' ') for d in current_data if d['municipio']
    ))
    
    update_time = current_update.strftime('%d/%m/%Y %H:%M:%S') if current_update else 'Nunca'
    
    # Prepara dados para o mapa (todos os dados, não apenas filtrados)
    # Mas filtra se houver filtro de cidade
    map_data = filtered_data if cidade_filtro else current_data
    
    return render_template(
        'index.html', 
        data=filtered_data, 
        map_data=map_data,  # Dados para o mapa
        municipios=municipios,
        cidade_filtro=cidade_filtro,
        update_time=update_time,
        total_estacoes=len(current_data)
    )

@app.route('/api/data')
def api_data():
    """API endpoint para retornar dados em JSON"""
    cidade_filtro = request.args.get('cidade', '').strip()
    
    with lock:
        current_data = data.copy()
        current_update = last_update
    
    if cidade_filtro:
        filtered_data = [
            d for d in current_data 
            if cidade_filtro.lower() in d['municipio'].lower().replace('_', ' ')
        ]
    else:
        filtered_data = current_data
    
    return jsonify({
        'data': filtered_data,
        'last_update': current_update.isoformat() if current_update else None,
        'total': len(filtered_data)
    })

def fetch_initial_data():
    """Busca dados iniciais antes de iniciar o servidor"""
    global data, last_update
    
    print("Iniciando busca inicial de dados...")
    try:
        response = requests.get(XML_URL, timeout=10, verify=False)
        if response.status_code == 200:
            new_data = parse_xml(response.content)
            with lock:
                data = new_data
                last_update = datetime.now()
            print(f"Dados iniciais carregados - {len(data)} estações encontradas")
        else:
            print(f"Erro ao buscar XML inicial: Status {response.status_code}")
    except Exception as e:
        print(f"Erro ao buscar dados iniciais: {e}")

if __name__ == '__main__':
    # Busca dados iniciais antes de iniciar o servidor
    fetch_initial_data()
    
    # Inicia thread para atualização periódica
    fetch_data_thread = threading.Thread(target=fetch_data, daemon=True)
    fetch_data_thread.start()
    
    print("Servidor Flask iniciando...")
    app.run(debug=True, host='0.0.0.0', port=4001)

