import heapq
from collections import defaultdict, deque
import json
from typing import Dict, List, Tuple, Optional
import math

class KochiMetroNetwork:
    def __init__(self):
        # Initialize the metro network graph
        self.graph = defaultdict(list)
        self.stations = set()
        self.station_info = {}
        
        # Build the Kochi Metro network
        self._build_network()
    
    def _build_network(self):
        """Build the Kochi Metro network with stations and connections"""
        
        # Kochi Metro Line 1 (Blue Line) - Main operational stations
        line1_stations = [
            "Aluva", "Pulinchodu", "Companypady", "Ambattukavu", "Muttom",
            "Kalamassery", "Cusat", "Pathadipalam", "Edapally", "Changampuzha Park",
            "Palarivattom", "J.L.N Stadium", "Kaloor", "Lissie", "M.G Road",
            "Maharajas", "Ernakulam South", "Kadavanthra", "Elamkulam",
            "Vyttila", "Thaikoodam", "Petta", "Thripunithura"
        ]
        
        # Add stations to our network
        for station in line1_stations:
            self.stations.add(station)
            # Store station information (can be expanded with coordinates, facilities, etc.)
            self.station_info[station] = {
                'line': 'Blue Line',
                'zone': self._get_zone(station)
            }
        
        # Add connections between consecutive stations on Line 1
        for i in range(len(line1_stations) - 1):
            station1 = line1_stations[i]
            station2 = line1_stations[i + 1]
            
            # Calculate realistic travel times, distances, and costs
            travel_time = self._calculate_travel_time(station1, station2)
            distance = self._calculate_distance(station1, station2)
            cost = self._calculate_cost(station1, station2)
            
            # Add bidirectional edges
            self.add_connection(station1, station2, travel_time, distance, cost)
            self.add_connection(station2, station1, travel_time, distance, cost)
    
    def add_connection(self, station1: str, station2: str, travel_time: float, 
                      distance: float, cost: float):
        """Add a connection between two stations"""
        self.graph[station1].append({
            'destination': station2,
            'travel_time': travel_time,
            'distance': distance,
            'cost': cost
        })
    
    def _get_zone(self, station: str) -> str:
        """Determine the zone of a station for fare calculation"""
        # Simplified zone classification
        if station in ["Aluva", "Pulinchodu", "Companypady"]:
            return "Zone 3"
        elif station in ["Thripunithura", "Petta", "Thaikoodam"]:
            return "Zone 3"
        elif station in ["M.G Road", "Maharajas", "Ernakulam South", "Lissie"]:
            return "Zone 1"
        else:
            return "Zone 2"
    
    def _calculate_travel_time(self, station1: str, station2: str) -> float:
        """Calculate travel time between adjacent stations (in minutes)"""
        # Base time + some variation based on station characteristics
        base_time = 2.5  # Average 2.5 minutes between stations
        
        # Add variation for specific segments
        special_segments = {
            ("Aluva", "Pulinchodu"): 3.0,
            ("Edapally", "Changampuzha Park"): 2.0,
            ("M.G Road", "Maharajas"): 1.5,
            ("Vyttila", "Thaikoodam"): 3.5
        }
        
        segment = (station1, station2)
        reverse_segment = (station2, station1)
        
        return special_segments.get(segment, special_segments.get(reverse_segment, base_time))
    
    def _calculate_distance(self, station1: str, station2: str) -> float:
        """Calculate distance between adjacent stations (in km)"""
        # Average distance between stations
        base_distance = 1.2
        
        # Specific distances for certain segments
        special_distances = {
            ("Aluva", "Pulinchodu"): 1.8,
            ("Vyttila", "Thaikoodam"): 2.1,
            ("M.G Road", "Maharajas"): 0.8
        }
        
        segment = (station1, station2)
        reverse_segment = (station2, station1)
        
        return special_distances.get(segment, special_distances.get(reverse_segment, base_distance))
    
    def _calculate_cost(self, station1: str, station2: str) -> float:
        """Calculate cost between adjacent stations (in INR)"""
        # Base cost per station
        return 5.0  # ₹5 per station hop (simplified)

