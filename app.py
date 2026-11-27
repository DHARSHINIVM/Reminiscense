from flask import Flask, render_template, request, jsonify
from memory import EpisodicMemory
import os
from datetime import datetime


app = Flask(__name__)

memory = EpisodicMemory()

IMAGE_FOLDER = "static/memories"

os.makedirs(IMAGE_FOLDER, exist_ok=True)


@app.route("/")
def dashboard():

    memories = memory.get_memories()

    return render_template(
        "dashboard.html",
        memories=memories
    )


@app.route("/upload_image", methods=["POST"])
def upload_image():

    image_data = request.get_data()

    if not image_data:
        return jsonify({
            "status": "error",
            "message": "No image received"
        }), 400

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    ) + ".jpg"

    filepath = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    with open(filepath, "wb") as file:
        file.write(image_data)

    print("IMAGE RECEIVED:", filename)

    # Return ONLY the filename
    return filename, 200

@app.route("/add_memory", methods=["POST"])
def add_memory():

    data = request.json

    memory_id = memory.add_memory(

        event=data.get(
            "event",
            "Memory captured"
        ),

        location=data.get(
            "location",
            "Unknown"
        ),

        activity=data.get(
            "activity",
            "Unknown"
        ),

        cognitive_state=data.get(
            "cognitive_state",
            "Engaged"
        ),

        accel_x=data.get(
            "accel_x",
            0
        ),

        accel_y=data.get(
            "accel_y",
            0
        ),

        accel_z=data.get(
            "accel_z",
            0
        ),

        image_path=data.get(
            "image_path"
        )
    )

    return jsonify({
        "status": "success",
        "memory_id": memory_id
    })


@app.route("/graph")
def graph():

    nodes = []

    for node, data in memory.graph.nodes(
        data=True
    ):

        nodes.append({
            "id": node,
            "label": data.get(
                "label",
                node
            ),
            "type": data.get(
                "type",
                "unknown"
            )
        })


    edges = []

    for source, target, data in memory.graph.edges(
        data=True
    ):

        edges.append({
            "source": source,
            "target": target,
            "relation": data.get(
                "relation",
                ""
            )
        })


    return jsonify({
        "nodes": nodes,
        "edges": edges
    })


@app.route("/search")
def search():

    query = request.args.get(
        "q",
        ""
    )

    return jsonify(
        memory.search(query)
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )