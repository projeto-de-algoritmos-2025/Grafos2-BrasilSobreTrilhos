import os
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from graph import CityGraph
from ui import NavigationUI
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualization'))
from map_viz import MapVisualizer

def main():
    print("=" * 50)
    print("Brasil sobre Trilhos")
    print("Este sistema demonstra o algoritmo de Dijkstra para encontrar rotas ideais na rede ferroviária brasileira")
    print("=" * 50)
    
    # Inicializa o grafo de cidades
    city_graph = CityGraph()
    print("\nCarregando dados da rede ferroviária do Brasil...")
    city_graph.load_or_download_map()
    print("Rede ferroviária carregada com sucesso!")
    
    # Inicializa a interface de navegação
    ui = NavigationUI(city_graph)
    
    # Inicializa o visualizador
    visualizer = MapVisualizer(city_graph)
    
    while True:
        print("\n" + "=" * 50)
        print("Menu de Navegação Ferroviária:")
        print("1. Encontrar uma rota de trem")
        print("2. Exibir cidades")
        print("3. Sair")
        
        choice = input("\nEscolha uma opção (1-3): ")
        
        if choice == '1':
            # Get route inputs
            inputs = ui.get_route_inputs()
            
            print("\nCalculando rota ferroviária...")
            route = city_graph.run_dijkstra(
                inputs['source']['node_id'], 
                inputs['destination']['node_id'],
                weight=inputs['weight']
            )
            
            # Print route details
            ui.print_route_details(route, inputs)
            
            # Save the map to an HTML file
            output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'railway_route_map.html')
            visualizer.save_map_to_html(output_file, route)
            
            print(f"\nMapa de rota ferroviária salvo para {output_file}")
            print("Você pode abrir este arquivo em um navegador da web para visualizar a rota.")
            
        elif choice == '2':
            ui.display_landmarks()
            
        elif choice == '3':
            print("\nObrigado por usar o Sistema Brasil sobre Trilhos!")
            print("Saindo...")
            break
            
        else:
            print("Escolha inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main() 