class MetroRouteOptimizer:
    def __init__(self, network: KochiMetroNetwork):
        self.network = network
    
    def dijkstra_multi_criteria(self, start_station: str, cost_weight: float = 0.3, 
                               time_weight: float = 0.4, stops_weight: float = 0.3) -> Dict:
        """
        Dijkstra's algorithm with multi-criteria optimization
        
        Args:
            start_station: Starting station
            cost_weight: Weight for cost factor (0-1)
            time_weight: Weight for time factor (0-1)
            stops_weight: Weight for stops factor (0-1)
        
        Returns:
            Dictionary with shortest paths to all stations
        """
        
        if start_station not in self.network.stations:
            raise ValueError(f"Station '{start_station}' not found in the network")
        
        # Initialize distances and previous stations
        distances = {station: float('inf') for station in self.network.stations}
        previous = {station: None for station in self.network.stations}
        costs = {station: float('inf') for station in self.network.stations}
        times = {station: float('inf') for station in self.network.stations}
        stops = {station: float('inf') for station in self.network.stations}
        
        # Set start station
        distances[start_station] = 0
        costs[start_station] = 0
        times[start_station] = 0
        stops[start_station] = 0
        
        # Priority queue: (distance, station)
        pq = [(0, start_station)]
        visited = set()
        
        while pq:
            current_distance, current_station = heapq.heappop(pq)
            
            if current_station in visited:
                continue
            
            visited.add(current_station)
            
            # Check all neighbors
            for connection in self.network.graph[current_station]:
                neighbor = connection['destination']
                
                if neighbor in visited:
                    continue
                
                # Calculate new metrics
                new_cost = costs[current_station] + connection['cost']
                new_time = times[current_station] + connection['travel_time']
                new_stops = stops[current_station] + 1
                
                # Normalize factors for fair comparison
                normalized_cost = new_cost / 100  # Normalize cost
                normalized_time = new_time / 60   # Normalize time
                normalized_stops = new_stops / 25 # Normalize stops
                
                # Calculate composite distance
                composite_distance = (cost_weight * normalized_cost + 
                                    time_weight * normalized_time + 
                                    stops_weight * normalized_stops)
                
                if composite_distance < distances[neighbor]:
                    distances[neighbor] = composite_distance
                    costs[neighbor] = new_cost
                    times[neighbor] = new_time
                    stops[neighbor] = new_stops
                    previous[neighbor] = current_station
                    heapq.heappush(pq, (composite_distance, neighbor))
        
        return {
            'distances': distances,
            'costs': costs,
            'times': times,
            'stops': stops,
            'previous': previous
        }
    
    def get_path(self, start_station: str, end_station: str, previous: Dict) -> List[str]:
        """Reconstruct the path from start to end station"""
        path = []
        current = end_station
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        
        if path[0] != start_station:
            return []  # No path found
        
        return path
    
    def find_optimal_routes(self, start_station: str, cost_weight: float = 0.3,
                           time_weight: float = 0.4, stops_weight: float = 0.3) -> Dict:
        """Find optimal routes from start station to all other stations"""
        
        results = self.dijkstra_multi_criteria(start_station, cost_weight, time_weight, stops_weight)
        
        routes = {}
        for station in self.network.stations:
            if station != start_station and results['distances'][station] != float('inf'):
                path = self.get_path(start_station, station, results['previous'])
                routes[station] = {
                    'path': path,
                    'total_cost': round(results['costs'][station], 2),
                    'total_time': round(results['times'][station], 2),
                    'total_stops': int(results['stops'][station]),
                    'composite_score': round(results['distances'][station], 4)
                }
        
        return routes

