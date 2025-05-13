import pandas as pd
import os

class NavigationUI:
    def __init__(self, city_graph):
        self.city_graph = city_graph
        self.landmarks = None
    
    def load_or_create_landmarks(self):
        """Carrega ou cria marcadores para seleção mais fácil do usuário"""
        landmarks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'data', 'landmarks.csv')
        
        if os.path.exists(landmarks_file):
            self.landmarks = pd.read_csv(landmarks_file)
        else:
            self.landmarks = pd.DataFrame({
                'name': [
                    'São Paulo',
                    'Rio de Janeiro',
                    'Belo Horizonte',
                    'Brasília',
                    'Salvador',
                    'Recife',
                    'Fortaleza',
                    'Belém',
                    'Manaus',
                    'Porto Alegre',
                    'Curitiba',
                    'Campo Grande',
                    'Cuiabá',
                    'Porto Velho',
                    'Goiânia',
                    'Teresina',
                    'Natal',
                    'João Pessoa',
                    'Maceió',
                    'Aracaju',
                    'Vitória',
                    'Florianópolis',
                    'Rio Branco',
                    'Boa Vista',
                    'São Luis',
                    'Palmas',
                    'Macapá'
                ],
                'latitude': [
                    -23.5505, # São Paulo
                    -22.9068, # Rio de Janeiro
                    -19.9167, # Belo Horizonte
                    -15.7797, # Brasília
                    -12.9714, # Salvador
                    -8.0539,  # Recife
                    -3.7172,  # Fortaleza
                    -1.4558,  # Belém
                    -3.1190,  # Manaus
                    -30.0368, # Porto Alegre
                    -25.4290, # Curitiba
                    -20.4697, # Campo Grande
                    -15.6014, # Cuiabá
                    -8.7619,  # Porto Velho
                    -16.6869, # Goiânia
                    -5.0920,  # Teresina
                    -5.7945,  # Natal
                    -7.1195,  # João Pessoa
                    -9.6658,  # Maceió
                    -10.9472, # Aracaju
                    -20.2976, # Vitória
                    -27.5969, # Florianópolis
                    -9.9754,  # Rio Branco
                    2.8235,   # Boa Vista
                    -2.5391,  # São Luis
                    -10.2491, # Palmas
                    0.0356    # Macapá
                ],
                'longitude': [
                    -46.6333, # São Paulo
                    -43.1729, # Rio de Janeiro
                    -43.9345, # Belo Horizonte
                    -47.9297, # Brasília
                    -38.5014, # Salvador
                    -34.8811, # Recife
                    -38.5433, # Fortaleza
                    -48.5044, # Belém
                    -60.0217, # Manaus
                    -51.2090, # Porto Alegre
                    -49.2671, # Curitiba
                    -54.6201, # Campo Grande
                    -56.0979, # Cuiabá
                    -63.9004, # Porto Velho
                    -49.2648, # Goiânia
                    -42.8019, # Teresina
                    -35.2094, # Natal
                    -34.8794, # João Pessoa
                    -35.7353, # Maceió
                    -37.0731, # Aracaju
                    -40.2957, # Vitória
                    -48.5495, # Florianópolis
                    -67.8249, # Rio Branco
                    -60.6758, # Boa Vista
                    -44.2829, # São Luis
                    -48.3243, # Palmas
                    -51.0705  # Macapá
                ]
            })
            
            # Save landmarks
            os.makedirs(os.path.dirname(landmarks_file), exist_ok=True)
            self.landmarks.to_csv(landmarks_file, index=False)
            
        return self.landmarks
    
    def display_landmarks(self):
        """Exibe as cidades disponíveis"""
        if self.landmarks is None:
            self.load_or_create_landmarks()
            
        print("\nCidades disponíveis:")
        for i, (_, landmark) in enumerate(self.landmarks.iterrows()):
            print(f"{i+1}. {landmark['name']}")
    
    def get_route_inputs(self):
        """Obtém entradas do usuário para navegação"""
        if self.landmarks is None:
            self.load_or_create_landmarks()
        
        self.display_landmarks()
        
        while True:
            try:
                source_idx = int(input("\nSelecione a cidade de origem (número): ")) - 1
                if 0 <= source_idx < len(self.landmarks):
                    source = self.landmarks.iloc[source_idx]
                    break
                print("Seleção inválida. Por favor, tente novamente.")
            except ValueError:
                print("Por favor, insira um número.")
        
        while True:
            try:
                dest_idx = int(input("Selecione a cidade de destino (número): ")) - 1
                if 0 <= dest_idx < len(self.landmarks) and dest_idx != source_idx:
                    destination = self.landmarks.iloc[dest_idx]
                    break
                elif dest_idx == source_idx:
                    print("A cidade de destino não pode ser a mesma que a cidade de origem.")
                else:
                    print("Seleção inválida. Por favor, tente novamente.")
            except ValueError:
                print("Por favor, insira um número.")
        
        weight = 'length'    
        source_node = self.city_graph.get_nearest_node((source['latitude'], source['longitude']))
        dest_node = self.city_graph.get_nearest_node((destination['latitude'], destination['longitude']))
        
        return {
            'source': {
                'name': source['name'],
                'node_id': source_node,
                'lat': source['latitude'],
                'lng': source['longitude']
            },
            'destination': {
                'name': destination['name'],
                'node_id': dest_node,
                'lat': destination['latitude'],
                'lng': destination['longitude']
            },
            'weight': weight
        }
        
    def print_route_details(self, route, inputs):
        """Printa detalhes da rota calculada"""
        if not route or 'edge_details' not in route:
            print("Nenhuma rota encontrada.")
            return
            
        print("\n===== RESUMO DA ROTA =====")
        print(f"De: {inputs['source']['name']}")
        print(f"Para: {inputs['destination']['name']}")
        
        if inputs['weight'] == 'length':
            print(f"Otimizado para: Distância mais curta")
            print(f"Distância Total: {route['total_distance']/1000:.2f} km")
            print(f"Tempo Estimado: {route['total_time']/60:.2f} minutos")
            
        print("\n===== DIREÇÕES PASSO A PASSO =====")
        for i, edge in enumerate(route['edge_details']):
            road_name = edge['name'] if isinstance(edge['name'], str) else "Ferrovia não nomeada"
            distance = edge['length']
            time = edge['travel_time']
            
            print(f"{i+1}. Continue on {road_name} for {distance/1000:.2f} km ({time/60:.1f} min)")
            
        print("\nRota calculada com sucesso!") 