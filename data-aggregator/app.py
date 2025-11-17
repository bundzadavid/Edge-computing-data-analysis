from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Kubernetes API endpoint for Grafana Operator dashboard
GRAFANA_OPERATOR_ENDPOINT = "http://grafana:3000/apis/dashboard.grafana.app/v1beta1/namespaces/default/dashboards/b769e395-d791-4d3c-8d79-2d6e7bbd4c85"

# Your API token
API_TOKEN = "glsa_Ty78fRqIZGLMtxuTH3EHgma5a1NeCZ73_c5b78868"

# Headers with the token
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/live/update-dashboard', methods=['PUT'])
def update_dashboard():
    data = request.json
    field = data.get("field")
    aggr = data.get("aggr")
    window = data.get("window", "1m")

    # Fetch the current dashboard JSON from Grafana Operator API
    response = requests.get(GRAFANA_OPERATOR_ENDPOINT, headers=headers)
    if response.status_code != 200:
        return jsonify({"status": "error", "details": "Failed to fetch the dashboard"}), 500

    dashboard = response.json()

    try:
        # Modify the Flux query in targets[0]
        new_query = f'''from(bucket: "my_db")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "environment_data")
  |> filter(fn: (r) => r["_field"] == "{field}")
  |> aggregateWindow(every: {window}, fn: {aggr}, createEmpty: false)
  |> yield(name: "{aggr}")'''

        dashboard["spec"]["panels"][0]["targets"][0]["query"] = new_query

        # Send the updated dashboard JSON back to Grafana Operator
        put_response = requests.put(GRAFANA_OPERATOR_ENDPOINT, headers=headers, json=dashboard)

        if put_response.status_code == 200:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "details": put_response.text}), 500

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