class MetroUI:
    def __init__(self):
        self.network = KochiMetroNetwork()
        self.optimizer = MetroRouteOptimizer(self.network)
    
    def display_stations(self):
        """Display all available stations"""
        print("\n" + "="*50)
        print("KOCHI METRO STATIONS")
        print("="*50)
        
        stations_list = sorted(list(self.network.stations))
        for i, station in enumerate(stations_list, 1):
            zone = self.network.station_info[station]['zone']
            print(f"{i:2d}. {station:20} ({zone})")
    
    def get_user_input(self) -> Tuple[str, float, float, float]:
        """Get user input for starting station and preferences"""
        
        self.display_stations()
        
        print("\n" + "-"*50)
        
        # Get starting station
        while True:
            start_station = input("Enter your starting station: ").strip()
            
            # Check if input is a number (station index)
            if start_station.isdigit():
                idx = int(start_station) - 1
                stations_list = sorted(list(self.network.stations))
                if 0 <= idx < len(stations_list):
                    start_station = stations_list[idx]
                    break
                else:
                    print("Invalid station number. Please try again.")
                    continue
            
            # Check if station name exists
            matching_stations = [s for s in self.network.stations 
                               if start_station.lower() in s.lower()]
            
            if len(matching_stations) == 1:
                start_station = matching_stations[0]
                break
            elif len(matching_stations) > 1:
                print(f"Multiple matches found: {', '.join(matching_stations)}")
                print("Please be more specific.")
            else:
                print("Station not found. Please try again.")
        
        # Get user preferences
        print("\nOptimization Preferences (weights should sum to 1.0):")
        print("Default: Cost=0.3, Time=0.4, Stops=0.3")
        
        use_default = input("Use default weights? (y/n): ").lower().strip()
        
        if use_default == 'y':
            return start_station, 0.3, 0.4, 0.3
        else:
            while True:
                try:
                    cost_weight = float(input("Cost weight (0-1): "))
                    time_weight = float(input("Time weight (0-1): "))
                    stops_weight = float(input("Stops weight (0-1): "))
                    
                    if abs(cost_weight + time_weight + stops_weight - 1.0) < 0.001:
                        return start_station, cost_weight, time_weight, stops_weight
                    else:
                        print("Weights should sum to 1.0. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter numbers between 0 and 1.")
    
    def display_results(self, start_station: str, routes: Dict):
        """Display the optimization results"""
        
        print(f"\n" + "="*80)
        print(f"OPTIMAL ROUTES FROM: {start_station.upper()}")
        print("="*80)
        
        # Sort routes by composite score (best first)
        sorted_routes = sorted(routes.items(), key=lambda x: x[1]['composite_score'])
        
        print(f"{'DESTINATION':<20} {'COST':<8} {'TIME':<8} {'STOPS':<6} {'ROUTE'}")
        print("-" * 80)
        
        for destination, route_info in sorted_routes:
            path_str = " → ".join(route_info['path'])
            if len(path_str) > 35:
                path_str = path_str[:32] + "..."
            
            print(f"{destination:<20} ₹{route_info['total_cost']:<7.0f} "
                  f"{route_info['total_time']:<7.1f}m {route_info['total_stops']:<6d} "
                  f"{path_str}")
    
    def run(self):
        """Main application loop"""
        print("KOCHI METRO ROUTE OPTIMIZER")
        print("Find the most efficient routes using Dijkstra's Algorithm")
        
        while True:
            try:
                # Get user input
                start_station, cost_weight, time_weight, stops_weight = self.get_user_input()
                
                print(f"\nOptimizing routes from {start_station}...")
                print(f"Weights - Cost: {cost_weight}, Time: {time_weight}, Stops: {stops_weight}")
                
                # Find optimal routes
                routes = self.optimizer.find_optimal_routes(
                    start_station, cost_weight, time_weight, stops_weight
                )
                
                # Display results
                self.display_results(start_station, routes)
                
                # Ask if user wants to continue
                print(f"\n" + "="*80)
                continue_choice = input("Would you like to plan another route? (y/n): ").lower().strip()
                
                if continue_choice != 'y':
                    print("\nThank you for using Kochi Metro Route Optimizer!")
                    break
                    
            except KeyboardInterrupt:
                print("\n\nThank you for using Kochi Metro Route Optimizer!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                print("Please try again.")

if __name__ == "__main__":
    # Create and run the metro route optimizer
    app = MetroUI()
    app.run()