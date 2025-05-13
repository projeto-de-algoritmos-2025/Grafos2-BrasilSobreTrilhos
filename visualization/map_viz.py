import folium
import folium.plugins
import matplotlib.pyplot as plt
from IPython.display import display

class MapVisualizer:
    def __init__(self, city_graph):
        self.city_graph = city_graph
    
    def plot_map_with_matplotlib(self, route=None, figsize=(12, 10)):
        """Plotar o mapa usando matplotlib"""
        if self.city_graph.graph is None:
            raise Exception("Grafo não carregado. Crie utilizando load_or_download_map() primeiro.")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Obter coordenadas dos nós
        node_Xs = [float(self.city_graph.graph.nodes[node]['x']) for node in self.city_graph.graph.nodes()]
        node_Ys = [float(self.city_graph.graph.nodes[node]['y']) for node in self.city_graph.graph.nodes()]
        
        # Plotar nós (cidades)
        ax.scatter(node_Xs, node_Ys, s=50, c='#B22222', zorder=2)
        
        # Plotar arestas (ferrovias)
        for u, v, data in self.city_graph.graph.edges(data=True):
            ax.plot([self.city_graph.graph.nodes[u]['x'], self.city_graph.graph.nodes[v]['x']],
                    [self.city_graph.graph.nodes[u]['y'], self.city_graph.graph.nodes[v]['y']],
                    c='#FFD700', linewidth=1.5, alpha=0.7, zorder=1)
        
        # Adicionar rótulos de cidade
        for node in self.city_graph.graph.nodes():
            x = self.city_graph.graph.nodes[node]['x']
            y = self.city_graph.graph.nodes[node]['y']
            name = self.city_graph.graph.nodes[node].get('name', f'Node {node}')
            ax.annotate(name, (x, y), fontsize=8, ha='right', va='bottom')
        
        # Destacar a rota se fornecida
        if route and 'path' in route:
            route_x = []
            route_y = []
            for node in route['path']:
                route_x.append(self.city_graph.graph.nodes[node]['x'])
                route_y.append(self.city_graph.graph.nodes[node]['y'])
            
            ax.plot(route_x, route_y, c='red', linewidth=3, zorder=3)
            
            # Destacar início e fim
            ax.scatter([route_x[0], route_x[-1]], [route_y[0], route_y[-1]], 
                      s=100, c=['green', 'red'], marker='*', edgecolors='black', zorder=4)
        
        # Definir a extensão do Brasil
        ax.set_xlim([-75, -35])
        ax.set_ylim([-35, 5])
        
        plt.title('Rede Ferroviária Brasileira')
        plt.tight_layout()
        return fig, ax
    
    def create_folium_map(self, route=None):
        """Create an interactive map using folium"""
        if self.city_graph.graph is None:
            raise Exception("Graph not loaded. Call load_or_download_map() first.")
        
        # Obter o centro do mapa (centro do Brasil - aproximadamente Brasília)
        center_lat = -15.7797
        center_lng = -47.9297
        
        # Criar um mapa com tiles do OpenStreetMap (mais confiável)
        m = folium.Map(
            location=[center_lat, center_lng], 
            zoom_start=4,
            tiles="OpenStreetMap",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        )
        
        # Adicionar todas as ferrovias ao mapa
        for u, v, data in self.city_graph.graph.edges(data=True):
            # Obter coordenadas dos nós
            u_lat = self.city_graph.graph.nodes[u]['y']
            u_lng = self.city_graph.graph.nodes[u]['x']
            v_lat = self.city_graph.graph.nodes[v]['y']
            v_lng = self.city_graph.graph.nodes[v]['x']
            
            # Adicionar aresta ao mapa
            folium.PolyLine(
                [(u_lat, u_lng), (v_lat, v_lng)],
                color='#FFD700',  # Cor dourada para ferrovias
                weight=2.5,
                opacity=0.7,
                tooltip=data.get('name', 'Ferrovia')
            ).add_to(m)
        
        # Adicionar marcadores de cidade
        for node, data in self.city_graph.graph.nodes(data=True):
            folium.CircleMarker(
                location=[data['y'], data['x']],
                radius=5,
                color='#B22222',  # Dark red
                fill=True,
                fill_color='#B22222',
                fill_opacity=0.7,
                tooltip=data.get('name', f'Node {node}')
            ).add_to(m)
        
        # Adicionar a rota se fornecida
        if route and 'path' in route:
            # Obter coordenadas para a rota
            route_coords = []
            city_names = []
            for node in route['path']:
                y = self.city_graph.graph.nodes[node]['y']
                x = self.city_graph.graph.nodes[node]['x']
                name = self.city_graph.graph.nodes[node].get('name', f'Node {node}')
                route_coords.append([y, x])
                city_names.append(name)
            
            # Adicionar a rota ao mapa
            folium.PolyLine(
                route_coords, 
                color='red',
                weight=4,
                opacity=0.8,
                tooltip='Rota de Trem'
            ).add_to(m)
            
            # Adicionar marcadores para início e fim
            folium.Marker(
                location=route_coords[0],
                popup=f"Início: {city_names[0]}",
                icon=folium.Icon(color='green', icon='train', prefix='fa')
            ).add_to(m)
            
            folium.Marker(
                location=route_coords[-1],
                popup=f"End: {city_names[-1]}",
                icon=folium.Icon(color='red', icon='train', prefix='fa')
            ).add_to(m)
            
            # Adicionar marcadores para cidades intermediárias
            for i in range(1, len(route_coords)-1):
                folium.CircleMarker(
                    location=route_coords[i],
                    radius=7,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.7,
                    tooltip=f"Stop: {city_names[i]}"
                ).add_to(m)
            
            # Adicionar resumo da rota
            route_summary = f"""
                <h3>Resumo da Rota Ferroviária</h3>
                <ul>
                    <li><b>De:</b> {city_names[0]}</li>
                    <li><b>Para:</b> {city_names[-1]}</li>
                    <li><b>Distância Total:</b> {route['total_distance']/1000:.2f} km</li>
                    <li><b>Tempo Estimado:</b> {route['total_time']/3600:.2f} horas</li>
                    <li><b>Paradas:</b> {', '.join(city_names[1:-1])}</li>
                </ul>
            """
            
            folium.Marker(
                location=route_coords[0],
                popup=folium.Popup(route_summary, max_width=300)
            ).add_to(m)
        
        return m
    
    def display_map_in_notebook(self, route=None):
        """Display the map in a Jupyter notebook"""
        m = self.create_folium_map(route)
        display(m)
        
    def save_map_to_html(self, filepath, route=None):
        """Save the map to an HTML file"""
        m = self.create_folium_map(route)
        
        # Adicionar mensagem de fallback caso os tiles não carreguem
        m.get_root().header.add_child(folium.Element("""
        <style>
        .leaflet-container {
            background-color: #f2f2f2;
        }
        </style>
        <script>
        var timeoutID = setTimeout(function() {
            if (document.querySelector('.leaflet-tile-pane').children.length < 1) {
                alert('Os tiles do mapa não carregaram. Por favor, verifique sua conexão com a internet.');
            }
        }, 5000);
        </script>
        """))
        
        m.save(filepath)
        print(f"Mapa salvo em {filepath}") 