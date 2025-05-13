import networkx as nx
import osmnx as ox
import os
import pickle
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

class CityGraph:
    def __init__(self, country_name="Brazil"):
        self.country_name = country_name
        self.center_point = (-15.7797, -47.9297)
        self.graph = None
        self.nodes = None
        self.edges = None
        
    def load_or_download_map(self, force_download=False):
        """Carregar mapa do cache ou baixar do OpenStreetMap"""
        cache_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'data', 'brazil_railway_graph.pkl')
        
        if os.path.exists(cache_file) and not force_download:
            print("Carregando rede ferroviária do cache...")
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.nodes = data['nodes']
                self.edges = data['edges']
        else:
            # Se não existir mapa do OpenStreetMap, criar um mapa simplificado
            print(f"Criando rede ferroviária para {self.country_name}...")
            self.graph = nx.Graph()
            # Adicionar atributo CRS ao grafo (EPSG:4326 - WGS84)
            self.graph.graph['crs'] = 'epsg:4326'
            
            # Capitais com suas coordenadas (lat, lon)
            cities = {
                'São Paulo': (-23.5505, -46.6333),
                'Rio de Janeiro': (-22.9068, -43.1729),
                'Belo Horizonte': (-19.9167, -43.9345),
                'Brasília': (-15.7797, -47.9297),
                'Salvador': (-12.9714, -38.5014),
                'Recife': (-8.0539, -34.8811),
                'Fortaleza': (-3.7172, -38.5433),
                'Belém': (-1.4558, -48.5044),
                'Manaus': (-3.1190, -60.0217),
                'Porto Alegre': (-30.0368, -51.2090),
                'Curitiba': (-25.4290, -49.2671),
                'Campo Grande': (-20.4697, -54.6201),
                'Cuiabá': (-15.6014, -56.0979),
                'Porto Velho': (-8.7619, -63.9004),
                'Goiânia': (-16.6869, -49.2648),
                'Teresina': (-5.0920, -42.8019),
                'Natal': (-5.7945, -35.2094),
                'João Pessoa': (-7.1195, -34.8794),
                'Maceió': (-9.6658, -35.7353),
                'Aracaju': (-10.9472, -37.0731),
                'Vitória': (-20.2976, -40.2957),
                'Florianópolis': (-27.5969, -48.5495),
                'Rio Branco': (-9.9754, -67.8249),  
                'Boa Vista': (2.8235, -60.6758),    
                'São Luis': (-2.5391, -44.2829),    
                'Palmas': (-10.2491, -48.3243),     
                'Macapá': (0.0356, -51.0705)        
            }
            
            # Adicionar nós (cidades)
            node_id = 0
            city_nodes = {}
            node_data = []
            
            for city, coords in cities.items():
                # Adicionar atributos de nó correspondentes à estrutura do grafo OSM
                self.graph.add_node(node_id, 
                                    y=coords[0],  # latitude
                                    x=coords[1],  # longitude
                                    name=city)
                city_nodes[city] = node_id
                
                # Armazenar dados de nó para GeoDataFrame
                node_data.append({
                    'node_id': node_id,
                    'y': coords[0],
                    'x': coords[1],
                    'name': city,
                    'geometry': Point(coords[1], coords[0])  # Note: Point(lon, lat)
                })
                
                node_id += 1
            
            # Adicionar arestas (conexões ferroviárias) com base na imagem
            # Distâncias medidas em linha reta pelo https://www.distancefromto.net/
            railroad_connections = [
                ('São Paulo', 'Rio de Janeiro', 360),
                ('São Paulo', 'Belo Horizonte', 490),
                ('São Paulo', 'Curitiba', 338),
                ('São Paulo', 'Brasília', 874), 
                ('Rio de Janeiro', 'Vitória', 412),
                ('Rio de Janeiro', 'Belo Horizonte', 340),
                ('Belo Horizonte', 'Brasília', 624),
                ('Belo Horizonte', 'Salvador', 1159),
                ('Belo Horizonte', 'Vitória', 381), 
                ('Vitória', 'Salvador', 1044),
                ('Salvador', 'Aracaju', 106),
                ('Salvador', 'Fortaleza', 833), 
                ('Salvador', 'Palmas', 1134),
                ('Aracaju', 'Maceió', 201),
                ('Maceió', 'Recife', 202),
                ('Recife', 'João Pessoa', 104),
                ('João Pessoa', 'Natal', 151),
                ('Natal', 'Fortaleza', 435),
                ('Fortaleza', 'Teresina', 496),
                ('Teresina', 'São Luis', 329),
                ('Teresina', 'Palmas', 832),
                ('São Luis', 'Belém', 482),
                ('Belém', 'Macapá', 329),
                ('Belém', 'Palmas', 970),
                ('Brasília', 'Goiânia', 173),
                ('Goiânia', 'Campo Grande', 705),
                ('Palmas', 'Cuiabá', 1033),
                ('Palmas', 'Manaus', 1511),
                ('Cuiabá', 'Porto Velho', 1137),
                ('Cuiabá', 'Campo Grande', 560),
                ('Campo Grande', 'Curitiba', 780),
                ('Curitiba', 'Florianópolis', 251),
                ('Florianópolis', 'Porto Alegre', 375),
                ('Porto Velho', 'Manaus', 759),
                ('Porto Velho', 'Rio Branco', 450),
                ('Manaus', 'Macapá', 1055),
                ('Manaus', 'Boa Vista', 662),
                ('Brasília', 'Salvador', 1061),
                ('Brasília', 'Cuiabá', 874),
                ('Brasília', 'Palmas', 623),
            ]
            
            # Armazenar dados de aresta para GeoDataFrame
            edge_data = []
            
            # Adicionar arestas com atributos
            for city1, city2, distance in railroad_connections:
                if city1 in city_nodes and city2 in city_nodes:
                    node1 = city_nodes[city1]
                    node2 = city_nodes[city2]
                    
                    # Calculate travel time (assuming 80 km/h train speed)
                    speed_kmh = 80
                    travel_time = (distance / speed_kmh) * 60 * 60  # seconds
                    
                    # Edge attributes
                    edge_attrs = {
                        'length': distance * 1000,  # meters
                        'travel_time': travel_time,  # seconds
                        'name': f"Railroad {city1}-{city2}",
                        'highway': "railway"
                    }
                    
                    # Add edge to graph
                    self.graph.add_edge(node1, node2, **edge_attrs)
                    
                    # Armazenar dados de aresta para GeoDataFrame
                    edge_data.append({
                        'u': node1,
                        'v': node2,
                        **edge_attrs
                    })
            
            print(f"Rede ferroviária criada com {len(self.graph.nodes)} nós e {len(self.graph.edges)} arestas")
            
            # Criar GeoDataFrames diretamente
            self.nodes = gpd.GeoDataFrame(node_data, crs="EPSG:4326")
            self.nodes.set_index('node_id', inplace=True)
            
            # Criar GeoDataFrames diretamente
            self.edges = pd.DataFrame(edge_data)
            
            # Salvar no cache
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'nodes': self.nodes,
                    'edges': self.edges
                }, f)
        
        return self.graph
    
    def get_nearest_node(self, point):
        """Encontrar o nó mais próximo a um ponto (lat, lng)"""
        return ox.distance.nearest_nodes(self.graph, point[1], point[0])
    
    def run_dijkstra(self, source, target, weight='travel_time'):
        """Executar o algoritmo de Dijkstra entre os nós de origem e destino"""
        if self.graph is None:
            raise Exception("Grafo não Existe. Crie utilizando load_or_download_map() primeiro.")
            
        # Calcular o caminho mais curto usando o algoritmo de Dijkstra
        path = nx.shortest_path(self.graph, source, target, weight=weight)
        
        # Obter detalhes das arestas para o caminho
        edge_details = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = self.graph.get_edge_data(u, v)
            
            # Obter os nomes das cidades para melhores direções
            u_name = self.graph.nodes[u].get('name', 'Unknown')
            v_name = self.graph.nodes[v].get('name', 'Unknown')
            
            # Adicionar detalhes das arestas do caminho
            edge_details.append({
                'from': u,
                'to': v,
                'from_name': u_name,
                'to_name': v_name,
                'length': edge_data.get('length', 0),
                'travel_time': edge_data.get('travel_time', 0),
                'name': edge_data.get('name', f"Railroad {u_name}-{v_name}")
            })
            
        return {
            'path': path,
            'edge_details': edge_details,
            'total_distance': sum(edge['length'] for edge in edge_details),
            'total_time': sum(edge['travel_time'] for edge in edge_details)
        } 