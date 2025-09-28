from flask import Flask, render_template, request
from dijkstra import KochiMetroNetwork, MetroRouteOptimizer

app = Flask(__name__)

# Initialize metro network and optimizer
network = KochiMetroNetwork()
optimizer = MetroRouteOptimizer(network)

@app.route("/", methods=["GET", "POST"])
def index():
    stations = sorted(list(network.stations))
    results = None
    error = None

    if request.method == "POST":
        start_station = request.form.get("start_station")
        try:
            cost_weight = float(request.form.get("cost_weight", 0.3))
            time_weight = float(request.form.get("time_weight", 0.4))
            stops_weight = float(request.form.get("stops_weight", 0.3))

            if abs(cost_weight + time_weight + stops_weight - 1.0) > 0.001:
                error = "Weights must sum to 1.0"
            elif start_station not in network.stations:
                error = "Invalid starting station"
            else:
                # Calculate optimal routes
                results = optimizer.find_optimal_routes(
                    start_station, cost_weight, time_weight, stops_weight
                )
                # Sort by composite score
                results = dict(sorted(results.items(), key=lambda x: x[1]["composite_score"]))
        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        stations=stations,
        results=results,
        error=error
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
