from flask import Flask, jsonify, request
import pickle
import os
import glob
import urllib.parse
import json

app = Flask(__name__)

@app.route('/api/v2/<path:subpath>', methods=['GET'])
def get_dynatrace_data(subpath):
    # Create a mapping of URL paths to pickle files
    url_to_pickle = {}
    for file in glob.glob("pickle_test_inputs/*_response.pkl"):
        # Extract the URL path from the filename and decode it
        url_path = file.split("_", 2)[2].rsplit("_", 1)[0]
        decoded_url_path = urllib.parse.unquote(url_path)

        # Only keep the part after 'api/v2/' in the URL path
        sub_path = decoded_url_path.split('api/v2/', 1)[-1]
        url_to_pickle[sub_path] = file

    # Print url_to_pickle mapping
    print("url_to_pickle:", url_to_pickle)

    # Remove parameters from subpath
    subpath = subpath.split('?', 1)[0]

    # Find the pickle file corresponding to the requested URL
    for path in sorted(url_to_pickle, key=len, reverse=True):
        if subpath.startswith(path):
            pickle_file_path = url_to_pickle[path]
            break
    else:
        return jsonify({"error": f"No pickle file found for endpoint: {subpath}"}), 404

    # Print subpath and pickle_file_path
    print("subpath:", subpath)
    print("pickle_file_path:", pickle_file_path)

    # Load pickle file
    with open(pickle_file_path, "rb") as pkl_file:
        data = pickle.load(pkl_file)

    # Return as JSON
    return data.json()

if __name__ == "__main__":
    app.run(port=12345)  # Run server on port 12345
